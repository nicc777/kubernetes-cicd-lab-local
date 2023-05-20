import sys
import os
import string
import traceback
import json
from datetime import datetime
import copy
import shutil
import re

import yaml
try:
    from yaml import CLoader as Loader, CDumper as Dumper
except ImportError:
    from yaml import Loader, Dumper


NAMESPACE_ALLOWED_CHARS = '{}{}'.format(string.ascii_letters, string.digits)
CHAR_REPLACEMENT = '-'
DEFAULT_PATTERNS_TO_IGNORE = [
    re.compile('.*\.git.*'),
    re.compile('.*README\.md'),
]


def _dir_walk_level(some_dir, level=1):
    # FROM https://stackoverflow.com/questions/229186/os-walk-without-digging-into-directories-below
    some_dir = some_dir.rstrip(os.path.sep)
    assert os.path.isdir(some_dir)
    num_sep = some_dir.count(os.path.sep)
    for root, dirs, files in os.walk(some_dir):
        yield root, dirs, files
        num_sep_this = root.count(os.path.sep)
        if num_sep + level <= num_sep_this:
            del dirs[:]


def print_variable_content(variable_name: str, content: str):
    name_len = len(variable_name) + 12
    print('-'*name_len)
    print('---   {}   ---'.format(variable_name))
    print('-'*name_len)
    print(content)
    print('~'*name_len)


def get_utc_timestamp(with_decimal: bool=False): # pragma: no cover
    epoch = datetime(1970,1,1,0,0,0)
    now = datetime.utcnow()
    timestamp = (now - epoch).total_seconds()
    if with_decimal:
        return timestamp
    return int(timestamp)


def create_directory(path: str):
    try:
        os.makedirs(path, exist_ok=True)
    except:
        traceback.print_exc()
        sys.exit(127)


def get_file_size(file_path: str)->int:
    size = None
    try:
        size = os.path.getsize(filename=file_path)
    except:
        pass
    return size


def pattern_match(input_str: str, patterns: list)->bool:
    try:
        for p in patterns:
            if p.match(input_str) is not None:
                return True
    except:
        pass
    return False


def list_files(directory: str, recurse: bool=False, include_size: bool=False, result: dict=dict(), ignore_patterns: list=DEFAULT_PATTERNS_TO_IGNORE)->dict:
    result = dict()
    try:
        for root, dirs, files in _dir_walk_level(some_dir=directory, level=0):
            if recurse is True:
                for dir in dirs:
                    if pattern_match(input_str=dir, patterns=ignore_patterns) is False:
                        result = {
                            **result,
                            **list_files(
                                directory='{}{}{}'.format(root, os.sep, dir),
                                recurse=recurse,
                                include_size=include_size,
                                result=copy.deepcopy(result)
                            )
                        }
            for file in files:
                if pattern_match(input_str=file, patterns=ignore_patterns) is False:
                    file_full_path = '{}{}{}'.format(root, os.sep, file)
                    file_metadata = dict()
                    file_metadata['size'] = None
                    if include_size is True:
                        file_metadata['size'] = get_file_size(file_path=file_full_path)
                    result[file_full_path] = copy.deepcopy(file_metadata)
    except:
        traceback.print_exc()
        sys.exit(127)
    return copy.deepcopy(result)


def copy_file(source_file_path: str, destination_directory: str, new_name: str=None)->str:
    try:
        parts = source_file_path.split(os.sep)
        source_file_name = parts[-1]
        final_destination = '{}{}'.format(destination_directory, os.sep)
        if new_name is not None:
            final_destination = '{}{}'.format(final_destination, new_name)
        else:
            final_destination = '{}{}'.format(final_destination, source_file_name)
        shutil.copyfile(source_file_path, final_destination)
        return final_destination
    except:
        traceback.print_exc()
        sys.exit(127)


def parse_args()->tuple:
    # Expecting: app.py ${env.BUILD_NUMBER} ${REPO_APP_DIR} ${APP_SOURCE_BRANCH} ${REPO_MAINT_DIR} lab awesome-application app-repo maint-repo
    args_result = list()
    if len(sys.argv) == 9:
        for i, arg in enumerate(sys.argv):
            args_result.append(arg)
            print(f"Argument {i:>6}: {arg}")
        args_result.pop(0)
    else:
        raise Exception('Unexpected number of command line arguments')
    return tuple(args_result)


def build_final_namespace(input_namespace: str)->str:
    final_namespace = ''
    for letter in input_namespace:
        if letter not in NAMESPACE_ALLOWED_CHARS:
            final_namespace = '{}{}'.format(final_namespace, CHAR_REPLACEMENT)
        else:
            final_namespace = '{}{}'.format(final_namespace, letter)
    return final_namespace


def build_final_branch_name(input_branch: str)->str:
    if len(input_branch) > 12:
        return input_branch[0:12]
    return input_branch


def read_text_file(path_to_file: str)->str:
    content = ''
    with open(path_to_file, 'r') as f:
        content = f.read()
    return content


def variable_replacement_and_write_text_file(destination_file: str, file_content: str, variables: dict):
    try:
        for variable_name, replacement_value in variables.items():
            file_content = file_content.replace(variable_name, '{}'.format(replacement_value))
        with open(destination_file, 'w') as f:
            f.write(file_content)
        print_variable_content(variable_name='variable_replacement_and_write_text_file(): destination_file={}'.format(destination_file), content=file_content)
    except:
        traceback.print_exc()
        sys.exit(127)


def read_suspend_configuration(deployment_environment: str='lab')->dict:
    config = dict()
    try:
        yaml_data = read_text_file(path_to_file='configs/application-suspend.yaml')
        for data in yaml.load_all(yaml_data, Loader=Loader):
            if 'environment' in data:
                if isinstance(data['environment'], list):
                    for environment_data in  data['environment']:
                        if environment_data['name'] == deployment_environment:
                            config['initial-deployment-uptime'] = environment_data['initial-deployment-uptime']
                            config['suspend-duration'] = environment_data['suspend-duration']
                            config['maximum-uptime'] = environment_data['maximum-uptime']
    except: 
        traceback.print_exc()
        sys.exit(127)
    return config


def read_helm_application_deployment_template(deployment_environment: str='lab', application_name: str='awesome-application')->str:
    template_data = ''
    try:
        file_path = 'helm_templates/{}/{}/argocd-application/application.yaml'.format(deployment_environment, application_name)
        template_data = read_text_file(path_to_file=file_path)
    except: 
        traceback.print_exc()
        sys.exit(127)
    return template_data


def prepare_final_application_deployment_manifest(
    template_data: str,
    namespace: str,
    expires: int,
    suspend_starts: int,
    suspend_ends: int,
    max_uptime: int,
    branch: str,
    jenkins_build_nr: int,
    repo_source: str
)->str:
    template_data = template_data.replace('__NAMESPACE__',        '{}'.format( namespace        ))
    template_data = template_data.replace('__EXPIRES__',          '{}'.format( expires          ))
    template_data = template_data.replace('__SUSPEND_STARTS__',   '{}'.format( suspend_starts   ))
    template_data = template_data.replace('__SUSPENDS_ENDS__',    '{}'.format( suspend_ends     ))
    template_data = template_data.replace('__MAX_UPTIME__',       '{}'.format( max_uptime       ))
    template_data = template_data.replace('__BRANCH__',           '{}'.format( branch           ))
    template_data = template_data.replace('__JENKINS_BUILD_NR__', '{}'.format( jenkins_build_nr ))
    template_data = template_data.replace('__REPO_SOURCE__',      '{}'.format( repo_source      ))
    return template_data


def create_deployment_directories(namespace_name: str, target_deployment_dir: str)->tuple:
    try:
        application_directory = '{}/deployments/lab/application-manifests/{}'.format(target_deployment_dir, namespace_name)
        helm_deployment_directory = '{}/deployments/lab/helm-manifests/{}'.format(target_deployment_dir, namespace_name)
        helm_deployment_templates_directory = '{}/deployments/lab/helm-manifests/{}/templates'.format(target_deployment_dir, namespace_name)
        create_directory(path=application_directory)
        create_directory(path=helm_deployment_directory)
        create_directory(path=helm_deployment_templates_directory)
        print('='*80)
        print('application_directory               : {}'.format(application_directory))
        print('helm_deployment_directory           : {}'.format(helm_deployment_directory))
        print('helm_deployment_templates_directory : {}'.format(helm_deployment_templates_directory))
        print('='*80)
        return (application_directory, helm_deployment_directory, helm_deployment_templates_directory)
    except: 
        traceback.print_exc()
        sys.exit(127)


def copy_application_manifests_to_deployment_directory(source_directory: str, namespace_name: str, target_deployment_dir: str, variables: dict=dict(), recurse_directory: bool=True, only_kubernetes_manifests: bool=False):
    try:
        files_to_copy = list_files(directory=source_directory, recurse=recurse_directory)
        print('source_directory: {}'.format(source_directory))
        print_variable_content(variable_name='files_to_copy', content=files_to_copy)
        for file in list(files_to_copy.keys()):
            ext = file.split('.')[-1]
            if ext not in ('yaml', 'json', 'yml',):
                if only_kubernetes_manifests is False:
                    copy_file(source_file_path=file, destination_directory=target_deployment_dir)
            else:
                content = read_text_file(path_to_file=file)
                file_name = file.split('/')[-1]
                variable_replacement_and_write_text_file(destination_file='{}/{}'.format(target_deployment_dir, file_name), file_content=content, variables=variables)
    except: 
        traceback.print_exc()
        sys.exit(127)


def get_app_version_from_version_file(source_dir: str):
    try:
        data = ''
        with open('{}/VERSION'.format(source_dir), 'r') as f:
            data = f.read()
        data = ''.join(data.split())
        if len(data) > 0:
            return data
    except:
        print('UNABLE TO DETERMINE APP VERSION')
    return '0.0.0'  # Equivalent of "unknown" version


def main():
    print('Starting with integration')
    try:
        now = get_utc_timestamp(with_decimal=False)
        build_nr, app_dir, app_branch, maint_dir, deployment_environment, application_name, repo_source, maintenance_repo = parse_args()
        interim_namespace_name = 'app-{}-{}'.format(
            build_final_branch_name(input_branch=app_branch),
            build_nr
        )
        namespace_name = build_final_namespace(input_namespace=interim_namespace_name)
        print('> Final namespace Name: {}'.format(namespace_name))
        deployment_config = read_suspend_configuration(deployment_environment=deployment_environment)
        print("> Deployment Configuration: {}".format(json.dumps(deployment_config)))
        helm_application_deployment_template_data = read_helm_application_deployment_template(deployment_environment=deployment_environment, application_name=application_name)

        # Create directories for the application deployment
        target_application_manifest_directory, target_helm_deployment_directory, helm_deployment_templates_directory = create_deployment_directories(namespace_name=namespace_name, target_deployment_dir=maint_dir)

        # Prepare variables
        variables = dict()
        variables['__NAMESPACE__'] = namespace_name
        variables['__EXPIRES__'] = now + deployment_config['maximum-uptime']
        variables['__SUSPEND_STARTS__'] = now + deployment_config['initial-deployment-uptime']
        variables['__SUSPENDS_ENDS__'] = now + deployment_config['maximum-uptime'] + deployment_config['suspend-duration']
        variables['__MAX_UPTIME__'] = deployment_config['maximum-uptime']
        variables['__BRANCH__'] = app_branch
        variables['__JENKINS_BUILD_NR__'] = int(build_nr)
        variables['__REPO_SOURCE__'] = repo_source
        variables['__MAINTENANCE_REPO__'] = maintenance_repo
        variables['__APP_VERSION__'] = get_app_version_from_version_file(source_dir=app_dir)
        variables['__TARGET_HELM_DEPLOYMENT_DIRECTORY__'] = 'deployments/{}/helm-manifests/{}'.format(deployment_environment, namespace_name)
        print_variable_content(variable_name='variables', content=json.dumps(variables))

        # Write application manifest
        variable_replacement_and_write_text_file(destination_file='{}/deployments/lab/application-manifests/{}.yaml'.format(maint_dir, namespace_name), file_content=helm_application_deployment_template_data, variables=variables)

        # Copy the manifests from the application repository to the Helm templates directory
        copy_application_manifests_to_deployment_directory(source_directory=app_dir, namespace_name=namespace_name, target_deployment_dir=helm_deployment_templates_directory, variables=variables, recurse_directory=True, only_kubernetes_manifests=True)

        # Copy the HELM Chart and values to the helm deployment target directory
        copy_application_manifests_to_deployment_directory(
            source_directory='{}/helm_templates/{}/{}/helm-chart'.format(
                maint_dir,
                deployment_environment,
                application_name
            ), 
            namespace_name=namespace_name,
            target_deployment_dir=target_helm_deployment_directory,
            variables=variables,
            recurse_directory=False
        )

        # Copy the HELM chart Templates to the helm deployment templates target directory
        copy_application_manifests_to_deployment_directory(
            source_directory='{}/helm_templates/{}/{}/helm-chart/templates'.format(
                maint_dir,
                deployment_environment,
                application_name
            ), 
            namespace_name=namespace_name,
            target_deployment_dir=helm_deployment_templates_directory,
            variables=variables,
            recurse_directory=True
        )

        
    except:
        traceback.print_exc()
        sys.exit(127)
    print('Done with integration')


if __name__ == '__main__':
    main()
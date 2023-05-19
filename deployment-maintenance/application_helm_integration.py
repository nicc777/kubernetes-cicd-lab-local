import sys
import os
import string
import traceback
import json
from datetime import datetime
import yaml
try:
    from yaml import CLoader as Loader, CDumper as Dumper
except ImportError:
    from yaml import Loader, Dumper


NAMESPACE_ALLOWED_CHARS = '{}{}'.format(string.ascii_letters, string.digits)
CHAR_REPLACEMENT = '-'


def get_utc_timestamp(with_decimal: bool=False): # pragma: no cover
    epoch = datetime(1970,1,1,0,0,0)
    now = datetime.utcnow()
    timestamp = (now - epoch).total_seconds()
    if with_decimal:
        return timestamp
    return int(timestamp)


def create_directory(path: str):
    try:
        os.mkdir(path)
    except:
        traceback.print_exc()
        sys.exit(127)


def parse_args()->tuple:
    # Expecting: app.py ${env.BUILD_NUMBER} ${REPO_APP_DIR} ${APP_SOURCE_BRANCH} ${REPO_MAINT_DIR} lab awesome-application
    args_result = list()
    if len(sys.argv) == 8:
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
        file_path = 'helm_templates/{}/{}/argocd-application/awesome-application.yaml'.format(deployment_environment, application_name)
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


def print_variable_content(variable_name: str, content: str):
    name_len = len(variable_name) + 12
    print('-'*80)
    print('-'*name_len)
    print('---   {}   ---'.format(variable_name))
    print('-'*name_len)
    print(content)
    print('-'*80)


def create_deployment_directories(namespace_name: str, target_deployment_dir: str):
    try:
        application_directory = '{}/deployments/lab/application-manifests/{}'.format(target_deployment_dir, namespace_name)
        helm_deployment_directory = '{}deployments/lab/helm-manifests/{}'.format(target_deployment_dir, namespace_name)
        create_directory(path=application_directory)
        create_directory(path=helm_deployment_directory)
        print('application_directory: {}'.format(application_directory))
        print('helm_deployment_directory: {}'.format(helm_deployment_directory))
    except: 
        traceback.print_exc()
        sys.exit(127)


def main():
    print('Starting with integration')
    try:
        now = get_utc_timestamp(with_decimal=False)
        build_nr, app_dir, app_branch, maint_dir, deployment_environment, application_name, repo_source = parse_args()
        interim_namespace_name = 'app-{}-{}'.format(
            build_final_branch_name(input_branch=app_branch),
            build_nr
        )
        namespace_name = build_final_namespace(input_namespace=interim_namespace_name)
        print('> Final namespace Name: {}'.format(namespace_name))
        deployment_config = read_suspend_configuration(deployment_environment=deployment_environment)
        print("> Deployment Configuration: {}".format(json.dumps(deployment_config)))
        helm_application_deployment_template_data = read_helm_application_deployment_template(deployment_environment=deployment_environment, application_name=application_name)
        helm_application_deployment_data = prepare_final_application_deployment_manifest(
            template_data=helm_application_deployment_template_data,
            namespace=namespace_name,
            expires=now + deployment_config['maximum-uptime'],
            suspend_starts=now + deployment_config['initial-deployment-uptime'],
            suspend_ends=now + deployment_config['maximum-uptime'] + deployment_config['suspend-duration'],
            max_uptime=deployment_config['maximum-uptime'],
            branch=app_branch,
            jenkins_build_nr=int(build_nr),
            repo_source=repo_source
        )
        print_variable_content(variable_name='helm_application_deployment_data', content=helm_application_deployment_data)
        create_deployment_directories(namespace_name=namespace_name, target_deployment_dir=maint_dir)
    except:
        traceback.print_exc()
        sys.exit(127)
    print('Done with integration')


if __name__ == '__main__':
    main()
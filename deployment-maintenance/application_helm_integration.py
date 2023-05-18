import sys
import string
import traceback
import json
import yaml
try:
    from yaml import CLoader as Loader, CDumper as Dumper
except ImportError:
    from yaml import Loader, Dumper


NAMESPACE_ALLOWED_CHARS = '{}{}'.format(string.ascii_letters, string.digits)
CHAR_REPLACEMENT = '-'
DEFAULT_ENVIRONMENT = 'lab'


def parse_args()->tuple:
    # Expecting: app.py ${env.BUILD_NUMBER} ${REPO_APP_DIR} ${APP_SOURCE_BRANCH} ${REPO_MAINT_DIR}
    args_result = list()
    if len(sys.argv) == 5:
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


def read_suspend_configuration(environment_name: str=DEFAULT_ENVIRONMENT)->dict:
    config = dict()
    try:
        yaml_data = read_text_file(path_to_file='configs/application-suspend.yaml')
        for data in yaml.load_all(yaml_data, Loader=Loader):
            if 'environment' in data:
                if isinstance(data['environment'], list):
                    for environment_data in  data['environment']:
                        if environment_data['name'] == environment_name:
                            config['initial-deployment-uptime'] = environment_data['initial-deployment-uptime']
                            config['suspend-duration'] = environment_data['suspend-duration']
                            config['maximum-uptime'] = environment_data['maximum-uptime']
    except: 
        traceback.print_exc()
        sys.exit(127)
    return config


def main():
    print('Starting with integration')
    try:
        build_nr, app_dir, app_branch, maint_dir = parse_args()
        interim_namespace_name = 'app-{}-{}'.format(
            build_final_branch_name(input_branch=app_branch),
            build_nr
        )
        namespace_name = build_final_namespace(input_namespace=interim_namespace_name)
        print('> Final namespace Name: {}'.format(namespace_name))
        deployment_config = read_suspend_configuration()
        print("> Deployment Configuration: {}".format(json.dumps(deployment_config)))
    except:
        traceback.print_exc()
        sys.exit(127)
    print('Done with integration')


if __name__ == '__main__':
    main()
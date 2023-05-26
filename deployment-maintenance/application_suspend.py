import sys
import os
import traceback
from datetime import datetime
import copy
import shutil
import re
import json

import yaml
try:
    from yaml import CLoader as Loader, CDumper as Dumper
except ImportError:
    from yaml import Loader, Dumper


EXPIRES_PATTERN         = [re.compile('\s+expires:\s+\d+'),]                #   expires: 1234567890
SUSPEND_START_PATTERN   = [re.compile('\s+suspend\-start:\s+\d+'),]         #   suspend-start: 1234567890
SUSPEND_END_PATTERN     = [re.compile('\s+suspend\-end:\s+\d+'),]           #   suspend-end: 1234567890
DEPLOYMENT_PATH_PATTERN = [re.compile('\s+path:\s+deployments\/lab\/.*'),]  #   path: deployments/lab/helm-manifests/app-issue-2-92
LINE_MATCH_REGEX        = EXPIRES_PATTERN + DEPLOYMENT_PATH_PATTERN + SUSPEND_START_PATTERN + SUSPEND_END_PATTERN


def get_utc_timestamp(with_decimal: bool=False):
    epoch = datetime(1970,1,1,0,0,0)
    now = datetime.utcnow()
    timestamp = (now - epoch).total_seconds()
    if with_decimal:
        return timestamp
    return int(timestamp)


def convert_unix_time_to_time_readable_string(unit_time: int)->str:
    ts = int('{}'.format(unit_time)) # Make sure it's an int
    ts_str = datetime.fromtimestamp(ts).strftime('%Y-%m-%d %H:%M:%S')
    return '{}   -> {}'.format(ts, ts_str)


def read_text_file(path_to_file: str, read_lines_that_match_this_regex: list=LINE_MATCH_REGEX)->list:
    content = list()
    with open(path_to_file, 'r') as f:
        for line in f:
            read_line = True
            if read_lines_that_match_this_regex is not None: # We are only interested really in a couple of lines in these files
                if isinstance(read_lines_that_match_this_regex, list):
                    if pattern_match(input_str=line, patterns=LINE_MATCH_REGEX) is True: 
                        print('* Matching line: {}'.format(line))
                        content.append(line)
                        read_line = False
            if read_line is True:
                content.append(line)
    return content


def read_suspend_configuration(deployment_environment: str='lab')->dict:
    config = dict()
    try:
        yaml_data = ''
        for line in read_text_file(path_to_file='configs/application-suspend.yaml', read_lines_that_match_this_regex=None):
            yaml_data = '{}{}\n'.format(yaml_data, line)
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


def parse_args()->tuple:
    # Expecting: app.py maint-repo-dir __MODE__
    args_result = list()
    if len(sys.argv) == 3:
        for i, arg in enumerate(sys.argv):
            args_result.append(arg)
            print(f"Argument {i:>6}: {arg}")
        args_result.pop(0)
    else:
        raise Exception('Unexpected number of command line arguments')
    return tuple(args_result)


def pattern_match(input_str: str, patterns: list)->bool:
    try:
        for p in patterns:
            if p.match(input_str) is not None:
                return True
    except:
        pass
    return False


def list_files(directory: str)->list:
    result = list()
    try:
        for root, dirs, files in os.walk(directory):
            for file_name in files:
                if file_name.lower().endswith('.yaml') or file_name.lower().endswith('.yml'):
                    if file_name.lower().startswith('app-issue-') or file_name.lower().startswith('app-test-'):
                        result.append('{}/{}'.format(directory, file_name))
    except:
        traceback.print_exc()
        sys.exit(127)
    return copy.deepcopy(result)


def delete_directory(dir: str)->bool:
    try:
        os.remove(dir)
    except:
        # Nested directory... deal with it
        try:
            shutil.rmtree(dir)
        except:
            return False
    return True


def identify_active_application_due_for_suspend(application_deployment_files: list)->dict:
    now = get_utc_timestamp(with_decimal=False)
    suspend_application_deployment_files = list()
    suspend_application_deployment_directories = list()
    for file_path in application_deployment_files:
        suspend = False
        expired = False
        deployment_path = None
        label_suspend_start = 0
        label_suspend_end = 0
        file_content_lines = read_text_file(path_to_file=file_path)
        for line in file_content_lines:
            if pattern_match(input_str=line, patterns=EXPIRES_PATTERN) is True:
                file_expiry_label_value = int(line.split(' ')[-1])
                if (now - file_expiry_label_value) > 0:
                    expired = True
            elif pattern_match(input_str=line, patterns=SUSPEND_END_PATTERN) is True:
                label_suspend_end = int(line.split(' ')[-1])
            elif pattern_match(input_str=line, patterns=SUSPEND_START_PATTERN) is True:
                label_suspend_start = int(line.split(' ')[-1])
            elif pattern_match(input_str=line, patterns=DEPLOYMENT_PATH_PATTERN) is True:
                deployment_path = line.split(' ')[-1]

        print('identify_active_application_due_for_suspend(): NOW           : {}'.format(convert_unix_time_to_time_readable_string(unit_time=now)))
        print('identify_active_application_due_for_suspend(): FILE          : {}'.format(file_path))
        print('identify_active_application_due_for_suspend(): EXPIRES AT    : {}'.format(convert_unix_time_to_time_readable_string(unit_time=file_expiry_label_value)))
        print('identify_active_application_due_for_suspend(): SUSPEND START : {}'.format(convert_unix_time_to_time_readable_string(unit_time=label_suspend_start)))
        print('identify_active_application_due_for_suspend(): SUSPEND END   : {}'.format(convert_unix_time_to_time_readable_string(unit_time=label_suspend_end)))

        if not expired:
            print('identify_active_application_due_for_suspend(): EXPIRED       : FALSE')
            if (now - label_suspend_start) >= 0  and (now - label_suspend_end) < 0:
                suspend = True
                print('identify_active_application_due_for_suspend(): SUSPEND       : TRUE')
            elif (now - label_suspend_start) >= 0  and (now - label_suspend_end) >= 0:
                suspend = False
                print('identify_active_application_due_for_suspend(): SUSPEND       : FALSE (Because also past suspend end timestamp)')
            else:
                print('identify_active_application_due_for_suspend(): SUSPEND       : FALSE')
        else:
            print('identify_active_application_due_for_suspend(): EXPIRED       : TRUE')
        if suspend is True:
            suspend_application_deployment_files.append(file_path)
            suspend_application_deployment_directories.append(deployment_path)
    return {
        'suspend_application_deployment_files': suspend_application_deployment_files,
        'suspend_application_deployment_directories': suspend_application_deployment_directories
    }


def identify_suspended_applications_due_for_resurrection(application_deployment_files: list)->dict:
    now = get_utc_timestamp(with_decimal=False)
    suspend_application_deployment_files = list()
    suspend_application_deployment_directories = list()
    expired_application_deployment_files = list()
    expired_application_deployment_directories = list()
    for file_path in application_deployment_files:
        un_suspend = False
        expired = False
        deployment_path = None
        label_suspend_start = 0
        label_suspend_end = 0
        file_content_lines = read_text_file(path_to_file=file_path)
        for line in file_content_lines:
            if pattern_match(input_str=line, patterns=EXPIRES_PATTERN) is True:
                file_expiry_label_value = int(line.split(' ')[-1])
                if file_expiry_label_value < now:
                    expired = True
            elif pattern_match(input_str=line, patterns=SUSPEND_START_PATTERN) is True:
                label_suspend_start = int(line.split(' ')[-1])
            elif pattern_match(input_str=line, patterns=SUSPEND_END_PATTERN) is True:
                label_suspend_end = int(line.split(' ')[-1])
            elif pattern_match(input_str=line, patterns=DEPLOYMENT_PATH_PATTERN) is True:
                deployment_path = line.split(' ')[-1]

        print('identify_suspended_applications_due_for_resurrection(): NOW           : {}'.format(convert_unix_time_to_time_readable_string(unit_time=now)))
        print('identify_suspended_applications_due_for_resurrection(): FILE          : {}'.format(file_path))
        print('identify_suspended_applications_due_for_resurrection(): EXPIRES AT    : {}'.format(convert_unix_time_to_time_readable_string(unit_time=file_expiry_label_value)))
        print('identify_suspended_applications_due_for_resurrection(): SUSPEND START : {}'.format(convert_unix_time_to_time_readable_string(unit_time=label_suspend_start)))
        print('identify_suspended_applications_due_for_resurrection(): SUSPEND END   : {}'.format(convert_unix_time_to_time_readable_string(unit_time=label_suspend_end)))

        if expired is False:
            print('Checking un_suspend time value: {}'.format(now - label_suspend_end))
            if (now - label_suspend_end) > 0:
                un_suspend = True
        else:
            expired_application_deployment_files.append(file_path)
            expired_application_deployment_directories.append(deployment_path)
        if un_suspend is True:
            suspend_application_deployment_files.append(file_path)
            suspend_application_deployment_directories.append(deployment_path)
    return {
        'suspend_application_deployment_files': suspend_application_deployment_files,
        'suspend_application_deployment_directories': suspend_application_deployment_directories,
        'expired_application_deployment_files': expired_application_deployment_files,
        'expired_application_deployment_directories': expired_application_deployment_directories,
    }


def update_application_manifest_timestamp_labels(file_path: str):
    print('Updating application manifest labels...')
    config = read_suspend_configuration()
    """
        config['initial-deployment-uptime']
        config['suspend-duration']
        config['maximum-uptime']
    """
    print('config: {}'.format(json.dumps(config)))

    application_manifest_content_lines = read_text_file(path_to_file=file_path, read_lines_that_match_this_regex=None)
    application_manifest_labels = read_text_file(path_to_file=file_path)

    updated_suspend_start = 0
    updated_suspend_end = 0
    expires = 0
    for line in application_manifest_labels:
            line = line.replace('\n', '')
            if pattern_match(input_str=line, patterns=SUSPEND_END_PATTERN) is True:
                current_suspend_end = int(line.split(' ')[-1])
            elif pattern_match(input_str=line, patterns=EXPIRES_PATTERN) is True:
                expires = int(line.split(' ')[-1])

    updated_suspend_start = current_suspend_end + config['initial-deployment-uptime']
    updated_suspend_end = updated_suspend_start + config['suspend-duration']
    
    print('updated_suspend_start = {}   -> {}'.format(updated_suspend_start, convert_unix_time_to_time_readable_string(unit_time=updated_suspend_start)))
    print('updated_suspend_end   = {}   -> {}'.format(updated_suspend_end, convert_unix_time_to_time_readable_string(unit_time=updated_suspend_end)))
    
    if updated_suspend_start > expires: # No need to suspend again
        updated_suspend_start = 9999999999
        updated_suspend_end   = 9999999999

    new_suspend_start_str = '    suspend-start: {}'.format(updated_suspend_start)
    new_suspend_end_str   = '    suspend-end: {}'.format(updated_suspend_end)

    application_manifest_content = ''
    for line in application_manifest_content_lines:
        if '    suspend-start:' in line:
            application_manifest_content = '{}{}\n'.format(application_manifest_content, new_suspend_start_str)
        elif '    suspend-end:' in line:
            application_manifest_content = '{}{}\n'.format(application_manifest_content, new_suspend_end_str)
        else:
            application_manifest_content = '{}{}\n'.format(application_manifest_content, line)
    print('Writing updated application manifest file to {}'.format(file_path))
    with open(file_path, 'w') as f:
        f.write(application_manifest_content)
    print('Update to file "{}" DONE'.format(file_path))
        

def main():
    # Step 1: Get the Git repo base directory
    do_git_push = True
    git_updates = False
    application_manifest_relative_directory = 'deployments/lab/application-manifests'
    application_deployments_templates_path = 'deployments/lab/helm-manifests'
    suspend_application_manifest_path = 'suspend/lab/application-manifests'
    suspend_application_deployments_templates_path = 'suspend/lab/helm-manifests'
    deployment_maintenance_repository_directory, mode = parse_args()
    if mode.lower().startswith('test'):
        do_git_push = False
    delete_helm_files_script_file_name = '{}/helm_directories_to_delete.txt'.format(deployment_maintenance_repository_directory)

    # Step 2: Delete previously marked helm charts
    if os.path.exists(delete_helm_files_script_file_name):
        print('Helm directories from previous application cleanup detected - deleting')
        try:
            with open(delete_helm_files_script_file_name, 'r') as f:
                for dir_to_delete in f:
                    print('   Deleting Helm directory: {}'.format(dir_to_delete.strip()))
                    delete_directory(dir=dir_to_delete.strip())
        except:
            traceback.print_exc()
            sys.exit(127)
    else:
        print('NO Helm directories from previous application cleanup detected')

    # step 3: Get all current active and suspended deployments in scope
    active_application_deployments = list_files(directory='{}/{}'.format(deployment_maintenance_repository_directory, application_manifest_relative_directory))
    suspended_application_deployments = list_files(directory='{}/{}'.format(deployment_maintenance_repository_directory, suspend_application_manifest_path))

    # Step 4: Identify deployments ready for suspend and resurrection actions
    active_applications_due_for_suspension = identify_active_application_due_for_suspend(application_deployment_files=active_application_deployments)
    suspended_applications_due_for_resurrection = identify_suspended_applications_due_for_resurrection(application_deployment_files=suspended_application_deployments)

    # Step 5: Move active applications due for suspension
    for application_deployment_file in active_applications_due_for_suspension['suspend_application_deployment_files']:        
        try:
            print('Suspend FILE          : {}'.format(application_deployment_file))
            destination_file = application_deployment_file.replace(application_manifest_relative_directory, suspend_application_manifest_path)
            print('    Destination       : {}'.format(destination_file))
            os.replace(src=application_deployment_file, dst=destination_file)
            git_updates = True
        except:
            traceback.print_exc()
            sys.exit(127)

    # Step 6: delete expired apps in suspended state
    for suspended_application_deployment_file in suspended_applications_due_for_resurrection['expired_application_deployment_files']:        
        try:
            print('DELETE    FILE        : {}'.format(suspended_application_deployment_file))
            os.unlink(suspended_application_deployment_file)
            git_updates = True
        except:
            traceback.print_exc()
            sys.exit(127)
    for helm_dir_newly_marked_for_delete in suspended_applications_due_for_resurrection['expired_application_deployment_directories']:
        try:
            with open(delete_helm_files_script_file_name, 'a') as f:
                f.write('{}\n'.format(helm_dir_newly_marked_for_delete))
        except:
            traceback.print_exc()
            sys.exit(127)

    # Step 7: Move suspended applications due for resurrection
    for suspended_application_deployment_file in suspended_applications_due_for_resurrection['suspend_application_deployment_files']:        
        try:
            print('Resurrect FILE        : {}'.format(suspended_application_deployment_file))
            destination_file = suspended_application_deployment_file.replace(suspend_application_manifest_path, application_manifest_relative_directory)
            print('    Destination       : {}'.format(destination_file))
            os.replace(src=suspended_application_deployment_file, dst=destination_file)
            update_application_manifest_timestamp_labels(file_path=destination_file)
            git_updates = True
        except:
            traceback.print_exc()
            sys.exit(127)
    
    # Step 8: PUSH Changes to GIT
    print('mode        : {}'.format(mode))
    print('do_git_push : {}'.format(do_git_push))
    print('git_updates : {}'.format(git_updates))
    if do_git_push is True and git_updates is True:
        print('Pushing changes to Git')
        try:
            with open('/tmp/command.sh', 'w') as f:
                f.write('git config --local user.email "jenkins@localhost"\n')
                f.write('git config --local user.name "jenkins"\n')
                f.write('eval `ssh-agent` && ssh-add /home/jenkins/.ssh/jenkins_gitlab && git add . && git commit -m "Deleted Expired Applications" && git push origin main\n')
            os.system('cd {} && /bin/bash /tmp/command.sh'.format(deployment_maintenance_repository_directory))
            print('MAIN BRANCH PUSHED')
        except:
            print('FAILED TO PUSH UPDATES TO GIT')
    elif do_git_push is False and git_updates is True:
        print()
        print("NOTE: There was changes, but changes was not pushed to git as we are in TEST mode")
        print()
    else:
        print("No changes - no need to push to git")


if __name__ == '__main__':
    main()
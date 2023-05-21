import sys
import os
import traceback
from datetime import datetime
import copy
import shutil
import re

"""
labels:
    name: awesome-application
    expires: __EXPIRES__
    suspend-start: __SUSPEND_STARTS__
    suspend-end: __SUSPENDS_ENDS__
    maximum-uptime: __MAX_UPTIME__
"""                                                                         # EXAMPLES:
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


def read_text_file(path_to_file: str)->list:
    content = list()
    with open(path_to_file, 'r') as f:
        for line in f:
            # We are only interested really in a couple of lines in these files
            if pattern_match(input_str=line, patterns=LINE_MATCH_REGEX) is True:
                print('* Matching line: {}'.format(line))
                content.append(line)
    return content


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
        print('identify_active_application_due_for_suspend(): NOW           : {}'.format(now))
        print('identify_active_application_due_for_suspend(): FILE          : {}'.format(file_path))
        print('identify_active_application_due_for_suspend(): EXPIRES AT    : {}'.format(file_expiry_label_value))
        print('identify_active_application_due_for_suspend(): SUSPEND START : {}'.format(label_suspend_start))
        print('identify_active_application_due_for_suspend(): SUSPEND END   : {}'.format(label_suspend_end))
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
    for file_path in application_deployment_files:
        suspend = False
        expired = True
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
        if not expired:
            if label_suspend_start < now and label_suspend_end > now:   # SHould we be in a suspended state now?
                suspend = True
        if suspend is True:
            suspend_application_deployment_files.append(file_path)
            suspend_application_deployment_directories.append(deployment_path)
    return {
        'suspend_application_deployment_files': suspend_application_deployment_files,
        'suspend_application_deployment_directories': suspend_application_deployment_directories
    }


def main():
    # Step 1: Get the Git repo base directory
    do_git_push = True
    application_manifest_relative_directory = 'deployments/lab/application-manifests'
    suspend_application_manifest_path = 'suspend/lab/application-manifests'
    suspend_application_deployments_templates_path = 'suspend/lab/helm-manifests'
    deployment_maintenance_repository_directory, mode = parse_args()
    if mode.lower().startswith('test'):
        do_git_push = False

    # step 2: Get all current active and suspended deployments in scope
    active_application_deployments = list_files(directory='{}/{}'.format(deployment_maintenance_repository_directory, application_manifest_relative_directory))
    suspended_application_deployments = list_files(directory='{}/{}'.format(deployment_maintenance_repository_directory, suspend_application_manifest_path))

    # Step 3: Identify deployments ready for suspend and resurrection actions
    active_applications_due_for_suspension = identify_active_application_due_for_suspend(application_deployment_files=active_application_deployments)
    suspended_applications_due_for_resurrection = identify_suspended_applications_due_for_resurrection(application_deployment_files=suspended_application_deployments)

    # Step 4: Move active applications due for suspension
    git_updates = False
    #for expired_application_deployment_file, expired_application_deployment_directory in expired_application_deployment_files.items():
    for application_deployment_file in active_applications_due_for_suspension['suspend_application_deployment_files']:        
        try:
            print('Suspend FILE          : {}'.format(application_deployment_file))
            # os.unlink(application_deployment_file)
            git_updates = True
        except:
            pass

    for expired_application_deployment_directory in active_applications_due_for_suspension['suspend_application_deployment_directories']:        
        try:
            deployment_directory = '{}/{}'.format(deployment_maintenance_repository_directory, expired_application_deployment_directory)
            deployment_directory = ''.join(deployment_directory.split())
            print('Suspend DIRECTORY     : {}'.format(deployment_directory))
            # delete_directory(dir=deployment_directory)
            git_updates = True
        except:
            pass

    # Step 4: Move suspended applications due for resurrection
    git_updates = False
    #for expired_application_deployment_file, expired_application_deployment_directory in expired_application_deployment_files.items():
    for application_deployment_file in suspended_applications_due_for_resurrection['suspend_application_deployment_files']:        
        try:
            print('Resurrect FILE        : {}'.format(deployment_directory))
            # os.unlink(application_deployment_file)
            git_updates = True
        except:
            pass

    for expired_application_deployment_directory in suspended_applications_due_for_resurrection['suspend_application_deployment_directories']:        
        try:
            deployment_directory = '{}/{}'.format(deployment_maintenance_repository_directory, expired_application_deployment_directory)
            deployment_directory = ''.join(deployment_directory.split())
            print('Resurrect DIRECTORY   : {}'.format(deployment_directory))
            # delete_directory(dir=deployment_directory)
            git_updates = True
        except:
            pass

    # PUSH Changes to GIT
    if do_git_push is True and git_updates is True:
        print('Pushing changes to Git')
        try:
            with open('/tmp/command.sh', 'w') as f:
                f.write('git config --local user.email "jenkins@localhost"\n')
                f.write('git config --local user.name "jenkins"\n')
                f.write('eval `ssh-agent` && ssh-add /home/jenkins/.ssh/jenkins_gitlab && git add . && git commit -m "Deleted Expired Applications" && git push origin main\n')
            # os.system('cd {} && /bin/bash /tmp/command.sh'.format(deployment_maintenance_repository_directory))
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
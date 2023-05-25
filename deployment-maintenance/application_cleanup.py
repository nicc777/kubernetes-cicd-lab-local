import sys
import os
import traceback
from datetime import datetime
import copy
import shutil
import re

                                                                            # EXAMPLES:
EXPIRES_PATTERN = [re.compile('\s+expires:\s+\d+'),]                        #   expires: 1684528753
DEPLOYMENT_PATH_PATTERN = [re.compile('\s+path:\s+deployments\/lab\/.*'),]  #   path: deployments/lab/helm-manifests/app-issue-2-92
LINE_MATCH_REGEX = EXPIRES_PATTERN + DEPLOYMENT_PATH_PATTERN


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


def identify_expired_applications(application_deployment_files: list)->dict:
    now = get_utc_timestamp(with_decimal=False)
    expired_application_deployment_files = list()
    expired_application_deployment_directories = list()
    for file_path in application_deployment_files:
        expired = False
        deployment_path = None
        file_content_lines = read_text_file(path_to_file=file_path)
        for line in file_content_lines:
            if pattern_match(input_str=line, patterns=EXPIRES_PATTERN) is True:
                file_expiry_label_value = int(line.split(' ')[-1])
                if file_expiry_label_value < now:
                    expired = True
            if pattern_match(input_str=line, patterns=DEPLOYMENT_PATH_PATTERN) is True:
                deployment_path = line.split(' ')[-1]
        if expired:
            expired_application_deployment_files.append(file_path)
            expired_application_deployment_directories.append(deployment_path)

        print('identify_expired_applications(): NOW           : {}'.format(convert_unix_time_to_time_readable_string(unit_time=now)))
        print('identify_expired_applications(): FILE          : {}'.format(file_path))
        print('identify_expired_applications(): EXPIRES AT    : {}'.format(convert_unix_time_to_time_readable_string(unit_time=file_expiry_label_value)))

    return {
        'expired_application_deployment_files': expired_application_deployment_files,
        'expired_application_deployment_directories': expired_application_deployment_directories
    }


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


def main():
    # Step 1: Get the Git repo base directory
    do_git_push = True
    application_manifest_relative_directory = 'deployments/lab/application-manifests'
    deployment_maintenance_repository_directory, mode = parse_args()
    if mode.lower().startswith('test'):
        do_git_push = False
    delete_helm_files_script_file_name = '{}/helm_directories_to_delete.txt'.format(deployment_maintenance_repository_directory)

    # step 2: Get all current deployments in scope
    current_application_deployments = list_files(directory='{}/{}'.format(deployment_maintenance_repository_directory, application_manifest_relative_directory))

    # Step 3: Identify expired files
    expired_applications = identify_expired_applications(application_deployment_files=current_application_deployments)

    # Step 4: Delete artifacts
    git_updates = False
    #for expired_application_deployment_file, expired_application_deployment_directory in expired_application_deployment_files.items():
    for expired_application_deployment_file in expired_applications['expired_application_deployment_files']:        
        try:
            print('Deleting FILE                  : {}'.format(expired_application_deployment_file))
            os.unlink(expired_application_deployment_file)
            git_updates = True
        except:
            pass

    for expired_application_deployment_directory in expired_applications['expired_application_deployment_directories']:        
        directory_to_delete = '{}/{}'.format(deployment_maintenance_repository_directory, expired_application_deployment_directory)
        directory_to_delete = ''.join(directory_to_delete.split())
        print('Marking for deletion DIRECTORY : {}'.format(directory_to_delete))
        # delete_directory(dir=directory_to_delete)
        try:
            with open(delete_helm_files_script_file_name, 'a') as f:
                f.write('{}\n'.format(expired_application_deployment_directory))
        except:
            traceback.print_exc()
        git_updates = True


    # Step 5: Update Git repo if required
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


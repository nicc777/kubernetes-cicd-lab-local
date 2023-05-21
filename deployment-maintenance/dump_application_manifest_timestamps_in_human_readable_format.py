import sys
import os
import traceback
from datetime import datetime, timezone, timedelta
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


now = get_utc_timestamp(with_decimal=False)


def parse_args()->tuple:
    # Expecting: app.py maint-repo-dir 
    args_result = list()
    if len(sys.argv) == 2:
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
    print('list_files(): DIR: {}'.format(directory))
    try:
        for root, dirs, files in os.walk(directory):
            for file_name in files:
                print('list_files(): Evaluating file "{}"'.format(file_name))
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


def convert_unix_time_to_time_readable_string(unit_time: int)->str:
    ts = int('{}'.format(unit_time)) # Make sure it's an int
    utc = datetime.fromtimestamp(ts)
    ts_str = datetime.fromtimestamp(ts).strftime('%Y-%m-%d %H:%M:%S')
    return '{}   -> {}'.format(ts, ts_str)


def identify_active_application_due_for_suspend(application_deployment_files: list)->dict:
    print("NOW: {}".format(now))
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


def identify_suspended_applications_due_for_resurrection(application_deployment_files: list)->dict:
    print("NOW: {}".format(now))
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
        print('identify_suspended_applications_due_for_resurrection(): NOW           : {}'.format(now))
        print('identify_suspended_applications_due_for_resurrection(): FILE          : {}'.format(file_path))
        print('identify_suspended_applications_due_for_resurrection(): EXPIRES AT    : {}'.format(file_expiry_label_value))
        print('identify_suspended_applications_due_for_resurrection(): SUSPEND START : {}'.format(label_suspend_start))
        print('identify_suspended_applications_due_for_resurrection(): SUSPEND END   : {}'.format(label_suspend_end))
        if not expired:
            if label_suspend_start < now and label_suspend_end > now:   # SHould we be in a suspended state now?
                suspend = True
        if suspend is True:
            suspend_application_deployment_files.append(file_path)
            suspend_application_deployment_directories.append(deployment_path)


def main():
    # Step 1: Get the Git repo base directory
    application_manifest_relative_directory = 'deployments/lab/application-manifests'
    suspend_application_manifest_path = 'suspend/lab/application-manifests'
    deployment_maintenance_repository_directory = parse_args()[0]

    # step 2: Get all current active and suspended deployments in scope
    active_application_deployments = list_files(directory='{}/{}'.format(deployment_maintenance_repository_directory, application_manifest_relative_directory))
    suspended_application_deployments = list_files(directory='{}/{}'.format(deployment_maintenance_repository_directory, suspend_application_manifest_path))

    # Step 3: Identify deployments ready for suspend and resurrection actions
    identify_active_application_due_for_suspend(application_deployment_files=active_application_deployments)
    identify_suspended_applications_due_for_resurrection(application_deployment_files=suspended_application_deployments)


if __name__ == '__main__':
    main()
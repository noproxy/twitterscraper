import os
from typing import List


def split_log(path: str):
    with open(path, 'r', encoding='utf-8') as log:
        user = ''
        user_logs = []
        for line in log.readlines():
            if line.startswith('Level 25'):
                new_user = line[len('Level 25: download user @'):-1].strip()
                if user:
                    with open(user, 'w') as output_file:
                        output_file.writelines(user_logs)
                else:
                    for item in user_logs:
                        print(item)

                user = new_user
                user_logs.clear()
                user_logs.append(line)
                continue

            user_logs.append(line)


def issuccess(lines: List[str]):
    if len(lines) == 3:
        if lines[0].startswith('Level 25: download user @') \
                and "Twitter returned : 'has_more_items'" in lines[1] \
                and lines[2].startswith('INFO: Got') \
                and 'tweets from username' in lines[2]:
            return True

    return False


def ismissing_image(lines: List[str]):
    has_image_fail = False
    for line in lines:
        if line.startswith('Level 25: download user') \
                or "INFO: Twitter returned : 'has_more_items'" in line \
                or line.startswith('INFO: Got'):
            continue
        if line.startswith('INFO: download ') and line.strip().endswith('retry = 1'):
            has_image_fail = True
            continue
        return False

    return has_image_fail


def slim_log(path: str):
    final_logs = []
    lines = []
    with open(path, 'r', encoding='utf-8') as log:
        lines = log.readlines()

    for line in lines:
        stripped = line.strip()
        if not stripped:
            continue
        if stripped.startswith('INFO: download '):
            if stripped.endswith(' retry = 5') \
                    or stripped.endswith(' retry = 4') \
                    or stripped.endswith(' retry = 3') \
                    or stripped.endswith(' retry = 2'):
                continue
        if stripped.startswith('INFO: Using proxy '):
            continue
        if 'DeprecationWarning' in stripped or 'elif isinstance(obj, collections.Iterable):' in stripped:
            continue
        if stripped.startswith('INFO: Scraping tweets from'):
            continue
        final_logs.append(line)

    with open(path, 'w', encoding='utf-8') as log:
        log.writelines(final_logs)


def move_to(path: str, dirname: str):
    new_dir = os.path.join(os.path.dirname(path), dirname)
    if not os.path.exists(new_dir):
        os.mkdir(new_dir)

    dest = os.path.join(os.path.dirname(path), dirname, os.path.basename(path))
    os.rename(path, dest)


def group_log(path: str):
    lines = []
    with open(path, 'r', encoding='utf-8') as log:
        lines = log.readlines()

    if issuccess(lines):
        move_to(path, 'success')

    if ismissing_image(lines):
        move_to(path, 'missing_images')


if __name__ == '__main__':
    split_log('/System/Volumes/Data/Users/yiyazhou/Projects/Configurations/work/twitter/log.txt')
    for log_file in os.listdir(os.path.curdir):
        if os.path.isfile(log_file):
            slim_log(log_file)
            group_log(log_file)

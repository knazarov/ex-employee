#!/usr/bin/env python3

import configparser
import argparse
import os
import gitlab


def get_users_in_group(group):
    users = group.members.list()

    return users


def access_level_to_string(access_level):
    levels = {10: 'guest',
              20: 'reporter',
              30: 'developer',
              40: 'maintainer',
              50: 'owner'}

    return levels[access_level]


def generate_report(gl, root_name, verbose=False):
    root = gl.groups.get(root_name)

    report = {}

    for group in gl.groups.list(all=True):
        if group.full_path.startswith(root_name):
            if verbose:
                print('scanning group: ', group.full_path)

            users = group.members.list(all=True)

            for user in users:
                report.setdefault(user.username, {'name': user.name, 'projects': {}})
                report[user.username]['projects'][group.full_path] = \
                    access_level_to_string(user.access_level)

    for project in root.projects.list(include_subgroups=True, all=True):
        if verbose:
            print('scanning project: ', project.path_with_namespace)

        project = gl.projects.get(project.id)
        users = project.members.list(all=True)

        for user in users:
            report.setdefault(user.username, {'name': user.name, 'projects': {}})

            report[user.username]['projects'][project.path_with_namespace] = access_level_to_string(user.access_level)

    print('--- report ---')

    for user, details in report.items():
        print('user: %s, %s' % (user, details['name']))
        for project, access_level in details['projects'].items():
            print('  %s: %s' % (project, access_level))
        print()


def ban_user(gl, root_name, user_names, verbose=False, dry_run=True):
    root = gl.groups.get(root_name)

    user_ids = {}

    for user_name in user_names:
        users = gl.users.list(username=user_name)

        if len(users) == 0:
            raise RuntimeError('No such user: %s', user_name)

        user_ids[user_name] = users[0].id

    for group in gl.groups.list(all=True):
        if group.full_path.startswith(root_name):
            if verbose:
                print('scanning group: ', group.full_path)

            for user_name in user_names:
                try:
                    member = group.members.get(user_ids[user_name])
                    print('removing %s from %s' % (user_name, group.full_path))
                    if not dry_run:
                        group.members.delete(user_ids[user_name])
                except gitlab.exceptions.GitlabGetError:
                    pass


    for project in root.projects.list(include_subgroups=True, all=True):
        if verbose:
            print('scanning project: ', project.path_with_namespace)

        project = gl.projects.get(project.id)

        for user_name in user_names:
            try:
                member = project.members.get(user_ids[user_name])
                print('removing %s from %s' % (user_name, project.path_with_namespace))
                if not dry_run:
                    project.members.delete(user_ids[user_name])

            except gitlab.exceptions.GitlabGetError:
                pass


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('-v', '--verbose', action='store_true', default=False)
    subparsers = parser.add_subparsers(title="commands", dest="command")
    subparsers.required = True

    report = subparsers.add_parser("report")
    ban = subparsers.add_parser("ban")

    report.add_argument('root')
    ban.add_argument('root')
    ban.add_argument('username', nargs='+')
    ban.add_argument('--dry-run', action='store_true', default=False)

    args = parser.parse_args()

    config = configparser.ConfigParser()

    if os.path.exists('ex-employee.ini'):
        config.read(os.path.expanduser("ex-employee.ini"))
    elif os.path.exists(os.path.expanduser("~/.ex-employee.ini")):
        config.read(os.path.expanduser("~/.ex-employee.ini"))
    else:
        raise RuntimeError('Configuration file not found')


    token = config['default']['gitlab_token']

    gl = gitlab.Gitlab('https://gitlab.com', private_token=token)

    if args.command == 'report':
        generate_report(gl, args.root, verbose=args.verbose)
    elif args.command == 'ban':
        ban_user(gl, args.root, args.username,
                 verbose=args.verbose, dry_run=args.dry_run)



if __name__ == '__main__':
    main()

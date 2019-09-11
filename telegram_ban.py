#!/usr/bin/env python3

import sys
import json
import datetime
import dateparser
import requests
import os
import configparser
import argparse

from telethon import TelegramClient, sync
from telethon.tl.functions.messages import CreateChatRequest
import telethon


def ban(client, usernames, whitelist, dry_run=True):
    dialogs = client.get_dialogs()

    for dialog in client.iter_dialogs(limit=None):
        if dialog.is_group and not dialog.is_channel and dialog.name not in whitelist:
            for user in client.iter_participants(dialog, limit=None):
                if user.username in usernames:
                    if dry_run:
                        print('will ban ', dialog.name, user.username)
                    else:
                        try:
                            print('banning ', dialog.name, user.username)
                            client.kick_participant(dialog, user)
                        except telethon.errors.rpcerrorlist.ChatAdminRequiredError:
                            print('failed to ban (need admin rights)', dialog.name, user.username)





def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('username', nargs='+')
    parser.add_argument('--dry-run', action='store_true', default=False)

    args = parser.parse_args()

    config = configparser.ConfigParser()

    if os.path.exists('ex-employee.ini'):
        config.read(os.path.expanduser("ex-employee.ini"))
    elif os.path.exists(os.path.expanduser("~/.ex-employee.ini")):
        config.read(os.path.expanduser("~/.ex-employee.ini"))
    else:
        raise RuntimeError('Configuration file not found')


    api_id = int(config['default']['telegram_api_id'])
    api_hash = config['default']['telegram_api_hash']
    bot_name = config['default']['telegram_bot_name']
    whitelist = [c.strip() for c in
                 config['default'].get('telegram_whitelist', '').split(',')]

    client = TelegramClient(bot_name, api_id, api_hash)

    client.start()
    ban(client, args.username, whitelist, args.dry_run)


if __name__ == "__main__":
    main()

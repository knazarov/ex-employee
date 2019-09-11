# ex-employee

This is a set of Python scripts to make sure that your ex-employees don't have access to any online accounts your team uses.

Create a configuration file either in `./ex-employee.ini` or `~/.ex-employee.ini` with the following content:

```ini
[default]
telegram_api_id=...
telegram_api_hash=...
telegram_whitelist=...
gitlab_token=...
```

Put your authorization tokens there accordingly. For Telegram you must get your own api_id and api_hash from https://my.telegram.org, under API Development.


Requirements:

- Telethon
- python-gitlab

## Telegram

To remove a person from all chats you share with them, except for those in `telegram_whitelist`, do:

```sh
./telegram_ban.py username
```


## GitLab

First, you likely have many repositories, and/or groups. To get a comprehensive report which users have access and where, type this:

```sh
./gitlab_ban.py report groupname
```

After you've looked through the report and decided which users you want to remove, do:

```sh
./gitlab_ban.py ban groupname username
```

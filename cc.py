#!/usr/bin/python

import sys
import os
import pprint
from datetime import datetime
from classes.Container import Container
from classes.CryptorRSA import CryptorRSA
from classes.LocalStorageFS import LocalStorageFS
from classes.RemoteStorageFS import RemoteStorageFS
from classes.ScanerJSON import ScanerJSON
from classes.DI import DI

def page_help():
    print(' *** HELP PAGE *** ')
    print('')

    print(' * C: container')
    print('    cc.py C - display all local containers')
    print('    cc.py Ccontainer_name - select container container_name')
    print('    cc.py C+container_name - generate new container')
    print('    cc.py C-container_name - delete container')
    print('    cc.py C@[container_name] - save container_name or current container if no container name given')
    print('    cc.py C?container_name - display information about container_name')
    print('    cc.py C^ - syncronize all containers')
    print('    cc.py C#[container_name] - upload container_name or current container if no container name given')
    print(' * U: user and users')
    print('    cc.py U - display all local users')
    print('    cc.py Uuser_name - select user user_name')
    print('    cc.py U+user_name - generate new user user_name')
    print('    cc.py U-user_name - delete user user_name')
    print(' * P: public messages')
    print('    cc.py P - display all local public messages')
    print('    cc.py P+ - edit new public message (generate if it does not exist)')
    print('    cc.py P= - edit new public message (generate if it does not exist)')
    print('    cc.py P- - delete your last public message')
    print('    cc.py P* - view all decrypted public messages in editor (** - inverted view)')
    print(' * M: messages from user to user')
    print('    cc.py M - display all local private messages')
    print("    cc.py M+[username+subject+reply_to_message] - generate new private message to username with subject\n"
          "(username and subject are optional if none given you will be prompt to select them)\n"
          "reply_to_message - signature of message you want to reply to (it must be message to you, type 'cc.py M*' to view all your decrypted messages), also optional")

    print("    cc.py M+[username+subject+%2020-06-23+15:02:18] - generate new private message to username with subject and reply to message "
          "sent to you from username at 2020-06-23+15:02:18")
    print('    cc.py M= - edit private message (selection mode)')
    print('    cc.py M- - delete private message (selection mode)')
    print('    cc.py M* - view all decrypted private messages in editor (** - inverted view)')
    print('')

    print(' * S: status - display information about current container and current user')
    print(' * F: configuration - view or set configuration options')
    print('    cc.py F - display all configuration options')
    print('    cc.py Fcontainer=container1+editor=vim')
    print('    passable configuration options: container, user, editor, remote, upload')
    print('        container: current container')
    print('        user: current user')
    print('        editor: editor for editing messages')
    print('        remote: remote path to search for remote containers')
    print('        upload: remote path to upload the current container')
    return


def page_config(param_full):
    local_storage = DI.create_local_storage()
    config = local_storage.get_config()

    if param_full == '':
        # out config
        pp = pprint.PrettyPrinter(indent=4)
        pp.pprint(config)
    else:
        # updating values and saving config.json
        value_pairs = param_full.split('+')

        for value_pair in value_pairs:
            value_pair_list = value_pair.split('=')
            if len(value_pair_list) == 2:
                if value_pair_list[0] in ['container', 'editor', 'remote', 'upload', 'user']:
                    config[value_pair_list[0]] = value_pair_list[1]
                    print("Param {} set to {}".format(value_pair_list[0], value_pair_list[1]))
                else:
                    print("Invalid param {}".format(value_pair_list[0]))
        local_storage.save_config(config)
    return


def page_container(param_sub, container_name):
    local_storage = DI.create_local_storage()
    config = DI.get_config()
    cnt = DI.create_container()

    if param_sub == '+':
        if cnt.generate_container(container_name):
            print("Container {} generated OK".format(container_name))
        else:
            print('Error')
    elif param_sub == '-':
        if container_name == '':
            print("No container selected")
            return False

        if cnt.container_exists(container_name):
            ask = input("Delete container {}, you will not be able to restore it (y/n) :".format(container_name))
            if ask.lower() == 'y':
                if cnt.delete_container(container_name):
                    print("Container {} deleted OK".format(container_name))
        else:
            print("Container {} does not exist".format(container_name))
        return
    elif param_sub == '@':
        if container_name == '':
            container_name = config['container']
        if container_name == '':
            print("No container selected")
            return False

        if 'user' not in config or config['user'] == '' or config['user'] not in cnt.list_users():
            print("You have no selected user, type 'cc.py Uusername' to select user")
            return False

        if 'upload' in config and config['upload'] == '':
            print("Upload path not defined, type 'cc.py Fupload=my_upload_path'")

        if cnt.container_exists(container_name):
            if cnt.save(container_name):
                cnt.decrypt(container_name)
                print("Container {} saved OK".format(container_name))
        else:
            print("Container {} does not exist".format(container_name))
        return
    elif param_sub == '?':
        if cnt.container_exists(container_name):
            container = cnt.get_container(container_name)
            print("Container '{}': ".format(container_name))
            t = datetime.fromtimestamp(int(container['container']['syncronized']))
            print("Syncronized: {} ".format(t.strftime("%Y-%m-%d %H:%M")))
            users = cnt.list_container_users(container_name)
            uu = []
            for user in users:
                if config['user'] == user:
                    user = '<' + user + '>'
                uu.append(user)

            uu = sorted(uu)
            print("    Container users: {}".format(", ".join(uu)))

            mcount = len(local_storage.list_priv_messages(container_name))
            if mcount > 0:
                print("    Private message count (unsaved): {}"
                      .format(mcount))
            else:
                print("    NO unsaved private messages")

            mcount = len(local_storage.list_pub_messages(container_name))
            if mcount > 0:
                print("    Public message count (unsaved): {}"
                      .format(mcount))
            else:
                print("    NO unsaved public messages")
        else:
            print("Container {} does not exist".format(container_name))
    elif param_sub == '^':
        if 'remote' in config and config['remote'] != '':
            cnt.sync()
        else:
            print("Remote path not defined, type 'cc.py Fremote=my_remote_path'")
        return
    elif param_sub == '#':
        if container_name == '':
            container_name = config['container']
        if container_name == '':
            print("No container selected")

        if cnt.container_exists(container_name):
            if cnt.container_upload(container_name):
                print("Container {} uploaded to {} OK".format(container_name, config['upload']))
            else:
                print("Error: uploading container {} to {}".format(container_name, config['upload']))
        else:
            print("Error: container '{}' does not exist".format(container_name))
        return
    elif param_sub != '':
        container_name = param_sub + container_name

        containers = cnt.list_containers()

        if len(containers) == 0:
            print('There are no containers')
            print('Type \'cc.py C+container_name\' to generate container')
            return False

        if container_name in containers:
            config['container'] = container_name
            local_storage.save_config(config)
            print("Container {} selected OK".format(container_name))
        else:
            print("Container {} does not exists".format(container_name))
    else:
        containers = cnt.list_containers()

        if len(containers) == 0:
            print('There are no containers')
            print('Type \'cc.py C+container_name\' to generate container')
            return False

        cc = []
        for container in containers:
            if container == config['container']:
                container = '<' + config['container'] + '>'
            cc.append(container)

        cc = sorted(cc)
        print("Containers: {}".format(", ".join(cc)))
    return


def page_users(param_sub, username):
    local_storage = DI.create_local_storage()
    config = DI.get_config()
    cnt = DI.create_container()

    if param_sub == '':
        users = cnt.list_users()
        users_list = []
        for user in users:
            if config['user'] == user:
                user = '<' + user + '>'
            users_list.append(user)

        if len(users_list) == 0:
            print("You have no users")
            print("type 'cc.py U+username' to generate user")
        else:
            users_list = sorted(users_list)
            print("My users: {}".format(", ".join(users_list)))

    elif param_sub == '+':
        if cnt.user_exists(username):
            print("User {} olready exists".format(username))
        else:
            ask = input("The user generation may take several minutes on slow machines, GENERATE user {} (y/n) :".format(username))
            if ask.lower()[0:1] == 'y':
                if cnt.generate_user(username):
                    print("User {} generated OK".format(username))
    elif param_sub == '-':
        if cnt.user_exists(username):
            ask = input("Delete user {}, you will not be able to restore it (y/n) :".format(username))
            if ask.lower()[0:1] == 'y':
                if cnt.delete_user(username):
                    print("User {} deleted OK".format(username))
        else:
            print("User '{}' does not exist".format(username))
    else:
        username = param_sub + username
        if cnt.user_exists(username):
            config = local_storage.get_config()
            config['user'] = username
            local_storage.save_config(config)
            print("User {} selected OK".format(username))
        else:
            print("User '{}' does not exist".format(username))

    return


def page_pub(param_sub, param_name):
    cnt = DI.create_container()
    local_storage = DI.create_local_storage()
    config = DI.get_config()

    if 'container' not in config or config['container'] == '':
        print("You have no selected container, type 'cc.py Ccontainer_name' to select container")
        return False

    if 'user' not in config or config['user'] == '' or config['user'] not in cnt.list_users():
        print("You have no selected user, type 'cc.py Uusername' to select user")
        return False

    cnt = DI.create_container()

    if not cnt.container_exists(config['container']):
        print("Container {} does not exist".format(config['container']))
        return False

    pub_messages = local_storage.list_pub_messages(config['container'])

    if param_sub in ('+', '='):
        if 'editor' not in config or config['editor'] == '':
            print("Editor not defined, type 'cc.py Feditor=my_editor'")
            return

        if len(pub_messages) and config['user'] in pub_messages:
            # print(pub_messages[config['user']])
            os.system(config['editor'] + ' ' + pub_messages[config['user']]['filename'])
        else:
            filename = cnt.generate_pub(config['container'], config['user'], "Type your message here ...")
            os.system(config['editor'] + ' ' + filename)
    elif param_sub == '-':
        if len(pub_messages) and config['user'] in pub_messages:
            if local_storage.delete_pub_message(config['container'], config['user']):
                print('Unsaved public message deleted')
    elif param_sub == '*':
        path = cnt.get_container_path(config['container'], config['user'])
        if param_name == '*':
            os.system(config['editor'] + ' ' + path['path_ipub'])
        else:
            os.system(config['editor'] + ' ' + path['path_pub'])
    else:
        msg = local_storage.list_pub_messages_user(config['container'], config['user'])
        if msg:
            msg = msg[config['user']]
            t = datetime.fromtimestamp(int(msg['created']))
            created = t.strftime("%Y-%m-%d %H:%M")
            print("You have unsaved message at {} in {}".format(created, msg['filename']))
            print("Type 'cc.py P=' to edit message, 'cc.py P-' to delete message and 'cc.py C@' to save current container")
        else:
            print('You have no unsaved messages, type \'cc.py P=\' to create new message')
    return


def page_msg(param_sub, param_name):
    local_storage = DI.create_local_storage()
    config = DI.get_config()
    cnt = DI.create_container()

    if not cnt.container_exists(config['container']):
        print("Container {} does not exist".format(config['container']))
        return False

    if 'user' not in config or config['user'] == '' or config['user'] not in cnt.list_users():
        print("You have no selected user, type 'cc.py Uusername' to select user")
        return False

    from_username = config['user']

    priv_messages = local_storage.list_priv_messages(config['container'])
    priv_messages_user = []
    for filename in priv_messages:
        if priv_messages[filename]['from'] == from_username:
                priv_messages_user.append(priv_messages[filename])

    userlist = sorted(cnt.list_container_users(config['container']))

    if param_sub == '+':
        if 'editor' not in config or config['editor'] == '':
            print("Editor not defined, type 'cc.py Feditor=my_editor'")
            return

        params = param_name.split('+')
        username = ''
        subject = ''
        reply = ''
        if len(params) > 0:
            username = params[0]
        if len(params) > 1:
            subject = params[1]
        if len(params) > 2:
            i = 2

            while len(params) > i:
                if reply != '':
                    reply += '+'
                reply += params[i]
                i += 1

        if reply[0:1] == '%':
            reply = reply.replace('+', ' ')

        if username == '':
            print("Select user you want to write to:")
            i = 0
            for i, usr in enumerate(userlist):
                print("{}: {}".format(i, usr))
            ask = input()[0].lower()

            if ask.isnumeric() and int(ask) < len(userlist):
                username = userlist[int(ask)]
            else:
                return False
        else:
            print(userlist)
            if username not in userlist:
                print("Error: {} not found in container users list ".format(username))
                return False

        if subject == '':
            subject = input('Type message subject:')

        filename = cnt.generate_msg(config['container'], config['user'], username, "Type your message here ...", {'subject': subject, 'reply': reply})

        os.system(config['editor'] + ' "' + filename + '"')
        return
    elif param_sub == '=':
        if 'editor' not in config or config['editor'] == '':
            print("Editor not defined, type 'cc.py Feditor=my_editor'")
            return

        if len(priv_messages_user) > 0:
            print('Select message to edit:')
            i = 0
            for i, msg in enumerate(priv_messages_user):
                print(i, ': ', os.path.basename(msg['filename']))

            ask = input()[0].lower()
            if ask.isnumeric() and int(ask) < len(priv_messages_user):
                os.system(config['editor'] + ' "' + priv_messages_user[int(ask)]['filename'] + '"')

        else:
            print("You have no unsaved messages")
        return
    elif param_sub == '-':
        if len(priv_messages_user) > 0:
            print('Select message to delete:')
            i = 0
            for i, msg in enumerate(priv_messages_user):
                print(i, ': ', os.path.basename(msg['filename']))

            ask = input()[0].lower()
            if ask.isnumeric() and int(ask) < len(priv_messages_user):
                os.unlink(priv_messages_user[int(ask)]['filename'])
        else:
            print("You have no unsaved messages")
        return
    elif param_sub == '*':
        path = cnt.get_container_path(config['container'], config['user'])
        if param_name == '*':
            os.system(config['editor'] + ' ' + path['path_vbox'])
        else:
            os.system(config['editor'] + ' ' + path['path_inbox'])
    else:
        if len(priv_messages_user) > 0:
            print("You have {} unsaved messages:".format(len(priv_messages_user)))
            i = 0
            for msg in priv_messages_user:
                t = datetime.fromtimestamp(int(msg['created']))
                print(t.strftime("%Y-%m-%d %H:%M:%S"), os.path.basename(msg['filename']))
        else:
            print("You have no unsaved messages")
        return

    return

def page_status():
    cnt = DI.create_container()
    local_storage = DI.create_local_storage()
    config = DI.get_config()

    users = cnt.list_users()
    uu = []
    for user in users:
        if config['user'] == user:
            user = '<' + user + '>'
        uu.append(user)

    if len(uu) == 0:
        print("You have no users")
        print("type 'cc.py U+username' to generate user")
    else:
        uu = sorted(uu)
        print("My users: {}".format(", ".join(uu)))

    containers = cnt.list_containers()
    if len(containers):
        cc = []
        for container in containers:
            if config['container'] == container:
                container = '<' + container + '>'
            cc.append(container)

        uu = sorted(cc)
        print("Containers: {}".format(", ".join(uu)))

        if 'container' in config and config['container'] != '':
            container = cnt.get_container(config['container'])

            print("Container '{}': ".format(config['container']))
            users = cnt.list_container_users(config['container'])
            uu = []
            for user in users:
                if config['user'] == user:
                    user = '<' + user + '>'
                uu.append(user)

            uu = sorted(uu)
            if len(uu) > 0:
                print("    Container users: {}".format(", ".join(uu)))
            else:
                print("    Container has no users")

            mcount = len(local_storage.list_priv_messages(config['container']))
            if mcount > 0:
                print("    Private message count (unsaved): {}"
                      .format(mcount))
            else:
                print("    NO unsaved private messages")

            mcount = len(local_storage.list_pub_messages(config['container']))
            if mcount > 0:
                print("    Public message count (unsaved): {}"
                      .format(mcount))
            else:
                print("    NO unsaved public messages")
    else:
        print("You have no containers")
    return


if len(sys.argv) < 2:
    page_help()
else:
    param1 = sys.argv[1]
    param_main = param1[0:1]
    param_sub = param1[1:2]
    param_name = param1[2:]
    param_full = param1[1:]
    param1 = param1.lower()

    if param_main == 'F':
        page_config(param_full)
    elif param_main == 'C':
        page_container(param_sub, param_name)
    elif param_main == 'U':
        page_users(param_sub, param_name)
    elif param_main == 'P':
        page_pub(param_sub, param_name)
    elif param_main == 'M':
        page_msg(param_sub, param_name)
    elif param_main == 'S':
        page_status()

    elif param1 == '?' or param1 == '-?' or param1 == 'help' or param1 == '-help':
        page_help()
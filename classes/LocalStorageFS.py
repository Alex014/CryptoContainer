from classes.BaseLocalStorage import BaseLocalStorage
import os
import json
import glob
from os import path
from shutil import copyfile, rmtree


class LocalStorageFS(BaseLocalStorage):
    def __init__(self):
        self.path_cwd = os.getcwd()
        self.path_containers = self.path_cwd + '/containers'
        self.path_etc = self.path_cwd + '/etc'
        self.file_users = self.path_etc + '/users.json'

        if not os.path.isdir(self.path_containers):
            os.mkdir(self.path_containers)
        if not os.path.isdir(self.path_etc):
            os.mkdir(self.path_etc)
        return

    def list_containers(self):
        dirs = glob.glob(self.path_containers + '/*')
        for i, dir in enumerate(dirs):
            dirs[i] = path.basename(dirs[i])
        return dirs

    def delete_container(self, container_name: str):
        path = self.path_containers + '/' + container_name + '/'
        rmtree(path)
        return True

    def list_pub_messages(self, container_name: str):
        files = glob.glob(self.path_containers + '/' + container_name + '/unsaved/pub/*')
        files_full = {}
        for file in files:
            filename = path.basename(file)
            # print(os.path.getmtime(file))
            f = open(file, 'r')
            files_full[filename] = {'msg': f.read(), 'created': int(os.path.getmtime(file)), 'filename': file}
            f.close()

        return files_full

    def list_pub_messages_user(self, container_name: str, username: str):
        files = glob.glob(self.path_containers + '/' + container_name + '/unsaved/pub/' + username)
        files_full = {}
        for file in files:
            filename = path.basename(file)
            # print(os.path.getmtime(file))
            f = open(file, 'r')
            files_full[filename] = {'msg': f.read(), 'created': int(os.path.getmtime(file)), 'filename': file}
            f.close()

        return files_full

    def delete_pub_message(self, container_name: str, username: str):
        files = glob.glob(self.path_containers + '/' + container_name + '/unsaved/pub/' + username)
        if len(files):
            for file in files:
                os.unlink(file)
                return True
        else:
            return False


    def list_priv_messages(self, container_name: str):
        files = glob.glob(self.path_containers + '/' + container_name + '/unsaved/msg/*')
        files_full = {}
        for file in files:
            filename = path.basename(file)
            f = open(file, 'r')
            files_full[filename] = {'msg': f.read(), 'created': int(os.path.getmtime(file)), 'filename': file}
            f.close()

            params = filename.split('_')
            for param in params:
                param_pair = param.split('-')
                files_full[filename][param_pair[0]] = param_pair[1]

        return files_full

    def container_exists(self, container_name):
        path_container = self.path_containers + '/' + container_name
        if not os.path.isdir(path_container):
            return False
        if not os.path.isfile(path_container + '/encrypted/container.json'):
            return False
        return True

    def generate_container(self, container_name: str, data: str):
        if not os.path.isdir(self.path_containers):
            os.mkdir(self.path_containers)
        if not os.path.isdir(self.path_etc):
            os.mkdir(self.path_etc)

        if not os.path.isdir(self.path_containers):
            os.mkdir(self.path_containers)

        path_container = self.path_containers + '/' + container_name
        path_container_unsaved = path_container + '/unsaved'
        path_container_pub = path_container + '/unsaved/pub'
        path_container_msg = path_container + '/unsaved/msg'
        path_container_encrypted = path_container + '/encrypted'
        file_container_encrypted = path_container + '/encrypted/container.json'
        path_container_decrypted = path_container + '/decrypted'

        if not os.path.isdir(path_container):
            os.mkdir(path_container)
        if not os.path.isdir(path_container_unsaved):
            os.mkdir(path_container_unsaved)
        if not os.path.isdir(path_container_pub):
            os.mkdir(path_container_pub)
        if not os.path.isdir(path_container_msg):
            os.mkdir(path_container_msg)
        if not os.path.isdir(path_container_encrypted):
            os.mkdir(path_container_encrypted)
        if not os.path.isdir(path_container_decrypted):
            os.mkdir(path_container_decrypted)

        file = open(file_container_encrypted, 'w+')
        file.write(json.dumps(data))
        file.close()

        return True

    def generate_container_pub(self, container_name: str, username: str, message: str):
        filename = self.path_containers + '/' + container_name + '/unsaved/pub/' + username

        file = open(filename, 'w+')
        file.write(message)
        file.close()
        return filename

    def generate_container_msg(self, container_name: str, from_user: str, to_user: str, message: str, params: dict):
        str_params = ''
        for param in params:
            if param != 'reply':
                str_params += '_' + param + '-' + params[param]
        filename = self.path_containers + '/' + container_name + '/unsaved/msg/from-' + \
            from_user + '_to-' + to_user + str_params

        file = open(filename, 'w+')
        file.write(message)
        file.close()
        return filename

    def list_users(self):
        if os.path.isfile(self.file_users):
            file = open(self.file_users, 'r')
            s_users = file.read()
            file.close()

            try:
                users = json.loads(s_users)
            except json.decoder.JSONDecodeError:
                users = {}
        else:
            users = {}

        return users

    def user_exists(self, username):
        users = self.list_users()
        return username in users

    def delete_user(self, username):
        if os.path.isfile(self.file_users):
            file = open(self.file_users, 'r')
            s_users = file.read()
            file.close()

            try:
                users = json.loads(s_users)
            except json.decoder.JSONDecodeError:
                users = {}

            del users[username]

            s_users = json.dumps(users)

            file = open(self.file_users, 'w+')
            file.write(s_users)
            file.close()
            return True
        else:
            return False

    def save_user(self, username, pub_key: bytes, priv_key: bytes):
        if os.path.isfile(self.file_users):
            file = open(self.file_users, 'r')
            s_users = file.read()
            file.close()

            try:
                users = json.loads(s_users)
            except json.decoder.JSONDecodeError:
                users = {}

            users[username] = {'pub': pub_key.decode('utf-8'), 'priv': priv_key.decode('utf-8')}
            s_users = json.dumps(users)
        else:
            users = {username: {'pub': pub_key.decode('utf-8'), 'priv': priv_key.decode('utf-8')}}
            s_users = json.dumps(users)

        file = open(self.file_users, 'w+')
        file.write(s_users)
        file.close()
        return True

    def get_container_path(self, container: str, username: str):
        path_container =    self.path_containers + '/' + container
        path_decrypted =    self.path_containers + '/' + container + '/decrypted'
        path_pub =          self.path_containers + '/' + container + '/decrypted/pub'
        path_ipub =         self.path_containers + '/' + container + '/decrypted/ipub'
        path_inbox =        self.path_containers + '/' + container + '/decrypted/inbox_' + username
        path_vbox =         self.path_containers + '/' + container + '/decrypted/vbox_' + username
        path_encrypted =    self.path_containers + '/' + container + '/encrypted'
        path_unsaved =      self.path_containers + '/' + container + '/unsaved'
        path_unsaved_msg =  self.path_containers + '/' + container + '/unsaved/msg'
        path_unsaved_pub =  self.path_containers + '/' + container + '/unsaved/pub/' + username
        return {
            'path_container': path_container,
            'path_decrypted': path_decrypted,
            'path_pub': path_pub,
            'path_ipub': path_ipub,
            'path_inbox': path_inbox,
            'path_vbox': path_vbox,
            'path_encrypted': path_encrypted,
            'path_unsaved': path_unsaved,
            'path_unsaved_msg': path_unsaved_msg,
            'path_unsaved_pub': path_unsaved_pub
        }

    def get_encrypted_container(self, container: str):
        path_container = self.path_containers + '/' + container
        file_container_encrypted = path_container + '/encrypted/container.json'

        if not path.isfile(file_container_encrypted):
            return False

        file = open(file_container_encrypted, 'r')
        s_container = file.read()
        file.close()

        return json.loads(s_container)

    def get_decrypted_container(self, container: str):
        path_container = self.path_containers + '/' + container
        file_container_decrypted = path_container + '/decrypted/container.json'

        if not path.isfile(file_container_decrypted):
            return False

        file = open(file_container_decrypted, 'r')
        s_container = file.read()
        file.close()

        return json.loads(s_container)

    def container_upload(self, container: str, upload_path: str):
        path_container = self.path_containers + '/' + container
        file_container_encrypted = path_container + '/encrypted/container.json'

        if os.path.isfile(file_container_encrypted) and os.path.isdir(upload_path):
            copyfile(file_container_encrypted, os.path.join(upload_path, container + '.json'))
            return True
        else:
            return False

    def save_encrypted_container(self, container: str, data):
        path_container = self.path_containers + '/' + container
        file_container_encrypted = path_container + '/encrypted/container.json'

        container_js = json.dumps(data)
        file = open(file_container_encrypted, 'w+')
        file.write(container_js)
        file.close()
        return True

    def save_decrypted_container(self, container: str, data):
        path_container = self.path_containers + '/' + container
        file_container_encrypted = path_container + '/decrypted/container.json'

        container_js = json.dumps(data)
        file = open(file_container_encrypted, 'w+')
        file.write(container_js)
        file.close()
        return True

    def save_decrypted_pub(self, container: str, data: str, inverted_data: str):
        path_container = self.path_containers + '/' + container

        file_pub = path_container + '/decrypted/pub'
        file = open(file_pub, 'w+')
        file.write(data)
        file.close()

        file_ipub = path_container + '/decrypted/ipub'
        file = open(file_ipub, 'w+')
        file.write(inverted_data)
        file.close()
        return True

    def save_decrypted_inbox(self, container: str, to_username: str, data: str, inverted_data: str):
        path_container = self.path_containers + '/' + container

        file_pub = path_container + '/decrypted/inbox_' + to_username
        file = open(file_pub, 'w+')
        file.write(data)
        file.close()

        file_ipub = path_container + '/decrypted/vbox_' + to_username
        file = open(file_ipub, 'w+')
        file.write(inverted_data)
        file.close()
        return True

    def get_config(self):
        file_config = self.path_etc + '/config.json'

        file = open(file_config, 'r')
        s_config = file.read()
        file.close()
        return json.loads(s_config)

    def save_config(self, config):
        file_config = self.path_etc + '/config.json'

        file = open(file_config, 'w+')
        file.write(json.dumps(config))
        file.close()
        return True
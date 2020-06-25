from classes.BaseLocalStorage import BaseLocalStorage
from classes.BaseRemoteStorage import BaseRemoteStorage
from classes.BaseCryptor import BaseCryptor
from classes.BaseScaner import BaseScaner
import os
import json
import time
import base64
from datetime import datetime

class Container:
    def __init__(self, local_storage : BaseLocalStorage, remote_storage: BaseRemoteStorage, cryptor: BaseCryptor):
        self.localStorage = local_storage
        self.remoteStorage = remote_storage
        self.cryptor = cryptor

        self.config = self.localStorage.get_config()
        return

    def container_exists(self, container_name: str):
        return self.localStorage.container_exists(container_name)

    def get_container(self, container_name: str):
        return self.localStorage.get_encrypted_container(container_name)

    def get_container_path(self, container: str, username: str):
        return self.localStorage.get_container_path(container, username)

    def container_upload(self, container_name: str):
        config = self.localStorage.get_config()
        if not config['upload']:
            return False
        return self.localStorage.container_upload(container_name, config['upload'])

    def list_containers(self):
        return self.localStorage.list_containers()

    def list_users(self):
        return self.localStorage.list_users()

    def user_exists(self, username):
        return self.localStorage.user_exists(username)

    def generate_container(self, container_name: str):
        if not self.container_exists(container_name):
            data = {
                'container': {'name': container_name,
                              'syncronized': '0'},
                'users': {},
                'msg': {},
                'pub': {}
            }
            self.localStorage.generate_container(container_name, data)
            return True
        else:
            return False

    def delete_user(self, username: str):
        return self.localStorage.delete_user(username)

    def generate_user(self, username: str):
        keypair = self.cryptor.generate()
        return self.localStorage.save_user(username, keypair[0], keypair[1])

    def generate_pub(self, container_name: str, username: str, message: str):
        return self.localStorage.generate_container_pub(container_name, username, message)

    def generate_msg(self, container_name: str, from_user: str, to_user: str, message: str, params: dict):
        if 'reply' in params and params['reply'] != '':
            reply = params['reply']

            container_decrypted = self.localStorage.get_decrypted_container(container_name)
            reply_msg = False

            if from_user in container_decrypted['inbox']:
                for msg in container_decrypted['inbox'][from_user]:
                    if (reply[0:1] == '%' and msg['datetime'] == reply[1:]) or msg['sig'] == reply:
                        reply_msg = msg

                if reply_msg:
                    reply_msg_split = reply_msg['msg'].split("\n")
                    message += "\n\n\t<<< REPLY TO: [from:{} subject:{} time:{} sig:{}] <<<"\
                        .format(reply_msg['from'], reply_msg['subject'], reply_msg['datetime'], reply_msg['sig'])
                    for line in reply_msg_split:
                        if line != '':
                            message += "\n\t" + line
                    message += "\n\t>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>"
        return self.localStorage.generate_container_msg(container_name, from_user, to_user, message, params)

    def list_container_users(self, container_name: str):
        container = self.localStorage.get_encrypted_container(container_name)
        if container:
            return list(container['users'])
        else:
            return ()

    def __sync_container(self, container_data):
        container_name = container_data['container']['name']
        users = container_data['users']

        # Loading local container
        container = self.localStorage.get_encrypted_container(container_name)
        if not container:
            self.generate_container(container_name)
            container = self.localStorage.get_encrypted_container(container_name)

        t = datetime.fromtimestamp(time.time())
        container['container']['synchronized'] = t.strftime("%Y-%m-%d %H:%M:%S")

        # syncing users
        for username in container_data['users']:
            container['users'][username] = container_data['users'][username]

        # checking msg
        for sig in container_data['msg']:
            if sig not in container['msg']:
                res_verify = self.cryptor.verify(container_data['msg'][sig]['msg'],
                                             users[container_data['msg'][sig]['from']],
                                             base64.b64decode(sig))
                container['msg'][sig] = container_data['msg'][sig]
                # print(res_verify, container_data['msg'][sig])

        # checking pub
        for sig in container_data['pub']:
            if sig not in container['pub']:
                res_verify = self.cryptor.verify(container_data['pub'][sig]['msg'],
                                                 users[container_data['pub'][sig]['from']],
                                                 base64.b64decode(sig))
                container['pub'][sig] = container_data['pub'][sig]
                # print(res_verify, container_data['pub'][sig])

        # Saving
        self.localStorage.save_encrypted_container(container_name, container)
        self.remoteStorage.save_container(container_name, container)
        return True

    def sync(self):
        res = self.remoteStorage.scan()
        # print(self.remoteStorage.containers)
        if len(res):
            for container_filename in self.remoteStorage.containers:
                if self.__sync_container(self.remoteStorage.containers[container_filename]):
                    print("Synchronizing {} ... OK ".format(container_filename))
                    self.decrypt(self.remoteStorage.containers[container_filename]['container']['name'])
                    print("Decrypting {} ... OK ".format(self.remoteStorage.containers[container_filename]['container']['name']))
        return True

    def delete_container(self, container_name: str):
        containers = self.localStorage.list_containers()
        if container_name in containers:
            return self.localStorage.delete_container(container_name)
        return False

    def save(self, container_name: str):
        if not self.container_exists(container_name):
            self.generate_container(container_name)

        container = self.localStorage.get_encrypted_container(container_name)
        # print(container)
        users = self.localStorage.list_users()
        container_users = self.list_container_users(container_name)
        users_used = []
        # print(users)

        # PUBLIC messages
        messages_pub_encrypted = {}
        messages_pub = self.localStorage.list_pub_messages(container_name)
        # print(messages_pub)
        for username in messages_pub:
            pub_message = messages_pub[username]
            sig = self.cryptor.sign(pub_message['msg'], users[username]['priv'])
            sig = base64.b64encode(sig).decode('utf-8')

            messages_pub_encrypted[sig] = {
                'msg': pub_message['msg'],
                'from': username,
                'created': pub_message['created']
            }

            if not username in users_used:
                users_used.append(username)

            os.unlink(pub_message['filename'])

        # PRIVATE messages
        messages_priv_encrypted = {}
        messages_priv = self.localStorage.list_priv_messages(container_name)
        # print(messages_priv)
        for params in messages_priv:
            message_data = {}

            params_list = params.split('_')
            for param in params_list:
                key_value = param.split('-')
                message_data[key_value[0]] = key_value[1]

            if not message_data['from']:
                raise Exception('Message must have "from" parameter')
            if not message_data['to']:
                raise Exception('Message must have "to" parameter')

            username_from = message_data['from']
            username_to = message_data['to']

            priv_message = messages_priv[params]
            # print(priv_message)

            # enc = self.cryptor.encrypt(priv_message, users[username_to]['pub'])

            final_priv_message = {
                'msg': priv_message['msg'],
                'from': username_from,
                'to': username_to,
                'created': priv_message['created']
            }

            for param in message_data:
                final_priv_message[param] = message_data[param]

            if final_priv_message['subject'] is None:
                final_priv_message['subject'] = '<NO SUBJECT>'

            edata = {
                'msg': final_priv_message['msg'],
                'subject': final_priv_message['subject'],
            }

            enc = self.cryptor.encrypt_multiple(edata, container['users'][username_to])

            final_priv_message['msg'] = base64.b64encode(enc[0]['msg']).decode('utf-8')
            final_priv_message['subject'] = base64.b64encode(enc[0]['subject']).decode('utf-8')
            final_priv_message['key'] = base64.b64encode(enc[1]).decode('utf-8')

            sig = self.cryptor.sign(final_priv_message['msg'], users[username_from]['priv'])
            sig = base64.b64encode(sig).decode('utf-8')

            messages_priv_encrypted[sig] = final_priv_message

            if not username_from in users_used:
                users_used.append(username_from)

            os.unlink(priv_message['filename'])

        # print(messages_pub_encrypted)
        # print(messages_priv_encrypted)
        for sig in messages_priv_encrypted:
            container['msg'][sig] = messages_priv_encrypted[sig]

        for sig in messages_pub_encrypted:
            container['pub'][sig] = messages_pub_encrypted[sig]

        users_container = {}
        for username in users_used:
            users_container[username] = users[username]['pub']
        # print(users_container)

        for username in users_container:
            container['users'][username] = users_container[username]

        # print(container)
        self.localStorage.save_encrypted_container(container_name, container)

        return True

    def decrypt(self, container_name: str):
        container = self.localStorage.get_encrypted_container(container_name)

        # Collect users
        users = {}
        for username in container['users']:
            users[username] = container['users'][username]
        # print(users)

        etc_users = self.localStorage.list_users()

        decrypted_container = {'container': container['container'], 'inbox': {}, 'pub': {}}

        # Decrypted INBOX
        messages_inbox = {}

        for sig in container['msg']:
            to_user = container['msg'][sig]['to']
            if to_user in etc_users:
                # print(container['msg'][sig]['msg'])
                res_verify = self.cryptor.verify(container['msg'][sig]['msg'],
                                                 users[container['msg'][sig]['from']],
                                                 base64.b64decode(sig))

                if res_verify:
                    decrypted = self.cryptor.decrypt_multiple({
                        'msg': base64.b64decode(container['msg'][sig]['msg']),
                        'sbj': base64.b64decode(container['msg'][sig]['subject'])},
                        base64.b64decode(container['msg'][sig]['key']),
                        etc_users[to_user]['priv'])
                    # print(decrypted)

                    message_inbox = {
                        'sig': sig,
                        'from': container['msg'][sig]['from'],
                        'created': container['msg'][sig]['created'],
                        'subject': decrypted['sbj'],
                        'msg': decrypted['msg']
                    }

                    t = datetime.fromtimestamp(int(message_inbox['created']))
                    message_inbox['datetime'] = t.strftime("%Y-%m-%d %H:%M:%S")

                    if to_user not in messages_inbox:
                        messages_inbox[to_user] = []
                    messages_inbox[to_user].append(message_inbox)

        for username in messages_inbox:
            messages_inbox[username] = sorted(messages_inbox[username], reverse=True, key=lambda row: row['created'])
        # print(messages_inbox)
        decrypted_container['inbox'] = messages_inbox

        # Decrypted PUB
        messages_pub = []

        for sig in container['pub']:
            res_verify = self.cryptor.verify(container['pub'][sig]['msg'],
                                             users[container['pub'][sig]['from']],
                                             base64.b64decode(sig))
            if res_verify:
                message_pub = container['pub'][sig]
                message_pub['sig'] = sig
                t = datetime.fromtimestamp(int(message_pub['created']))
                message_pub['datetime'] = t.strftime("%Y-%m-%d %H:%M:%S")
                messages_pub.append(message_pub)

        decrypted_container['pub'] = sorted(messages_pub, reverse=True, key=lambda row: row['created'])

        # Saving decrypted container
        self.localStorage.save_decrypted_container(container_name, decrypted_container)

        # Saving inbox(your) messages
        for to_user in decrypted_container['inbox']:
            text_inbox = ''
            for inbox_msg in decrypted_container['inbox'][to_user]:
                text_inbox += "*** {} - {} - {} - {}".format(inbox_msg['from'], inbox_msg['subject'], inbox_msg['datetime'], inbox_msg['sig']) + "\n"
                text_inbox += inbox_msg['msg']
                text_inbox += "\n"
            # print(text_inbox)
            text_inbox_inverse = ''
            for inbox_msg in reversed(decrypted_container['inbox'][to_user]):
                text_inbox_inverse += "*** {} - {} - {} - {}".format(inbox_msg['from'], inbox_msg['subject'], inbox_msg['datetime'], inbox_msg['sig']) + "\n"
                text_inbox_inverse += inbox_msg['msg']
                text_inbox_inverse += "\n"
            # print(text_inbox_inverse)
            self.localStorage.save_decrypted_inbox(container_name, to_user, text_inbox, text_inbox_inverse)
        # Saving PUB messages
        text_pub = ''
        for pub_msg in decrypted_container['pub']:
            text_pub += "*** {} - {} - {}".format(pub_msg['from'], pub_msg['datetime'], pub_msg['sig']) + "\n"
            text_pub += pub_msg['msg']
            text_pub += "\n"
        # print(text_pub)

        text_pub_inverse = ''
        for pub_msg in reversed(decrypted_container['pub']):
            text_pub_inverse += "*** {} - {} - {}".format(pub_msg['from'], pub_msg['datetime'], pub_msg['sig']) + "\n"
            text_pub_inverse += pub_msg['msg']
            text_pub_inverse += "\n"
        # print(text_pub_inverse)
        self.localStorage.save_decrypted_pub(container_name, text_pub, text_pub_inverse)
        return

    def save_config(self, data):
        self.config = self.localStorage.get_config()
        for i in data:
            self.config[i] = data[i]
        self.localStorage.save_config(self.config)
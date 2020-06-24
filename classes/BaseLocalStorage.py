import abc


class BaseLocalStorage:
    @abc.abstractmethod
    def list_containers(self):
        pass

    def delete_container(self, container_name: str):
        pass

    @abc.abstractmethod
    def list_pub_messages(self, container_name: str):
        pass

    @abc.abstractmethod
    def list_pub_messages_user(self, container_name: str, username: str):
        pass

    @abc.abstractmethod
    def delete_pub_message(self, container_name: str, username: str):
        pass

    @abc.abstractmethod
    def list_priv_messages(self, container_name: str):
        pass

    @abc.abstractmethod
    def container_exists(self, container_name: str):
        pass

    @abc.abstractmethod
    def generate_container(self, container_name: str, data: str):
        pass

    @abc.abstractmethod
    def generate_container_pub(self, container_name: str, username: str, message: str):
        pass

    @abc.abstractmethod
    def generate_container_msg(self, container_name: str, from_user: str, to_user: str, message: str, params: dict):
        pass

    @abc.abstractmethod
    def list_users(self):
        pass

    @abc.abstractmethod
    def user_exists(self, username):
        pass

    @abc.abstractmethod
    def delete_user(self, username):
        pass

    @abc.abstractmethod
    def save_user(self, username, pub_key: bytes, priv_key: bytes):
        pass

    @abc.abstractmethod
    def get_container_path(self, container: str, username: str):
        pass

    @abc.abstractmethod
    def save_encrypted_container(self, container: str, data):
        return

    @abc.abstractmethod
    def get_encrypted_container(self, container: str):
        return

    @abc.abstractmethod
    def get_decrypted_container(self, container: str):
        return

    @abc.abstractmethod
    def container_upload(self, container: str, upload_path: str):
        return

    @abc.abstractmethod
    def save_decrypted_container(self, container: str, data):
        return

    @abc.abstractmethod
    def save_decrypted_pub(self, container: str, data: str, inverted_data: str):
        return

    @abc.abstractmethod
    def save_decrypted_inbox(self, container: str, from_username: str, data: str, inverted_data: str):
        return

    @abc.abstractmethod
    def get_config(self):
        return

    @abc.abstractmethod
    def save_config(self, config):
        return

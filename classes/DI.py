from classes.Container import Container
from classes.CryptorRSA import CryptorRSA
from classes.LocalStorageFS import LocalStorageFS
from classes.RemoteStorageFS import RemoteStorageFS
from classes.ScanerJSON import ScanerJSON


class DI:
    @staticmethod
    def create_container():
        if not hasattr(DI, 'container'):
            DI.container = Container(DI.create_local_storage(), DI.create_remote_storage(), DI.create_cryptor())
        return DI.container
        return

    @staticmethod
    def create_scanner():
        if not hasattr(DI, 'scanner'):
            DI.scanner = ScanerJSON()
        return DI.scanner

    @staticmethod
    def create_remote_storage():
        if not hasattr(DI, 'remote_storage'):
            DI.remote_storage = RemoteStorageFS(DI.create_scanner(), DI.get_config()['remote'])
        return DI.remote_storage

    @staticmethod
    def create_local_storage():
        if not hasattr(DI, 'local_storage'):
            DI.local_storage = LocalStorageFS()

            DI.local_storage.default_config = {
                  "user": "",
                  "container": "",
                  "remote": "",
                  "upload": "",
                  "editor": ""
                }
        return DI.local_storage

    @staticmethod
    def create_cryptor():
        if not hasattr(DI, 'cryptor'):
            DI.cryptor = CryptorRSA(rsa_bits=4096, blowfish_bits=256)
        return DI.cryptor

    @staticmethod
    def get_config():
        if not hasattr(DI, 'config'):
            DI.config = DI.create_local_storage().get_config()
        return DI.config

    @staticmethod
    def exist_container():
        if not hasattr(DI, 'config'):
            DI.config = DI.create_local_storage().get_config()
        return 'container' in DI.get_config()

    @staticmethod
    def exist_user():
        if not hasattr(DI, 'config'):
            DI.config = DI.create_local_storage().get_config()
        return 'user' in DI.get_config()
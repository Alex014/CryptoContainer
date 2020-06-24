from classes.Container import Container
from classes.CryptorRSA import CryptorRSA
from classes.LocalStorageFS import LocalStorageFS
from classes.RemoteStorageFS import RemoteStorageFS
from classes.ScanerJSON import ScanerJSON
import base64
import random

cryptor = CryptorRSA(rsa_bits=512, blowfish_bits=256)
local_storage = LocalStorageFS()
scanner = ScanerJSON(local_storage.get_config()['remote'])
remote_storage = RemoteStorageFS()

cnt = Container(local_storage, remote_storage, scanner, cryptor)


# cnt.save_config({'test': 'test'})

cnt.generate_container('container_test')
cnt.generate_user('user1')
cnt.generate_user('user2')
cnt.generate_user('user3')
cnt.generate_pub('container_test', 'user1', "Test message 1\n111111")
cnt.generate_pub('container_test', 'user2', "Test message 2\n222222")
cnt.generate_pub('container_test', 'user3', "Test message 3\n3333333333\n333")
cnt.generate_msg('container_test', 'user1', 'user2', "sdfoijgsdk;fgjsd;lkf", {'subject': 'Hello world !'})
cnt.generate_msg('container_test', 'user1', 'user2', "567;222222", {'subject': 'Hello 2'})
cnt.generate_msg('container_test', 'user2', 'user1', "54575;33333", {'subject': 'Hello 3'})

print(local_storage.list_containers())
print(cnt.container_exists('container_test'))
print(local_storage.list_users('container_test'))

cnt.save('container_test')
cnt.decrypt('container_test')
from classes.Container import Container
from classes.CryptorRSA import CryptorRSA
from classes.LocalStorageFS import LocalStorageFS
from classes.RemoteStorageFS import RemoteStorageFS
from classes.ScanerJSON import ScanerJSON

scanner = ScanerJSON()
remote_storage = RemoteStorageFS(scanner, '/run/media/user/CRYPTODRIVE')
cryptor = CryptorRSA(rsa_bits=512, blowfish_bits=256)
local_storage = LocalStorageFS()

cnt = Container(local_storage, remote_storage, cryptor)

cnt.sync()
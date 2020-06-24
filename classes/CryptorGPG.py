from classes.BaseCryptor import BaseCryptor
from pretty_bad_protocol import gnupg


class CryptorGPG(BaseCryptor):
    def __init__(self):
        return

    def generate(self):
        return

    def sign(self, data, key):
        return

    def verify(self, data, pub_key, signature):
        return

    def crypt(self, data, pub_key):
        return

    def decrypt(self, data, key):
        return

    def test(self):
        print(1)
        gpg = gnupg.GPG(
            binary='/usr/bin/gpg',
            homedir='./keys',
            keyring='pubring.gpg',
            secring='secring.gpg')
        print(2)
        key_input = gpg.gen_key_input(
            key_type='RSA',
            key_length=4096)
        print(key_input)
        key = gpg.gen_key(key_input)
        print(4)
        assert key.fingerprint
        print(key.fingerprint)
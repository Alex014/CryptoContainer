from classes.BaseCryptor import BaseCryptor
import rsa
import rsa.randnum
from Crypto.Cipher import Blowfish


class CryptorRSA(BaseCryptor):
    def __init__(self, **kwargs):
        """
        Encryption using RSA (asymmetric) and BLOWFISH (symmetric) algos
        :param kwargs:
            rsa_bits RSA encryption strength (1 .. 4096)
            blowfish_bits BLOWFISH encryption strength (1 .. 256)
        """
        super(CryptorRSA, self).__init__(16)
        
        if 'rsa_bits' in kwargs:
            self.rsa_bits = kwargs['rsa_bits']
        else:
            self.rsa_bits = 512

        if 'blowfish_bits' in kwargs:
            self.blowfish_bits = kwargs['blowfish_bits']
        else:
            self.blowfish_bits = 256

        return

    def generate(self):
        (pubkey, privkey) = rsa.newkeys(self.rsa_bits)
        pubkey_pkcs1 = pubkey.save_pkcs1()
        privkey_pkcs1 = privkey.save_pkcs1()
        return (pubkey_pkcs1, privkey_pkcs1)

    def sign(self, data, priv_key):
        privkey = rsa.PrivateKey(1,3,5,7,9)
        privkey = privkey.load_pkcs1(priv_key)

        return rsa.sign(data.encode('utf8'), privkey, 'MD5')

    def verify(self, data, pub_key, signature):
        pubkey = rsa.PublicKey(1, 3)
        pubkey = pubkey.load_pkcs1(pub_key)

        verify = True
        try:
            rsa.verify(data.encode('utf8'), signature, pubkey)
        except rsa.pkcs1.VerificationError:
            verify = False

        return verify

    def encrypt(self, data, pub_key):
        pubkey = rsa.PublicKey(1, 3)
        pubkey = pubkey.load_pkcs1(pub_key)

        blowfish_key = rsa.randnum.read_random_bits(self.blowfish_bits)
        encryptor = Blowfish.new(blowfish_key)

        encrypted_blowfish_key = rsa.encrypt(blowfish_key, pubkey)
        cipher_text = encryptor.encrypt(self._pad(data))

        return cipher_text, encrypted_blowfish_key

    def encrypt_multiple(self, data, pub_key):
        pubkey = rsa.PublicKey(1, 3)
        pubkey = pubkey.load_pkcs1(pub_key)

        blowfish_key = rsa.randnum.read_random_bits(self.blowfish_bits)
        encryptor = Blowfish.new(blowfish_key)

        encrypted_blowfish_key = rsa.encrypt(blowfish_key, pubkey)

        for key in data:
            data[key] = encryptor.encrypt(self._pad(data[key]))

        return data, encrypted_blowfish_key

    def decrypt(self, data, encrypted_blowfish_key, priv_key):
        privkey = rsa.PrivateKey(1,3,5,7,9)
        privkey = privkey.load_pkcs1(priv_key)

        blowfish_key = rsa.decrypt(encrypted_blowfish_key, privkey)
        decryptor = Blowfish.new(blowfish_key)
        msg = self._unpad(decryptor.decrypt(data))

        return msg.decode('utf8')

    def decrypt_multiple(self, data, encrypted_blowfish_key, priv_key):
        privkey = rsa.PrivateKey(1,3,5,7,9)
        privkey = privkey.load_pkcs1(priv_key)

        blowfish_key = rsa.decrypt(encrypted_blowfish_key, privkey)
        decryptor = Blowfish.new(blowfish_key)

        for key in data:
            data[key] = self._unpad(decryptor.decrypt(data[key])).decode('utf8')

        return data
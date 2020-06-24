import abc


class BaseCryptor:
    def __init__(self, BLOCK_SIZE):
        self.__BLOCK_SIZE = BLOCK_SIZE

    def _pad(self, s):
        return s + (self.__BLOCK_SIZE - len(s) % self.__BLOCK_SIZE) * chr(self.__BLOCK_SIZE - len(s) % self.__BLOCK_SIZE)

    def _unpad(self, s):
        return s[:-ord(s[len(s) - 1:])]

    @abc.abstractmethod
    def generate(self):
        pass

    @abc.abstractmethod
    def sign(self, data, key):
        pass

    @abc.abstractmethod
    def verify(self, data, pub_key, signature):
        pass

    @abc.abstractmethod
    def encrypt(self, data, pub_key):
        pass

    @abc.abstractmethod
    def encrypt_multiple(self, data, pub_key):
        pass

    @abc.abstractmethod
    def decrypt(self, data, encrypted_blowfish_key, priv_key):
        pass

    @abc.abstractmethod
    def decrypt_multiple(self, data, encrypted_blowfish_key, priv_key):
        """
        Decrypted multiple items
        :param data: dictionary of items to be decrypted
        """
        pass

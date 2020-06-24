from classes.CryptorRSA import CryptorRSA
import base64
import rsa

cryptor = CryptorRSA(rsa_bits=512, blowfish_bits=256)

(pubkey, privkey) = cryptor.generate()

print("\n *** Public key: \n" + pubkey.decode('utf-8'))
print("\n *** Private key: \n" + privkey.decode('utf-8'))

msg = "Pure Python RSA implementationPyPI Build Status Coverage Status Code Climate\n" \
      "Python-RSA is a pure-Python RSA implementation. It supports encryption and decryption, signing and verifying signatures, and key generation according to PKCS#1 version 1.5. It can be used as a Python library as well as on the commandline. The code was mostly written by Sybren A. Stüvel.\n" \
      "Documentation can be found at the Python-RSA homepage. For all changes, check the changelog."

print("\n *** Original message: \n" + msg)

encryption = cryptor.encrypt(msg, pubkey)
ciphertext = encryption[0]
bkey = encryption[1]

ciphertext = base64.b64encode(ciphertext)
bkey = base64.b64encode(bkey)

ciphertext = base64.b64decode(ciphertext)
bkey = base64.b64decode(bkey)

msg = cryptor.decrypt(ciphertext, bkey, privkey)

print("\n *** Decrypted message: \n" + msg)

# *******************************************

sig = cryptor.sign(msg, privkey)
sig = base64.b64encode(sig)
print("\n  *** Message signature: " + sig.decode('utf-8'))

sig = base64.b64decode(sig)
verify = cryptor.verify(msg, pubkey, sig)

print("\n  *** Verification result: ")
print(verify)
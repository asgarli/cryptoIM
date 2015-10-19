#!/usr/bin/python
import os
import getopt
import select
import socket
import sys
import hashlib
from base64 import b64encode, b64decode
from Crypto import Random
from M2Crypto.EVP import Cipher
from M2Crypto.EVP import HMAC
from M2Crypto.EVP import EVPError
from M2Crypto import RSA

class AbstractCryptoModule():
    
    def server_handshake(self, sock):
        pass
    
    def client_handshake(self, sock):
        pass
    
    def encrypt(self, message):
        return message
    
    def decrypt(self, ciphertext):
        return ciphertext

class SymEncCryptoModule(AbstractCryptoModule):
    def __init__(self, key_enc, key_auth):
        self.enc_alg = 'aes_128_cbc'
        self.auth_alg = 'sha1'
        self.ENC_OP, self.DEC_OP = 1, 0
        self.key_enc = hashlib.sha256(key_enc).digest()
        self.key_auth = hashlib.sha256(key_auth).digest()

    def server_handshake(self, sock):
        pass
    
    def client_handshake(self, sock):
        pass
    
    def encrypt(self, message):
        # 1. Encrypt
        iv = Random.new().read(16)
        encrypter = Cipher(self.enc_alg, self.key_enc, iv, self.ENC_OP)
        c = b64encode(encrypter.update(message) + encrypter.final())
        encryption = b64encode(iv) + c # b64encode(iv) size is always 24
        
        # 2. Sign
        hmac = HMAC(self.key_auth, self.auth_alg)
        hmac.update(encryption)
        auth_sig = b64encode(hmac.digest()) # auth_sig size is always 28
        
        return auth_sig + encryption
    
    def decrypt(self, sig_encryption):
        auth_sig = sig_encryption[:28]
        encryption = sig_encryption[28:]
        
        # 1. Verify signature
        hmac = HMAC(self.key_auth, self.auth_alg)
        hmac.update(encryption)
        if auth_sig != b64encode(hmac.digest()):
            raise EVPError("Authentication failure: " +  
                auth_sig + " does not match " + b64encode(hmac.digest()))

        # 2. Decrypt
        iv = b64decode(encryption[:24])
        ciphertext = b64decode(encryption[24:])
        decrypter = Cipher(self.enc_alg, self.key_enc, iv, self.DEC_OP)
        
        return decrypter.update(ciphertext) + decrypter.final()
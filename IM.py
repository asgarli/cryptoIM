#!/usr/bin/python
import os
import getopt
import select
import socket
import sys
from Utils import *
from IMCrypto import *
from M2Crypto.EVP import *
    
class TcpIpIM():
    def __init__(self, name, crypto_module, ip_port, ip_address=None):
        errprint("Initializing TcpIpIM ", name, "...")
        self.name = name
        self.crypto_module = crypto_module
        self.ss, self.cs = None, None
        self.ip_port, self.ip_address = ip_port, ip_address
        
        self.is_server = ip_address is None
    
    def run(self):
        try:
            self.run_server() if self.is_server else self.run_client()
            self.handle_client_connection()
        except EVPError as e:
            errprint("Encryption/Authentication error", e)
        except KeyboardInterrupt:
            errprint("Goodbye!")
        finally: 
            if self.cs is not None:
                self.cs.close()
            if self.ss is not None:
                self.ss.close()
            
    def run_server(self):
        self.ss = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.ss.bind(('', self.ip_port))
        self.ss.listen(1) # 1 should be enough since we only wait for 1 connection?
        errprint("Waiting for connection...")
        inputready, outputready, errorready = select.select([self.ss], [], []) 
        for e in errorready:
            errprint("ERROR", e)
        if self.ss in inputready: 
            if self.cs is None:
                self.cs, self.addr = self.ss.accept()
                errprint("Connection established!") 
            else:
                errprint("Connection already exists, ignoring request...")
    
    def run_client(self):
        self.cs = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        errprint("Connecting...")
        self.cs.connect((self.ip_address, self.ip_port))
        errprint("Connection established!")

    def handle_client_connection(self):
        self.crypto_module.server_handshake(self.cs)
        
        self.cs.setblocking(0)
        input_list = [sys.stdin, self.cs] 
        while True: 
            inputready, outputready, errorready = select.select(input_list, [], []) 
            for e in errorready:
                errprint("ERROR", e)
            for s in inputready: 
                if s == sys.stdin: 
                    message = sys.stdin.readline()
                    if message:
                        message = self.crypto_module.encrypt(message)
                        self.cs.sendall(message) # 
                    else:
                        errprint("Goodbye!")
                        return
                else: # if self.cs == s
                    message = s.recv(8192) 
                    if not message: 
                        errprint("Connection terminated by the other party!")
                        return
                    sys.stdout.write(
                        self.crypto_module.decrypt(message))
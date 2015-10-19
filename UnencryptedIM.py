#!/usr/bin/python
import argparse
import os
import select
import socket
import sys
from IM import *
from IMCrypto import *

def main(argv):
    
    port = 9999
    im = None
    
    parser = argparse.ArgumentParser(description='Unncrypted IM.')
    group = parser.add_mutually_exclusive_group()
    group.add_argument("-s", "--server", action="store_true", 
                    help='if you want to run as server')
    group.add_argument('-c', "--client", 
                    help='if you want to run as client and connect to CLIENT')

    args = parser.parse_args()

    cm = AbstractCryptoModule()

    if args.server:
        im = TcpIpIM("Bob", cm, port)
    elif args.client:
        im = TcpIpIM("Alice", cm, port, args.client)    
          
    if im is not None:
        im.run()
 
if __name__ == "__main__":
   main(sys.argv[1:])
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
    
    parser = argparse.ArgumentParser(description='Encrypted IM.')
    group = parser.add_mutually_exclusive_group()
    group.add_argument("-s", "--server", action="store_true", 
                    help='if you want to run as server')
    group.add_argument('-c', "--client", 
                    help='if you want to run as client and connect to CLIENT')
    
    parser.add_argument('-confkey', help='confidentiality key')
    parser.add_argument('-authkey', help='authenticity key')

    args = parser.parse_args()

    if not args.confkey:
        print "Error: provide confidentiality key with -confkey"
        sys.exit(2)
    if not args.authkey:
        print "Error: provide authenticity key with -authkey"
        sys.exit(2)
        
    cm = SymEncCryptoModule(args.confkey, args.authkey)
        
    if args.server:
        im = TcpIpIM("Bob", cm, port)
    elif args.client:
        im = TcpIpIM("Alice", cm, port, args.client)    
          
    if im is not None:
        im.run()
 
if __name__ == "__main__":
   main(sys.argv[1:])
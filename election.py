#!/usr/bin/env python2.7
import time, socket, os, uuid, sys, kazoo, logging, signal, inspect
from kazoo.client import KazooClient
from kazoo.client import KazooState
from kazoo.exceptions import KazooException

ELECTION_PATH="/election"

class Election:

    def __init__(self, zk, guid, func, args):
        self.election_path = ELECTION_PATH + "/" + guid.__str__
        self.zk = zk
        self.is_leader = False
        if not (inspect.isfunction(func)) and not(inspect.ismethod(func)):
            logging.debug("not a function "+str(func))
            raise SystemError
        self.real_path = self.zk.create(self.election_path, ephemeral=True, sequence=True)
        print("**********")
        print("Creaded node real path: " + real_path)
        print("Watch node: " + args[0])
        print("Callback function: " + func.__str__)
        print("**********")
        self.zk.get(args[0], watch=func)
        
        def signal_handler(signal, frame):
            print(frame)
            del self
        signal.signal(signal.SIGTERM, signal_handler)
    
    def is_leading(self):
        return self.is_leader
    
    #perform a vote..    
    def ballot(self,children):
        #TO COMPLETE
        pass


if __name__ == '__main__':
    zkhost = "127.0.0.1:2181" #default ZK host
    logging.basicConfig(format='%(asctime)s %(message)s',level=logging.DEBUG)
    if len(sys.argv) == 2:
        zkhost=sys.argv[2]
        print("Using ZK at %s"%(zkhost))
    zk = utils.init()
    if zk.exists(ELECTION_PATH) == None:
        zk.create(ELECTION_PATH, ephemeral=False)
    while True:
        time.sleep(1)
#!/usr/bin/env python2.7
import time, socket, os, uuid, sys, kazoo, logging, signal, utils
from election import Election
from utils import MASTER_PATH
from utils import TASKS_PATH
from utils import DATA_PATH
from utils import WORKERS_PATH


class Worker:

    def __init__(self,zk):
        self.zk = zk
        self.uuid = uuid.uuid4()
        self.znodePath = WORKERS_PATH + "/" + self.uuid.__str__()
        zk.create(self.znodePath, ephemeral=False)
        # Watch for children aka task assignments.
        zk.get_children(self.znodePath, watch=self.assignment_change, include_data=True)
    
    #do something upon the change on assignment    
    def assignment_change(self, atask):
        print(atask)
        utils.task(atask)
        self.zk.set(DATA_PATH + "/" + atask.path.__str__(), '0') # Set task result into data node.
        self.zk.get_children(self.znodePath, watch=self.assignment_change, include_data=True)
        

if __name__ == '__main__':
    zk = utils.init()    
    worker = Worker(zk)
    while True:
        time.sleep(1)

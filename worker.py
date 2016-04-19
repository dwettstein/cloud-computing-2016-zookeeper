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
        self.znodePath = WORKERS_PATH + "/" + self.uuid.__str__
        zk.create(self.znodePath, ephemeral=False)
        # Watch for children aka task assignments.
        zk.get_children(self.znodePath, watch=assignment_change)
    
    #do something upon the change on assignment    
    def assignment_change(self, atask, stat):
        print("Version: %s, data: %s" % (stat.version, atask.decode("utf-8")))
        print(atask)
        print(stat)
        # TO COMPLETE
        

if __name__ == '__main__':
    zk = utils.init()    
    worker = Worker(zk)
    while True:
        time.sleep(1)

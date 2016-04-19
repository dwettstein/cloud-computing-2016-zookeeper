#!/usr/bin/env python2.7
import time, socket, os, uuid, sys, kazoo, logging, signal, utils
from election import Election
from utils import MASTER_PATH
from utils import TASKS_PATH
from utils import DATA_PATH
from utils import WORKERS_PATH


class Master:

    #initialize the master
    def __init__(self,zk):
        self.master = False
        self.zk = zk
        self.znodePath = MASTER_PATH + "/manualMaster"
        zk.create(self.znodePath, ephemeral=False)
        # Watch for children aka task assignments.
        zk.get_children(TASKS_PATH, watch=self.assign)
    
    #assign tasks                    
    def assign(self,children):
        workers = self.zk.get_children(WORKERS_PATH)
        free_worker = None
        least_assignments = sys.maxint
        for worker in workers:
            assignments = self.zk.get_children(WORKERS_PATH + "/" + worker.__str__())
            if (len(assignments) < least_assignments):
                least_assignments = len(assignments)
                free_worker = worker
        if free_worker != None 
            self.zk.create(WORKERS_PATH + "/" + worker.__str__() + "/" + children.__str__())


if __name__ == '__main__':
    zk = utils.init()
    master = Master(zk)
    while True:
        time.sleep(1)

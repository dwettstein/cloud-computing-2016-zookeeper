#!/usr/bin/env python2.7
import time, socket, os, uuid, sys, kazoo, logging, signal, utils
from election import Election
from utils import MASTER_PATH
from utils import TASKS_PATH
from utils import DATA_PATH
from utils import WORKERS_PATH


class Worker:

    def __init__(self, zk):
        self.zk = zk
        self.uuid = uuid.uuid4()
        self.znodePath = WORKERS_PATH + "/" + self.uuid.__str__()
        self.zk.create(self.znodePath, ephemeral=False)
        # Watch for children aka task assignments.
        self.zk.get_children(self.znodePath, watch=self.assignment_change)
    
    #do something upon the change on assignment    
    def assignment_change(self, workerNode):
        # task object: WatchedEvent(type='CHILD', state='CONNECTED', path=u'/workers/a7deabb6-ecc0-4249-9fee-87e301a71747')
        print(workerNode)
        children = self.zk.get_children(workerNode.path.__str__())
        for child in children:
            print("Found child '%s' in worker '%s'." % (child, workerNode.path.__str__()))
            childTuple = self.zk.get(child)
            print("childTuple: " + childTuple)
            utils.task(childTuple)
            dataPath = DATA_PATH + "/" + (childTuple.path.__str__().replace(WORKERS_PATH, ""))
            self.zk.set(dataPath, '0') # Set task result into data node.
        self.zk.get_children(self.znodePath, watch=self.assignment_change)
        

if __name__ == '__main__':
    zk = utils.init()    
    worker = Worker(zk)
    while True:
        time.sleep(1)

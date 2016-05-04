#!/usr/bin/env python2.7
import time, socket, os, uuid, sys, kazoo, logging, signal, utils
from election import Election
from utils import MASTER_PATH
from utils import TASKS_PATH
from utils import DATA_PATH
from utils import WORKERS_PATH
from utils import WORKERSEPH_PATH


class Worker:

    def __init__(self, zk):
        self.zk = zk
        self.uuid = uuid.uuid4()
        self.znodePath = WORKERS_PATH + "/" + self.uuid.__str__()
        self.znodePath2 = WORKERSEPH_PATH + "/" + self.uuid.__str__()
        self.zk.create(self.znodePath, ephemeral=False)
        self.zk.create(self.znodePath2, ephemeral=True)
        # Watch for children aka task assignments.
        self.zk.get_children(self.znodePath, watch=self.assignment_change)
    
        def signal_handler(signal, frame):
            zk = utils.init()
            worker_children = zk.get_children(WORKERS_PATH)
            for child in worker_children:
                print("Deleting worker child: " + str(child))
                zk.delete(WORKERSEPH_PATH + "/" + child)
                return
        signal.signal(signal.SIGTERM, signal_handler)
    
    #do something upon the change on assignment    
    def assignment_change(self, workerNode):
        self.zk.get_children(self.znodePath, watch=self.assignment_change)
        # task object: WatchedEvent(type='CHILD', state='CONNECTED', path=u'/workers/a7deabb6-ecc0-4249-9fee-87e301a71747')
        print("**********")
        print(workerNode.__str__())
        print("**********")
        children = self.zk.get_children(workerNode.path.__str__())
        for child in children:
            print("**********")
            print("Found child '%s' in worker '%s'." % (child.__str__(), workerNode.path.__str__()))
            print("**********")
            #childTuple = self.zk.get(workerNode.path.__str__() + "/" + child.__str__())
            dataPath = DATA_PATH + "/" + child
            dataTuple = self.zk.get(dataPath)
            #print("**********")
            #print("dataTuple: " + dataTuple.__str__())
            #print("**********")
            utils.task(dataTuple)
            if self.zk.exists(workerNode.path.__str__()):
                self.zk.set(dataPath, '0') # Set task result into data node.
                self.zk.delete(workerNode.path.__str__() + "/" + child)


if __name__ == '__main__':
    zk = utils.init()
    for i in range(3):
        worker = Worker(zk)
    while True:
        time.sleep(1)

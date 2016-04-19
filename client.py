#!/usr/bin/env python2.7
import time, socket, os, uuid, sys, kazoo, logging, signal, utils, random
from election import Election
from utils import MASTER_PATH
from utils import TASKS_PATH
from utils import DATA_PATH
from utils import WORKERS_PATH


class Client:
    
    def __init__(self,zk):
        self.zk = zk
    
    def submit_task(self):
        self.uuid = uuid.uuid4()
        self.taskPath = TASKS_PATH + "/" + self.uuid.__str__
        self.dataPath = DATA_PATH + "/" + self.uuid.__str__
        # Create task.
        self.zk.create(self.taskPath, ephemeral=False)
        # Watch for task change.
        self.zk.get_children(self.taskPath, watch=task_completed)
        # Create data.
        self.zk.create(self.dataPath, value='data', ephemeral=False)
        
    #REACT to changes on the submitted task..                   
    def task_completed(self, data, stat):
        print("Version: %s, data: %s" % (stat.version, data.decode("utf-8")))
        print(data)
        print(stat)
        #self.zk.delete()
        #TO COMPLETE
    
    def submit_task_loop(self):
        max_iterations = 2
        current_iteration = 0
        while (current_iteration < max_iterations):
            current_iteration++
            self.submit_task()


if __name__ == '__main__':
    zk = utils.init()    
    client = Client(zk)
    client.submit_task_loop()
    while True:
        time.sleep(1)


#!/usr/bin/env python2.7
import time, socket, os, uuid, sys, kazoo, logging, signal, utils, random
from election import Election
from utils import MASTER_PATH
from utils import TASKS_PATH
from utils import DATA_PATH
from utils import WORKERS_PATH


class Client:
    
    def __init__(self, zk):
        self.zk = zk
    
    def submit_task(self):
        self.uuid = uuid.uuid4()
        self.taskPath = TASKS_PATH + "/" + self.uuid.__str__()
        self.dataPath = DATA_PATH + "/" + self.uuid.__str__()
        # Create data.
        self.zk.create(self.dataPath, value='3', ephemeral=False) # A task takes 3 seconds for completion.
        # Create task.
        self.zk.create(self.taskPath, value='0', ephemeral=False) # Value 0 means unassigned.
        # Watch for data change.
        self.zk.get(self.dataPath, watch=self.task_completed)
        
    #REACT to changes on the submitted task..                   
    def task_completed(self, dataNode):
        print("**********")
        print(dataNode.__str__())
        print("**********")
        result = self.zk.get(dataNode.path)
        print("**********")
        print("result: " + result.__str__())
        print("**********")
        taskId = dataNode.path.__str__().replace(DATA_PATH, "")
        self.zk.delete(TASKS_PATH + taskId)
        self.zk.delete(dataNode.path)
    
    def submit_task_loop(self):
        max_iterations = 20
        current_iteration = 0
        while (current_iteration < max_iterations):
            current_iteration += 1
            self.submit_task()
            time.sleep(1)


if __name__ == '__main__':
    zk = utils.init()    
    client = Client(zk)
    client.submit_task_loop()
    while True:
        time.sleep(1)
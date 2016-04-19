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
        # children: WatchedEvent(type='CHILD', state='CONNECTED', path=u'/tasks')", data='', acl=[ACL(perms=31, acl_list=['ALL'], id=Id(scheme='world', id='anyone'))], flags=0)
        tasks = self.zk.get_children(TASKS_PATH) # TASKS_PATH should be equal to children.path
        unassignedTasks = []
        for task in tasks:
            taskTuple = self.zk.get(TASKS_PATH + "/" + task.__str__()).__str__()
            print("taskTuple: " + taskTuple[0])
            if taskTuple[0] == '0':
                unassignedTasks.append(task)
        print("Found %i unassigned tasks." % len(unassignedTasks))    
        # Assign open tasks to workers. Usually there should be only one unassigned task at a time.
        for unassignedTask in unassignedTasks:
            workers = self.zk.get_children(WORKERS_PATH)
            free_worker = None
            least_assignments = sys.maxint
            for worker in workers:
                assignments = self.zk.get_children(WORKERS_PATH + "/" + worker.__str__())
                if (len(assignments) < least_assignments):
                    least_assignments = len(assignments)
                    free_worker = worker
            if free_worker != None: 
                self.zk.create(WORKERS_PATH + "/" + worker.__str__() + "/" + unassignedTask.__str__())
                self.zk.set(TASKS_PATH + "/" + unassignedTask, '1')
        self.zk.get_children(TASKS_PATH, watch=self.assign)
        

if __name__ == '__main__':
    zk = utils.init()
    master = Master(zk)
    while True:
        time.sleep(1)

#!/usr/bin/env python2.7
import time, socket, os, uuid, sys, kazoo, logging, signal, utils
from election import Election
from utils import MASTER_PATH
from utils import TASKS_PATH
from utils import DATA_PATH
from utils import WORKERS_PATH


class Master:

    #initialize the master
    def __init__(self, zk, prev_election):
        self.master = prev_election == None ? True : False
        self.zk = zk
        self.uuid = uuid.uuid4()
        self.election = Election(self.zk, self.uuid, self.start_election, prev_election)
        
        self.znodePath = MASTER_PATH + "/" + self.uuid.__str__()
        self.zk.create(self.znodePath, ephemeral=False)
        # Watch for children aka task assignments.
        self.zk.get_children(TASKS_PATH, watch=self.assign)
    
    def start_election(self, election_child):
        print("************* Election Child: " + election_child.__str__)
    
    #assign tasks                    
    def assign(self, tasks):
        self.zk.get_children(TASKS_PATH, watch=self.assign)
        # children: WatchedEvent(type='CHILD', state='CONNECTED', path=u'/tasks')", data='', acl=[ACL(perms=31, acl_list=['ALL'], id=Id(scheme='world', id='anyone'))], flags=0)
        if self.master:
            tasks = self.zk.get_children(TASKS_PATH) # TASKS_PATH should be equal to tasks.path
            unassignedTasks = []
            for task in tasks:
                taskTuple = self.zk.get(TASKS_PATH + "/" + task.__str__())
                print("**********")
                print("taskTuple: " + taskTuple.__str__())
                print("**********")
                if taskTuple[0] == '0':
                    unassignedTasks.append(task)
            print("**********")
            print("Found %i unassigned tasks." % len(unassignedTasks))
            print("**********")  
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
                    self.zk.set(TASKS_PATH + "/" + unassignedTask, '1') # set value to "assigned"
                    print("**********")
                    print("Assigned task '%s' to worker '%s'." % (unassignedTask.__str__(), worker.__str__()))
                    print("**********")
        
        

if __name__ == '__main__':
    zk = utils.init()
    
    prev_election = None
    for i in 1..5:
        master = Master(zk, prev_election)
        prev_election = master.election
    while True:
        time.sleep(1)

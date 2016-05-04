#!/usr/bin/env python2.7
import time, socket, os, uuid, sys, kazoo, logging, signal, utils
from election import Election
from utils import MASTER_PATH
from utils import TASKS_PATH
from utils import DATA_PATH
from utils import WORKERS_PATH
from utils import WORKERSEPH_PATH
from utils import ELECTION_PATH


class Master:

    #initialize the master
    def __init__(self, zk, prev_election):
        self.zk = zk
        self.uuid = uuid.uuid4()
        self.election = Election(self.zk, self.uuid, self.start_election, prev_election)
        self.znodePath = MASTER_PATH + "/" + self.uuid.__str__()
        self.zk.create(self.znodePath, ephemeral=False)
        # Watch for children aka task assignments.
        self.zk.get_children(TASKS_PATH, watch=self.assign)
        # Watch for worker deletion.
        self.zk.get_children(WORKERSEPH_PATH, watch=self.reset_to_unassigned)
    
    def start_election(self, election_child):
        print("**********")
        print("Deleted election child: " + str(election_child))
        print("**********")
        splits = str(election_child.path).split("_")
        child_guid = splits[0].replace(ELECTION_PATH + "/", "")
        child_number = splits[1]
        self.zk.delete(MASTER_PATH + "/" + child_guid)
        election_children = self.zk.get_children(ELECTION_PATH)
        election_nodes = []
        
        # deleted node
        node_to_delete = None
        for master in utils.master_list:
            if str(master.uuid) == child_guid:
                node_to_delete = master
        node_to_delete.election.is_leader = False
        utils.master_list.remove(node_to_delete)
        for child in election_children:
            child_splits = str(child).split("_")
            child_tuple = (child_splits[0], child_splits[1])
            election_nodes.append(child_tuple)
        sorted_list = sorted(election_nodes, key=lambda x: x[1])
        new_master = sorted_list[0]
        
        # Check if first item of cutted list is equal to the new master.
        # cutted_sorted_list = [elem for elem in sorted_list if elem[1] < child_number]
        # if len(cutted_sorted_list) > 0:
        #     next_election_child = cutted_sorted_list[len(cutted_sorted_list) - 1]
        #     self.zk.get(ELECTION_PATH + "/" + next_election_child[0] + "_" + next_election_child[1], watch=self.start_election)
        
        print("New elected master: " + new_master[0])
        for master in utils.master_list:
            if str(master.uuid) == new_master[0]:
                master.election.is_leader = True
                return
        
    #assign tasks                    
    def assign(self, tasks_event):
        self.zk.get_children(TASKS_PATH, watch=self.assign)
        # children: WatchedEvent(type='CHILD', state='CONNECTED', path=u'/tasks')", data='', acl=[ACL(perms=31, acl_list=['ALL'], id=Id(scheme='world', id='anyone'))], flags=0)
        if self.election.is_leading:
            tasks = self.zk.get_children(TASKS_PATH) # TASKS_PATH should be equal to tasks.path
            unassignedTasks = []
            for task in tasks:
                taskTuple = self.zk.get(TASKS_PATH + "/" + task.__str__())
                #print("**********")
                #print("taskTuple: " + taskTuple.__str__())
                #print("**********")
                if taskTuple[0] == '0':
                    unassignedTasks.append(task)
            #print("**********")
            #print("Found %i unassigned tasks." % len(unassignedTasks))
            #print("**********")  
            # Assign open tasks to workers. Usually there should be only one unassigned task at a time.
            for unassignedTask in unassignedTasks:
                workers = self.zk.get_children(WORKERS_PATH)
                free_worker = None
                least_assignments = sys.maxint
                for worker in workers:
                    assignments = self.zk.get_children(WORKERS_PATH + "/" + worker.__str__())
                    #print("**********")
                    #print("worker: " + worker.__str__())
                    #print("number of assignments: " + len(assignments).__str__())
                    #print("least assignments: " + least_assignments.__str__())
                    #print("**********")
                    if (len(assignments) < least_assignments):
                        least_assignments = len(assignments)
                        free_worker = worker
                if free_worker != None: 
                    self.zk.create(WORKERS_PATH + "/" + free_worker.__str__() + "/" + unassignedTask.__str__())
                    self.zk.set(TASKS_PATH + "/" + unassignedTask, free_worker.__str__()) # set value to assigned worker guid
                    print("**********")
                    print("Assigned task '%s' to worker '%s'." % (unassignedTask.__str__(), free_worker.__str__()))
                    print("**********")

    def reset_to_unassigned(self, deleted_worker):
        self.zk.get_children(WORKERSEPH_PATH, watch=self.reset_to_unassigned)
        if self.election.is_leading:
            all_workers = self.zk.get_children(WORKERSEPH_PATH)
            all_tasks = self.zk.get_children(TASKS_PATH)
            for task in all_tasks:
                task_node = self.zk.get(TASKS_PATH + "/" + task.__str__())
                #print("task_node: " + task_node.__str__())
                if not (task_node[0].__str__() in all_workers):
                    print("Reset to unassigned, task: " + task.__str__())
                    self.zk.set(TASKS_PATH + "/" + task.__str__(), '0')
                    self.zk.delete(WORKERS_PATH + "/" + task_node[0].__str__(), recursive=True)
            self.assign(None)

if __name__ == '__main__':
    zk = utils.init()
    
    prev_election = None
    for i in range(2):
        master = Master(zk, prev_election)
        prev_election = master.election
        utils.master_list.append(master)
    while True:
        time.sleep(1)

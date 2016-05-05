TODO [EXERCISE] Consider scenario 4 and assume that the master lags (e.g., due to a long garbage-collection cycle) instead of crashing.

# Cloud Computing Systems 2016 - Apache ZooKeeper
Implementation of fault-tolerance techniques in a distributed setting based on master/worker architecture.

#### Authors

- Reto Schiegg
- David Wettstein


#### Git repository

- https://github.com/dwettstein/zk


#### Deployment

| **ID** | **Owner**  | **Group** | **Name**                     | **Status** | **Host**      | **IPs**      |
|--------|------------|-----------|------------------------------|------------|---------------|--------------|
|  7415  | r.schiegg1 |   ccs16   | SchieggWettstein_ZooKeeper_3 |  RUNNING   | newcluster-33 | 172.16.2.122 |
|  7413  | r.schiegg1 |   ccs16   | SchieggWettstein_ZooKeeper_2 |  RUNNING   | newcluster-19 | 172.16.2.121 |
|  7412  | r.schiegg1 |   ccs16   | SchieggWettstein_ZooKeeper_1 |  RUNNING   | newcluster-26 | 172.16.2.120 |


# Description of the project

## Setup

#### Used technologies/resources

- [Apache ZooKeeper](http://zookeeper.apache.org)
- [Python 2.7](https://docs.python.org/2.7/)
- [Kazoo library](http://kazoo.readthedocs.org/en/latest/)
- [zk-shell](https://github.com/rgs1/zk_shell)


#### Running ZooKeeper

Use _ssh_ for connecting to the appropriate VM, _cd_ to the project's repository and start the Python scripts in the following order:
```
ubuntu@ubuntu:~/zk$ . reset_zookeeper.sh
ubuntu@ubuntu:~/zk$ python master.py
ubuntu@ubuntu:~/zk$ python worker.py
ubuntu@ubuntu:~/zk$ python client.py
ubuntu@ubuntu:~/zk$ zk-shell localhost     # see what's happening
```

To remove/kill a master or a worker:
```
ubuntu@ubuntu:~/zk$ ps aux
ubuntu@ubuntu:~/zk$ kill {master.py_process_id | worker.py_process_id}
```


## Apache ZooKeeper

TODO: Short description about ZooKeeper.


## Master/Worker architecture

![Architecture](../architecture.png?raw=true)

TODO: Short description about architecture.

#### Master/Worker responsibilities

TODO David: Show responsibilities and the different watchers (sketch).

#### Leader election

TODO: Explain our implemented leader election algorithm and how it works.


## Load-balancing

TODO David


## Fault-tolerance

In this chapter, we will discuss the different fault-tolerance scenarios. In the more complex scenarios, a log file is provided in order to proove the correctness of our algorithm. A log file is separated by the following: zk-shell tree, master, worker, client.

#### c1w1m1 - A worker or client fails

If a client fail, no more tasks will be created and a new client could be started straight forward. The only side effect is, that executed tasks will not be deleted, if the result is available. However, this side effect does not conflict with functions of the system. In addition, this can be easily fixed by just iterating once over all data and look, if the result is already stored in the value of the znode.
If a single worker fails, no more tasks will be executed and all tasks remain unassigned. After starting a new worker instance, the unassigned tasks will be assigned to the new worker. Therefore, there will be no further issues.

#### c1w2m1 - A worker fails

Log: [c1w2m1 - A worker fails](../logs/20160503_c1w2m1-worker_fail.log?raw=true)

After starting a client, a master and two workers, we waited until both workers had more than 3 tasks assigned. Due to our load-balancing the tasks were equally split. By sending a kill command to the worker process, one ephemeral worker node was deleted. As the master watches on changes in the "/workers_eph" node, he recognized that 4 tasks were assigned to a worker that does not exist anymore. Consequentely, the master reassigned the 4 tasks to the other worker. This behavior is more than apparent by the output of the master, where is says that 4 tasks were reassigned. In addition, the zookeeper tree indicates well that tasks were assigned to both workers, a worker got deleted and all tasks were executed (no more tasks nodes in the tree after stopping the client).


#### c2w2m1 - Workers compete in executing the tasks

Log: [c2w2m1 - Workers compete in executing the tasks](../logs/20160503_c2w2m1-workers_compete_in_executing_the_tasks.log?raw=true)

First, we started two workers, one master and two clients. Due to our load-balancing implemented in the master, each worker gets the same amount of tasks assigned. This is cearly visible in the master log section, where the assignment of a task is almost alternately by the worker. As we store the assigned tasks underneath a workers node, the workers do not conflict in executing the tasks. After stopping the client is is clear, that all tasks were executed as no more tasks are in the zookeeper tree.


#### c2w2m2 - The backup resumes the job of the master upon a failure

Log: [c2w2m2 - A master fails](../logs/20160503_c2w2m2-master_fail.log?raw=true)

After starting two master instance, two workers and two clients, the master node election was successfully exectued as the node with the lower sequencial number (0000000000) was initially selected as the master. Next, we waited until the master assigned a couple of tasks to both workers. Then, we exectued the kill command with the master's process-id  in order to delete the master. This is more than apparent in the zookeeper tree where the election node with the number (0000000000) and the master node was deleted. In addition, it is also clearly visible in the master log section, where it says "New elected master" with the new master node id (previos the backup). To test, if still further tasks were assigned, we continued the execution of the system. In all section of the log, you can examine that the client still generates tasks, the master still assigns tasks and the worker still executes tasks.


## Cluster mode

When zookeeper is in cluster mode, the zookeeper tree is shared with all servers. Therefore, zookeeper synchronizes all modifications made in the tree between the servers. As the configuration of such a cluster is done within minutes, it is very convenient to scale such a system. We tested our system by running the two instances of clients, workers and masters. However, an instance of a type (client, worker, master) is only on one server. Therefore, if a server is fails, there still exists at least an instance of each type. As the master-election nodes and the worker nodes are denoted as ephemeral, they will be deleted when the corresponding thread dies resp. when the server crashes. As a result, the master/worker system would detect the change and act accordingly.

Example: If the server with a worker instance crashes, the corresponding ephemeral node will be deleted. As the master watches on "/workers_eph", the master will detect the change and will search for tasks which are assigned to the deleted worker. Due to the worker instance on another server, there still are workers and the master can start the re-assignment accordingly to the c1w2m1-case in the fault-tolerance chapter.


## Summary

Zookeeper is a very helpful system for developing scaleable applications with lots of distributed coordination. Firstly, it takes some effort to understand the complexity of the master/worker system as well as the different functionalities of zookeeper. However, after working with zookeeper a bit, you get the comprehension of working with the zookeeper tree, its znodes and the watcher-callback-functions.
In addition, we were surprised how simple it is to configure a zookeeper in cluster mode. Consequentely, zookeeper is a big support in terms of implementing scaleable distributed systems.
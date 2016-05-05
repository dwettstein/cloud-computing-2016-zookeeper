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

If a client fail, no more tasks will be created and a new client could be started straight forward. The only side effect is, that executed tasks will not be deleted, if the result is available. However, this side effect does not conflict with functions of the system. In addition, this be easily fixed by just iterating once over all data and look, if the result is already stored in the value of the znode.
If a single worker fails, no more tasks will be executed and all tasks remain unassigned. After starting a new worker instance, the unassigned tasks will be assigned to the new worker. Therefore, there will be no further issues.

#### c1w2m1 - A worker fails

Log: [c1w2m1 - A worker fails](../logs/20160503_c1w2m1-worker_fail.log?raw=true)

TODO  Reto


#### c2w2m1 - Workers compete in executing the tasks

Log: [c2w2m1 - Workers compete in executing the tasks](../logs/20160503_c2w2m1-workers_compete_in_executing_the_tasks.log?raw=true)

TODO  Reto


#### c2w2m2 - The backup resumes the job of the master upon a failure

Log: [c2w2m2 - A master fails](../logs/20160503_c2w2m2-master_fail.log?raw=true)

TODO  Reto


## Cluster mode

TODO Reto: Describe the observations in cluster mode.


## Summary

TODO Reto
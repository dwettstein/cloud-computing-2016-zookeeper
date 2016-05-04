#!/usr/bin/env bash

zk-shell --run-once "rmr /tasks" localhost
zk-shell --run-once "rmr /data" localhost
zk-shell --run-once "rmr /workers" localhost
zk-shell --run-once "rmr /workers_eph" localhost
zk-shell --run-once "rmr /master" localhost
zk-shell --run-once "rmr /election" localhost
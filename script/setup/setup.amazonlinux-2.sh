#!/bin/bash

yum upgrade -y
yum install -y gcc gcc-c++ python3 python3-pip python3-devel make cmake3 git wget zip unzip tar xz numactl
yum clean all && rm -rf /var/cache/yum

#!/bin/bash

apt upgrade -y
apt install -y gcc g++ python3 python3-pip make cmake git wget zip libz-dev vim numactl cpufreqd
apt clean

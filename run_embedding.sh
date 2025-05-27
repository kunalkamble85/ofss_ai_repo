#!/bin/bash
export http_proxy=http://www-proxy-hqdc.us.oracle.com:80
export https_proxy=http://www-proxy-hqdc.us.oracle.com:80
export no_proxy=localhost,127.0.0.1,.us.oracle.com,.oraclecorp.com
export PYTHONPATH=./src/utils:$PYTHONPATH
export PATH=$PATH:$PYTHONPATH
export ORACLE_WALLET_PASSWORD=EMsingle@12345
nohup python ./src/embedding_job/create_embedding.py > ./logs/embedding.log 2>&1 &
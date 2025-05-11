#!/bin/bash
export HF_HOME=/home/opc/hf_home
export HUGGINGFACEHUB_API_TOKEN=
export JIRA_API_TOKEN=
export JIRA_INSTANCE_URL=https://kunalkamble85.atlassian.net
export JIRA_USERNAME=kunalkamble85@gmail.com
export JIRA_CLOUD=False
export http_proxy=http://www-proxy-hqdc.us.oracle.com:80
export https_proxy=http://www-proxy-hqdc.us.oracle.com:80
export no_proxy=localhost,127.0.0.1,.us.oracle.com,.oraclecorp.com
export PYTHONPATH=/src/utils:$PYTHONPATH
export PATH=$PATH:$PYTHONPATH
nohup uvicorn src.rest_endpoint:app --host 0.0.0.0 --port 9200 > fastapi_serv.log 2>&1 &
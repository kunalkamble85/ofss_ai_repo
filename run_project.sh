#!/bin/bash
export HF_HOME=/home/opc/hf_home
export HUGGINGFACEHUB_API_TOKEN=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
export JIRA_API_TOKEN=ATATT3xFfGF0aa8AHSZNm9AOkUipYel9tcRXFTBZlGZT624zjjCa-uBjEkX6P2z8C4mobQ83XMZlH98VVBY0IyqkH-skflVPr132jMxL5rFGhIWLTHY_Kf08OpZ21ikpUJ9g1sU8hYzob7Ois_2ApfpllleI9fx7co4OSZbl2L7vEPz3p5E0fCs=15ABCC9E
export JIRA_INSTANCE_URL=https://kunalkamble85.atlassian.net
export JIRA_USERNAME=kunalkamble85@gmail.com
export JIRA_CLOUD=False
export http_proxy=http://www-proxy-hqdc.us.oracle.com:80
export https_proxy=http://www-proxy-hqdc.us.oracle.com:80
export no_proxy=localhost,127.0.0.1,.us.oracle.com,.oraclecorp.com
export PYTHONPATH=./src/utils:$PYTHONPATH
export PATH=$PATH:$PYTHONPATH
export ORACLE_WALLET_PASSWORD=EMsingle@12345
nohup uvicorn src.rest_endpoint:app --host 0.0.0.0 --port 9200 > fastapi_serv.log 2>&1 & 
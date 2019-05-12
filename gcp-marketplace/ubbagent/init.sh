#!/bin/bash

set -ex

TIERS=("small_node_time" "small_high_memory_node_time" "medium_high_memory_node_time" "large_high_memory_node_time" "extra_large_high_memory_node_timei")


get_cpu_tier () {
  cpu=$1
  cpu_tier=1
    if [ $cpu -gt  4000 ]
    then
      cpu_tier=2
    elif [ $cpu -ge 8000 ]
    then
      cpu_tier=3 
    elif [ $cpu -ge 16000 ]
    then
      cpu_tier=4 
    elif [ $cpu -ge 32000 ]
    then
      cpu_tier=5
    else
      cpu_tier=1
    fi

  echo $cpu_tier
}

get_mem_tier () {
  mem=$1
  mem_tier=1
    if [ $mem -gt 15 ]
    then
      mem_tier=1
    elif [ $mem -ge 26 ]
    then
      mem_tier=2 
    elif [ $mem -ge 52 ]
    then
      mem_tier=3 
    elif [ $mem -ge 104 ]
    then
      mem_tier=4
    elif [ $mem -ge 208 ]
    then
      mem_tier=5
    else
      mem_tier=1
    fi

  echo $mem_tier
}

max_tier () {
 max=$(( $1 > $2 ? $1 : $2 ))
 echo $max
}

get_cpu_tier 4000
get_mem_tier 15
max_tier $cpu_tier $mem_tier

TIER=${TIERS[$max]}
echo **FOUND TIER=$TIER**
#exit 234

mkdir -p /opt/persistent/ubbagent

if [ -z "$AGENT_LOCAL_PORT" ]; then
  echo "AGENT_LOCAL_PORT environment variable must be set"
  exit 1
fi

ls -lh /runtime/agent-config-*


/usr/local/bin/ubbagent-start --config /runtime/agent-config-${TIER}.yaml 




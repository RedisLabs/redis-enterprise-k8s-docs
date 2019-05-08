#!/bin/sh

set -ex


mkdir -p /opt/persistent/ubbagent

if [ -z "$AGENT_LOCAL_PORT" ]; then
  echo "AGENT_LOCAL_PORT environment variable must be set"
  exit 1
fi

ls agent-config-*


/usr/local/bin/ubbagent-start --config /runtime/agent-config-small_node_time.yaml 

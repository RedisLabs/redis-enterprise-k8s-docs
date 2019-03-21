#!/bin/bash

set -e


mkdir /opt/persistent/ubbagent

if [ -z "$AGENT_LOCAL_PORT" ]; then
  echo "AGENT_LOCAL_PORT environment variable must be set"
  exit 1
fi

/usr/local/bin/ubbagent-start

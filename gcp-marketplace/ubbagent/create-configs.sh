set -x

# Create configs for all node types, later we will use on of them to run ubbagent --config=<config>

for n in `cat node-types`; 
  do echo $n; 
  NODE_TYPETIME=$n ;
  echo ${NODE_TYPETIME#redislabs.mp-redislabs-public.appspot.com/}  ;  
  envsubst  ${NODE_TYPETIME} < "agent-config.yaml.template" > "agent-config-${NODE_TYPETIME#redislabs.mp-redislabs-public.appspot.com/}.yaml"  ; 
done


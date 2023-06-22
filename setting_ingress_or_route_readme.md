<!-- omit in toc -->
# Establish external routing with an Ingress controller or Openshift Routes on K8s

This document describes how to set Ingress controller or Openshift Routes for the REC, REDB and REAADB on Kubernetes.

## Overview

For requests to be routed to the REC, REDB and REAADB  from outside the K8s cluster, you need an Ingress controller or Openshift Routes.
Redis Enterprise Software on Kubernetes supports three Ingress controllers: HAProxy, Nginx and Istio; as well as Openshift Routes.

### Redis Enterprise Cluster (REC) API

For any Redis Enterprise Cluster the Redis Enterprise operator creates a service that allows requests to be routed to that cluster API. Redis Enterprise supports three types of services for accessing the cluster: ClusterIP, loadBalancer and nodePort.
By default, the operator creates a ClusterIP type service, which exposes a cluster-internal IP and can only be accessed from within the K8s cluster.

### Redis Enterprise Database (REDB)

Every time a Redis Enterprise database is created with the Redis Enterprise operator, a service is created that allows requests to be routed to that database. Redis Enterprise supports three types of services for accessing databases: ClusterIP, headless, or LoadBalancer.
By default, the operator creates a ClusterIP type service, which exposes a cluster-internal IP and can only be accessed from within the K8s cluster.

### Redis Enterprise Active Active Database (REAADB)

Every time a Redis Enterprise Active Active Database is created with the Redis Enterprise operator, a service is created that allows requests to be routed to that active-active database. Redis Enterprise supports three types of services for accessing databases: ClusterIP, headless, or LoadBalancer.
By default, the operator creates a ClusterIP type service, which exposes a cluster-internal IP and can only be accessed from within the K8s cluster.

## Ingress installation

Install one of the supported ingresses, if not installed already on your K8s cluster:
  * [Nginx ingress controller installation guide](https://kubernetes.github.io/ingress-nginx/deploy/)
  * [HAProxy ingress getting started](https://haproxy-ingress.github.io/docs/getting-started/)
  * Istio - follow the "Install and configure Istio for Redis Enterprise" [here](https://docs.redis.com/latest/kubernetes/re-databases/ingress_routing_with_istio/)
  * [Openshift Routes](https://docs.redis.com/latest/kubernetes/re-databases/routes/)

Warning - You’ll need to make sure `ssl-passthrough` is enabled. It’s enabled by default for HAProxy, but disabled by default for NGINX. See the [Nginx User Guide](https://kubernetes.github.io/ingress-nginx/user-guide/tls/#ssl-passthrough) for details.

## Configure DNS

To reach the cluster and databases we need DNS records that will resolve to the Ingress/ Routes load balancer service that exposes external endpoint.

1. To find the load balancer service with the exposed endpoint of HAProxy or Nginx controller, please run the following, replace the <ingress service name> with "haproxy-ingress" or "ingress-ngnix-controller" for HAProxy or Nginx respectively and the  <ingress ctrl namespace> with the namespace the ingress resides in:
```
  kubectl get svc <ingress service name> -n <ingress ctrl namespace>
```
Below is example output for an HAProxy ingress controller running on a K8s cluster hosted by AWS:
```
  NAME              TYPE           CLUSTER-IP    EXTERNAL-IP                                                              PORT(S)                      AGE
  haproxy-ingress   LoadBalancer   10.43.62.53   a56e24df8c6173b79a63d5da54fd9cff-676486416.us-east-1.elb.amazonaws.com   80:30610/TCP,443:31597/TCP   21m
```

2. Create the following DNS entries that resolves to the exposed load balancer endpoint, use the `EXTERNAL-IP` found in the previous step.

a. REC API DNS:  
We recommend using the following convention for the REC API FQDN:
`api-<REC name>-<REC namespace>.<subdomain>`
- Replace `<REC name>` with the REC name
- Replace `<REC namespace>` with the namespace the REC resides in
- Replace `<subdomain>` with your subdomain
For example, REC API DNS of a REC named: "rec1" with the namespace "ns1" and the subdomain "redis.com":
api-rec1-ns1.redis.com

b. The databases and Active-Active databases FQDN suffix DNS:  
The FQDN for REDB custom resources (databases) or REAADB custom resources  (Active-Active databases) is comprised from two parts: The custom resource name and a FQDN suffix. We recommend configuring a wildcard DNS record with the FQDN suffix.
We recommend using the following convention for the DB FQDN suffix:
`*-db-<REC name>-<REC namespace>.<subdomain>`
- Replace `<REC name>` with the REC name
- Replace `<REC namespace>` with the namespace the REC resides in
- Replace `<subdomain>` with your subdomain:
For example, wildcard DB FQDN suffix DNS of a REC named "rec1", with the namespace "ns1", and the subdomain "redis.com":
*-db-rec1-ns1.redis.com

## Configure Ingress or Routes on the REC

On the namespace where the REC resides, do the following:

Please configure the Ingress controller or Openshift Routes configurations via the 'ingressOrRouteSpec' field on the REC spec.
For example, configuring a Nginx ingress via the above configurations on a REC named "rec1" with the namespace "ns1":
```
  kubectl patch rec  rec1 --type merge --patch "{\"spec\": \
    {\"ingressOrRouteSpec\": \
      {\"apiFqdnUrl\": \"api-rec1-ns1.redis.com\", \
      \"dbFqdnSuffix\": \"-db-rec1-ns1.redis.com\", \
      \"ingressAnnotations\": {\"kubernetes.io/ingress.class\": \"nginx\", \"nginx.ingress.kubernetes.io/ssl-passthrough\": \"true\"}, \
      \"method\": \"ingress\"}}}"
```

Some clearification about the above example:
  - The 'apiFqdnUrl' is the FQDN for the REC API.
  - The 'dbFqdnSuffix' is the suffix that will be added for each REDB and REAADB  custom resources names, meaning the active-active database convention is as follows: <REDB name | REAADB name><dbFqdnSuffix>.

Notes:
  * For more info please view the REC custom resource definition or the API doc.

For more information please view the following links:
  - [Redis doc - set up ingress controller](https://docs.redis.com/latest/kubernetes/re-databases/set-up-ingress-controller/)
  - [Redis doc - create aa database](https://docs.redis.com/latest/kubernetes/re-clusters/create-aa-database/)
  - [Redis doc - Openshift Routes](https://docs.redis.com/latest/kubernetes/re-databases/routes/)

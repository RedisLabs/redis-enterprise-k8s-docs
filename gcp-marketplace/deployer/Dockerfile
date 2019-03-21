FROM gcr.io/cloud-marketplace-tools/k8s/deployer_envsubst:latest

ADD manifest/* /data/manifest/
ADD schema.yaml /data/

# Provide registry prefix and tag for default values for images.
ARG REGISTRY=gcr.io/proven-reality-226706
ARG TAG=latest
RUN cat /data/schema.yaml \
    | env -i "REGISTRY=$REGISTRY" "TAG=$TAG" envsubst \
    > /data/schema.yaml.new \
    && mv /data/schema.yaml.new /data/schema.yaml

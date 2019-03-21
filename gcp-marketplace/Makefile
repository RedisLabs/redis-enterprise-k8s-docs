kubectl apply -f "https://raw.githubusercontent.com/GoogleCloudPlatform/marketplace-k8s-app-tools/master/crd/app-crd.yaml"
export APP_INSTANCE_NAME=redis-1
export NAMESPACE=default
export IMAGE_REDIS=redislabs/operator:498_f987b08
export SERVICE_ACCOUNT=redis-enterprise-operator
export REPLICAS=3
export REDIS_ADMIN=admin@acme.com
export IMAGE_UBBAGENT=launcher.gcr.io/google/ubbagent


awk 'FNR==1 {print "---"}{print}' manifest/* \
  | envsubst '$APP_INSTANCE_NAME $NAMESPACE $IMAGE_REDIS $REPLICAS $REDIS_ADMIN $SERVICE_ACCOUNT' \
  > "${APP_INSTANCE_NAME}_manifest.yaml"

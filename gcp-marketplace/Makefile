include helper/app.Makefile
include helper/crd.Makefile
include helper/gcloud.Makefile
include helper/var.Makefile


TAG ?= 1.8
REGISTRY ?= gcr.io/proven-reality-226706
METRICS_EXPORTER_TAG ?= v0.7.1

$(info ---- TAG = $(TAG))

APP_DEPLOYER_IMAGE ?= $(REGISTRY)/redislabs/deployer:$(TAG)
NAME ?= redislabs-1

ifdef METRICS_EXPORTER_ENABLED
  METRICS_EXPORTER_ENABLED_FIELD = , "metrics.enabled": "$(METRICS_EXPORTER_ENABLED)"
endif

APP_PARAMETERS ?= { \
  "name": "$(NAME)", \
  "namespace": "$(NAMESPACE)" \
  $(METRICS_EXPORTER_ENABLED_FIELD) \
}

TESTER_IMAGE ?= $(REGISTRY)/redislabs/tester:$(TAG)


app/build:: .build/redislabs/deployer \
            .build/redislabs/redislabs \


.build/redislabs: | .build
	mkdir -p "$@"


.build/redislabs/deployer: deployer/* \
                           schema.yaml \
                           .build/var/APP_DEPLOYER_IMAGE \
                           .build/var/MARKETPLACE_TOOLS_TAG \
                           .build/var/REGISTRY \
                           .build/var/TAG \
                           | .build/redislabs
	docker build \
	    --build-arg REGISTRY="$(REGISTRY)/redislabs" \
	    --build-arg TAG="$(TAG)" \
	    --build-arg MARKETPLACE_TOOLS_TAG="$(MARKETPLACE_TOOLS_TAG)" \
	    --tag "$(APP_DEPLOYER_IMAGE)" \
	    -f deployer/Dockerfile \
	    .
	docker push "$(APP_DEPLOYER_IMAGE)"
	@touch "$@"


.build/redislabs/redislabs: .build/var/REGISTRY \
                            .build/var/TAG \
                            | .build/redislabs
	docker pull redislabs/operator:498_f987b08
	docker tag  redislabs/operator:498_f987b08 \
	    "$(REGISTRY)/redislabs:$(TAG)"
	docker push "$(REGISTRY)/redislabs:$(TAG)"
	@touch "$@"



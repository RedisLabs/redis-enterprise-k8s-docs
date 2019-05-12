FROM gcr.io/ubbagent/metering/ubbagent
RUN mkdir /runtime
RUN apk update && apk add bash #needed for init script
WORKDIR /runtime
COPY . . 
RUN  ./create-configs.sh

CMD ["/runtime/init.sh"]

FROM gcr.io/ubbagent/metering/ubbagent
RUN mkdir /runtime
WORKDIR /runtime
COPY . . 
RUN  ./create-configs.sh

CMD ["/runtime/init.sh"]

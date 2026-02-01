{{- define "redis-enterprise-operator.operator.image" }}
{{- $defaultRepository := ternary "registry.connect.redhat.com/redislabs/redis-enterprise-operator" "redislabs/operator-internal" .Values.isOpenshift }}
{{- $repository := default $defaultRepository .Values.operator.image.repository }}
{{ $repository }}:{{ .Values.operator.image.tag }}
{{- end }}

{{- define "redis-enterprise-operator.operator.image" }}
{{- if and .Values.global .Values.global.azure .Values.global.azure.images .Values.global.azure.images.operator }}
{{- with .Values.global.azure.images.operator }}
{{ .registry }}/{{ .image }}@{{ .digest }}
{{- end }}
{{- else }}
{{- $defaultRepository := ternary "registry.connect.redhat.com/redislabs/redis-enterprise-operator" "redislabs/operator" .Values.isOpenshift }}
{{- $repository := default $defaultRepository .Values.operator.image.repository }}
{{ $repository }}:{{ .Values.operator.image.tag }}
{{- end }}
{{- end }}

{{- define "redis-enterprise-operator.operator.image" }}
{{- if (.Values.global).azure }}
{{- with .Values.global.azure.images.operator }}
{{ .registry }}/{{ .image }}@{{ .digest }}
{{- end }}
{{- else }}
{{- $defaultRepository := ternary "registry.connect.redhat.com/redislabs/redis-enterprise-operator" "redislabs/operator" .Values.openshift.mode }}
{{- $repository := default $defaultRepository .Values.operator.image.repository }}
{{ $repository }}:{{ .Values.operator.image.tag }}
{{- end }}
{{- end }}

{{- define "redis-enterprise-operator.annotations" }}
{{- if ne .Values.versionAnnotations false -}}
redis.io/helm-chart-ver: {{ .Chart.Version }}
redis.io/operator-ver: {{ .Values.operator.image.tag }}
{{- end }}
{{- end }}

{{/*
Evaluates to a TLS configuration for the admission webhook, either by retrieving an
existing configuration from the "admission-tls" Secret, or by generating a new one.
Returns a TLS configuration YAML object with a "cert" and "privateKey" keys.
*/}}
{{- define "redis-enterprise-operator.admissionTLSConfig" }}
  {{- $tlsConfig := dict }}
  {{- $secret := (lookup "v1" "Secret" .Release.Namespace "admission-tls") }}
  {{- if $secret }}
    {{ $tlsConfig = $secret.data }}
  {{- else}}
    {{ $cna := printf "admission.%s" .Release.Namespace }}
    {{ $cnb := printf "admission.%s.svc" .Release.Namespace }}
    {{ $cnc := printf "admission.%s.svc.cluster.local" .Release.Namespace }}
    {{ $cert := genSelfSignedCert $cnb nil (list $cna $cnb $cnc) (int (mul 365 5)) }}
    {{ $_ := set $tlsConfig "cert" ($cert.Cert | b64enc) }}
    {{ $_ := set $tlsConfig "privateKey" ($cert.Key | b64enc) }}
  {{- end }}
  {{ $tlsConfig | toYaml | nindent 2 }}
{{- end }}

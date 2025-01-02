{{- define "redis-enterprise-operator.operator.image" }}
{{- if (.Values.global).azure }}
{{- with .Values.global.azure.images.operator }}
{{ .registry }}/{{ .image }}@{{ .digest }}
{{- end }}
{{- else }}
{{- $defaultRepository := ternary "registry.connect.redhat.com/redislabs/redis-enterprise-operator" "redislabs/operator" .Values.isOpenshift }}
{{- $repository := default $defaultRepository .Values.operator.image.repository }}
{{ $repository }}:{{ .Values.operator.image.tag }}
{{- end }}
{{- end }}


{{- define "redis-enterprise-operator.annotations" }}
{{- if ne .Values.versionAnnotations false }}
redis.io/helm-chart-ver: {{ .Chart.Version }}
redis.io/operator-ver: {{ .Values.operator.image.tag }}
{{- end }}
{{- end }}

{{- define "redis-enterprise-operator.caComment" }}
"" # Fill in with BASE64 encoded signed cert
{{- end }}

{{/*
"redis-enterprise-operator.getCa" generates or retrieves CA certificates. It
checks for a Secret "admission-tls" in each namespace, generates new
certificates if needed, and returns a dictionary of all certificates.
*/}}
{{- define "redis-enterprise-operator.getCa" }}
  {{ $CERTS := dict }}
  {{- range $ns := . }}
    {{- $secret := (lookup "v1" "Secret" $ns "admission-tls")}}
    {{- if $secret }}
      {{ $_ := set $CERTS $ns $secret.data }}
    {{- else}}
      {{ $cna := printf "admission.%s" $ns }}
      {{ $cnb := printf "admission.%s.svc" $ns }}
      {{ $cnc := printf "admission.%s.svc.cluster.local" $ns }}
      {{ $ca := genCA $cnb 365 }}
      {{ $_cert := genSignedCert $cnb nil (list $cna $cnb $cnc) 365 $ca }}
      {{ $cert := dict }}
      {{ $_ := set $cert "cert" ($_cert.Cert | b64enc) }}
      {{ $_ := set $cert "privateKey" ($_cert.Key | b64enc) }}
      {{ $_ := set $CERTS $ns $cert }}
    {{- end }}
  {{- end }}
  {{ $CERTS | toYaml | nindent 2 }}
{{- end }}

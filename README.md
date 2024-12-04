kubectl kustomize "https://github.com/nginxinc/nginx-gateway-fabric/config/crd/gateway-api/standard?ref=v1.5.0" | kubectl apply -f -
customresourcedefinition.apiextensions.k8s.io/gatewayclasses.gateway.networking.k8s.io created
customresourcedefinition.apiextensions.k8s.io/gateways.gateway.networking.k8s.io created
customresourcedefinition.apiextensions.k8s.io/grpcroutes.gateway.networking.k8s.io created
customresourcedefinition.apiextensions.k8s.io/httproutes.gateway.networking.k8s.io created
customresourcedefinition.apiextensions.k8s.io/referencegrants.gateway.networking.k8s.io created

helm pull oci://ghcr.io/nginxinc/charts/nginx-gateway-fabric --untar
cd nginx-gateway-fabric/
helm install ngf . --create-namespace -n nginx-gateway

# k get pods -n nginx-gateway
NAME                                        READY   STATUS    RESTARTS   AGE
ngf-nginx-gateway-fabric-777ccd44f5-ktzgz   2/2     Running   0          7m59s
root@raspberrypi4-5:~gateway-api-nginx#

# k get svc -n nginx-gateway
NAME                       TYPE           CLUSTER-IP    EXTERNAL-IP     PORT(S)                      AGE
ngf-nginx-gateway-fabric   LoadBalancer   10.43.79.11   192.168.1.131   80:32158/TCP,443:30888/TCP   8m2s

root@raspberrypi4-5:~gateway# cat gateway.yaml
apiVersion: gateway.networking.k8s.io/v1
kind: Gateway
metadata:
  name: cafe-gateway
spec:
  gatewayClassName: nginx
  listeners:
  - name: http
    protocol: HTTP
    port: 80
root@raspberrypi4-5:~gateway# k apply -f gateway.yaml
gateway.gateway.networking.k8s.io/cafe-gateway created
root@raspberrypi4-5:~gateway#
root@raspberrypi4-5:~gateway#
root@raspberrypi4-5:~gateway#
root@raspberrypi4-5:~gateway# k get Gateway -A
NAMESPACE   NAME           CLASS   ADDRESS         PROGRAMMED   AGE
default     cafe-gateway   nginx   192.168.1.131   True         8s




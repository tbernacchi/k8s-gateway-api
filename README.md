# k8s-gateway-api

> This repo contains instructions to install the Gateway API and convert Ingresses to Gateway API resources.

### Install Gateway API CRDs 

```bash
kubectl kustomize "https://github.com/nginxinc/nginx-gateway-fabric/config/crd/gateway-api/standard?ref=v1.5.0" | kubectl apply -f -
```

```bash
helm pull oci://ghcr.io/nginxinc/charts/nginx-gateway-fabric --untar
cd nginx-gateway-fabric/
helm install ngf . --create-namespace -n nginx-gateway
```

Checking pods and services:

```bash
# kubectl get pods -n nginx-gateway
NAME                                        READY   STATUS    RESTARTS   AGE
ngf-nginx-gateway-fabric-777ccd44f5-ktzgz   2/2     Running   0          8m2s

# k get svc -n nginx-gateway
NAME                       TYPE           CLUSTER-IP    EXTERNAL-IP     PORT(S)                      AGE
ngf-nginx-gateway-fabric   LoadBalancer   10.43.79.11   192.168.1.131   80:32158/TCP,443:30888/TCP   8m2s
```

### Usage

```bash
git clone git@github.com:tbernacchi/k8s-gateway-api.git
kubectl apply -f gateway/coffee-gateway.yaml
```

You should see the Gateway resource created in the `default` namespace:

```bash
# k get gateway -n default
NAME           CLASS   ADDRESS         PROGRAMMED   AGE
cafe-gateway   nginx   192.168.1.131   True         12s
```

Deploy `coffee-app/` and the `HTTPRoute` resources:

```bash
kubectl apply -f coffee-app/
kubectl apply -f routing/coffee-routing.yaml
```

You should see the `HTTPRoute` resource created in the `default` namespace:

```bash
# kubectl get httproute -n default
NAME           HOSTNAMES              AGE
coffee-route   ["cafe.example.com"]   10s
```

### Testing

```bash
# curl -is -H "Host: cafe.example.com" http://192.168.1.131:80/
HTTP/1.1 200 OK
Server: nginx
Date: Wed, 04 Dec 2024 00:34:35 GMT
Content-Type: text/html; charset=utf-8
Content-Length: 24
Connection: keep-alive
X-Powered-By: Express
ETag: W/"18-/S5aYysmu93xpyhqZzInpCZ0M2U"

Hello From COFFEE (V1)!
```

```bash
# curl -is -H "Host: cafe.example.com" -H "version: v2" http://192.168.1.131:80/
HTTP/1.1 200 OK
Server: nginx
Date: Wed, 04 Dec 2024 00:37:30 GMT
Content-Type: text/html; charset=utf-8
Content-Length: 24
Connection: keep-alive
X-Powered-By: Express
ETag: W/"18-U4qjRk0fi49MfsSJ6en/kMpd8P0"

Hello From COFFEE (V2)!
```

### Convert Ingress resources to Gateway API resources

On the `kong-convert/ingress2gateway/` directory you will find the official Kong conversion tool and a script to convert the ingress resources to HTTPRoute resources.

```bash
# tree kong-convert -L 1
kong-convert
├── dest_dir
├── ingress2gateway
└── source_dir

4 directories, 0 files
```

I've installed mine on an arm64 machine, this was how I did it:

```bash
cd kong-convert/ingress2gateway/
wget -O ingress2gateway_Linux_arm64.tar.gz https://github.com/Kong/ingress2gateway/releases/download/v0.1.0/ingress2gateway_Linux_arm64.tar.gz && \
tar -xzf ingress2gateway_Linux_arm64.tar.gz && \
chmod +x ingress2gateway && rm -f ingress2gateway_Linux_arm64.tar.gz
```

* Be attention of your architecture when downloading the ingress2gateway binary. [[releases]](https://github.com/Kong/ingress2gateway/releases/)

In order to convert the ingress resources to Gateway API resources you will need to have the ingress resources in the `source_dir` directory and the destination directory will be populated with the converted `HTTPRoute` resources. [[See more]](https://docs.konghq.com/kubernetes-ingress-controller/latest/guides/migrate/ingress-to-gateway/)

To accomplish this there is this `ingress-yaml-generator.py` script:

```bash
cd kong-convert/
./source_dir/ingress-yaml-generator.py
```

This script will generate all the current ingress resources in the `source_dir/ingress-manifests` directory. 

Converting the ingresses to HTTPRoute resources:

```bash
cd ingress2gateway/
for file in ${SOURCE_DIR}/*; do ./ingress2gateway print --input-file ${file} -A --providers=kong --all-resources > ${DEST_DIR}/$(basename -- $file); done
```

### WIP

- [ ] I just want to create HTTPRoute on the output of the ingress2gateway conversion, not the Gateway resource.

### References

- https://blog.nginx.org/blog/5-reasons-to-try-the-kubernetes-gateway-api
- https://blog.nashtechglobal.com/hands-on-kubernetes-gateway-api-with-nginx-gateway-fabric/
- https://docs.nginx.com/nginx-gateway-fabric/installation/installing-ngf/helm/

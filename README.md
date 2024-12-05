# k8s-gateway-api

> Install the Gateway API and convert Ingresses to HTTPRoute resources.

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
kubectl apply -f gateway/001-coffee-gateway.yaml
```

You should see the Gateway resource created in the `default` namespace:

```bash
# k get gateway -n default
NAME           CLASS   ADDRESS         PROGRAMMED   AGE
cafe-gateway   nginx   192.168.1.131   True         12s
```

Deploy `coffee-app/` and the `HTTPRoute` resources:

```bash
kubectl apply -f coffee-app/000-coffee-app.yaml
kubectl apply -f routing/002-coffee-routing.yaml
```

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

### Convert Ingress resources to HTTPRoute/Gateway API resources

On the `python-convert/` directory it contains two python scripts:

```bash
k8s-gateway-api|main⚡ ⇒ tree python-convert -L 1
python-convert
├── httproute-manifests
├── ingress-manifests
├── ingress-yaml-generator.py
└── ingress2httproute.py
```

`ingress-yaml-generator.py` generates all the current ingresses resources to the `ingress-manifests` directory.

```bash
cd python-convert/
./ingress-yaml-generator.py
```

`ingress2httproute.py` converts all the manifests in `ingress-manifests` to `HTTPRoute` manifests in `httproute-manifests` directory.

```bash
cd python-convert/
./ingress2httproute.py <your-gateway-namespace>
```

* Another way to accomplish this is using the [ingress2gateway](https://docs.konghq.com/kubernetes-ingress-controller/latest/guides/migrate/ingress-to-gateway/) tool.

> In my case I'm converting all my ingresses to `HTTPRoute` resources and using only one Gateway resource for all the ingresses, different from [ingress2gateway](https://github.com/Kong/ingress2gateway/releases/) which creates a Gateway resource for each ingress along with the `HTTPRoute` resources.

### References

- https://blog.nginx.org/blog/5-reasons-to-try-the-kubernetes-gateway-api
- https://blog.nashtechglobal.com/hands-on-kubernetes-gateway-api-with-nginx-gateway-fabric/
- https://docs.nginx.com/nginx-gateway-fabric/installation/installing-ngf/helm/
- https://docs.konghq.com/kubernetes-ingress-controller/latest/guides/migrate/ingress-to-gateway/

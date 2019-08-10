# KubeServiceManager

KubeServiceManager is a Multiple-Kubernetes-Cluster manager, work together with [KubeService](https://github.com/Coderhypo/KubeService).

# What is KubeServiceManager?

When deploying app in Multiple Kubernetes Cluster, what you need to do is just to select target cluster in you app, and then apply it in whichever cluster. KubeServiceManager do the rest for you.

KubeServiceManager will deploy app and microservice in all clusters, but only the deployment in the corresponding cluster.

# How does KubeServiceManager work?

When an app is deployed in one cluster, the cluster sends a webhook to KubeServiceManager. Then KubeServiceManager will call api to create or update app in other clusters. KubeService itself decides which deployment in microservice is belonged to itself and deploy it.

![]()

# App demo

```yaml
apiVersion: app.o0w0o.cn/v1
kind: App
metadata:
  name: voting-sample
spec:
  microServices:
    - name: voting-web
      spec:
        clusterName: desktop
        loadBalance:
          service:
            name: voting-web
            spec:
              ports:
                - protocol: TCP
                  port: 80
                  targetPort: 80
          ingress:
            name: voting-web
            spec:
              rules:
                - host: voting.o0w0o.cn
                  http:
                    paths:
                      - path: /
                        backend:
                          serviceName: voting-web
                          servicePort: 80
        versions:
          - name: v1
            template:
              replicas: 2
              selector:
                matchLabels:
                  app: voting-web
              template:
                metadata:
                  labels:
                    app: voting-web
                spec:
                  containers:
                    - image: daocloud.io/w0v0w/voting-demo-voting:v1
                      name: voting-web
          - name: v2
            canary:
              weight: 30
            template:
              replicas: 1
              selector:
                matchLabels:
                  app: voting-web-for-kid
              template:
                metadata:
                  labels:
                    app: voting-web-for-kid
                spec:
                  containers:
                    - image: daocloud.io/w0v0w/voting-demo-voting:v2
                      name: voting-web-for-kid
        currentVersionName: v1
    - name: voting-result
      spec:
        clusterName: minikube
        loadBalance:
          service:
            name: voting-result
            spec:
              ports:
                - protocol: TCP
                  port: 80
                  targetPort: 80
          ingress:
            name: voting-result
            spec:
              rules:
                - host: result.voting.o0w0o.cn
                  http:
                    paths:
                      - path: /
                        backend:
                          serviceName: voting-result
                          servicePort: 80
        versions:
          - name: v1
            template:
              replicas: 1
              selector:
                matchLabels:
                  app: voting-result
              template:
                metadata:
                  labels:
                    app: voting-result
                spec:
                  containers:
                    - image: daocloud.io/w0v0w/voting-demo-result:v1
                      name: voting-result
        currentVersionName: v1
```
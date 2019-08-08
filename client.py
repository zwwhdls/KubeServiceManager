from kubernetes import client as kube_client


class KubeClient:
    def __init__(self, *, cluster_host, cluster_token):
        self.cluster_host = cluster_host
        self.cluster_token = cluster_token
        self.client = None

    def connect_cluster(self):
        configuration = kube_client.Configuration()
        configuration.host = self.cluster_host
        configuration.verify_ssl = False

        configuration.api_key = {
            "authorization": "Bearer " + self.cluster_token}
        self.client = kube_client.ApiClient(configuration)

    def create_app(self, *, api_group, version, kind, yml):
        api = kube_client.CustomObjectsApi(self.client)
        api.create_cluster_custom_object(
            group=api_group,
            version=version,
            plural=kind,
            body=yml,
        )

    def update_app(self, *, resource_name, api_group, version, kind, yml):
        api = kube_client.CustomObjectsApi(self.client)
        api.patch_cluster_custom_object(
            name=resource_name,
            group=api_group,
            version=version,
            plural=kind,
            body=yml,
        )

    def get_app(self, *, resource_name, api_group, version, kind, yml):
        api = kube_client.CustomObjectsApi(self.client)
        resource = api.get_cluster_custom_object(
            name=resource_name,
            group=api_group,
            version=version,
            plural=kind,
        )

        return resource


if __name__ == "__main__":
    client = KubeClient(
        cluster_host="https://localhost:6443",
        cluster_token="eyJhbGciOiJSUzI1NiIsImtpZCI6IiJ9.eyJpc3MiOiJrdWJlcm5ldGVzL3NlcnZpY2VhY2NvdW50Iiwia3ViZXJuZXRlcy5pby9zZXJ2aWNlYWNjb3VudC9uYW1lc3BhY2UiOiJkZWZhdWx0Iiwia3ViZXJuZXRlcy5pby9zZXJ2aWNlYWNjb3VudC9zZWNyZXQubmFtZSI6ImFkbWluLXVzZXItdG9rZW4teGI5emQiLCJrdWJlcm5ldGVzLmlvL3NlcnZpY2VhY2NvdW50L3NlcnZpY2UtYWNjb3VudC5uYW1lIjoiYWRtaW4tdXNlciIsImt1YmVybmV0ZXMuaW8vc2VydmljZWFjY291bnQvc2VydmljZS1hY2NvdW50LnVpZCI6ImQ3ODNmNGZkLWI4ZWUtMTFlOS04NzY1LTAyNTAwMDAwMDAwMSIsInN1YiI6InN5c3RlbTpzZXJ2aWNlYWNjb3VudDpkZWZhdWx0OmFkbWluLXVzZXIifQ.XZkvFVDoJ3quPc-0OyzD6E2D8IpY1ISxyfX_X2hdAbJSbWmCmJlQiyjP5w8DILqtUFE5tD66L9mtjgvdk09JkaELUPNjHd0lWzn_396b7zkOpoRci_fLrytwjpEjxCdTCYrUHOb2OqQP8Clp_M6bLK70Ysx1XbCLJ07p7JrvJJ6E5nnKojf4BNsLOYl57OUs-uO5SdF0pEEpmbDPR8148nRQGSp7hbGFG0Q_ejJyLJCyVyiufRon5TKBNU9A4nO4eE8GYyHJhNdtYkfGt-nfwWenzictiYFxAPfh7Cu6EPGWlz7yBxEFUShdSNC951SUOT6-4jAnLBs_7eWQ59G4oA",
    )
    client.connect_cluster()
    client.get_app(
        resource_name="voting-sample",
        api_group="app.o0w0o.cn",
        version="v1",
        kind="App",
        yml=""
    )

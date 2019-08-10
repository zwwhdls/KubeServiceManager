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

    def create_app(self, *, namespace, api_group, version, kind, yml):
        api = kube_client.CustomObjectsApi(self.client)
        api.create_namespaced_custom_object(
            namespace=namespace,
            group=api_group,
            version=version,
            plural="apps",
            body=yml,
        )

    def update_app(self, *, resource_name, namespace, api_group, version, kind,
                   yml):
        api = kube_client.CustomObjectsApi(self.client)
        api.patch_namespaced_custom_object(
            name=resource_name,
            namespace=namespace,
            group=api_group,
            version=version,
            plural="apps",
            body=yml,
        )

    def get_app(self, *, resource_name, namespace, api_group, version, kind):
        api = kube_client.CustomObjectsApi(self.client)
        resource = api.get_namespaced_custom_object(
            name=resource_name,
            namespace=namespace,
            group=api_group,
            version=version,
            plural="apps",
        )

        if resource:
            return resource, True
        return resource, False

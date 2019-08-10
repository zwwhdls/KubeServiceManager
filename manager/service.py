import re
import logging
import yaml as yaml_util
from kubernetes.client.rest import ApiException

from manager.model import Cluster, session
from manager.client import KubeClient

LOG = logging.getLogger(__name__)


#################################
#
# Cluster
#
#################################

def add_cluster(*, cluster_name, cluster_host, cluster_token):
    cluster = Cluster(
        cluster_name=cluster_name,
        cluster_host=cluster_host,
        cluster_token=cluster_token
    )
    session.add(cluster)
    session.commit()


def get_clusters_except_this(cluster_name):
    clusters = session.query(Cluster).filter(
        Cluster.cluster_name != cluster_name).all()
    return clusters


def get_clusters():
    clusters = session.query(Cluster).all()
    clusters = [c.render() for c in clusters]
    return clusters


def delete_cluster(cluster_name):
    session.query(Cluster).filter_by(cluster_name=cluster_name).delete()
    session.commit()


def deploy_app(yml, cluster: Cluster):
    client = KubeClient(
        cluster_host=cluster.cluster_host,
        cluster_token=cluster.cluster_token
    )
    client.connect_cluster()
    LOG.info("Cluster [{}] {} is connected.".format(cluster.cluster_name,
                                                    cluster.cluster_host))
    deploy_info = get_group_version_from_yaml(yml)

    # 判断是创建还是更新
    try:
        app, is_existed = client.get_app(
            resource_name=deploy_info.name,
            api_group=deploy_info.group,
            version=deploy_info.version,
            kind=deploy_info.kind,
            namespace=deploy_info.namespace
        )
    except ApiException as e:
        LOG.error(e)
        if e.status == 404:
            is_existed = False
            app = {}
        else:
            raise
    try:
        if not is_existed:
            LOG.info(
                "app {} is not existed. created it.".format(deploy_info.name))
            status = deploy_info.yml.get("status", {})
            status["fromManager"] = "Created"
            deploy_info.yml["status"] = status
            client.create_app(
                api_group=deploy_info.group,
                namespace=deploy_info.namespace,
                version=deploy_info.version,
                kind=deploy_info.kind,
                yml=deploy_info.yml
            )
        else:
            LOG.info("app {} is already existed.".format(deploy_info.name))
            if app["spec"] == deploy_info.yml["spec"]:
                LOG.info("No change. skip.")
                return
            LOG.info("Update it.")
            status = deploy_info.yml.get("status", {})
            status["fromManager"] = "Updated"
            deploy_info.yml["status"] = status
            client.update_app(
                resource_name=deploy_info.name,
                namespace=deploy_info.namespace,
                api_group=deploy_info.group,
                version=deploy_info.version,
                kind=deploy_info.kind,
                yml=deploy_info.yml
            )
    except ApiException as e:
        LOG.error(e)


#################################
#
# Yaml Parser
#
#################################

class DeployInfo:
    def __init__(self, *, name, namespace, group, version, kind, yml):
        self.name = name
        self.namespace = namespace
        self.group = group
        self.version = version
        self.kind = kind
        self.yml = yml


def get_group_version_from_yaml(yml):
    try:
        content = yaml_util.load(yml, Loader=yaml_util.SafeLoader)

        api_version = content.get("apiVersion")
        kind = content.get("kind")
        if not kind:
            content["kind"] = "App"
        metadata = content["metadata"]
        resource_name = metadata["name"]
        namespace = metadata.get("namespace", "default")
        new_metadata = {
            "name": metadata["name"],
            "namespace": namespace,
        }
        content["metadata"] = new_metadata

        if not api_version:
            selflink = metadata.get("selfLink")
            api_version = re.findall(r'apis/(.+)/namespaces', selflink)[0]
            content["apiVersion"] = api_version

        api_results = list(api_version.split("/"))
        if len(api_results) == 1:
            api_group = ""
            version = api_results[0]
        else:
            api_group, version = api_results[0], api_results[1]
    except Exception:
        # todo
        raise

    result = DeployInfo(
        name=resource_name,
        namespace=namespace,
        group=api_group,
        version=version,
        kind=kind,
        yml=content
    )
    return result

import logging
import yaml as yaml_util
from kubernetes.client.rest import ApiException

from model import Cluster, session
from client import KubeClient

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
        is_existed = client.get_app(
            resource_name=deploy_info.name,
            api_group=deploy_info.group,
            version=deploy_info.version,
            kind=deploy_info.kind,
            yml=deploy_info.yml
        )
        if not is_existed:
            LOG.info(
                "app {} is not existed. created it.".format(deploy_info.name))
            client.create_app(
                api_group=deploy_info.group,
                version=deploy_info.version,
                kind=deploy_info.kind,
                yml=deploy_info.yml
            )
        else:
            LOG.info("app {} is already existed. updated it.".format(
                deploy_info.name))
            client.update_app(
                resource_name=deploy_info.name,
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
    def __init__(self, *, name, group, version, kind, yml):
        self.name = name
        self.group = group
        self.version = version
        self.kind = kind
        self.yml = yml


def get_group_version_from_yaml(yml):
    try:
        content = yaml_util.load(yml, Loader=yaml_util.SafeLoader)

        api_version = content["apiVersion"]
        kind = content["kind"]
        metadata = content["metadata"]
        resource_name = metadata["name"]
    except Exception:
        # todo
        raise

    api_results = list(api_version.split("/"))
    if len(api_results) == 1:
        api_group = ""
        version = api_results[0]
    else:
        api_group, version = api_results[0], api_results[1]

    result = DeployInfo(
        name=resource_name,
        group=api_group,
        version=version,
        kind=kind,
        yml=yml
    )
    return result

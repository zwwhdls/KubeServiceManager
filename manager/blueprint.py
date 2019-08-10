import logging
from flask import request, jsonify, Blueprint

from manager.service import add_cluster, get_clusters, deploy_app, \
    get_clusters_except_this, delete_cluster

bp = Blueprint("multi-clusters", __name__)
LOG = logging.getLogger(__name__)


@bp.route("/apps", methods=["POST"])
def manager():
    data = request.json
    yml = data.get("yml")
    cluster_name = data.get("cluster_name")
    if not yml:
        # todo
        raise Exception

    clusters = get_clusters_except_this(cluster_name)
    LOG.info(
        "There are {} clusters need to be informed.".format(len(clusters)))
    for c in clusters:
        deploy_app(yml, c)
    return ""


@bp.route("/clusters/register", methods=["POST"])
def register_cluster():
    data = request.json
    cluster_name = data.get("cluster_name")
    cluster_host = data.get("cluster_host")
    cluster_token = data.get("cluster_token")

    add_cluster(
        cluster_name=cluster_name,
        cluster_host=cluster_host,
        cluster_token=cluster_token
    )
    return ""


@bp.route("/clusters", methods=["GET"])
def get_all_clusters():
    clusters = get_clusters()
    return jsonify(clusters)


@bp.route("/clusters/<cluster_name>", methods=["DELETE"])
def delete_cluster_by_name(cluster_name):
    delete_cluster(cluster_name)
    return ""

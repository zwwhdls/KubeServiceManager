import logging
from sqlalchemy.exc import ProgrammingError, OperationalError

from manager.app import app_object
from manager.model import Base, engine, session

LOG = logging.getLogger(__name__)


def initdb():
    """
    init database, create all tables
    """
    try:
        check_sql = "SELECT COUNT(*) FROM clusters"
        session.execute(check_sql)
        session.close()
        return
    except (ProgrammingError, OperationalError):
        pass
    LOG.info("init database...")
    try:
        # declare tables
        from manager.model import Cluster
        Base.metadata.create_all(engine)

    except Exception as e:
        LOG.error(e)
    LOG.info("finish.")


if __name__ == "__main__":
    initdb()
    app_object.run("0.0.0.0", port=5000)

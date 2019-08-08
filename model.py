import os
import uuid

from sqlalchemy import create_engine
from sqlalchemy.orm import scoped_session, sessionmaker
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Column, String

db_name = os.getenv("DB_NAME", "ksm.db")
engine = create_engine('sqlite:////var/lib/{}'.format(db_name), echo=True)
session = scoped_session(sessionmaker(
    autocommit=False, autoflush=False, bind=engine))
Base = declarative_base()


class Cluster(Base):
    __tablename__ = "clusters"
    id = Column(String(64), primary_key=True)
    cluster_name = Column(String(128), unique=True, nullable=False)
    cluster_host = Column(String(128), unique=True, nullable=False)
    cluster_token = Column(String(360), unique=True, nullable=False)

    def __init__(self, *, cluster_name, cluster_host, cluster_token):
        self.id = str(uuid.uuid4())
        self.cluster_name = cluster_name
        self.cluster_host = cluster_host
        self.cluster_token = cluster_token

    def render(self):
        return {
            "name": self.cluster_name,
            "host": self.cluster_host
        }

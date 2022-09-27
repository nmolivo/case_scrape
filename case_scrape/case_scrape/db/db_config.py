import os
from dataclasses import dataclass
from typing import Optional

from sqlalchemy.engine import create_engine
from sqlalchemy.engine.base import Engine

# This is where credentials are passed so that we can easily switch databases,
# ie from local to a cloud one


@dataclass
class DBConfig(Config):
    password: Optional[str] = None
    user: Optional[str] = None
    database: str = "cuyacourts"
    scheme: str = "postgresql"
    host: str = "localhost"
    schema: str = "public"

    def get_engine(self, **kwargs) -> Engine:
        """Get a SQLAlchemy Engine"""
        engine = create_engine(
            f"{self.schema}://{self.user}:{self.password}@{self.host}/{self.database}",
            connect_args={"connect_timeout": 90},
            **kwargs,
        )
        return engine

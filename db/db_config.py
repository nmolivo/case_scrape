import os
from dataclasses import dataclass
from typing import Optional

from sqlalchemy.engine import create_engine
from sqlalchemy.engine.base import Engine

# This is where credentials are passed so that we can easily switch databases,
# ie from local to a cloud one


@dataclass
class DBConfig:
    password: Optional[str] = os.getenv("DB_PASSWORD")
    user: Optional[str] = os.getenv("DB_USER")
    database: str = os.getenv("DB_DATABASE")
    host: str = os.getenv("DB_HOST")
    port: int = os.getenv("DB_PORT")
    scheme: str = os.getenv("DB_SCHEME")

    def get_engine(self, **kwargs) -> Engine:
        """Get a SQLAlchemy Engine"""
        engine = create_engine(
            f"{self.scheme}://{self.user}:{self.password}@{self.host}:{self.port}/{self.database}",
            connect_args={"connect_timeout": 90},
            **kwargs,
        )
        return engine

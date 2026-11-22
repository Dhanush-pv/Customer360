import os
from dataclasses import dataclass

from dotenv import load_dotenv

load_dotenv()

@dataclass(frozen=True)
class Settings:
    db_host: str = os.getenv("C360_DB_HOST", "localhost")
    db_port: int = int(os.getenv("C360_DB_PORT", "5432"))
    db_name: str = os.getenv("C360_DB_NAME", "customer360")
    db_user: str = os.getenv("C360_DB_USER", "c360_app")
    db_password: str = os.getenv("C360_DB_PASSWORD", "local_dev_only_change_me")

    def connection_kwargs(self):
        return dict(host=self.db_host, port=self.db_port, dbname=self.db_name,
                    user=self.db_user, password=self.db_password)

settings = Settings()

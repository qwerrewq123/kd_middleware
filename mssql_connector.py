
import pymssql
import logging
from typing import List, Dict, Any, Optional

logger = logging.getLogger(__name__)


class MSSQLConnector:
    def __init__(self, host: str, port: int, database: str, username: str, password: str):
        self.host = host
        self.port = port
        self.database = database
        self.username = username
        self.password = password
        self.connection = None
        self.connect()

    def connect(self):
        self.connection = pymssql.connect(
            server=self.host,
            port=str(self.port),
            user=self.username,
            database=self.database,
            password=self.password,
            autocommit=False,
        )
        try:
            logger.info(f"MSSQL Connect Success: {self.host}:{self.port}/{self.database}")
            return True
        except Exception as e:
            logger.error(f"MSSQL Connect Fail: {e}")
            return False

    def disconnect(self):
        """Disconnect MSSQL"""
        if self.connection:
            self.connection.close()
            self.connection = None
            logger.info("Disconnect MSSQL")

    def execute_query(self, query: str, params: Optional[tuple] = None) -> List[Dict[str, Any]]:
        """select query"""
        if not self.connection:
            raise ConnectionError("Connection Fail")

        try:
            with self.connection.cursor(as_dict=True) as cursor:
                cursor.execute(query, params or ())
                result = cursor.fetchall()
                return result
        except Exception as e:
            logger.error(f"execute query fail: {e}")
            raise e

    def test_connection(self) -> bool:
        """connection test"""
        try:
            result = self.execute_query("SELECT 1 as test")
            return len(result) > 0
        except:
            return False
    def start_transaction(self):
        pass
    def commit(self):
        self.connection.commit()
    def rollback(self):
        self.connection.rollback()


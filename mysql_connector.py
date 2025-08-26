import pymysql
import logging
from typing import List, Dict, Any, Optional

logger = logging.getLogger(__name__)


class MySQLConnector:
    def __init__(self, host: str, port: int, database: str, username: str, password: str):
        """MySQL/MariaDB Connection Initialization"""
        self.host = host
        self.port = port
        self.database = database
        self.username = username
        self.password = password
        self.connection = None
        
    def connect(self):
        """Connect to MySQL"""
        try:
            self.connection = pymysql.connect(
                host=self.host,
                port=self.port,
                database=self.database,
                user=self.username,
                password=self.password,
                charset='utf8mb4',
                cursorclass=pymysql.cursors.DictCursor
            )
            logger.info(f"MySQL Connect Success: {self.host}:{self.port}/{self.database}")
            return True
        except Exception as e:
            logger.error(f"MySQL Connect Fail: {e}")
            return False
            
    def disconnect(self):
        """Disconnect MySQL"""
        if self.connection:
            self.connection.close()
            self.connection = None
            logger.info("Disconnect MySQL")
            
    def execute_query(self, query: str, params: Optional[tuple] = None) -> List[Dict[str, Any]]:
        """select query"""
        if not self.connection:
            if not self.connect():
                return []
                
        try:
            with self.connection.cursor() as cursor:
                cursor.execute(query, params or ())
                result = cursor.fetchall()
                return result
        except Exception as e:
            logger.error(f"execute query fail: {e}")
            return []
            
    def execute_update(self, query: str, params: Optional[tuple] = None) -> int:
        """INSERT/UPDATE/DELETE query execution"""
        if not self.connection:
            if not self.connect():
                return 0
                
        try:
            with self.connection.cursor() as cursor:
                cursor.execute(query, params or ())
                self.connection.commit()
                return cursor.rowcount
        except Exception as e:
            logger.error(f"insert/update/delete query fail: {e}")
            self.connection.rollback()
            return 0

            
    def test_connection(self) -> bool:
        """connection test"""
        try:
            result = self.execute_query("SELECT 1 as test")
            return len(result) > 0
        except:
            return False
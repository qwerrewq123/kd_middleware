import schedule
import time
import logging
import threading
from typing import Optional

from fcm_dto import FcmDto
from push_fcm import PushFcm
from push_sql import PushSql
import toml

from mysql_connector import MySQLConnector

logger = logging.getLogger(__name__)


class Scheduler:
    def __init__(self, interval: int = 3):

        with open("config.toml", 'r', encoding='utf-8') as f:
            config = toml.load(f)
            logger.info("Load config.toml file")
        mysql_config = config['database']['mariadb']
        self.interval = interval
        self.is_running = False
        self.thread: Optional[threading.Thread] = None
        self.mysql_connector: MySQLConnector = MySQLConnector(
        host=mysql_config['host'],
        port=mysql_config['port'],
        database=mysql_config['database'],
        username=mysql_config['username'],
        password=mysql_config['password']
        )
        if self.mysql_connector.test_connection():
            print('MYSQL Connection Test Success')
        else:
            print('MYSQL Connection Test Failed')
        logger.info("MYSQL Connector Successful")
        self.push_sql: PushSql = PushSql()
        self.push_fcm: PushFcm = PushFcm()



        
    def job(self):
        """실행할 작업"""
        result = self.mysql_connector.execute_query(query=self.push_sql.select_query)[0]
        count = result['count(*)']
        if count :
            try:
                self.mysql_connector.execute_update(query=self.push_sql.fcm_query)
                rows = self.mysql_connector.execute_query(query=self.push_sql.fcm_select_query)
                fcm_list = [FcmDto(row['TOKEN'],row['TITLE'],row['CONTENT']) for row in rows]
                self.push_fcm.push(fcm_list)
            except Exception as e:
                logger.error(f"FCM 쿼리 실행 실패: {e}")
                if self.mysql_connector.connection:
                    self.mysql_connector.connection.rollback()
                    logger.info("트랜잭션 롤백 완료")

    def run_continuously(self):
        """백그라운드에서 스케줄 실행"""
        while self.is_running:
            schedule.run_pending()
            time.sleep(1)
            
    def start(self):
        """스케줄러 시작"""
        if self.is_running:
            logger.warning("스케줄러가 이미 실행 중입니다")
            return
            
        schedule.every(self.interval).seconds.do(self.job)

        self.is_running = True
        self.thread = threading.Thread(target=self.run_continuously)
        self.thread.daemon = True
        self.thread.start()
        
        logger.info(f"스케줄러 시작 (간격: {self.interval}초)")
        
    def stop(self):
        """스케줄러 중지"""
        self.is_running = False
        if self.thread:
            self.thread.join()
        schedule.clear()
        logger.info("스케줄러 중지")

    def run(self):
        logging.basicConfig(level=logging.INFO)

        scheduler = Scheduler(interval=3)
        scheduler.start()

        try:
            # 계속 실행
            while True:
                time.sleep(1)
        except KeyboardInterrupt:
            scheduler.stop()
            print("\n스케줄러 종료")


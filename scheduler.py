import schedule
import time
import logging
import threading
from typing import Optional

from fcm_dto import FcmDto
from push_fcm import PushFcm
from push_sql import PushSql
import toml
from utils import get_resource_path,get_sync_rows,process_to_tuple

from mysql_connector import MySQLConnector
logger = logging.getLogger(__name__)


class Scheduler:
    def __init__(self, interval: int = 5):
        if not logging.getLogger().handlers:
            logging.basicConfig(level=logging.INFO)

        config_path = get_resource_path("config.toml")
        with open(config_path, 'r', encoding='utf-8') as f:
            config = toml.load(f)
            logger.info(f"Load config.toml file from {config_path}")
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
        self.push_sql: PushSql = PushSql()
        self.push_fcm: PushFcm = PushFcm()




    def job(self):

        self.mysql_connector.start()
        if self.mysql_connector.test_connection():
            logger.info('MYSQL Connection Test Success')
        else:
            logger.info('MYSQL Connection Test Fail')
        logger.info("MYSQL Connector Successful")
        logger.info('check fcm')
        result = self.mysql_connector.execute_query(query=self.push_sql.select_query)
        idx_list = [res['idx'] for res in result]
        count = len(idx_list)
        logger.info(f'count is {count}')
        logger.info(f'interval is {self.interval}')

        if count > 0:
            try:
                a = self.mysql_connector.execute_update(query=self.push_sql.fcm_query)
                logger.info(f'a = {a}')
                rows = self.mysql_connector.execute_query(query=self.push_sql.fcm_select_query)
                fcm_list = [FcmDto(row['TOKEN'], row['TITLE'], row['CONTENT']) for row in rows]
                docno_list = [row['DOCNO'] for row in rows]
                ret_list = self.push_fcm.push(fcm_list)
                for idx in ret_list:
                    self.mysql_connector.execute_update(self.push_sql.alarm_fcm_update_query, params=(docno_list[idx],))
                for idx in idx_list:
                    self.mysql_connector.execute_update(self.push_sql.alarm_event_update_query, params=(idx,))
                # for docno, idx in zip(docno_list, idx_list):
                #     self.mysql_connector.execute_update(self.push_sql.alarm_fcm_update_query, params=(docno,))
                #     self.mysql_connector.execute_update(self.push_sql.alarm_event_update_query, params=(idx,))
            except Exception as e:
                logger.error(f"Fcm Query Execution Fail: {e}")
        self.mysql_connector.disconnect()







    def run_continuously(self):
        """Schedule in Background"""
        while self.is_running:
            schedule.run_pending()
            time.sleep(1)

    def start(self):
        """Start Scheduler"""
        if self.is_running:
            logger.warning("Scheduler already running")
            return

        schedule.every(self.interval).seconds.do(self.job)

        self.is_running = True
        self.thread = threading.Thread(target=self.run_continuously)
        self.thread.daemon = True
        self.thread.start()

        logger.info(f"Scheduler (interval: {self.interval}seconds)")

    def stop(self):
        """Stop Scheduler"""
        self.is_running = False
        if self.thread:
            self.thread.join()
        schedule.clear()
        logger.info("Stop Scheduler")

    def run(self):
        logging.basicConfig(level=logging.INFO)

        self.start()

        try:
            # 계속 실행
            while True:
                time.sleep(1)
        except KeyboardInterrupt:
            self.stop()
            print("\nend Scheduler")


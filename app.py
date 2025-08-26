import logging

from fcm_dto import FcmDto
from scheduler import Scheduler
from push_fcm import PushFcm

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


if __name__ == "__main__":
    scheduler = Scheduler()
    scheduler.run()

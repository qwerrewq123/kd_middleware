import logging

from scheduler import Scheduler

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


if __name__ == "__main__":
    scheduler = Scheduler()
    scheduler.run()

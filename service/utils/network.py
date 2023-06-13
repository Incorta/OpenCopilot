import time
from utils import logger


def retry(action, retries=3, delay=2):
    last_e = None

    for i in range(retries):
        try:
            return action()

        except Exception as e:
            last_e = e
            logger.error(f"Attempt {i + 1} failed with error: {e}")
            if i < retries - 1:
                time.sleep(delay)

    raise Exception(f"Action failed after {retries} attempts, with error: {last_e}")

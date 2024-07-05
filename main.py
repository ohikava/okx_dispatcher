from loguru import logger
from utils import OKX


if __name__ == '__main__':
    try:
        session = OKX()
        session.add_to_whitelists()
        logger.success("done!")
    except Exception as e:
        logger.error(f"error: {e}\n\n")

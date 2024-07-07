from loguru import logger
from utils import OKX


if __name__ == '__main__':
    try:
        session = OKX()
        user_input = input('Choice the desired option: [1] add wallets to whitelist [2] remove wallets from whitelist')
        session.add_to_whitelists()
        logger.success("done!")
    except Exception as e:
        logger.error(f"error: {e}\n\n")

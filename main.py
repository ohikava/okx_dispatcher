from loguru import logger
from whitelister import Whitelister
import json 
from dispatcher import Dispatcher
from dotenv import dotenv_values

SECRETS = dotenv_values(".env")

if __name__ == '__main__':
    
    try:
        with open("wallets.txt", "r") as f:
            WALLETS = [i.strip() for i in f.readlines()]

        with open("config.json", "r") as f:
            CONFIG = json.load(f)

        dispatcher = Dispatcher(WALLETS=WALLETS, CONFIG=CONFIG, SECRETS=SECRETS)
        session = None 
        while True:
            logger.info("""сhoice the desired option:\n[1] add wallets to whitelist\n[2] remove wallets from whitelist\n[3] randomly dispatch\n[q] quit\n""")
            user_input = input("your input: ")
            
            if user_input == str(1):
                if not session:
                    session = Whitelister(WALLETS=WALLETS, CONFIG=CONFIG)
                session.add_to_whitelists()
                logger.info('completed...')
            elif user_input == str(2):
                if not session:
                    session = Whitelister(WALLETS=WALLETS, CONFIG=CONFIG)
                session.delete_wallets()
                logger.info('completed...')
            elif user_input == str(3):
                dispatcher.dispatch()
                logger.info('completed...')
            elif user_input == 'q':
                break 
            else:
                logger.error("incorrect option. Try again")
    except Exception as e:
        logger.error(f"error: {e}\n\n")

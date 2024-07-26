import ccxt 
import random 
import json 
import os
from loguru import logger
import time 

class Dispatcher:
    def __init__(self, WALLETS, CONFIG, SECRETS) -> None:
        self.WALLETS = WALLETS
        self.CONFIG = CONFIG
        self.SECRETS = SECRETS

        self.exchange = ccxt.okx({
            "apiKey": self.SECRETS['APIKEY'],
            "secret": self.SECRETS['SECRET'],
            "password": self.SECRETS['PASSWORDOKX']
        })

        self._min_sol_amount = float(CONFIG['minSolAmount'])
        self._max_sol_amount = float(CONFIG['maxSolAmount'])
        self._dispatch_config_path = CONFIG['dispatchConfigPath']
        self._fee = float(CONFIG['fee'])
        self._token = CONFIG['token']
        self._token_chain = f"{CONFIG['token']}-{CONFIG['chain']}"
        


    def dispatch(self):
        with open(self._dispatch_config_path, "r") as file:
            self.dispatch_config = json.load(file)
            
        self._dispatch()

    def withdraw(self, amount: float, address: str):
        params = {
            "fee": self._fee,
            "chain": self._token_chain
        }

        tx = self.exchange.withdraw(
            self._token,
            amount,
            address,
            params=params
        )
        return tx 

    def _dispatch(self):
        success_rate = 0
        unsucessful_wallets = []
        n = len(self.WALLETS)
        for ix, wallet in enumerate(self.WALLETS):
            sol_amount = self.dispatch_config[wallet]
            try:
                tx = self.withdraw(sol_amount, wallet)
                wdId = tx.get("info", {}).get("wdId", None)
                logger.success(f"{ix}/{n} successful withdraw {sol_amount} SOL, {wallet[:5]}, wdId: {wdId}")
                success_rate += 1
            except Exception as e:
                logger.error(str(e))
                unsucessful_wallets.append(wallet) 
            
            time.sleep(1)
            
        logger.info(f"success rate {success_rate / n}")
        logger.error(f"unsucessful wallets: {str(unsucessful_wallets)}")

                

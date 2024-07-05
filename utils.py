import json
import time 
from seleniumbase import Driver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.common.exceptions import ElementClickInterceptedException, TimeoutException, StaleElementReferenceException
from selenium.webdriver.support import expected_conditions as ec
import sys 
import ccxt 
from loguru import logger

with open("wallets.txt", "r") as f:
    WALLETS = [i.strip() for i in f.readlines()]

with open("config.json", "r") as f:
    CONFIG = json.load(f)

WAIT_TIME = 10
class OKX:
    def __init__(self):
        self.okx_url_login = "https://www.okx.com/ru/account/login"
        self.driver = Driver(uc=True)
        self._zero = 0
        self._len_wallets = len(WALLETS)
        self.wallets_batches = [WALLETS[i:i + 20] for i in range(0, len(WALLETS), 20)] 
        self.okx_api = ccxt.okx(
            {
                "apiKey": CONFIG['apiKey'],
                "secret": CONFIG['secret'],
                "password": CONFIG['passwordOKX']
            }
        )

    @staticmethod
    def manual_login():
        logger.info('Log in to your account and press ENTER')
        input()

    def filling_addresses(self, batch):
        element = self.wait_an_element(By.XPATH, """/html/body/div[1]/div/div/div/div[2]/div/form/div[1]/div[3]/div[2]/div/div/div/div/div/div/input[2]""")
        if element:
            try:
                element.click() 
            except (ElementClickInterceptedException, StaleElementReferenceException):
                time.sleep(3)
                element = self.wait_an_element(By.XPATH, """/html/body/div[1]/div/div/div/div[2]/div/form/div[1]/div[3]/div[2]/div/div/div/div/div/div/input[2]""")
                element.click()

            chains = self.driver.find_elements(By.CLASS_NAME, "balance_okui-select-item")
            try:
                for i in chains:
                    if CONFIG['chain'].lower() in i.text.lower():
                        i.click()
            except Exception as error:
                logger.error(f"Error in filling_addresses function: {error}") 
            
        time.sleep(0.3)
        for i in range(0, len(WALLETS)-1):
            btn = self.driver.find_element(By.XPATH, "/html/body/div[1]/div/div/div/div[2]/div/form/button")
            if btn:
                btn.click()
            else:
                self.driver.find_element(By.XPATH, "/html/body/div[1]/div/div/div/div[2]/div/form/button").click()
                self.scroll_window()
            time.sleep(0.5)
        
        input_forms = [i for i in self.driver.find_elements(By.CLASS_NAME, "balance_okui-input-input") if i.accessible_name == 'Адрес / домен']
        for wallet, form in zip(batch, input_forms):
            self._zero += 1 
            logger.info(f'add : {wallet} [{self._zero}/{self._len_wallets}]')
            form.send_keys(wallet)
            time.sleep(0.01)
            
        self.driver.find_element(By.XPATH, "/html/body/div[1]/div/div/div/div[2]/div/form/div[3]/div/div/div/label/span[1]/input").click()
        self.driver.find_element(By.XPATH, "/html/body/div[1]/div/div/div/div[2]/div/form/div[4]/div/div/div/button").click()
        time.sleep(1)

    def scroll_window(self, x: int = 0, y: int = 50, up: bool = False):
        """
        Scrolls the window by the specified amount.

        Args:
            x (int): The horizontal scroll amount (default is 0).
            y (int): The vertical scroll amount (default is 50).
            up (bool): If True, scrolls the window upwards; if False, scrolls the window downwards (default is False).

        Returns:
            None
        """
        if up:
            y = -y
        self.driver.execute_script(f"window.scrollBy({x}, {y})")



    def confirmations(self):
        while True:
            for i in range(5):
                try:
                    time.sleep(1)
                    element = self.wait_an_element(By.XPATH, "//span[text()='Отправить код']")
                    if element:
                        element.click()
                    logger.success('Send code to email')
                    time.sleep(15)
                    break
                except Exception as error:
                    logger.error(f'Error in confirmations function: {error}')

            email_code = input(' Enter the code from the email: ')
            if email_code:
                break

        self.driver.find_element(By.XPATH, "/html/body/div[7]/div/div[2]/div/div/div/div/div/div/div/form/div[1]/div[2]/div/div/div/div/div/div/input[2]").send_keys(email_code)

        two_fa = input('Enter 2FA code: ')
        self.driver.find_element(By.XPATH, "/html/body/div[7]/div/div[2]/div/div/div/div/div/div/div/form/div[2]/div[2]/div/div/div/div/div/div/input[2]").send_keys(two_fa)
        time.sleep(2)
        self.driver.find_elements(By.XPATH, "/html/body/div[7]/div/div[3]/div/button[2]").click()
        time.sleep(2)
        
    def add_to_whitelists(self):
        self.driver.get(self.okx_url_login)
        time.sleep(5)
        self.manual_login()
        time.sleep(5)
        self.driver.get(CONFIG['withdrawalLink'])
        time.sleep(5)

        for batch in self.wallets_batches:
            while True:
                self.filling_addresses(batch)
                self.confirmations()
                break
            logger.info("60 seconds pause")
            time.sleep(60)

    def wait_an_element(self, by, element_selector: str, wait_time: int = 10):
        try:
            WebDriverWait(self.driver, wait_time).until(ec.presence_of_element_located((by, element_selector)))
            return self.driver.find_element(by, element_selector)
        except TimeoutException:
            logger.error(f'Error while waiting for an element: {element_selector}')
            sys.exit(-1)


# if __name__ == '__main__':
#     try:
#         session = OKX()
#         session.add_to_whitelists()
#         session.filling_addresses(WALLETS)

#         logger.success("done!")
#     except Exception as e:
#         logger.error(f"error: {e}\n\n")





import time 
from seleniumbase import Driver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.common.exceptions import ElementClickInterceptedException, TimeoutException, StaleElementReferenceException
from selenium.webdriver.support import expected_conditions as ec
from tqdm import tqdm 
import sys 
from loguru import logger

WAIT_TIME = 10
class Whitelister:
    def __init__(self, WALLETS, CONFIG, driver=None):
        self.CONFIG = CONFIG
        self.WALLETS = WALLETS
        self.okx_url_login = "https://www.okx.com/ru/account/login"
        if not driver:
            driver = Driver(uc=True)
            
        self.driver = driver 
        self._zero = 0
        self._len_wallets = len(self.WALLETS)
        self.wallets_batches = [self.WALLETS[i:i + 20] for i in range(0, len(self.WALLETS), 20)] 

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
                    if self.CONFIG['chain'].lower() in i.text.lower():
                        i.click()
            except Exception as error:
                logger.error(f"Error in filling_addresses function: {error}") 
            
        time.sleep(0.3)
        for i in range(0, len(batch)-1):
            btn = self.driver.find_element(By.XPATH, "/html/body/div[1]/div/div/div/div[2]/div/form/button/span")
            if btn:
                btn.click()
            else:
                self.driver.find_element(By.XPATH, "/html/body/div[1]/div/div/div/div[2]/div/form/button").click()
                self.scroll_window()
            time.sleep(1)
        
        input_forms = [i for i in self.driver.find_elements(By.CLASS_NAME, "balance_okui-input-input") if i.accessible_name == 'Адрес']
        for wallet, form in zip(batch, input_forms):
            self._zero += 1 
            logger.info(f'add : {wallet} [{self._zero}/{self._len_wallets}]')
            form.send_keys(wallet)
            time.sleep(0.01)
            
        self.driver.find_element(By.XPATH, "/html/body/div[1]/div/div/div/div[2]"
                                           "/div/form/div[3]/div/div/div/label/span[1]/input").click()
        self.driver.find_element(By.XPATH, "/html/body/div[1]/div/div/div"
                                           "/div[2]/div/form/div[4]/div/div/div/button").click()
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

        code_forms = self.driver.find_elements(By.XPATH, "//input[@placeholder='Ввести код']")
        code_forms[0].clear()
        code_forms[0].send_keys(email_code)
        time.sleep(0.2)
        totp = input("Enter 2fa code: ")
        code_forms[1].clear()
        code_forms[1].send_keys(totp)

        time.sleep(1)
        self.wait_an_element(By.XPATH, """//*[@id="body"]/div[6]/div/div[3]/div/button[2]/span""").click()
        time.sleep(2)

    def add_batch_to_whitelist(self, batch):
        self.driver.get(self.CONFIG['withdrawalLink'])
        time.sleep(5)
        while True:
            self.filling_addresses(batch)
            self.confirmations()
            break
    def add_to_whitelists(self):
        self.driver.get(self.okx_url_login)
        time.sleep(5)
        self.manual_login()
        time.sleep(5)
        for batch in tqdm(self.wallets_batches):
            self.add_batch_to_whitelist(batch)
            logger.info('60s pause')
            time.sleep(60)

    def wait_an_element(self, by, element_selector: str, wait_time: int = 10):
        try:
            WebDriverWait(self.driver, wait_time).until(ec.presence_of_element_located((by, element_selector)))
            return self.driver.find_element(by, element_selector)
        except TimeoutException:
            logger.error(f'Error while waiting for an element: {element_selector}')
            sys.exit(-1)
    def delete_wallets_from_one_page(self):
        rows = self.driver.find_elements(By.CLASS_NAME, "balance_okui-table-row")
        ix = 0
        with tqdm(total=len(self.WALLETS)) as pbar:
            while ix < len(rows):
                row = rows[ix]
                address = [i for i in row.find_elements(By.CSS_SELECTOR, "div") if i.get_property("className") == "AddressList_address__e+1Hh"][0]

                if address.text in self.WALLETS:
                    logger.info(f"deleting address: {address}")
                    row.find_elements(By.CLASS_NAME, "btn-content")[0].click()
                    self.wait_an_element(By.XPATH, "/html/body/div[7]/div/div[3]/div/button[2]").click()
                    pbar.update(1)
                    time.sleep(2)
                    ix = 0
                    rows = self.driver.find_elements(By.CLASS_NAME, "balance_okui-table-row")
                    time.sleep(2)
                else:
                    ix += 1

    def delete_wallets(self):
        self.driver.get(self.CONFIG['whitelistPage'])
        time.sleep(2)
        while True:
            self.delete_wallets_from_one_page()
            try:
                next_ = driver.find_element(By.XPATH, '//*[@id="root"]/div/div/div[2]/div/div[2]/ul/li[2]')
                next_disabled = "balance_okui-pagination-disabled" in next_.get_property("className")
                if next_disabled:
                    break 
                next_.click()
                time.sleep(5)
            except:
                break
        
import json
import undetected_chromedriver as uc
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time

def initialize_driver():
    return uc.Chrome()

def initialize_wait(driver, timeout=30):
    return WebDriverWait(driver, timeout)


def main():
    driver = initialize_driver()
    wait = initialize_wait(driver)
    driver.maximize_window()

    try:

        # Navigate to the eBay login page
        driver.get("https://www.ebay.com/")
        
        myEbay = wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, 'a[title="My eBay"]')))
        myEbay.click()

        email_field = wait.until(EC.element_to_be_clickable((By.ID, 'userid')))
        email_field.send_keys("support@neiltix.com")
        continue_btn = wait.until(EC.element_to_be_clickable((By.ID, 'signin-continue-btn')))
        continue_btn.click()
        
        pass_field = wait.until(EC.element_to_be_clickable((By.ID, 'pass')))
        pass_field.send_keys("xBHUQs9uAPnkEpehcfjTd3")
        sign_in_btn = wait.until(EC.element_to_be_clickable((By.ID, 'sgnBt')))
        sign_in_btn.click()

        time.sleep(20)  # Allow time for the login process

    except Exception as e:
        print(f"An error occurred: {e}")

if __name__ == "__main__":
    main()

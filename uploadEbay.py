import undetected_chromedriver as uc
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.keys import Keys
import csv, os, json, random, time

# Initialize undetected Chrome WebDriver
def initialize_driver_with_user_agent():
    user_agents = [
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64)",
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7)",
        "Mozilla/5.0 (X11; Linux x86_64)",
    ]
    chrome_options = Options()
    chrome_options.add_argument(f"user-agent={random.choice(user_agents)}")
    return uc.Chrome(options=chrome_options)

# Define WebDriverWait
def initialize_wait(driver, timeout=30):
    return WebDriverWait(driver, timeout)

# Load existing product IDs from the CSV file
def load_existing_ids(file_name="product_ids.csv"):
    try:
        with open(file_name, mode="r") as file:
            reader = csv.reader(file)
            next(reader)  # Skip header
            return set(row[0] for row in reader)
    except FileNotFoundError:
        return set()

# Main function
def main():
    driver = initialize_driver_with_user_agent()
    wait = initialize_wait(driver)
    driver.maximize_window()

    driver.get('https://www.ebay.com')
    
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
    skipBtn = wait.until(EC.presence_of_element_located((By.ID, 'passkeys-cancel-btn')))
    skipBtn.click()
    time.sleep(5)  
    
    sellBtn = wait.until(EC.element_to_be_clickable((By.XPATH, '//a[text()=" Sell"]')))
    sellBtn.click()
    createListing =  wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, 'button[aria-controls="nid-qhy-1-content"]')))
    createListing.click()
    
    singleListing =  wait.until(EC.element_to_be_clickable((By.XPATH, '//span[contains(text(), "Single listing")]')))
    singleListing.click()
    
    inputSearch = wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, "input[aria-label*='Tell us what you']")))
    inputSearch.send_keys("Mark mcmorris infinite air playstation 4 brand new")
    searchBtn = wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, 'button[aria-label="Search"]')))
    searchBtn.click()
    time.sleep(60)


if __name__ == "__main__":
    main()

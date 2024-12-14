import undetected_chromedriver as uc
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.keys import Keys
import time
import csv, os, json

# Initialize undetected Chrome WebDriver
def initialize_driver():
    return uc.Chrome()

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

# Append new product IDs to the CSV file
def append_to_csv(product_ids, file_name="product_ids.csv"):
    with open(file_name, mode="a", newline="") as file:
        writer = csv.writer(file)
        for pid in product_ids:
            writer.writerow([pid])

# Accept cookies if present
def accept_cookies(driver, wait):
    try:
        accept_cookies_btn = wait.until(EC.presence_of_element_located((By.ID, "truste-consent-button")))
        accept_cookies_btn.click()
        print("Cookies accepted.")
    except:
        print("No cookies to accept.")

# Search for products
def perform_search(driver, wait, search_term="video games"):
    search_input = wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, "[data-testid='SearchInput']")))
    search_input.send_keys(search_term)
    search_input.send_keys(Keys.ENTER)
    print(f"Search initiated for '{search_term}'.")

# Apply filters
def apply_filters(driver, wait):
    try:
        for_sale_button = wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, 'label[label="For sale"]')))
        for_sale_button.click()

        time.sleep(2)
        driver.execute_script("window.scrollBy(0, 300);")
        usa_button = wait.until(EC.presence_of_element_located((By.XPATH, '//label//div[text()="USA"]')))
        usa_button.click()

        time.sleep(2)
        driver.execute_script("window.scrollBy(0, 300);")
        open_price = wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, 'button[data-testid="SearchAccordion-Price"]')))
        open_price.click()

        minimum_price = wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, 'input[data-testid="MinPriceInput"]')))
        minimum_price.send_keys('1')
        maximum_price = wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, 'input[data-testid="MaxPriceInput"]')))
        maximum_price.send_keys('200')

        apply_button = wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, 'button[data-testid="RefineApply"]')))
        apply_button.click()
        print("Filters applied successfully.")
    except Exception as e:
        print(f"Error while applying filters: {e}")

# Scroll and scrape product IDs with stale element handling
def scrape_product_ids(driver, wait, existing_ids, max_attempts=20, scroll_increment=800):
    attempts = 0
    last_height = driver.execute_script("return document.body.scrollHeight")

    while attempts < max_attempts:
        try:
            # Get all product elements (re-locate each time inside the loop)
            product_elements = driver.find_elements(By.CSS_SELECTOR, "[data-testid='ItemContainer']")
            new_ids = set()

            # Extract product IDs
            for element in product_elements:
                try:
                    product_id = element.get_attribute("data-productid")
                    if product_id and product_id not in existing_ids:
                        new_ids.add(product_id)
                except Exception as e:
                    print(f"Error accessing element: {e}")
                    continue  # Skip the problematic element

            # Append new IDs to the CSV
            if new_ids:
                append_to_csv(new_ids)
                existing_ids.update(new_ids)
                print(f"Added {len(new_ids)} new product IDs. Total: {len(existing_ids)}.")

            # Scroll down slowly
            driver.execute_script(f"window.scrollBy(0, {scroll_increment});")
            time.sleep(2)

            # Check if scrolling has reached the bottom
            new_height = driver.execute_script("return document.body.scrollHeight")
            if new_height == last_height:
                attempts += 1  # Increment if no new content is loaded
                print(f"No new content detected. Attempt {attempts}/{max_attempts}.")
            else:
                attempts = 0  # Reset attempts if new content is loaded
            last_height = new_height

        except Exception as e:
            print(f"Error during scraping: {e}")
            attempts += 1  # Count as a failed attempt and retry
            time.sleep(2)  # Allow some delay before retrying

    print(f"Scraping completed. {len(existing_ids)} total product IDs saved.")

# Scrape product details and save data
def scrape_product_details(driver, wait, csv_file="product_ids.csv"):
    with open(csv_file, mode="r") as file:
        product_ids = [line.strip() for line in file]

    for product_id in product_ids:
        try:
            url = f"https://www.mercari.com/us/item/{product_id}/?ref=search_results"
            driver.get(url)
            time.sleep(3)

            # Create folder for product
            product_folder = os.path.join("products", product_id)
            os.makedirs(product_folder, exist_ok=True)

            # Scrape title, price, description
            title = wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, "[data-testid='ItemName']"))).text
            price = wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, "[data-testid='ItemPrice']"))).text
            description = wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, "[data-testid='ItemDetailsDescription']"))).text

            # Save data to JSON
            data = {"title": title, "price": price, "description": description}
            with open(os.path.join(product_folder, f"{product_id}.json"), "w") as json_file:
                json.dump(data, json_file, indent=4)

            # Scrape and download images
            image_elements = driver.find_elements(By.CSS_SELECTOR, "img[src*='photos']")
            for index, img_element in enumerate(image_elements):
                img_url = img_element.get_attribute("src")
                img_path = os.path.join(product_folder, f"image{index + 1}.jpg")
                download_image(img_url, img_path)

            print(f"Saved details and images for product: {product_id}")

        except Exception as e:
            print(f"Error scraping product {product_id}: {e}")

# Download image from URL
def download_image(url, file_path):
    import requests
    response = requests.get(url, stream=True)
    if response.status_code == 200:
        with open(file_path, "wb") as file:
            for chunk in response.iter_content(1024):
                file.write(chunk)

# Main function
def main():
    driver = initialize_driver()
    wait = initialize_wait(driver)
    driver.maximize_window()

    try:
        driver.get('https://www.mercari.com')
        time.sleep(5)

        accept_cookies(driver, wait)
        perform_search(driver, wait)
        apply_filters(driver, wait)

        existing_ids = load_existing_ids()
        print(f"Loaded {len(existing_ids)} existing product IDs.")

        scrape_product_ids(driver, wait, existing_ids)
        
        scrape_product_details(driver, wait)
    except Exception as e:
        print(f"An error occurred: {e}")

    finally:
        try:
            driver.quit()
        except Exception as e:
            print(f"Error while closing the browser: {e}")

if __name__ == "__main__":
    main()

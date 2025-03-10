import requests
import re
import json
import pandas as pd
import time
import os
import threading
import concurrent.futures
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.edge.service import Service
from selenium.webdriver.edge.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import NoSuchElementException, TimeoutException
from tqdm import tqdm

class PoyaScraper:
    def __init__(self, query, save_folder="./data", edge_driver_path="/usr/local/bin/msedgedriver"):
        self.query = query
        self.save_folder = save_folder
        self.edge_driver_path = edge_driver_path
        self.headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/114.0.0.0 Safari/537.36"
        }
        
        # Make sure the save directory exists
        if not os.path.exists(self.save_folder):
            os.makedirs(self.save_folder)
        
        # Thread lock for safe printing in concurrent environments
        self.print_lock = threading.Lock()
        
        # For storing all products
        self.products_info = None
        self.products_with_specs = None
    
    def safe_print(self, message):
        with self.print_lock:
            print(message)
    
    def fetch_product_list(self):
        base_url = f'https://www.poyabuy.com.tw/catalog/search?q="{self.query}"&startIndex='
        
        all_products = []
        i = 0
        products_on_page = True
        
        print(f"Searching for products with query: '{self.query}'")
        
        pbar = tqdm(desc="Fetching product pages", unit="page")
        
        while products_on_page:
            start_index = 50 * i
            url = f'{base_url}{start_index}'
            
            try:
                response = requests.get(url, headers=self.headers)
                if response.status_code != 200:
                    self.safe_print(f"Request failed, status code: {response.status_code}")
                    break
                
                soup = BeautifulSoup(response.text, "html.parser")
                script_tag = None
                
                # Find the script tag containing product data
                for script in soup.find_all("script"):
                    if "nineyi.dependencies" in script.text:
                        script_tag = script.text
                        break
                        
                if not script_tag:
                    self.safe_print("JSON data not found")
                    break
                
                # Extract JSON data using regex
                match = re.search(r'nineyi.dependencies = ({.*?});', script_tag, re.DOTALL)
                if not match:
                    self.safe_print("JSON data block not found")
                    break
                    
                json_text = match.group(1)
                data = json.loads(json_text)
                
                # Extract product list from the JSON data
                items = data.get("serverRenderData", {}).get("searchResult", {}).get("SalePageList", [])
                if not items:
                    products_on_page = False
                    pbar.update(1)  # Update for the final page
                    pbar.close()
                    print(f"Completed scraping all pages (total {i + 1} pages)")
                    break
                
                # Extract product information
                for item in items:
                    title = item.get("Title", "N/A")
                    product_id = item.get("Id", "N/A")
                    product_url = f"https://www.poyabuy.com.tw/SalePage/Index/{product_id}"
                    all_products.append([title, product_url])
                
                pbar.update(1)  # Update progress bar
                pbar.set_postfix({"Products": len(all_products)})
                
                i += 1
                
                # Avoid sending requests too frequently
                time.sleep(0.5)
                
            except Exception as e:
                self.safe_print(f"Error occurred while scraping product list: {e}")
                break

        # Convert to DataFrame
        products_info = pd.DataFrame(all_products)
        if not products_info.empty:
            products_info.columns = ["Product Name", "Product URL"]
            self.products_info = products_info

        return products_info
    
    def process_single_product(self, product_info):
        """Process a single product to extract specifications"""
        product_name, product_url, index, total = product_info
        
        # Store basic product info
        product_data = {
            'Product Name': product_name,
            'Product URL': product_url
        }
        
        # Setup Edge browser in headless mode
        edge_options = Options()
        edge_options.add_argument("--headless")
        edge_options.add_argument("--disable-gpu")
        edge_options.add_argument("--window-size=1920,1080")
        edge_options.add_argument("--disable-dev-shm-usage")
        edge_options.add_argument("--disable-extensions")
        edge_options.add_argument("--disable-logging")
        edge_options.add_argument("--disable-images")
        
        service = Service(executable_path=self.edge_driver_path)
        driver = webdriver.Edge(service=service, options=edge_options)
        
        try:
            # Open product page
            driver.get(product_url)
            
            # Use explicit wait instead of sleep, wait max 5 seconds
            wait = WebDriverWait(driver, 5)
            
            # Try to find and click the specifications tab
            try:
                # Wait for spec button and click it
                spec_button = wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, 'a[href="#salepage-specification"]')))
                spec_button.click()
                
                # Wait for the specs table to load
                wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, '.simple-table')))
                
                # Find specification table rows
                table_rows = driver.find_elements(By.CSS_SELECTOR, '.simple-table .simple-table-row')
                
                # Extract specifications
                spec_count = 0
                for row in table_rows:
                    title = row.find_element(By.CSS_SELECTOR, '.simple-table-td-left').text.strip()
                    content = row.find_element(By.CSS_SELECTOR, '.simple-table-td-right').text.strip()
                    
                    # Add to this product's data
                    product_data[title] = content
                    spec_count += 1
                
            except (NoSuchElementException, TimeoutException):
                pass  # No specs found, continue with next product
                
        except Exception as e:
            pass  # Handle silently and continue
        
        finally:
            # Close the browser
            driver.quit()
        
        return product_data
    
    def scrape_product_specs(self, max_workers=6):
        if self.products_info is None or self.products_info.empty:
            print("No products to scrape specifications from. Run fetch_product_list first.")
            return None
        
        print(f"Scraping specifications for {len(self.products_info)} products")
        
        # Prepare product info list for multithreading
        product_info_list = [
            (row['Product Name'], row['Product URL'], index+1, len(self.products_info)) 
            for index, row in self.products_info.iterrows()
        ]
        
        # Use thread pool to process products in parallel
        all_product_data = []
        
        # Create a progress bar
        with tqdm(total=len(product_info_list), desc="Scraping product specs", unit="product") as pbar:
            with concurrent.futures.ThreadPoolExecutor(max_workers=max_workers) as executor:
                # Submit all tasks
                future_to_product = {
                    executor.submit(self.process_single_product, product_info): product_info
                    for product_info in product_info_list
                }
                
                # Process results as they complete
                for future in concurrent.futures.as_completed(future_to_product):
                    product_data = future.result()
                    all_product_data.append(product_data)
                    pbar.update(1)
        
        # Convert to DataFrame
        result_df = pd.DataFrame(all_product_data)
        self.products_with_specs = result_df
        
        return result_df
    
    def save_to_csv(self, filename=None):
        if self.products_with_specs is None or self.products_with_specs.empty:
            print("No data to save. Please run both fetch_product_list and scrape_product_specs first.")
            return False
        
        if filename is None:
            filename = f"Poya_{self.query}.csv"
        
        # Ensure filename has .csv extension
        if not filename.endswith('.csv'):
            filename += '.csv'
        
        # Combine complete file path
        filepath = os.path.join(self.save_folder, filename)
        
        try:
            self.products_with_specs.to_csv(filepath, index=False, encoding='utf-8-sig')
            print(f"Data successfully saved to {filepath}")
            return True
        except Exception as e:
            print(f"Error occurred while saving data: {e}")
            return False
    
    def run(self, max_workers=6, filename=None):
        """
        Run the complete workflow: fetch products, get specs, and save to CSV
        """
        # Step 1: Fetch product list
        self.fetch_product_list()
        
        if self.products_info is None or self.products_info.empty:
            print("No products found. Exiting.")
            return False
        
        # Step 2: Scrape product specifications
        self.scrape_product_specs(max_workers=max_workers)
        
        # Step 3: Save results to CSV
        result = self.save_to_csv(filename)

        # Summary
        if self.products_with_specs is not None:
            spec_columns = self.products_with_specs.shape[1] - 2  # Minus the original two columns
            print(f"Total products: {len(self.products_with_specs)}")
        
        return result
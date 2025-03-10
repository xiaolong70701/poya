# PoyaScraper 🛍️

A Python-based web scraper for extracting product information and specifications from **Poya** using **Selenium** and **BeautifulSoup**. The scraper finds products via search, fetches detailed specifications for each item, and saves all data in a structured CSV file.

---

## 📌 Features
✔ **Complete Product Information** - Extracts product names, URLs, and detailed specifications.  
✔ **Multi-threaded Scraping** - Uses parallel processing to significantly increase scraping speed.  
✔ **Visual Progress Tracking** - Displays real-time progress bars for both product listing and specification scraping.  
✔ **Unified Data Output** - Combines product information and specifications in a single, well-organized CSV file.  
✔ **Customizable Folder Path** - Allows users to specify the save location (defaults to `./data`).  

---

## 📦 **Installation**

Before running the scraper, install the required dependencies:

```bash
pip install requests beautifulsoup4 pandas selenium tqdm
```

Alternatively, if you have added `poya` as a package:

```bash
pip install git+https://github.com/xiaolong70701/poya.git
```

---

## 🖥 **Install Microsoft Edge WebDriver (`msedgedriver`)**
The scraper uses **Microsoft Edge WebDriver (`msedgedriver`)** to automate browsing.  
You must **download and configure it** before running the script.

### **📌 Step 1: Download Edge WebDriver**
1. Open **[Microsoft Edge WebDriver](https://developer.microsoft.com/en-us/microsoft-edge/tools/webdriver/)**.
2. Download the **version that matches your Edge browser**.
   - Check your Edge version: Open **Edge** → Click `...` (Menu) → **Settings** → **About Microsoft Edge**.
3. Extract the downloaded file to a location accessible by your system.

### **📌 Step 2: Add `msedgedriver` to System PATH**
You must ensure that `msedgedriver` is accessible from the command line.

#### **Windows (Recommended Path)**
1. Move `msedgedriver.exe` to:
   ```
   C:\Program Files\msedgedriver\msedgedriver.exe
   ```
2. Add it to your **System PATH**:
   - Open **Start Menu** → Search `Environment Variables`.
   - Click `Edit the system environment variables`.
   - Under **System Properties**, go to `Advanced` → Click `Environment Variables`.
   - Find `Path` under **System Variables** → Click `Edit`.
   - Click `New` and add:  
     ```
     C:\Program Files\msedgedriver\
     ```
   - Click `OK` → Restart your computer.

#### **macOS (Default Path)**
Move `msedgedriver` to:
```bash
sudo mv msedgedriver /usr/local/bin/msedgedriver
```
Verify installation:
```bash
msedgedriver --version
```

If the command returns the version, it's correctly installed. After checking the installation of `msedgedriver`, open Terminal and input the following command to give driver permission:

```bash
chmod +x /usr/local/bin/msedgedriver
```

---

## 🚀 **Example Usage**

Run the following script to scrape Poya for toilet paper (衛生紙) products and their specifications:

```python
from poya.scraper import PoyaScraper

query = "衛生紙"
scraper = PoyaScraper(query=query)
scraper.run(max_workers=6)
```

This will:

1. Fetch all toilet paper products from Poya's search results.
2. Extract detailed specifications for each product.
3. Save the combined results in a CSV file located in `./data/Poya_衛生紙_complete.csv`.

---

## ⚙ **Customization**

### **Specify Save Folder**
By default, the CSV files are saved in `./data/`. You can specify a different folder:

```python
scraper = PoyaScraper(query="洗髮精", save_folder="./my_results")
scraper.run()
```
📌 This will save the output file to `./my_results/Poya_洗髮精_complete.csv`.

### **Adjust Thread Count**
To increase or decrease the number of parallel threads for specification scraping:

```python
scraper = PoyaScraper(query="面膜")
scraper.run(max_workers=8)
```
📌 This increases the parallel threads from **6** (default) to **8**.

### **Custom Output Filename**
To specify a custom filename for the output CSV:

```python
scraper = PoyaScraper(query="保養品")
scraper.run(filename="my_skincare_products.csv")
```
📌 This saves the results to `./data/my_skincare_products.csv`.

---

## 📊 **Advanced Usage**

For more control over the scraping process, you can run each step separately:

```python
scraper = PoyaCompletePoyaScraperScraper(query="保濕乳")

# Step 1: Just fetch product listings
products_df = scraper.fetch_product_list()

# Step 2: Scrape specifications for the products
specs_df = scraper.scrape_product_specs(max_workers=4)

# Step 3: Save the results
scraper.save_to_csv(filename="poya_moisturizers.csv")
```

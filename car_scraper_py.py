from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager
from bs4 import BeautifulSoup
import pandas as pd
import re
import time
import shutil  # Add this at the top


# -------- Helper Functions --------

def extract_price(price_str):
    """Extract price number from price string"""
    if not price_str:
        return None
    # Find all numbers in the string
    numbers = re.findall(r'\d[\d,]*', str(price_str))
    if numbers:
        # Take the last/largest number and remove commas
        return int(numbers[-1].replace(',', ''))
    return None

def parse_title(title):
    """Parse car title into components"""
    if not title:
        return None, None, None, None
    
    parts = title.strip().split()
    if len(parts) < 2:
        return None, None, None, None
    
    year = parts[0] if parts[0].isdigit() else None
    brand = parts[1] if len(parts) > 1 else None
    
    if len(parts) >= 3:
        model = " ".join(parts[2:-1]) if len(parts) > 3 else parts[2]
        vehicle_type = parts[-1] if len(parts) > 3 else None
    else:
        model = None
        vehicle_type = None
    
    return year, brand, model, vehicle_type


import shutil

def setup_driver(headless=True):
    """Setup Chrome driver with basic options"""
    options = Options()

    if headless:
        options.add_argument("--headless=new")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument("--disable-gpu")
    options.add_argument("--window-size=1920,1080")

    # Manually set the path to the Chrome binary if it's found
    import os
    print("🔍 PATH seen by Jenkins:", os.environ.get("PATH"))
    print("🔍 Is google-chrome in PATH?", shutil.which("google-chrome"))

    chrome_path = shutil.which("google-chrome") or shutil.which("google-chrome-stable")
    if chrome_path:
        options.binary_location = "/usr/bin/google-chrome"

    else:
        print("❌ Google Chrome binary not found in PATH.")
        return None

    try:
        driver = webdriver.Chrome(
            service=Service(ChromeDriverManager().install()),
            options=options
        )
        return driver
    except Exception as e:
        print(f"❌ Error setting up driver: {e}")
        return None

def scrape_single_page(driver, page_num, max_retries=3):
    """Scrape one page and return data"""
    url = f"https://www.one2car.com/en/cars-for-sale?page_number={page_num}&page_size=26"
    print(f"Scraping page {page_num}...")
    
    for attempt in range(max_retries):
        try:
            driver.get(url)
            time.sleep(3)  # Wait for page to load
            
            # Wait for listings to appear
            wait = WebDriverWait(driver, 15)
            wait.until(EC.presence_of_element_located((By.CLASS_NAME, "listing")))
            
            # Get page source and parse
            soup = BeautifulSoup(driver.page_source, "html.parser")
            articles = soup.find_all("article", class_="listing")
            
            if not articles:
                print(f"No articles found on page {page_num}")
                return []
            
            page_data = []
            
            for article in articles:
                try:
                    # Extract data from article attributes
                    title = article.get("data-display-title")
                    year = article.get("data-year")
                    mileage = article.get("data-mileage")
                    transmission = article.get("data-transmission")
                    car_url = article.get("data-url")
                    image_src = article.get("data-image-src")
                    
                    # Extract price from price div
                    price_div = article.find("div", class_="listing__price")
                    price_text = price_div.get_text(strip=True) if price_div else None
                    
                    car_data = {
                        "Title": title,
                        "Year": year,
                        "Mileage": mileage,
                        "Transmission": transmission,
                        "Price": price_text,
                        "URL": car_url,
                        "Image": image_src
                    }
                    
                    page_data.append(car_data)
                    
                except Exception as e:
                    print(f"Error extracting car data: {e}")
                    continue
            
            print(f"Found {len(page_data)} cars on page {page_num}")
            return page_data
            
        except Exception as e:
            print(f"Attempt {attempt + 1} failed for page {page_num}: {e}")
            if attempt < max_retries - 1:
                time.sleep(5)
            else:
                print(f"Failed to scrape page {page_num} after {max_retries} attempts")
                return []
    
    return []

def scrape_pages(start_page, end_page, headless=True):
    """Scrape multiple pages sequentially"""
    print(f"Starting to scrape pages {start_page} to {end_page}")
    
    # Setup driver
    driver = setup_driver(headless)
    if not driver:
        print("Failed to setup driver")
        return []
    
    all_data = []
    
    try:
        for page in range(start_page, end_page + 1):
            page_data = scrape_single_page(driver, page)
            all_data.extend(page_data)
            
            # Small delay between pages
            time.sleep(2)
            
            print(f"Total cars collected so far: {len(all_data)}")
    
    except KeyboardInterrupt:
        print("Scraping interrupted by user")
    
    except Exception as e:
        print(f"Error during scraping: {e}")
    
    finally:
        driver.quit()
        print("Driver closed")
    
    return all_data

def process_and_save_data(data, filename="car_data.csv"):
    """Process scraped data and save to CSV"""
    if not data:
        print("No data to save")
        return
    
    print(f"Processing {len(data)} cars...")
    
    # Create DataFrame
    df = pd.DataFrame(data)
    
    # Parse titles
    df[['Year_parsed', 'Brand', 'Model', 'Vehicle_type']] = df['Title'].apply(
        lambda x: pd.Series(parse_title(x))
    )
    
    # Extract numeric price
    df['Price_numeric'] = df['Price'].apply(extract_price)
    
    # Clean mileage (extract numbers)
    df['Mileage_numeric'] = df['Mileage'].apply(
        lambda x: int(re.findall(r'\d+', str(x).replace(',', ''))[0]) 
        if x and re.findall(r'\d+', str(x).replace(',', '')) else None
    )
    
    # Save to CSV
    df.to_csv(filename, index=False)
    print(f"Data saved to {filename}")
    
    # Print summary
    print(f"\nSummary:")
    print(f"Total cars: {len(df)}")
    print(f"Cars with prices: {df['Price_numeric'].notna().sum()}")
    print(f"Cars with mileage: {df['Mileage_numeric'].notna().sum()}")
    print(f"Unique brands: {df['Brand'].nunique()}")
    
    return df

# -------- Main Execution --------

def main():
    """Main function to run the scraper"""
    
    # Configuration
    START_PAGE = 1
    END_PAGE = 10
    HEADLESS = True  # Set to True to run in background
    OUTPUT_FILE = "one2car_data.csv"
    
    print("🚗 Car Scraper Starting...")
    print(f"Pages: {START_PAGE} to {END_PAGE}")
    print(f"Headless mode: {HEADLESS}")
    print("-" * 50)
    
    # Scrape data
    scraped_data = scrape_pages(START_PAGE, END_PAGE, headless=HEADLESS)
    
    if scraped_data:
        print(f"\n✅ Scraping completed! Found {len(scraped_data)} cars")
        
        # Process and save
        df = process_and_save_data(scraped_data, OUTPUT_FILE)
        
        print(f"\n🎉 All done! Check {OUTPUT_FILE} for results")
        return df
    else:
        print("\n❌ No data was scraped")
        return None

# Run the scraper
if __name__ == "__main__":
    result = main()

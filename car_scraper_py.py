from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
import shutil

options = Options()
options.add_argument('--headless')
options.add_argument('--no-sandbox')
options.add_argument('--disable-dev-shm-usage')
options.add_argument("--window-size=1920,1080")
options.binary_location = "/usr/bin/google-chrome"


chrome_path = shutil.which("google-chrome") or shutil.which("google-chrome-stable")
print("✅ Chrome found:", chrome_path)
if chrome_path:
    options.binary_location = chrome_path
    driver = webdriver.Chrome(service=Service(), options=options)
    driver.get("https://google.com")
    print(driver.title)
    driver.quit()
else:
    print("❌ Chrome not found")

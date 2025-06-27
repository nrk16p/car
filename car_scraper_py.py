from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager
import shutil
import os

options = Options()
options.add_argument('--headless')
options.add_argument('--no-sandbox')
options.add_argument('--disable-dev-shm-usage')
options.add_argument("--window-size=1920,1080")

# Fallback path
chrome_path = shutil.which("google-chrome") or shutil.which("google-chrome-stable") or "/usr/bin/google-chrome"
print("✅ Chrome found:", chrome_path)

if os.path.exists(chrome_path):
    options.binary_location = chrome_path
    driver = webdriver.Chrome(
        service=Service(ChromeDriverManager().install()),
        options=options
    )
    driver.get("https://google.com")
    print("✅ Page title:", driver.title)
    driver.quit()
else:
    print("❌ Chrome not found")

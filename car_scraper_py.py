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

# Fallback path for Chrome
chrome_path = shutil.which("google-chrome") or shutil.which("google-chrome-stable") or "/usr/bin/google-chrome"
print("🔍 Detected Chrome path:", chrome_path)

# ตรวจสอบว่า path มีอยู่จริงและสามารถ execute ได้
if chrome_path and os.path.exists(chrome_path) and os.access(chrome_path, os.X_OK):
    print("✅ Chrome path exists and is executable.")
    options.binary_location = chrome_path
    driver = webdriver.Chrome(
        service=Service(ChromeDriverManager().install()),
        options=options
    )
    driver.get("https://google.com")
    print("✅ Page title:", driver.title)
    driver.quit()
else:
    print("❌ Chrome not found or not executable.")

from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager

# ใช้ path ตรงของ Chrome
chrome_path = "/usr/bin/google-chrome-stable"
print("✅ Forcing Chrome binary at:", chrome_path)

options = Options()
options.binary_location = chrome_path
options.add_argument("--headless")
options.add_argument("--no-sandbox")
options.add_argument("--disable-dev-shm-usage")
options.add_argument("--window-size=1920,1080")

# รัน Chrome โดยไม่เช็ค os.access แล้ว
driver = webdriver.Chrome(
    service=Service(ChromeDriverManager().install()),
    options=options
)

driver.get("https://www.google.com")
print("✅ Page title:", driver.title)
driver.quit()

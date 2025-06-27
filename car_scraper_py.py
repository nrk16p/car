from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager
import subprocess

# Path to Chrome
chrome_path = "/usr/bin/google-chrome-stable"
print("✅ Forcing Chrome binary at:", chrome_path)

# Get Chrome version manually
def get_chrome_version():
    try:
        output = subprocess.check_output([chrome_path, '--version']).decode('utf-8')
        version = output.strip().split()[-1]
        print("✅ Detected Chrome version:", version)
        return version
    except Exception as e:
        print("❌ Failed to get Chrome version:", str(e))
        return None

chrome_version = get_chrome_version()

options = Options()
options.binary_location = chrome_path
options.add_argument('--headless')
options.add_argument('--no-sandbox')
options.add_argument('--disable-dev-shm-usage')
options.add_argument("--window-size=1920,1080")

# Tell webdriver-manager exactly which version of chromedriver to use
if chrome_version:
    driver = webdriver.Chrome(
        service=Service(ChromeDriverManager(version=chrome_version).install()),
        options=options
    )
    driver.get("https://google.com")
    print("✅ Page title:", driver.title)
    driver.quit()
else:
    print("❌ Chrome version not found. Cannot continue.")

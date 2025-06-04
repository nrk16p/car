from selenium import webdriver

driver = webdriver.Remote(
    command_executor=SelenoidIP/wd/hub)
driver.get("http://www.google.com")
driver.quit() 

# pip install selenium pandas webdriver-manager
# pip install selenium webdriver-manager openpyxl
# py (your file name).py

import time
import signal
import sys
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.support.ui import Select
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from webdriver_manager.chrome import ChromeDriverManager
import openpyxl

options = webdriver.ChromeOptions()
driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)

# Set page to navigate to
driver.get("example.com")

# Explicit waits to bypass website antibot
wait = WebDriverWait(driver, 3, poll_frequency=0.2)

# Find country drop down and SMS credits dropdown using aria-labelledby attributes
country_dropdown_element = wait.until(EC.presence_of_element_located((By.XPATH, "//select[@aria-labelledby='pricing--sms-country']")))
sms_credits_dropdown_element = wait.until(EC.presence_of_element_located((By.XPATH, "//select[@aria-labelledby='pricing--sms-credits']")))

country_dropdown = Select(country_dropdown_element)
sms_credits_dropdown = Select(sms_credits_dropdown_element)

# Get all options
countries = [option.text for option in country_dropdown.options]
sms_credit_options = [option.get_attribute('value') for option in sms_credits_dropdown.options]

# Store results
pricing_data = []

def save_data(signum, frame):
    workbook = openpyxl.Workbook()
    sheet = workbook.active
    sheet.title = "SMS Pricing"

    # Headers
    sheet.append(["Country", "Credits", "Price"])
    for row in pricing_data:
        sheet.append(row)
    workbook.save("sms_pricing_data_full.xlsx")
    print("Data saved to sms_pricing_data_full.xlsx")
    sys.exit(0)

signal.signal(signal.SIGINT, save_data) 
signal.signal(signal.SIGTERM, save_data)

for country in countries:
    country_dropdown.select_by_visible_text(country)
    
    for credit in sms_credit_options:
        sms_credits_dropdown.select_by_value(credit)

        try:
            price_element = wait.until(EC.presence_of_element_located((By.XPATH, "(//div[@class='variants__TypographyBase-sc-g6bgyl-1 ibGRBr styles__Text-sc-1h89h4m-3 kZXoXB']//strong)[2]")))
            price = price_element.text.strip().replace("$", "")  
        except Exception as e:
            price = "0.0360" 
            print(f"Price not found for {country} {credit}, defaulting to $0.0360")

        pricing_data.append([country, credit, price])

driver.quit()

save_data(None, None)

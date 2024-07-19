import undetected_chromedriver as webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time

options = webdriver.ChromeOptions()
profile = "C:\\Users\\weszi\\AppData\\Local\\Google\\Chrome\\User Data"
# options.add_argument(f"user-data-dir={profile}")
print("before get")
driver = webdriver.Chrome(options=options, use_subprocess=True)
driver.get("https://app.pluralsight.com/id")
print("after get")
# Login credentials
email = "sami.belhadj@oddo-bhf.com"
password = "7cB3MP.6y9.Z?c?"

# Wait for the username field to be present and input email
WebDriverWait(driver, 20).until(EC.presence_of_element_located((By.ID, "Username"))).send_keys(email)

# Wait for the password field to be present and input password
WebDriverWait(driver, 20).until(EC.presence_of_element_located((By.ID, "Password"))).send_keys(password)

# Wait for the login button to be present and click it
WebDriverWait(driver, 20).until(EC.element_to_be_clickable((By.ID, "login"))).click()

# get generated cookies:
# cookies = driver.get_cookies()
# print(cookies)

# find the generated cookie : {"name":"Identity.Session"}
# for cookie in cookies:
#     if cookie['name'] == "Identity.Session":
#         # print the value of the cookie
#         print(cookie)
#         break

# keep the browser open forever
while True:
    time.sleep(1)
    pass

from flask import Flask, jsonify
from flask_cors import CORS
import undetected_chromedriver as webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time

app = Flask(__name__)
CORS(app)  # Enable CORS for all routes
# Global variable to store the WebDriver instance
driver = None

def fetch_cookie(email, password):
    global driver
    print("fetch_cookie")
    options = webdriver.ChromeOptions()
    # profile = "C:\\Users\\weszi\\AppData\\Local\\Google\\Chrome\\User Data"
    # options.add_argument(f"user-data-dir={profile}")
    driver = webdriver.Chrome(options=options, use_subprocess=True)
    
    # options.add_argument("--headless") # Headless mode

    # driver.get("https://app.pluralsight.com/id")
    driver.get("https://app.pluralsight.com/id")

    print("after get")

    # sleep for 5 seconds
    driver.implicitly_wait(5)

    # Wait for the username field to be present and input email
    WebDriverWait(driver, 20).until(EC.presence_of_element_located((By.ID, "Username"))).send_keys(email)

    # sleep for 2 seconds
    driver.implicitly_wait(2)

    # Wait for the password field to be present and input password
    WebDriverWait(driver, 20).until(EC.presence_of_element_located((By.ID, "Password"))).send_keys(password)

    # sleep for 4 seconds
    driver.implicitly_wait(4)

    # Wait for the login button to be present and click it
    WebDriverWait(driver, 20).until(EC.element_to_be_clickable((By.ID, "login"))).click()

@app.route('/get_cookie', methods=['GET'])
def get_cookie():
    email = "sami.belhadj@oddo-bhf.com"  # replace with dynamic value if needed
    password = "7cB3MP.6y9.Z?c?"  # replace with dynamic value if needed
    print("before fetch_cookie")
    fetch_cookie(email, password)
    print("after fetch_cookie")
    # keep the browser open forever
    while True:
        time.sleep(1)
        pass

@app.route('/close', methods=['GET'])
def close():
    global driver
    if driver:
        driver.quit()
        driver = None
        print("Browser closed")
        return {"message":"Browser closed"}

if __name__ == '__main__':
    app.run(debug=True)

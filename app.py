from flask import Flask, jsonify, request
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
    print("starting the driver ...")
    options = webdriver.ChromeOptions()
        
    # disable save password popup
    options.add_argument("--password-store=basic")
    options.add_experimental_option(
        "prefs",
        {
            "credentials_enable_service": False,
            "profile.password_manager_enabled": False,
        },
    )
    

    driver = webdriver.Chrome(options=options, use_subprocess=True, version_main = 126 )
    driver.get("https://app.pluralsight.com/id")


    print("driver started")
    # Wait for the fields to be present and input text or click
    WebDriverWait(driver, 20).until(EC.presence_of_element_located((By.ID, "Username"))).send_keys(email)
    WebDriverWait(driver, 20).until(EC.presence_of_element_located((By.ID, "Password"))).send_keys(password)
    # WebDriverWait(driver, 20).until(EC.element_to_be_clickable((By.ID, "login"))).click()
    print("login clicked")
    

@app.route('/get_cookie', methods=['POST'])
def get_cookie():
    # email = "sami.belhadj@oddo-bhf.com"  # replace with dynamic value if needed
    # password = "7cB3MP.6y9.Z?c?"  # replace with dynamic value if needed

    data = request.get_json()
    email = data.get("email")
    password = data.get("password")
    if not email or not password:
        return jsonify({"error": "Email and password are required"}), 400
    
    print(email)
    print(password)

    print("before fetch_cookie")
    fetch_cookie(email, password)
    print("after fetch_cookie")
    # return a http response
    return {"message":"Cookie fetched successfully"}
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

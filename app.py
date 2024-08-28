import signal
import sys
from datetime import datetime, timedelta
from threading import Thread
from flask import Flask, jsonify, request
from flask_cors import CORS
import undetected_chromedriver as webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import NoSuchWindowException
import time
import requests
from requests.exceptions import RequestException
import warnings
from urllib3.exceptions import InsecureRequestWarning
import logging
from start import start

# Suppress InsecureRequestWarning
warnings.simplefilter('ignore', InsecureRequestWarning)
# requests.packages.urllib3.add_stderr_logger()

app = Flask(__name__)
CORS(app)  # Enable CORS for all routes
# Global variable to store the WebDriver instance
driver = None
licenceId = None
endTime = None
stopChecking = False



def open_driver(email, password):
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

    options.add_argument("--disable-gpu")
    
    driver = webdriver.Chrome(options=options, use_subprocess=True, version_main=128)
    driver.get("https://app.pluralsight.com/id")

    print("driver started")
    # Wait for the fields to be present and input text or click
    WebDriverWait(driver, 20).until(EC.presence_of_element_located((By.ID, "Username"))).send_keys(email)
    WebDriverWait(driver, 20).until(EC.presence_of_element_located((By.ID, "Password"))).send_keys(password)
    # WebDriverWait(driver, 20).until(EC.element_to_be_clickable((By.ID, "login"))).click()

    print("login clicked")

@app.route('/open', methods=['POST'])
def open_pluralsight():
    print("open pluralsight request received")
    global licenceId, endTime, stopChecking
    data = request.get_json()
    unformattedEndTime= data.get("endTime")
    endTime = datetime.fromisoformat(unformattedEndTime[:23])
    email = data.get("email")
    password = data.get("password")
    licenceId = data.get("licenceId")
    print("endtime:",endTime)
    if not email or not password:
        return jsonify({"error": "Email and password are required"}), 400
    open_driver(email, password)
    response = jsonify({"message": "pluralsight opened"})
    response.status_code = 200
    response.headers['Custom-Header'] = 'Header-Value'
    stopChecking = False
    Thread(target = background_timeLeft, daemon=True).start()
    return response

@app.route('/close', methods=['GET'])
def close():
    global stopChecking, endTime, driver, licenceId
    print("close request received")
    if driver:
        driver.close()
        driver.quit()
        driver = None
        endTime = None      
        licenceId = None
        stopChecking=True
        print("Browser closed")
        return {"message": "Browser closed"}
    else:
        return {"message": "No browser to close"}, 400
    
@app.route('/extend', methods=['GET'])
def extend():
    global endTime
    print("extend request received")
    endTime= datetime.now() + timedelta(hours=2)
    print("endtime:",endTime)
    return jsonify({"message":"End time extended successfully"}),200

# Background task to automatically close the session
def background_timeLeft():     
    global endTime, licenceId, stopChecking, driver
    while not stopChecking:
        print("time left: ", endTime-datetime.now())
        if endTime and datetime.now() >= endTime:
            automatic_close()
            endTime = None      # Reset endTime after closing
            stopChecking=True
        # check if the browser has been closed by the user:
        if driver and is_browser_closed(driver):
            print("Browser closed by user")
            driver = None
            stopChecking=True
            automatic_close()
        time.sleep(10)  # Check every 10 seconds

def automatic_close():
    global driver, licenceId
    if driver:
        print("closing driver ...")
        driver.close()
        driver.quit()
        print("Browser closed")
    backend_url =  f"https://localhost:7189/api/Licence/return/{licenceId}"
    try:
        print("sending request to ", backend_url)
        response = requests.post(backend_url, verify=False, json={"isBrowserClosed": True}) 
        response.raise_for_status()
        print("licence returned successfully") 
        licenceId = None
        driver = None
    except RequestException as e:
        print(f"error: {e}")
        if response is not None:
            print(f"Response content: {response.content}")

def is_browser_closed(driver):
    try:
        # Try accessing something in the browser
        driver.current_url
        return False  # Browser is still open
    except NoSuchWindowException:
        return True  # Browser is closed


def shutdown_handler(signal, frame):
    global licenceId
    print("Detected kill signal, shutting down...")
    if licenceId:
        automatic_close()
    if driver:
        print("closing driver ...")
        driver.close()
        driver.quit()
        print("Browser closed")
    sys.exit(0) # Register signal handlers 
 
signal.signal(signal.SIGINT, shutdown_handler) # Handle Ctrl+C 
signal.signal(signal.SIGTERM, shutdown_handler) # Handle termination signal

if __name__ == '__main__':
    # response = start()
    app.run(debug=True, use_reloader=False)



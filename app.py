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
import time
import subprocess
import requests
import webbrowser
from requests.exceptions import RequestException
import warnings
from urllib3.exceptions import InsecureRequestWarning
import logging
# Suppress InsecureRequestWarning

warnings.simplefilter('ignore', InsecureRequestWarning)
requests.packages.urllib3.add_stderr_logger()

app = Flask(__name__)
CORS(app)  # Enable CORS for all routes
# Global variable to store the WebDriver instance
driver = None
licenceId = None
endTime = None
stopChecking = False



def fetch_cookie(email, password):
    global driver
    print("starting the driver ...")
    options = webdriver.ChromeOptions()

    options.add_experimental_option("debuggerAddress", "localhost:9250")
        
    # disable save password popup
    options.add_argument("--password-store=basic")
    options.add_experimental_option(
        "prefs",
        {
            "credentials_enable_service": False,
            "profile.password_manager_enabled": False,
        },
    )
    
    driver = webdriver.Chrome(options=options, use_subprocess=True, version_main=126)
    driver.get("https://app.pluralsight.com/id")

    print("driver started")
    # Wait for the fields to be present and input text or click
    # WebDriverWait(driver, 20).until(EC.presence_of_element_located((By.ID, "Username"))).send_keys(email)
    # WebDriverWait(driver, 20).until(EC.presence_of_element_located((By.ID, "Password"))).send_keys(password)
    print("login clicked")

@app.route('/get_cookie', methods=['POST'])
def get_cookie():
    global licenceId
    global endTime
    data = request.get_json()
    email = data.get("email")
    password = data.get("password")
    licenceId = data.get("licenceId")
    endTime= data.get("formattedEndTime")
    print("licenceId:",licenceId)
    print("endtime:",endTime)
    if not email or not password:
        return jsonify({"error": "Email and password are required"}), 400
    
    print(email)
    print(password)

    print("before fetch_cookie")
    fetch_cookie(email, password)
    print("after fetch_cookie")
    
    response = jsonify({"message": "pluralsight opened"})
    response.status_code = 200
    response.headers['Custom-Header'] = 'Header-Value'
    # Thread(target = automatic_close_task, daemon=True).start()
    return response
    # automatic_close_task()


@app.route('/close', methods=['GET'])
def close():
    print("close request received")
    global driver
    if driver:
        driver.quit()
        driver = None
        print("Browser closed")
        return {"message": "Browser closed"}
    else:
        return {"message": "No browser to close"}, 400

def start_ngrok():
    # Start ngrok tunnel
    ngrok = subprocess.Popen(['./ngrok.exe', 'http', '5000'])
    
    # Allow some time for ngrok to initialize
    time.sleep(5)
    
    # Fetch the ngrok public URL
    ngrok_url = requests.get('http://localhost:4040/api/tunnels').json()['tunnels'][0]['public_url']
    return ngrok_url


def start():
    # Open the Angular application with the ngrok URL as a query parameter
    # angular_url = f"http://localhost:4200/?ngrokUrl={ngrok_url}"
    angular_url = f"http://localhost:4200"
    webbrowser.open(angular_url)
    return "Angular application opened", 200

# Background task to automatically close the session
def automatic_close_task():     
    global endTime, licenceId, stopChecking
    formattedTime = datetime.fromisoformat(endTime[:23])+timedelta(minutes=5)
    while not stopChecking:
        print("time left: ", formattedTime-datetime.now())
        if endTime and datetime.now() >= formattedTime:
            automatic_close(licenceId)
            endTime = None      # Reset endTime after closing
            stopChecking=True
        time.sleep(10)  # Check every 10 seconds

def automatic_close(id):
    global driver
    backend_url =  f"https://localhost:7189/api/Licence/{id}/return"
    print("sending close request to ", backend_url)
    try:
        response = requests.get(backend_url, verify=False) 
        response.raise_for_status()
        print("browser closed") 
    except RequestException as e:
        print(f"error: {e}")

def shutdown_handler(signal, frame):
    global licenceId
    print("Shutting down server...")
    if licenceId:
        print("sending logout request...")
        automatic_close(licenceId)
        time.sleep(10)
    if driver:
        print("closing driver ...")
        driver.quit()
    sys.exit(0) # Register signal handlers 
 
signal.signal(signal.SIGINT, shutdown_handler) # Handle Ctrl+C 
signal.signal(signal.SIGTERM, shutdown_handler) # Handle termination signal

if __name__ == '__main__':
    # Start ngrok and notify the remote server
    # ngrok_url = start_ngrok()
    # Thread(target = automatic_close_task, daemon=True).start()
    # response = start()
    # print(f"Ngrok URL sent to remote server ")
    response= requests.get("https://localhost:7189/api/Licence/", verify=False)
    print(response)
    app.run(debug=True, use_reloader=False)

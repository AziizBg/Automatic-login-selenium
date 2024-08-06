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

app = Flask(__name__)
CORS(app)  # Enable CORS for all routes
# Global variable to store the WebDriver instance
driver = None

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
    WebDriverWait(driver, 20).until(EC.presence_of_element_located((By.ID, "Username"))).send_keys(email)
    WebDriverWait(driver, 20).until(EC.presence_of_element_located((By.ID, "Password"))).send_keys(password)
    print("login clicked")

@app.route('/get_cookie', methods=['POST'])
def get_cookie():
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
    
    response = jsonify({"message": "pluralsight opened"})
    response.status_code = 200
    response.headers['Custom-Header'] = 'Header-Value'
    return response

@app.route('/close', methods=['GET'])
def close():
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
    ngrok = subprocess.Popen(['C:/Users/weszi/Downloads/ngrok-v3-stable-windows-amd64/ngrok.exe', 'http', '5000'])
    
    # Allow some time for ngrok to initialize
    time.sleep(5)
    
    # Fetch the ngrok public URL
    ngrok_url = requests.get('http://localhost:4040/api/tunnels').json()['tunnels'][0]['public_url']
    return ngrok_url


def start():
    # Open the Angular application with the ngrok URL as a query parameter
    angular_url = f"http://localhost:4200/?ngrokUrl={ngrok_url}"
    webbrowser.open(angular_url)
    return "Angular application opened", 200

if __name__ == '__main__':
    # Start ngrok and notify the remote server
    ngrok_url = start_ngrok()
    response = start()
    print(f"Ngrok URL sent to remote server ")
    app.run(debug=True)

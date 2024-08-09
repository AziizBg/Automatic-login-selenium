import time
import subprocess
import requests
import webbrowser


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
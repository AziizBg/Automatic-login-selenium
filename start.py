import webbrowser

def start():
    # Open the Angular application 
    angular_url = f"http://localhost:4200"
    webbrowser.open(angular_url)
    return "Angular application opened", 200
import requests

try:
    # Test home page
    response = requests.get("http://127.0.0.1:3000/")
    print(f"Home page status: {response.status_code}")
    
    # Test messages page
    response = requests.get("http://127.0.0.1:3000/messages")
    print(f"Messages page status: {response.status_code}")
    
except Exception as e:
    print(f"Error: {e}")

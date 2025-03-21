import requests
from bs4 import BeautifulSoup

try:
    # Test simple messages page
    response = requests.get("http://127.0.0.1:3000/messages_simple")
    print(f"Messages Simple status: {response.status_code}")
    
    # Test regular messages page
    response = requests.get("http://127.0.0.1:3000/messages")
    print(f"Messages status: {response.status_code}")
    
    if response.status_code == 200:
        # Parse the HTML
        soup = BeautifulSoup(response.text, 'html.parser')
        print(f"Page Title: {soup.title.string}")
    else:
        print(f"Error content: {response.text}")
        
except Exception as e:
    print(f"Error: {e}")

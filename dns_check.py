import requests
from bs4 import BeautifulSoup
import argparse

def check_meta_tag(url):
    try:
        # User-Agent-sträng för Mac Chrome-webbläsare
        headers = {
            "User-Agent": (
                "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
                "AppleWebKit/537.36 (KHTML, like Gecko) "
                "Chrome/116.0.5845.111 Safari/537.36"
            )
        }
        
        # Skicka GET-förfrågan med User-Agent
        response = requests.get(url, headers=headers, timeout=10)
        response.raise_for_status()  # Kontrollera om förfrågan var framgångsrik
        
        # Parsar HTML med BeautifulSoup
        soup = BeautifulSoup(response.text, 'html.parser')
        
        # Hitta meta-tagg med name="currentNode"
        meta_tag = soup.find('meta', attrs={'name': 'currentNode'})
        
        if meta_tag:
            content = meta_tag.get('content', '')
            if "green" in content.lower():
                print("green")
            elif "blue" in content.lower():
                print("blue")
            else:
                print("Neither GREEN nor BLUE found in content. Found:", content)
        else:
            print('Meta tag with name="currentNode" not found.')
    
    except requests.exceptions.RequestException as e:
        print(f"Error while making the request: {e}")

if __name__ == "__main__":
    # Hantera kommandoradsargument
    parser = argparse.ArgumentParser(description="Check meta tag for green or blue status.")
    parser.add_argument("url", help="The URL to check.")
    args = parser.parse_args()
    
    # Kör funktionen med den angivna URL:en
    check_meta_tag(args.url)


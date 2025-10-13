import requests
import bs4 # BeautifulSoup4

# Source: https://www.slingacademy.com/article/extract-all-links-from-a-webpage-using-python-and-beautiful-soup/

base_url = 'https://www.britannica.com/'

# Fetch all the HTML source from the url

# Parse HTML and extract links

def get_first_link(url):
    # Follow the link
    response = requests.get(URL)
    
    soup = bs4.BeautifulSoup(response.text, 'html.parser')
    links = soup.select('a')
    for link in links:
        if link.get('href') != None:
            if 'https://' in link.get('href'):
                return link.get('href')
            else:
                return base_url + link.get('href') # Convert relative URL to absolute URL

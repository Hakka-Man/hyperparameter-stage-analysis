import requests
from bs4 import BeautifulSoup

headers = {
    "User-Agent":
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_13_6) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/80.0.3987.87 Safari/537.36"
}


def getTicker(name):
    page = requests.get(
        "https://www.google.com/search?q="+name+"+stock",
        headers=headers)
    soup = BeautifulSoup(page.content, 'html.parser')
    ticker = soup.find('div', attrs={'class': "HfMth PZPZlf"})
    return ticker.get_text().split(" ")[1]
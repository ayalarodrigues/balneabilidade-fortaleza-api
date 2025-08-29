import requests
from bs4 import BeautifulSoup

url_base = "https://www.semace.ce.gov.br/boletim-de-balneabilidade/"
res = requests.get(url_base)
soup = BeautifulSoup(res.text, "html.parser")

links = [a['href'] for a in soup.find_all('a', href=True)]
print("Total de links encontrados:", len(links))

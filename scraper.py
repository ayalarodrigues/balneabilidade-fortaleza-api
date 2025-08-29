import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin

# --- Baixar o boletim mais recente da Sema ---
url_base = "https://www.semace.ce.gov.br/boletim-de-balneabilidade/"
res = requests.get(url_base)
soup = BeautifulSoup(res.text, "html.parser")

links_boletim = [
    a['href'] for a in soup.find_all('a', href=True) #percorre todas as tags <a> que possuem atributo href e guarda apenas o valor do link (URL)
    if "Boletim das Praias de Fortaleza" in a.get_text() #link do boletim correspondente á cidade de Fortaleza
]

if not links_boletim:
    raise ValueError("Nenhum boletim encontrado.")

ultimo_boletim_url = urljoin(url_base, links_boletim[0])
print("Último boletim:", ultimo_boletim_url)

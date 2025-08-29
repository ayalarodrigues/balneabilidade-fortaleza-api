import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin
import pdfplumber

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


#--- Baixar o arquivo .pdf ---
res = requests.get(ultimo_boletim_url, stream=True) #faz uma requisição HTTP para baixar o arquivo PDF do boletim
arquivo_pdf = "boletim_fortaleza.pdf"
with open(arquivo_pdf, "wb") as f:
    for chunk in res.iter_content(8192): #8192 = 8KB por vez
        #o arquivo é baixo em partes(chunks) para evitar que seja carregado todo de uma vez na memória
        f.write(chunk)

print(f"PDF salvo em {arquivo_pdf}")


arquivo_pdf = "boletim_fortaleza.pdf"

with pdfplumber.open(arquivo_pdf) as pdf:
    texto_pg1 = pdf.pages[0].extract_text() #extrai o texto da primeira página do pdf
    print("Texto da primeira página:", texto_pg1[:200])  # só primeiros 200 chars

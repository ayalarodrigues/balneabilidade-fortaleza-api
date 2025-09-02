import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin
import pdfplumber
import unicodedata
from datetime import datetime, timedelta
import camelot
import pandas as pd

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
#print("Último boletim:", ultimo_boletim_url)


#--- Baixar o arquivo .pdf ---
res = requests.get(ultimo_boletim_url, stream=True) #faz uma requisição HTTP para baixar o arquivo PDF do boletim
arquivo_pdf = "boletim_fortaleza.pdf"
with open(arquivo_pdf, "wb") as f:
    for chunk in res.iter_content(8192): #8192 = 8KB por vez
        #o arquivo é baixo em partes(chunks) para evitar que seja carregado todo de uma vez na memória
        f.write(chunk)

print(f"PDF salvo em {arquivo_pdf}")


#--- Extração de metadados ---

arquivo_pdf = "boletim_fortaleza.pdf"

with pdfplumber.open(arquivo_pdf) as pdf:
    texto_pg1 = pdf.pages[0].extract_text()
    texto_pg1 = " ".join(texto_pg1.split())  # tudo em uma linha

periodo = ""
numero_boletim = ""
tipos_amostragem = ""

if "Nº" in texto_pg1 and "Período:" in texto_pg1 and "Tipos de amostras:" in texto_pg1:
    bol_index = texto_pg1.find("Nº")
    per_index = texto_pg1.find("Período:", bol_index)
    tipos_index = texto_pg1.find("Tipos de amostras:", per_index)

    numero_boletim = texto_pg1[bol_index + 2:per_index].strip()
    periodo = texto_pg1[per_index + len("Período:"):tipos_index].strip()

    # pega só até o primeiro ponto final (.)
    resto = texto_pg1[tipos_index + len("Tipos de amostras:"):].strip()
    tipos_amostragem = resto.split(".")[0].strip()

# gera lista de dias a partir do período
dias_periodo = expand_periodo(periodo)
data_extracao = datetime.today().strftime("%Y-%m-%d")


# --- Remove acentos e sinais de uma string ---
def strip_accents(s: str) -> str:
    return "".join(c for c in unicodedata.normalize("NFD", s) if unicodedata.category(c) != "Mn") # filtra apenas os caracteres que não são marcas de acento (categoria Mn = Mark, Nonspacing)

# normaliza a string para a forma NFD (Normalization Form Decomposition),
# que decompõe caracteres acentuados em caractere base + acento.
# Exemplo: "á" -> "a" + "´"


# --- Classificação das zonas com base no nome das praias ----
def classify_zona(nome: str) -> str:
    """Classifica a zona da praia com base no nome"""
    n = strip_accents((nome or "").lower())
    leste_kw = ["futuro", "caca e pesca", "abreulandia", "sabiaguaba", "titanzinho"]
    centro_kw = ["iracema", "meireles", "mucuripe", "volta da jurema", "beira mar", "estressados"]
    oeste_kw = ["barra do ceara", "pirambu", "cristo redentor", "leste oeste", "formosa", "colonia"]

    if any(k in n for k in leste_kw): return "Leste"
    if any(k in n for k in centro_kw): return "Centro"
    if any(k in n for k in oeste_kw): return "Oeste"
    return "Desconhecida"

print(classify_zona("Praia do Pirambu"))


#--- Recebe um período e define os dias dentro dele ---
def expand_periodo(periodo_str: str):
    try:
        #divide a string pelo "a" que separa as datas
        #exemplo: "11/08/2025 a 17/08/2025" -> ["11/08/2025", "17/08/2025"]
        inicio_str, fim_str = [p.strip() for p in periodo_str.split("a")]

        #converte as strings de data para objetos datetime
        dt_inicio = datetime.strptime(inicio_str, "%d/%m/%Y")
        dt_fim = datetime.strptime(fim_str, "%d/%m/%Y")
        
        #cria uma lista para armazenar as datas do período
        dias = []
        #começa a partir da data inicial
        atual = dt_inicio

        #enquanto a data atual for menor ou igual à data final
        while atual <= dt_fim:

            #converte a data atual para string no formato "YYYY-MM-DD"
            dias.append(atual.strftime("%Y-%m-%d"))
             #incrementa um dia
            atual += timedelta(days=1)
        return dias
        #retorna a lista de todas as datas no período
    except Exception:
        return []

#print(expand_periodo("11/08/2025 a 17/08/2025"))

# --- Extração das tabelas ---
arquivo_pdf = "boletim_fortaleza.pdf"

#extrai todas as tabelas do boletim
tables = camelot.read_pdf(arquivo_pdf, pages="1-end", flavor="stream")
print("Total de tabelas encontradas:", len(tables))

#exibe as primeiras linhas da primeira tabela
if tables:
    print(tables[0].df.head())


#--- Filtragem de dados da tabela e normalização ---

#limpezado dos status em 'P' ou 'I'
def clean_status_token(tok: str) -> str:

    #remove espaços extras e converte para maiúscula
    tok = tok.strip().upper()
    #retorna apenas se for P (Própria) ou I (Imprópria), caso contrário retorna vazio
    return tok if tok in ("P", "I") else ""

#verifica se a linha é ruído (não contém informação válida de praia)
def is_noise_row(nome: str, status: str) -> bool:
    #junta nome e status em uma string só (em minúsculo)
    txt = f"{str(nome)} {str(status)}".lower()
    #palavras-chave que indicam linha inútil (títulos, rodapés, cabeçalhos, etc.)
    noise_terms = ["nome", "status", "trecho", "ponto", "boletim", "semace"]
    #se a linha tiver menos de 3 caracteres, é descartada
    if len(txt.strip()) < 3:
        return True
    #se tiber qualquer palavra de ruído, também é descartada
    return any(term in txt for term in noise_terms)


#lista para acumular dfs
dfs_norm = []

#iteração sobre todas as tabelas detectadas pelo Camelot
for t in tables:
    df_raw = t.df.copy()  #copia a tabela bruta
    if df_raw.shape[1] < 2:
        continue  #ignora tabelas inválidas com menos de 2 colunas

    #mantém apenas as duas primeiras colunas (Nome e Status)
    df_raw = df_raw.iloc[:, :2]
    df_raw.columns = ["Nome", "Status"]

    linhas = []  #lista para armazenar os registros válidos

    #percorre cada linha da tabela
    for _, row in df_raw.iterrows():
        #quebra o campo "Nome" em várias linhas (caso contenha "\n") e remove espaços extras
        nomes = [x.strip() for x in row["Nome"].split("\n") if x.strip()]
        #faz o mesmo para "Status", limpando os tokens com clean_status_token
        status_tokens = [clean_status_token(x) for x in row["Status"].split("\n")]
        status_tokens = [x for x in status_tokens if x]  # remove vazios

        #caso não não tem nome ou status, pula a linha
        if not nomes or not status_tokens:
            continue

        #isso aqui é para corrigir um caso em que vários status apareciam para uma única linha; 
        #um único status para várias praias (ex: várias linhas de nomes, mas só um "P")
        if len(status_tokens) == 1 and len(nomes) > 1:
            for n in nomes:
                if not is_noise_row(n, status_tokens[0]):
                    linhas.append({"Nome": n, "Status": status_tokens[0]})
        else:
            #caso mais comum: cada nome tem um status correspondente
            #verificar esse zip
            for n, s in zip(nomes, status_tokens):
                if not is_noise_row(n, s):
                    linhas.append({"Nome": n, "Status": s})

    #se encontrou linhas válidas nessa tabela, adiciona ao conjunto
    if linhas:
        dfs_norm.append(pd.DataFrame(linhas))

#junta todos os dfs das tabelas em um só
df = pd.concat(dfs_norm, ignore_index=True) if dfs_norm else pd.DataFrame(columns=["Nome","Status"])

#teste
print(df.head())



# --- Limpar campo 'Nome' ----

#remove espaços extras entre palavras do nome da praia
#exemplo: "  Praia   do Futuro " -> "Praia do Futuro"  esse caso de fato ocorre na tabela do pdf
df["Nome"] = df["Nome"].apply(lambda x: " ".join(x.split())) #função anônima = pensada para a disciplina de programação funcional


# --- Adicionar informações extras ---

# criauma nova coluna "Zona" a partir da função classify_zona
# exemplo: "Praia do Futuro" -> "Leste"
df["Zona"] = df["Nome"].apply(classify_zona)


#coloca na coluna "Periodo" o período do boletim coletado (ex: "11/08/2025 a 17/08/2025")
df["Periodo"] = periodo

#expande o período em uma lista de dias e salva em string
#a mesma lista de dias é repetida para todas as praias (len(df) vezes)
df["Dias_Periodo"] = [", ".join(expand_periodo(periodo))] * len(df)



# ---Traduz status ---
#cnverte "P" em "Própria para banho" e "I" em "Imprópria para banho"
df["Status"] = df["Status"].map({
    "P": "Própria para banho",
    "I": "Imprópria para banho"
})

# ---Adiciona metadados ---
#número do boletim atual
df["Numero_Boletim"] = numero_boletim

#tipo de amostragem (informação que a Semace traz no PDF)
df["Tipos_Amostragem"] = tipos_amostragem

#daata em que o script foi executado (extração)
df["Data_Extracao"] = datetime.today().strftime("%Y-%m-%d")



#cria uma coluna "id" com números sequenciais (1, 2, 3, ...)
#e insere essa coluna na primeira posição do DataFrame
df.insert(0, "id", range(1, len(df) + 1))


#teste
print(df.head(10))

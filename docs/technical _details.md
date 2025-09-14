# Detalhes Técnicos do Projeto

Esta seção contém informações complementares que são impórtantes para a compreensão da arquitetura, das decisões de projeto e do funcionamento interno da aplicação.

### Detalhamento do Processo de Web Scraping (`scraper.py`)
O `scraper.py` é o componente responsável pela coleta automatizada dos dados da SEMACE. Seu funcionamento ocorre nos seguintes passos:

1.  **Busca do Boletim:** O script acessa a página de boletins da SEMACE e, usando `BeautifulSoup`, analisa o HTML para encontrar o link do PDF do boletim mais recente de Fortaleza.
2.  **Download do PDF:** A URL encontrada é usada para baixar o arquivo `.pdf` e salvá-lo localmente.
3.  **Extração de Metadados:** Com a biblioteca `pdfplumber`, o script lê a primeira página do PDF para extrair informações textuais como o número do boletim e o período de validade.
4.  **Extração de Tabelas:** A biblioteca `camelot-py` é utilizada para identificar e extrair as tabelas de dados de dentro do PDF, convertendo-as para um formato com o qual o `pandas` pode trabalhar.
5.  **Limpeza e Normalização:** As tabelas extraídas são processadas para remover ruídos (cabeçalhos, rodapés), padronizar os dados (ex: 'P' para "Própria para banho") e corrigir inconsistências de formatação.
6.  **Enriquecimento dos Dados:** O script adiciona informações contextuais a cada registro, como a Zona (Leste, Centro, Oeste) e as coordenadas geográficas, buscando-as no módulo `coordenadas.py`.
7.  **Exportação:** Ao final do processo, um arquivo `boletim_fortaleza.csv` é gerado na raiz do projeto, e então é consumido pela API Flask.

### Estratégia de Testes (Pytest)
Conforme solicitado na atividade, o projeto inclui **testes unitários para os endpoints principais**, localizados no diretório `tests/`.
- **`test_app.py`**: Contém os casos de teste para cada uma das rotas da API. Ele valida tanto respostas de sucesso (código 200) quanto o tratamento de erros esperado para entradas inválidas (códigos 404, 400, etc.).
- **`conftest.py`**: É um arquivo de configuração do Pytest que fornece *fixtures* (como o cliente de teste do Flask) e *mocks*. Os mocks simulam as respostas das APIs externas, permitindo que os testes sejam executados de forma rápida e isolada, sem depender de uma conexão real com a internet.
- **Como executar os testes:**
  ```bash
  pytest -v


# API de Balneabilidade e Previsão do Tempo - Praias de Fortaleza

## Descrição

Este projeto consiste em uma **API RESTful** desenvolvida em **Python** com **Flask**, que realiza a integração de dois sistemas distintos para fornecer dados consolidados sobre as condições das praias de Fortaleza, Ceará. A API combina informações sobre a balneabilidade (qualidade da água para banho) com dados meteorológicos atualizados.

As fontes de dados integradas são:

* Superintendência Estadual do Meio Ambiente (SEMACE): Os dados de balneabilidade são obtidos através de um script de web scraping (scraper.py) que extrai e processa o boletim semanal mais recente diretamente do site da SEMACE.

* API Open-Meteo: Utilizando as coordenadas geográficas de cada praia, a aplicação consome a API externa Open-Meteo para obter previsões do tempo detalhadas, incluindo temperatura, velocidade do vento e altura das ondas.

## Objetivo do Trabalho

O objetivo principal deste projeto é desenvolver uma solução prática que demonstre as competências adquiridas na disciplina de Técnicas de Integração de Sistemas. Para isso, foi criada uma API RESTful que atende aos seguintes requisitos acadêmicos:

* Integrar no mínimo dois sistemas distintos: A solução integra dados públicos da SEMACE (via web scraping) com uma API externa de meteorologia (Open-Meteo).

* Desenvolver uma API funcional: Utilizando Python e Flask para criar endpoints que seguem os princípios da arquitetura REST.

* Documentar a solução: Criar uma documentação clara e detalhada, incluindo um README.md, rotas da API e uma coleção para testes no Postman.

* Garantir a qualidade do código: Implementar testes unitários automatizados para os principais endpoints da aplicação.

Este projeto está diretamente alinhado ao Objetivo de Desenvolvimento Sustentável (ODS) 11 da ONU: Cidades e Comunidades Sustentáveis.

A solução contribui especificamente para a Meta 11.7, que visa "proporcionar o acesso universal a espaços públicos seguros, inclusivos, acessíveis e verdes". As praias de Fortaleza são espaços públicos vitais para o lazer, turismo e bem-estar da comunidade.

Ao transformar dados públicos brutos (boletins em PDF) em informação acessível via API, o projeto capacita cidadãos e turistas a tomar decisões informadas sobre o uso desses espaços. Saber se uma praia está 'Própria' ou 'Imprópria' para banho, combinado com a previsão do tempo, promove a segurança e a saúde, permitindo que todos desfrutem da orla de Fortaleza de forma mais consciente e segura.

## Descrição funcional da solução

A API de Balneabilidade de Fortaleza é uma ferramenta que centraliza e fornece dados sobre as condições das praias da cidade. Do ponto de vista funcional, a solução permite que um usuário final (ou outra aplicação) realize as seguintes operações:

1. Consultar a Balneabilidade: Obter a lista de praias monitoradas pela Superintendência Estadual do Meio Ambiente (SEMACE), com o status atualizado de "Própria" ou "Imprópria" para banho.

2. Obter Previsão do Tempo: Para qualquer praia, solicitar dados meteorológicos detalhados para uma data futura, como temperatura, velocidade do vento e altura das ondas.

3. Filtrar Resultados: Pesquisar praias por zona geográfica (Leste, Centro, Oeste) ou por status de balneabilidade.

Para garantir que os dados sejam sempre recentes, a aplicação executa um *script* de *scraping* automaticamente ao ser iniciada, buscando o último boletim de balneabilidade disponível no site da SEMACE.

## Arquitetura da API

A arquitetura do projeto foi desenhada para integrar duas fontes de dados, seguindo o modelo requisição-resposta da arquitetura RESTful.

### Descrição da Arquitetura
1. **Sistema 1 (Dados de Balneabilidade)**: Um *script* (scraper.py) coleta os dados do site da SEMACE. Ele baixa o boletim em PDF, extrai as informações e as salva de forma estruturada em um arquivo local (boletim_fortaleza.csv).

2. **Núcleo da API (Orquestrador)**: A aplicação Flask (app.py) atua como o centro da solução. Ela lê os dados locais de balneabilidade e os expõe através de seus *endpoints*.

3. **Sistema 2 (Dados Meteorológicos)**: Quando um *endpoint* de previsão é acionado, a API Flask utiliza as coordenadas da praia para fazer uma requisição em tempo real à API externa **Open-Meteo**, buscando os dados de previsão.

4. **Consolidação**: A API combina as informações de balneabilidade e previsão do tempo em uma única resposta JSON e a entrega ao cliente.

### Considerações sobre as Fontes de Dados
Para a correta utilização da API, é fundamental compreender a periodicidade e a disponibilidade dos dados das fontes integradas:

* **Boletins da SEMACE (Balneabilidade)**: Os dados de balneabilidade são baseados nos boletins semanais da SEMACE. A API foi projetada para buscar e processar sempre o boletim mais recente disponível publicamente. Contudo, a própria SEMACE pode não atualizar os boletins em uma data rigorosamente fixa. Isso significa que pode haver um pequeno atraso na publicação, e o boletim mais recente pode ainda se referir à semana anterior. Se um usuário solicitar uma data para a qual o boletim ainda não foi liberado, a API retornará os dados do último período válido.

* **API Open-Meteo (Previsão do Tempo)**: A previsão do tempo é fornecida em tempo real pela API Open-Meteo. Esta API oferece previsões para uma janela de tempo limitada (geralmente até 16 dias no futuro a partir da data atual). Portanto, não é possível obter previsões para datas muito distantes ou para o passado através deste endpoint. Se uma data fora desse intervalo for solicitada, a API indicará que os dados de previsão não estão disponíveis.

### Diagrama da Arquitetura

```mermaid
graph LR
    %% Blocos principais
    subgraph "👤 Cliente"
        A[Usuário / Postman]
    end

    subgraph "🖥️ Backend (Flask)"
        B["API Flask<br/>src/app.py"]
    end

    subgraph "🌊 Sistema 1: Balneabilidade"
        D["Scraper<br/>src/scraper.py"]
        E["boletim_fortaleza.csv"]
    end

    subgraph "☀️ Sistema 2: Meteorologia"
        F[API Externa<br/>Open-Meteo]
    end

    %% Fonte externa SEMACE
    SEMACE["SEMACE<br/>Boletim de Balneabilidade"]

    %% Fluxo
    SEMACE -->|PDF| D
    D -->|Atualiza CSV| E
    B -->|Executa Scraper| D
    B -->|Lê CSV| E
    B -->|Requisição Previsão| F
    F -->|Retorna Dados Tempo| B
    A -->|Requisição HTTP| B
    B -->|Resposta JSON Consolidada| A





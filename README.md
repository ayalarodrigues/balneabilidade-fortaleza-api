<<<<<<< HEAD
=======
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
>>>>>>> 0f04c615c43ac4340761675c254b8db48b6c0504

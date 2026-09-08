# 🤖 WhatsApp RAG Chatbot with Flask, WAHA & Google Gemini or Groq com llama

Este repositório contém a solução completa de automação para um **Chatbot RAG (Retrieval-Augmented Generation)** no WhatsApp. O sistema utiliza a API do **WAHA (WhatsApp HTTP API)** para integração com o WhatsApp, **Flask** para orquestração de webhooks, **ChromaDB** como banco de dados vetorial local, **LangChain** para RAG e o modelo **Google Gemini** ou **Groq com llama** para geração de respostas inteligentes baseadas na base de conhecimento.

---

## 🏗️ Arquitetura do Sistema

![](https://pickle-reading-bd9.notion.site/image/https%3A%2F%2Fprod-files-secure.s3.us-west-2.amazonaws.com%2F17354937-4524-429d-83e0-cf764a3a7c06%2F5fe3575c-b79e-463d-abe2-d2ee81394e0b%2Fimage.png?table=block&id=11e9956f-3dc9-815a-825d-c7752de8bf75&spaceId=17354937-4524-429d-83e0-cf764a3a7c06&width=2000&userId=&cache=v2&imgBuildSrc=requestProxiedImageUrl)

## 🛠️ Tecnologias Utilizadas

---

- **Linguagem:** Python 3.11+
- **Framework Web:** Flask
- **WhatsApp Engine:** WAHA (`NOWEB` Engine)
- **Framework RAG:** LangChain, `langchain-text-splitters`, `langchain-huggingface`
- **Embeddings:** `sentence-transformers/all-MiniLM-L6-v2`
- **Vector Database:** ChromaDB (Persistente)
- **Leitor de Documentos:** PyPDF
- **LLM:** Google Gemini API ou Groq llama
- **Containerização:** Docker e Docker Compose

---

## 📂 Estrutura do Projeto

```
automacao_waha/
├── app.py                  # Servidor Flask principal e manipulador de Webhooks
├── bot/
│   ├── __init__.py
│   └── ai_bot.py           # Lógica do RAG, integração com ChromaDB e Gemini
├── services/
│   ├── __init__.py
│   └── waha.py             # Cliente de comunicação com os endpoints da API WAHA
├── rag/
│   ├── rag.py              # Script de ingestão, chunking e indexação de PDFs
│   └── data/               # Diretório contendo os arquivos PDF da base de conhecimento
├── chroma_data/            # Volume persistente do banco de dados vetorial ChromaDB
├── docker-compose.yml      # Configuração dos serviços Docker (WAHA + Flask App)
├── Dockerfile              # Dockerfile da aplicação Flask/Python
└── requirements.txt        # Dependências do projeto Python
```

## 📦 Dependências (requirements.txt)

```
flask
requests
google-generativeai
langchain
langchain-community
langchain-text-splitters
langchain-huggingface
sentence-transformers
pypdf
chromadb
```

## 🚀 Como Executar o Projeto

1. Pré-requisitos
   Docker e Docker Compose instalados no servidor/máquina.

Chave de API do Google Gemini (GEMINI_API_KEY).

2. Configuração do Arquivo docker-compose.yml version: YAML'3.8'

```Python
services:
  waha:
    image: devlikeapro/waha:latest
    container_name: waha
    restart: always
    environment:
      - WAHA_ENGINE=NOWEB
      - WAHA_PRINT_QR=true
    ports:
      - "3000:3000"

  wppbotapi:
    build: .
    container_name: wppbotapi
    restart: always
    ports:
      - "5000:5000"
    environment:
      - WAHA_API_URL=http://waha:3000
      - WAHA_API_KEY=
      - GEMINI_API_KEY=SUA_CHAVE_GEMINI_AQUI
    volumes:
      - .:/app
      - chroma_data:/app/chroma_data
    depends_on:
      - waha

volumes:
  chroma_data:
```

3. Inicialização dos Containers
   Suba os serviços utilizando o Docker Compose:

Bash

```Shell
docker compose up -d --build
```

4. Conectar ao WhatsApp (QR Code)
   Acesse o painel ou veja os logs do container do WAHA:

Bash

```Shell
docker logs -f waha
```


Escaneie o QR Code gerado no terminal utilizando seu aplicativo do WhatsApp.

5. Ingestão da Base de Conhecimento (RAG)
   Insira os arquivos .pdf contendo as informações da empresa/atendimento dentro da pasta rag/documentos/.

Execute o script de geração de embeddings e população do vetor ChromaDB dentro do container:

Bash

```Shell
docker exec -it wppbotapi python3 /app/rag/rag.py
```


## 🛡️ Licença e Boas Práticas

* Mantenha suas chaves de API (`GEMINI_API_KEY` e `WAHA_API_KEY`) protegidas em variáveis de ambiente.
* Não envie requisições em massa sem intervalo de tempo para evitar bloqueios ou banimento do número no WhatsApp.

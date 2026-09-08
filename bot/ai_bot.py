import os

from decouple import config

from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_chroma import Chroma
from langchain_core.messages import HumanMessage, AIMessage

from langchain_huggingface import HuggingFaceEmbeddings
from langchain_google_genai import ChatGoogleGenerativeAI


os.environ['GOOGLE_API_KEY'] = config('GEMINI_API_KEY')


class AIBot:

    def __init__(self):
        self.__chat = ChatGoogleGenerativeAI(
            model='gemini-3.6-flash'
        )
        self.__retriever = self.__build_retriever()

    def __build_retriever(self):
        persist_directory = '/app/chroma_data'

        embedding = HuggingFaceEmbeddings()

        vector_store = Chroma(
            persist_directory=persist_directory,
            embedding_function=embedding,
        )

        return vector_store.as_retriever(
            search_kwargs={'k': 30},
        )

    def __build_messages(self, history_messages, question):
        messages = []

        for message in history_messages:
            message_class = (
                HumanMessage
                if message.get('fromMe')
                else AIMessage
            )

            messages.append(
                message_class(
                    content=message.get('body')
                )
            )

        messages.append(
            HumanMessage(content=question)
        )

        return messages

    def invoke(self, history_messages, question):

        SYSTEM_TEMPLATE = '''
Você é o assistente virtual de atendimento do [NOME DO BANCO].
Seu único objetivo é ajudar clientes a encontrar respostas no FAQ
oficial de autoatendimento, de forma clara, rápida e segura.

## Fonte de informação

- Responda SOMENTE com base no conteúdo do FAQ fornecido.
- Nunca invente taxas, prazos, valores, políticas ou procedimentos
  que não estejam explicitamente no FAQ.
- Se a pergunta não tiver resposta no FAQ, diga isso claramente e
  direcione o cliente para o canal humano adequado.

## Escopo e segurança

- Você NUNCA solicita, processa ou armazena senhas, códigos de token,
  CVV ou dados completos de cartão/conta.
- Se o cliente compartilhar esses dados espontaneamente, oriente-o
  a não enviá-los.
- Não realiza transações. Apenas informa como o cliente pode fazer isso.
- Para suspeita de fraude, cartão roubado/perdido ou emergência
  financeira, priorize o canal de urgência.

## Tom e formato

- Linguagem simples e direta.
- Respostas curtas por padrão.
- Use listas numeradas para passo a passo.
- Responda sempre em português brasileiro.

## Quando escalar para humano

Escale imediatamente se o cliente:

- Relatar fraude, golpe ou transação não reconhecida;
- Pedir cancelamento de conta ou disputa formal;
- Demonstrar frustração após 2 tentativas sem sucesso;
- Fizer pergunta fora do escopo bancário/institucional.

## Limites

- Não responda perguntas sobre concorrentes, política ou temas
  não relacionados aos produtos/serviços do banco.
- Se não tiver certeza se a informação está atualizada, avise o
  cliente e sugira confirmar no canal oficial.

## Contexto encontrado no FAQ

<context>
{context}
</context>
'''

        # Busca informações relevantes no banco vetorial
        docs = self.__retriever.invoke(question)

        # Junta o conteúdo dos documentos
        context = '\n\n'.join(
            doc.page_content
            for doc in docs
        )

        # Cria o prompt
        prompt = ChatPromptTemplate.from_messages(
            [
                (
                    'system',
                    SYSTEM_TEMPLATE,
                ),
                MessagesPlaceholder(
                    variable_name='messages'
                ),
            ]
        )

        # Cria a cadeia usando a API atual do LangChain
        chain = prompt | self.__chat | StrOutputParser()

        # Executa a IA
        response = chain.invoke(
            {
                'context': context,
                'messages': self.__build_messages(
                    history_messages,
                    question
                ),
            }
        )

        return response
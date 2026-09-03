import os

from decouple import config

from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import PromptTemplate
from langchain_google_genai import ChatGoogleGenerativeAI


os.environ['GOOGLE_API_KEY'] = config('GEMINI_API_KEY')


class AIBot:

    def __init__(self):
        self.__chat = ChatGoogleGenerativeAI(model='gemini-3.6-flash')

    def invoke(self, question):
        prompt = PromptTemplate(
            input_variables=['texto'],
            template='''
            Você é um tradutor de textos que traduz o texto do usuário para ingles.
            <texto>
            {texto}
            </texto>
            '''
        )
        chain = prompt | self.__chat | StrOutputParser()
        response = chain.invoke({
            'texto': question,
        })
        return response
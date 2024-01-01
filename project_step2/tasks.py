from langchain_core.runnables.base import Runnable
from langchain_core.output_parsers import StrOutputParser
from langchain.chat_models import ChatOpenAI
from langchain.prompts import (
    ChatPromptTemplate,
    SystemMessagePromptTemplate,
    HumanMessagePromptTemplate
)

class ClassifyMessage(Runnable):
    def generate_chat_template(self):
        chat_template = ChatPromptTemplate.from_messages([
            SystemMessagePromptTemplate.from_template(
                "You are a helpful assitant who works for a software service"
                "provider named '카카오'.  Your job is to answer questions "
                "about a service named '카카오싱크'."
            ),
            HumanMessagePromptTemplate.from_template(
                "Below is a service documentation for '카카오싱크':\n"
                "\n"
                "{kakaosync_documentation}\n"
                "\n"
                "The user has sent the following message:\n"
                "\n"
                "Message: {user_message}\n"
                "\n"
                "If the message is not a question, say 'generic'. If the "
                "message is a question about '카카오싱크' and can be "
                "answered using the documentation above, say 'question'. If "
                "the question cannot be answered, say 'deny'."
            )
        ])
        return chat_template

    def invoke(self, input, config=None):
        chain = (
            self.generate_chat_template()
            | ChatOpenAI(temperature=0.8)
            | StrOutputParser()
        )
        return chain.invoke(input, config)

class AnswerQuestion(Runnable):
    def generate_chat_template(self):
        chat_template = ChatPromptTemplate.from_messages([
            SystemMessagePromptTemplate.from_template(
                "You are a helpful assitant who works for a software service"
                "provider named '카카오'.  Your job is to answer questions "
                "about a service named '카카오싱크'."
            ),
            HumanMessagePromptTemplate.from_template(
                "Below is a service documentation for '카카오싱크':\n"
                "\n"
                "{kakaosync_documentation}\n"
                "\n"
                "Answer the question using the information given by the "
                "documentation above.\n"
                "\n"
                "Question: {user_message}\n"
                "\n"
                "Your answer must be in Korean, using less than 150 words. "
                "Answer politely, please."
            )
        ])
        return chat_template

    def invoke(self, input, config=None):
        chain = (
            self.generate_chat_template()
            | ChatOpenAI(temperature=0.8)
            | StrOutputParser()
        )
        return chain.invoke(input, config)

class ReplyGenericMessage(Runnable):
    def generate_chat_template(self):
        chat_template = ChatPromptTemplate.from_messages([
            SystemMessagePromptTemplate.from_template(
                "You are a helpful assitant who works for a software service"
                "provider named '카카오'.  Your job is to answer questions "
                "about a service named '카카오싱크'."
            ),
            HumanMessagePromptTemplate.from_template(
                "Below is a service documentation for '카카오싱크':\n"
                "\n"
                "{kakaosync_documentation}\n"
                "\n"
                "The user has sent the following message:\n"
                "\n"
                "Message: {user_message}\n"
                "\n"
                "Reply to the message above, including a suggestion for "
                "using '카카오싱크'. Try to use any related information from "
                "the documentation given above. Your answer must be in "
                "Korean, using less than 50 words."
            )
        ])
        return chat_template

    def invoke(self, input, config=None):
        chain = (
            self.generate_chat_template()
            | ChatOpenAI(temperature=0.8)
            | StrOutputParser()
        )
        return chain.invoke(input, config)

class ExplainWhyItCantBeAnswered(Runnable):
    def generate_chat_template(self):
        chat_template = ChatPromptTemplate.from_messages([
            SystemMessagePromptTemplate.from_template(
                "You are a helpful assitant who works for a software service"
                "provider named '카카오'.  Your job is to answer questions "
                "about a service named '카카오싱크'.\n"
                "\n"
                "You are allowed to refer to the following documentation for "
                "answering questions related to '카카오싱크':\n"
                "\n"
                "{kakaosync_documentation}"
            ),
            HumanMessagePromptTemplate.from_template(
                "You must explain why the following question cannot be "
                "answered:\n"
                "\n"
                "Question: {user_message}\n"
                "\n"
                "Your answer must be in Korean, and it should be less than "
                "50 words. If the question includes negative sentiment, "
                "apologize instead of giving excuses. Answer politely, "
                "please."
            )
        ])
        return chat_template

    def invoke(self, input, config=None):
        chain = (
            self.generate_chat_template()
            | ChatOpenAI(temperature=0.8)
            | StrOutputParser()
        )
        return chain.invoke(input, config)


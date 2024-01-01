import json
import chromadb
import sqlite3
from chromadb.config import Settings
from langchain_core.runnables.base import Runnable
from langchain_core.output_parsers import StrOutputParser
from langchain.chat_models import ChatOpenAI
from langchain.prompts import (
    ChatPromptTemplate,
    SystemMessagePromptTemplate,
    HumanMessagePromptTemplate
)
from langchain.memory import ChatMessageHistory

with open("keywords.json") as f:
    service_keywords = json.load(f)

def get_last_conversation(user_id):
    db = sqlite3.connect("conversation_history.db")
    cur = db.cursor()
    result = cur.execute("""
    CREATE TABLE IF NOT EXISTS
    chat_history (
        user_id TEXT NOT NULL PRIMARY KEY,
        user_message TEXT,
        ai_message TEXT
    )
    """).execute("""
    SELECT user_id, user_message, ai_message FROM chat_history
    WHERE user_id = ?
    """, [user_id]).fetchone()
    db.close()
    return result

def store_last_conversation(user_id, user_message, ai_message):
    db = sqlite3.connect("conversation_history.db")
    cur = db.cursor()
    result = cur.execute("""
    CREATE TABLE IF NOT EXISTS
    chat_history (
        user_id TEXT NOT NULL PRIMARY KEY,
        user_message TEXT,
        ai_message TEXT
    )
    """).execute("""
    REPLACE INTO chat_history (user_id, user_message, ai_message) VALUES (?, ?, ?)
    """, [user_id, user_message, ai_message])
    db.commit()
    db.close()

class ClassifyMessage(Runnable):
    def generate_chat_template(self):
        chat_template = ChatPromptTemplate.from_messages([
            SystemMessagePromptTemplate.from_template(
                "You are a helpful assitant who works for a software service "
                "provider named '카카오'.  Your job is to read user messages "
                "and route these enquiries to other appropriate assistants."
            ),
            HumanMessagePromptTemplate.from_template(
                "The following is a YAML dictionary whose keys are the names "
                "of services, and values are keywords that represent the "
                "services:\n"
                "\n"
                "kakaotalk_channel: {kakaotalk_channel}\n"
                "kakaosync: {kakaosync}\n"
                "kakaosocial: {kakaosocial}\n"
                "\n"
                "The user inquiry was the following:\n"
                "\n"
                "User inquiry: {{user_message}}\n"
                "\n"
                "Based on the keywords given above, determine which service "
                "the inquiry is most likely to be asking about. Your answer "
                "must be exactly one of the keys of the YAML document "
                "provided above. If there are no services that match the "
                "inquiry, write 'no_match'.".format(**service_keywords)
            )
        ])
        return chat_template

    def invoke(self, input, config=None):
        chain = (
            self.generate_chat_template()
            | ChatOpenAI(temperature=0.8)
            | StrOutputParser()
        )
        message_category = chain.invoke(input, config)
        input_copy = input.copy()
        input_copy["message_category"] = message_category
        return input_copy

class ExtractKeywords(Runnable):
    def generate_chat_template(self):
        chat_template = ChatPromptTemplate.from_messages([
            SystemMessagePromptTemplate.from_template(
                "You are a helpful assitant who works for a software service "
                "provider named '카카오'.  Your job is to read user messages "
                "and route these enquiries to other appropriate assistants."
            ),
            HumanMessagePromptTemplate.from_template(
                "The user inquiry was the following:\n"
                "\n"
                "User inquiry: {user_message}\n"
                "\n"
                "Extract as many keywords as possible from the given user "
                "inquiry. The keywords must be in Korean."
            )
        ])
        return chat_template

    def invoke(self, input, config=None):
        chain = (
            self.generate_chat_template()
            | ChatOpenAI(temperature=0.8)
            | StrOutputParser()
        )
        extracted_keywords = chain.invoke(input, config)
        input_copy = input.copy()
        input_copy["extracted_keywords"] = extracted_keywords
        return input_copy

class AnswerQuestionsUsingDocuments(Runnable):
    def __init__(self, collection_name, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._collection_name = collection_name

    def generate_chat_template(self, conversation_history=None):
        chat_template = ChatPromptTemplate.from_messages([
            SystemMessagePromptTemplate.from_template(
                "You are a helpful assitant who works for a software service "
                "provider named '카카오'.  Your job is to answer user "
                "inquiries by the information from provided documentation."
            )]
            + ([] if conversation_history is None else conversation_history.messages)
            + [HumanMessagePromptTemplate.from_template(
                "The user inquiry was the following:\n"
                "\n"
                "User inquiry: {user_message}\n"
                "\n"
                "The documentation to use as an information source is given "
                "below:\n"
                "\n"
                "{documentation_to_refer_to}\n"
                "\n"
                "Answer the user inquiry using the documentation given "
                "above. Your answer must use information given in the "
                "above documentation only.  You must answer in Korean. "
                "Your answer must be less than 300 words.  Answer politely, "
                "please."
            )
        ])
        return chat_template

    def invoke(self, input, config=None):
        chroma_client = chromadb.Client(Settings(anonymized_telemetry=False))
        collections = chroma_client.get_collection(name=self._collection_name)
        results = collections.query(
            query_texts=[input["extracted_keywords"]],
            n_results=1
        )
        documentation = results["documents"][0][0]
        input_copy = input.copy()
        input_copy["documentation_to_refer_to"] = documentation
        last_conversation = get_last_conversation(input["user_id"])
        conversation_history = None
        if last_conversation is not None:
            conversation_history = ChatMessageHistory()
            conversation_history.add_user_message(last_conversation[1])
            conversation_history.add_ai_message(last_conversation[2])
        chain = (
            self.generate_chat_template(conversation_history)
            | ChatOpenAI(temperature=0.8)
            | StrOutputParser()
        )
        result = chain.invoke(input_copy, config)
        store_last_conversation(input["user_id"], input["user_message"], result)
        return result

class ReplyGenericMessage(Runnable):
    def generate_chat_template(self, conversation_history=None):
        chat_template = ChatPromptTemplate.from_messages([
            SystemMessagePromptTemplate.from_template(
                "You are a helpful assitant who works for a software service "
                "provider named '카카오'.  Your job is to reply to user "
                "inquiries that were failed to be sent to correct service "
                "assistants."
            )]
            + ([] if conversation_history is None else conversation_history.messages)
            + [HumanMessagePromptTemplate.from_template(
                "The following is a YAML dictionary whose keys are the names "
                "of services, and values are keywords that represent the "
                "services:\n"
                "\n"
                "카카오톡채널: {kakaotalk_channel}\n"
                "카카오싱크: {kakaosync}\n"
                "카카오소셜: {kakaosocial}\n"
                "\n"
                "The user inquiry was the following:\n"
                "\n"
                "User inquiry: {{user_message}}\n"
                "\n"
                "Give the user some suggestions about which service to use. "
                "You can use any information given above as you like.  Your "
                "answer must be in Korean. Answer politely, please.".format(
                    **service_keywords
                )
            )
        ])
        return chat_template

    def invoke(self, input, config=None):
        last_conversation = get_last_conversation(input["user_id"])
        conversation_history = None
        if last_conversation is not None:
            conversation_history = ChatMessageHistory()
            conversation_history.add_user_message(last_conversation[1])
            conversation_history.add_ai_message(last_conversation[2])
        chain = (
            self.generate_chat_template(conversation_history)
            | ChatOpenAI(temperature=0.8)
            | StrOutputParser()
        )
        result = chain.invoke(input, config)
        store_last_conversation(input["user_id"], input["user_message"], result)
        return result


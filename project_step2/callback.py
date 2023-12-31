from dto import ChatbotRequest
from samples import list_card
import aiohttp
import time
import logging
import openai
from langchain.chat_models import ChatOpenAI
from langchain.prompts import (
    ChatPromptTemplate,
    SystemMessagePromptTemplate,
    HumanMessagePromptTemplate
)
from langchain.chains import LLMChain
from langchain.schema import BaseOutputParser

with open("kakaosync_prompt_data.json") as f:
    kakaosync_intro_document = f.read()

logger = logging.getLogger("Callback")

class StringOutputParser(BaseOutputParser):
    def parse(self, text: str):
        return text

def complete_user_utterance(user_utterance):
    chat_template = ChatPromptTemplate.from_messages([
        SystemMessagePromptTemplate.from_template(
            "You are a helpful assitant who works for a software service"
            "provider named '카카오'.  Your job is to answer questions about "
            "a service named '카카오싱크'.  Your answer must be in Korean."
        ),
        HumanMessagePromptTemplate.from_template("{user_message}")
    ])
    chain = chat_template | ChatOpenAI(temperature=0.8) | StringOutputParser()
    return chain.invoke({
        "service_manual_for_kakaosync": kakaosync_intro_document,
        "user_message": user_utterance
    })

async def callback_handler(request: ChatbotRequest) -> dict:

    # ===================== start =================================
    completion = complete_user_utterance(request.userRequest.utterance)

    # 참고링크 통해 payload 구조 확인 가능
    payload = {
        "version": "2.0",
        "template": {
            "outputs": [
                {
                    "simpleText": {
                        "text": completion
                    }
                }
            ]
        }
    }
    # ===================== end =================================
    # 참고링크1 : https://kakaobusiness.gitbook.io/main/tool/chatbot/skill_guide/ai_chatbot_callback_guide
    # 참고링크1 : https://kakaobusiness.gitbook.io/main/tool/chatbot/skill_guide/answer_json_format

    url = request.userRequest.callbackUrl

    if url:
        async with aiohttp.ClientSession() as session:
            async with session.post(url=url, json=payload, ssl=False) as resp:
                obj = await resp.json()

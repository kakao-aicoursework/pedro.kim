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

with open("kakaosync_prompt_data.json") as f:
    kakaosync_intro_document = f.read()

logger = logging.getLogger("Callback")

def complete_user_utterance(user_utterance):
    chat_template = ChatPromptTemplate.from_messages(
        [
            SystemMessagePromptTemplate.from_template(
                template=(
                    "You are a service provider whose company name is "
                    "'카카오'.  You provide a service named '카카오싱크'."
                    "The following JSON document is a service manual for "
                    "'카카오싱크':\n\n"
                    "{service_manual_for_kakaosync}\n\n"
                    "When the user asks you about '카카오싱크', you have to "
                    "answer the question from the information provided by "
                    "the service manual."
                )
            ),
            HumanMessagePromptTemplate.from_template("{user_message}")
        ]
    )
    chat = ChatOpenAI(temperature=0.8)
    chain = LLMChain(llm=chat, prompt=chat_template)
    return chain.run(
        service_manual_for_kakaosync=kakaosync_intro_document,
        user_message=user_utterance
    )

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

    time.sleep(1.0)

    url = request.userRequest.callbackUrl

    if url:
        async with aiohttp.ClientSession() as session:
            async with session.post(url=url, json=payload, ssl=False) as resp:
                await resp.json()

import time
import logging

import aiohttp
from langchain_core.runnables import (
    RunnableParallel,
    RunnablePassthrough,
    RunnableLambda,
    RunnableBranch
)

from dto import ChatbotRequest
from samples import list_card
from tasks import (
    ClassifyMessage,
    ExtractKeywords,
    AnswerQuestionsUsingDocuments,
    ReplyGenericMessage,
)

logger = logging.getLogger("Callback")

with open("kakaosync_prompt_data.json") as f:
    kakaosync_documentation = f.read()

def complete_user_utterance(user_utterance):
    #from langchain_core.globals import set_debug, set_verbose
    #set_debug(True)
    #set_verbose(True)
    chain = (
        ClassifyMessage()
        | RunnableBranch(
            (lambda x: "kakaotalk_channel" in x["message_category"].lower(),
             ExtractKeywords()
             | AnswerQuestionsUsingDocuments("kakaotalk_channel")),
            (lambda x: "kakaosync" in x["message_category"].lower(),
             ExtractKeywords()
             | AnswerQuestionsUsingDocuments("kakaosync")),
            (lambda x: "kakaosocial" in x["message_category"].lower(),
             ExtractKeywords()
             | AnswerQuestionsUsingDocuments("kakaosocial")),
            ReplyGenericMessage()
        )
    )
    return chain.invoke({ "user_message": user_utterance })

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

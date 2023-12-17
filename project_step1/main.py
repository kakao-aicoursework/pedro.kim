import sys
import os
from conversation_gui import MessengerSession
import chatbot

def create_kakaosync_chatbot():
    with open("../prompt_data/refined_data/project_data_카카오톡채널.json") as f:
        json_text = f.read()
    system_prompt = f"""
You are a helpful assistant, specialized in answering questions about a
service named "카카오톡 채널".

The following JSON document contains information about "카카오톡 채널"
service:

{json_text}

When someone asks you about "카카오톡 채널", answer to them using the
information given in the JSON document just provided. Your answer must be in
Korean.
"""
    return chatbot.Chatbot(system_prompt)

def main():
    if "OPENAI_API_KEY" not in os.environ:
        print(
            "OPENAI_API_KEY 환경 변수가 설정되어 있지 않습니다. "
            "export OPENAI_API_KEY='...' 와 같은 형태로 API 키를 "
            "export해주세요."
        )
        sys.exit(1)

    init_data = {
        "chatbot": create_kakaosync_chatbot()
    }
    messenger = MessengerSession(init_data)
    messenger.mainloop()

if __name__ == "__main__":
    main()

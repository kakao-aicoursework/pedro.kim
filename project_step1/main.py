import sys
import os
from conversation_gui import MessengerSession
import chatbot

def main():
    if "OPENAI_API_KEY" not in os.environ:
        print(
            "OPENAI_API_KEY 환경 변수가 설정되어 있지 않습니다. "
            "export OPENAI_API_KEY='...' 와 같은 형태로 API 키를 "
            "export해주세요."
        )
        sys.exit(1)

    init_data = {
        "chatbot": chatbot.Chatbot("You are a helpful assistant.")
    }
    messenger = MessengerSession(init_data)
    messenger.mainloop()

if __name__ == "__main__":
    main()

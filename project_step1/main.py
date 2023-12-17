import sys
import os
import os.path
import json

from conversation_gui import MessengerSession
import chatbot

def create_kakaotalk_channel_chatbot():
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

def create_kakaotalk_channel_chatbot_using_embeddings():
    import chromadb
    chroma_client = chromadb.Client()
    collections = chroma_client.get_or_create_collection(name="kakaotalk_channel_docs")
    with open("../prompt_data/refined_data_for_embedding/index.json") as f:
        doc_index = json.load(f)
    documents = []
    for fn in doc_index["project_data_카카오톡채널.json"]:
        with open(os.path.join("../prompt_data/refined_data_for_embedding/", fn)) as f:
            documents.append(f.read())
    collections.add(
        documents=documents,
        ids=doc_index["project_data_카카오톡채널.json"]
    )

    system_prompt = f"""
You are a helpful assistant, specialized in answering questions about a
service named "카카오톡 채널".

When someone asks you about "카카오톡 채널", you have to answer the question
by looking up the documentation. The documentation must come from vector DB.

Your answer must be in Korean.
"""

    def get_appropriate_documentation(user_query, vectordb_query):
        results = collections.query(
            query_texts=[vectordb_query],
            n_results=1
        )
        documentation = results["documents"][0][0]
        cb = chatbot.Chatbot(f"""
You are a helpful assistant, specialized in answering questions about a
service named "카카오톡 채널".

When someone asks you about "카카오톡 채널", you have to answer the question
using the following JSON document:

{documentation}

Your answer must be in Korean.
        """)
        dialogue = f"""
A user asked the following:

{user_query}

Answer the question.
        """
        response = cb.create_session().respond_to_user_dialogue(dialogue)
        return response

    functions = [{
        "name": "get_appropriate_documentation",
        "description": "Get appropriate documentation for 카카오톡채널 service from vector DB.",
        "parameters": {
            "type": "object",
            "properties": {
                "vectordb_query": {
                    "type": "string",
                    "description": "Keywords to use for querying appropriate documentation for 카카오톡채널."
                }
            }
        },
        "_actual_function": get_appropriate_documentation
    }]

    return chatbot.Chatbot(
        system_prompt=system_prompt,
        functions=functions
    )

def main():
    if "OPENAI_API_KEY" not in os.environ:
        print(
            "OPENAI_API_KEY 환경 변수가 설정되어 있지 않습니다. "
            "export OPENAI_API_KEY='...' 와 같은 형태로 API 키를 "
            "export해주세요."
        )
        sys.exit(1)

    init_data = {
        "chatbot": create_kakaotalk_channel_chatbot_using_embeddings()
    }
    messenger = MessengerSession(init_data)
    messenger.mainloop()

if __name__ == "__main__":
    main()

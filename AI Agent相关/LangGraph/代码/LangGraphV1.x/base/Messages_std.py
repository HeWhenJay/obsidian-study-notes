from langchain_core.messages import SystemMessage, HumanMessage, AIMessage
from langchain_openai import ChatOpenAI
import os

from dotenv import load_dotenv
load_dotenv()

llm = ChatOpenAI(
    model_name="deepseek-v3",
    api_key=os.getenv("DASHSCOPE_API_KEY"),
    base_url=os.getenv("API_BASE_URL")
)

messages = [
    SystemMessage(content="你是一个乐于助人的AI助手，回答时尽量简洁。"),
    HumanMessage(content="你好！你能介绍下自己吗？"),
    AIMessage(content='你好！我是AI助手，可以帮你解决问题。'),
    HumanMessage('Python里如何写"Hello World"')
]
print(llm.invoke(messages).content)


import os

from dotenv import load_dotenv
from langchain_openai import ChatOpenAI
from langgraph.graph import StateGraph, MessagesState, START
from langgraph.checkpoint.redis import RedisSaver
"""
该代码需要pip install -U langgraph-checkpoint-redis
"""

load_dotenv()

model = ChatOpenAI(
    model_name="deepseek-v3",
    api_key=os.getenv("DASHSCOPE_API_KEY"),
    base_url=os.getenv("API_BASE_URL")
)

DB_URI = "redis://localhost:6379"
with RedisSaver.from_conn_string(DB_URI) as checkpointer:
    def call_model(state: MessagesState):
        response = model.invoke(state["messages"])
        return {"messages": response}

    builder = StateGraph(MessagesState)
    builder.add_node(call_model)
    builder.add_edge(START, "call_model")

    graph = builder.compile(checkpointer=checkpointer)

    config = {
        "configurable": {
            "thread_id": "1"
        }
    }

    for chunk in graph.stream(
        {"messages": [{"role": "user", "content": "你好，我是云帆"}]},
        config,
        stream_mode="values"
    ):
        chunk["messages"][-1].pretty_print()

    for chunk in graph.stream(
        {"messages": [{"role": "user", "content": "我叫什么名字"}]},
        config,
        stream_mode="values"
    ):
        chunk["messages"][-1].pretty_print()
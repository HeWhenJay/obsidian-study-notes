import operator
from typing import Annotated, Sequence
from typing_extensions import TypedDict
from langchain_core.messages import BaseMessage, HumanMessage
from langgraph.graph import END, StateGraph, START
from langchain_openai import ChatOpenAI
import os
from dotenv import load_dotenv  # 用于加载环境变量
load_dotenv()  # 加载.env文件中的环境变量

ali_max_llm = ChatOpenAI(
    model_name="qwen-max-2025-01-25",
    api_key=os.getenv("DASHSCOPE_API_KEY"),
    base_url=os.getenv("API_BASE_URL")
)
deepseek_llm = ChatOpenAI(
    model_name="deepseek-chat",
    api_key=os.getenv("Deepseek_Key"),
    base_url=os.getenv("DEEPSEEK_URL")
)

class AgentState(TypedDict):
    messages: Annotated[Sequence[BaseMessage], operator.add]

from langchain_core.runnables.config import RunnableConfig
models = {
    "deepseek": deepseek_llm,
    "ali": ali_max_llm,
}

def _call_model(state: AgentState, config: RunnableConfig):
    # print('###',config["configurable"])

    model_name = config["configurable"].get("model", "ali")
    print('model_name：',model_name)
    model = models[model_name]
    response = model.invoke(state["messages"])
    return {"messages": [response]}


builder = StateGraph(AgentState)
builder.add_node("model", _call_model)
builder.add_edge(START, "model")
builder.add_edge("model", END)

graph = builder.compile()

config = {"configurable": {"model": "deepseek"}}
print(graph.invoke({"messages": [HumanMessage(content="你是谁？")]}, config=config))
config = {"configurable": {"model": "ali"}}
print(graph.invoke({"messages": [HumanMessage(content="你是谁？")]}, config=config))
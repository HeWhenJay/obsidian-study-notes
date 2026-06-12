from typing import Literal
from langchain_core.tools import tool
from langgraph.checkpoint.memory import MemorySaver
from langgraph.graph import MessagesState, StateGraph, START, END
from langgraph.prebuilt import ToolNode
from dotenv import load_dotenv
from langchain_core.messages import RemoveMessage
from langgraph.graph import END
load_dotenv()
from langchain_openai import ChatOpenAI
from langchain_core.messages import HumanMessage
import os

memory = MemorySaver()

@tool
def web_search(query: str):
    """网络搜索"""
    # 代替实际实现
    return "上海阳光明媚"

tools = [web_search]
tool_node = ToolNode(tools)
model = ChatOpenAI(
    model_name="deepseek-v3",
    api_key=os.getenv("DASHSCOPE_API_KEY"),
    base_url=os.getenv("API_BASE_URL")
)
bound_model = model.bind_tools(tools)

def should_continue(state: MessagesState):
    last_message = state["messages"][-1]
    if not last_message.tool_calls:
        return END
    return "action"

def call_model(state: MessagesState):
    response = model.invoke(state["messages"])
    return {"messages": response}

workflow = StateGraph(MessagesState)
workflow.add_node("agent", call_model)
workflow.add_node("action", tool_node)
workflow.add_edge(START, "agent")
workflow.add_conditional_edges(
    "agent",
    should_continue,
    ["action", END],
)
workflow.add_edge("action", "agent")
app = workflow.compile(checkpointer=memory)


'自定义'
def delete_messages(state):
    messages = state["messages"]
    if len(messages) > 2:
        return {"messages": [RemoveMessage(id=m.id) for m in messages[:2]]}

# 我们需要修改逻辑来调用delete_messages，而不是立即结束
def should_continue(state: MessagesState) -> Literal["action", "delete_messages"]:
    last_message = state["messages"][-1]
    if not last_message.tool_calls:
        return "delete_messages"
    return "action"

workflow = StateGraph(MessagesState)
workflow.add_node("agent", call_model)
workflow.add_node("action", tool_node)
workflow.add_node(delete_messages)
workflow.add_edge(START, "agent")
workflow.add_conditional_edges(
    "agent",
    should_continue,
)
workflow.add_edge("action", "agent")

# 这是我们增加的新edge:删除消息后结束
workflow.add_edge("delete_messages", END)
app = workflow.compile(checkpointer=memory)
app.get_graph().draw_mermaid_png(output_file_path='../imgs/删除消息节点.png')
config = {"configurable": {"thread_id": "3"}}
input_message = HumanMessage(content="你好，我是云帆")
for event in app.stream({"messages": [input_message]}, config, stream_mode="values"):
    print(event)
    print([(message.type, message.content) for message in event["messages"]])

input_message = HumanMessage(content="我叫什么名字？")
for event in app.stream({"messages": [input_message]}, config, stream_mode="values"):
    print([(message.type, message.content) for message in event["messages"]])
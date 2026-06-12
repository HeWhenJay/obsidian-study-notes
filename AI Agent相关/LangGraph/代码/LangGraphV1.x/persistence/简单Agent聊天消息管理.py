from dotenv import load_dotenv
load_dotenv()
import os
from langchain_openai import ChatOpenAI
from langchain_core.messages import HumanMessage
from langchain_core.tools import tool
from langgraph.checkpoint.memory import MemorySaver
from langgraph.graph import MessagesState, StateGraph, START, END
from langgraph.prebuilt import ToolNode

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
    response = bound_model.invoke(state["messages"])
    print(response)
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
app.get_graph().draw_mermaid_png(output_file_path='../imgs/简单Agent聊天消息管理.png')

config = {"configurable": {"thread_id": "1"}}

input_message = HumanMessage(content="你好，我是云帆")
for event in app.stream({"messages": [input_message]}, config, stream_mode="values"):
    event["messages"][-1].pretty_print()

input_message = HumanMessage(content="我叫什么名字？")
for event in app.stream({"messages": [input_message]}, config, stream_mode="values"):
    event["messages"][-1].pretty_print()
from dotenv import load_dotenv
load_dotenv()
from langchain_core.tools import tool
from langgraph.prebuilt import ToolNode
from langgraph.graph import StateGraph, MessagesState, START, END
from langchain_openai import ChatOpenAI
import os
@tool
def get_weather(location: str):
    """获取当前天气."""
    if location.lower() in ["SH", "上海"]:
        return "气温23度，有雾."
    else:
        return "气温30度，阳光明媚."

@tool
def get_coolest_cities():
    """获得最凉快城市列表"""
    return "青岛, 上海"

tools = [get_weather, get_coolest_cities]
tool_node = ToolNode(tools)

model_with_tools = ChatOpenAI(
    model_name="deepseek-v3",
    api_key=os.getenv("DASHSCOPE_API_KEY"),
    base_url=os.getenv("API_BASE_URL"),
    temperature=0
).bind_tools(tools)

def should_continue(state: MessagesState):
    messages = state["messages"]
    last_message = messages[-1]
    if last_message.tool_calls:
        return "tools"
    return END


def call_model(state: MessagesState):
    messages = state["messages"]
    response = model_with_tools.invoke(messages)
    return {"messages": [response]}


workflow = StateGraph(MessagesState)

# Define the two nodes we will cycle between
workflow.add_node("agent", call_model)
workflow.add_node("tools", tool_node)
workflow.add_edge(START, "agent")
workflow.add_conditional_edges("agent", should_continue, ["tools", END])
workflow.add_edge("tools", "agent")
app = workflow.compile()

app.get_graph().draw_mermaid_png(output_file_path='../imgs/LangGraph_ToolNode.png')
# example with a single tool call
for chunk in app.stream(
    {"messages": [("human", "上海的天气怎么样??")]}, stream_mode="values"
):
    chunk["messages"][-1].pretty_print()


print('######################')


# example with a multiple tool calls in succession
for chunk in app.stream(
    {"messages": [("human", "最凉快城市有哪些?天气如何？")]},
    stream_mode="values",
):
    chunk["messages"][-1].pretty_print()
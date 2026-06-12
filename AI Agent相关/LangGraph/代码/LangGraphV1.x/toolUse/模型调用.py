from langchain_core.messages import AIMessage
from langchain_core.tools import tool
from dotenv import load_dotenv
load_dotenv()
from langgraph.prebuilt import ToolNode
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

print(model_with_tools.invoke("上海的天气怎么样?").tool_calls)
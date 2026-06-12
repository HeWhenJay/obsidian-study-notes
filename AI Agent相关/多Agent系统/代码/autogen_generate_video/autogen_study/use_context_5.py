from autogen_agentchat.agents import AssistantAgent
from autogen_agentchat.messages import TextMessage
from autogen_core import CancellationToken
from autogen_core.model_context import BufferedChatCompletionContext
from autogen_ext.models.openai import OpenAIChatCompletionClient
import asyncio
import os
from dotenv import load_dotenv

load_dotenv()

# 定义一个网络搜索工具
async def web_search(query: str) -> str:
    """在网络上查找信息"""
    return "AutoGen 是一个用于构建多代理应用程序的编程框架。"


# 创建一个使用 qwen 模型的Agent
model_client = OpenAIChatCompletionClient(
    model="qwen-plus-latest",
    api_key=os.getenv("DASHSCOPE_API_KEY"),
    base_url=os.getenv("API_BASE_URL"),
    model_info={
        "vision": True,
        "function_calling": True,
        "json_output": True,
        "family": "unknown",
        "structured_output": False
    },
)

agent = AssistantAgent(
    name="assistant",
    model_client=model_client,
    tools=[web_search],  # 假设已经定义了 web_search 工具
    system_message="使用工具来解决任务。",
    model_context=BufferedChatCompletionContext(buffer_size=5),  # 只使用最近 5 条消息
)

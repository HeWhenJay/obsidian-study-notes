from autogen_agentchat.agents import AssistantAgent
from autogen_agentchat.messages import TextMessage
from autogen_agentchat.ui import Console
from autogen_core import CancellationToken
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
        "vision": False,
        "function_calling": True,
        "json_output": True,
        "family": "unknown",
        "structured_output": False
    },
    )

# 创建AssistantAgent
agent = AssistantAgent(
    name="assistant",
    model_client=model_client,
    tools=[web_search],
    system_message="使用工具来解决任务。",
)

async def assistant_run_stream() -> None:
    await Console(
        # 使用on_messages_stream()
        agent.on_messages_stream(
            [TextMessage(content="查找关于 AutoGen 的信息", source="user")],
            cancellation_token=CancellationToken(),
        )
    )

asyncio.run(assistant_run_stream())
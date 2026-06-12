from autogen_agentchat.agents import AssistantAgent
from autogen_ext.models.openai import OpenAIChatCompletionClient
from autogen_agentchat.ui import Console
from typing import Literal
from pydantic import BaseModel
import asyncio
import os
from dotenv import load_dotenv
load_dotenv()

# 定义代理的响应格式，使用 Pydantic BaseModel
class AgentResponse(BaseModel):
    thoughts: str
    response: Literal["高兴", "悲伤", "一般"]

# 客户端里，就要配置 输出格式
model_client = OpenAIChatCompletionClient(
    model="qwen-plus-latest",
    api_key=os.getenv("DASHSCOPE_API_KEY"),
    base_url=os.getenv("API_BASE_URL"),
    response_format=AgentResponse,
    model_info={
        "vision": True,
        "function_calling": True,
        "json_output": True,
        "family": "unknown",
        "structured_output": True
    },
)

agent = AssistantAgent(
    "assistant",
    model_client=model_client,
    system_message='''按照以下JSON格式将输入分类为高兴、悲伤或一般：
    {
        "thoughts": "分析用户情绪的原因", 
        "response": "高兴|悲伤|一般"
    }'''
)

asyncio.run(Console(agent.run_stream(task="我今天心情很好")))

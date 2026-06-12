from autogen_ext.models.openai import OpenAIChatCompletionClient
from autogen_core.models import UserMessage
import asyncio
import os
from dotenv import load_dotenv
load_dotenv()

# 创建模型客户端
model_client = OpenAIChatCompletionClient(
    model="qwen-plus-latest",
    api_key=os.getenv("DASHSCOPE_API_KEY"),
    base_url=os.getenv("API_BASE_URL"),
    model_info={
        "vision": False, # 模型是否支持图片识别
        "function_calling": True, #模型是否支持函数调用
        "json_output": True, # 模型是否支持json格式输出
        "family": "unknown", # 模型是否来自：["gpt-4o","o1","o3","gpt-4","gpt-35","r1","unknown"]
        "structured_output": False
    },
    )

result = asyncio.run(model_client.create([UserMessage(content="法国的首都在哪里?", source="user")]))
print(result)
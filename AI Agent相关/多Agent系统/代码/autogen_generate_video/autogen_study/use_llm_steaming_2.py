from autogen_agentchat.agents import AssistantAgent
from autogen_agentchat.messages import TextMessage
from autogen_core import CancellationToken
from autogen_ext.models.openai import OpenAIChatCompletionClient
import asyncio
import os
from dotenv import load_dotenv

load_dotenv()

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


"""
AgentChat 提供了一组预设Agent，每个Agent对消息的响应方式各不相同：
- AssistantAgent：是一个内置的Agent，使用大语言模型，并且具有使用工具的能力
- UserProxyAgent： 接受用户输入并将其作为响应返回的代理。
- CodeExecutorAgent： 可以执行代码的代理。
- OpenAIAssistantAgent： 由 OpenAI Assistant 支持的代理，能够使用自定义工具。
- MultimodalWebSurfer： 可以搜索网络并访问网页以获取信息的多模态代理。
- FileSurfer： 可以搜索和浏览本地文件以获取信息的代理。
- VideoSurfer： 可以观看视频以获取信息的代理。
"""
work_assistant = AssistantAgent(
    name="assistant",
    model_client=model_client,
    system_message="你是一位得力的助手",
    model_client_stream=True,  # 流式传输模型客户端生成的文本
)

#调用大模型获得响应，非流式输出
async def assistant_run() -> None:
    #on_messages（） 方法来获取代理对给定消息的响应
    response = await work_assistant.on_messages(
        [TextMessage(content="请说出两个南美洲城市的名字", source="user")],
        cancellation_token=CancellationToken(),
    )
    # run() 和 run_stream() ：便捷方法分别调用 on_messages() 和 on_messages_stream()
    # 使用run()方法返回 TaskResult 对象，打印print(response)
    # response = await work_assistant.run(
    #     task = TextMessage(content="查找关于 AutoGen 的信息", source="user"),
    #     cancellation_token=CancellationToken(),
    # )
    print("assistant_run_inner_messages:",response.inner_messages)
    print()
    print("assistant_run_chat_message:",response.chat_message)

asyncio.run(assistant_run())

#调用大模型获得响应，流式输出
async def assistant_run_stream():
    async for message in work_assistant.on_messages_stream(
            [TextMessage(content="请说出两个南美洲城市的名字", source="user")],
            cancellation_token=CancellationToken(),
    ):
        print("stream_message:",message)

    # # 使用run_stream()产生同样的效果
    # async for message in work_assistant.run_stream(task="Name two cities in North America."):
    #     print(message)


asyncio.run(assistant_run_stream())
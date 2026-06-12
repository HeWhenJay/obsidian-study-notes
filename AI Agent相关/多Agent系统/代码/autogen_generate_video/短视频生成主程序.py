from autogen_agentchat.agents import AssistantAgent
from autogen_agentchat.teams import RoundRobinGroupChat
from autogen_agentchat.conditions import TextMentionTermination
from autogen_agentchat.ui import Console
from autogen_ext.models.openai import OpenAIChatCompletionClient
from pydantic import BaseModel
from dotenv import load_dotenv
import asyncio
import os

from tools import (
    generate_voiceovers,
    generate_images,
    generate_video,
)

# 加载环境变量
load_dotenv()


# 定义脚本输出结构
class ScriptOutput(BaseModel):
    topic: str  #主题
    takeaway: str #要点
    captions: list[str]  #字幕


async def main():
    # 初始化OpenAI客户端
    model_client = OpenAIChatCompletionClient(
        model="qwen3-max",
        api_key=os.getenv("DASHSCOPE_API_KEY"),
        base_url=os.getenv("API_BASE_URL"),
        #response_format=ScriptOutput,
        model_info={
            "vision": False,
            "function_calling": True,
            "json_output": True,
            "family": "unknown",
            "structured_output": True
        },
    )


    # 创建脚本Agent，负责把主题转成字幕
    script_writer = AssistantAgent(
        name="script_writer",
        model_client=model_client,
        system_message='''
            您是一名创意助理，负责为一个短视频编写脚本。
            脚本应包含旨在显示在屏幕上的字幕，并遵循以下准则：
                1. 每个字幕必须简短且有影响力（不超过 8 个字），以免让观众感到不知所措。
                2. 脚本应包含 5 个字幕，每个字幕代表故事中的一个关键时刻。
                3. 字幕的流动必须感觉自然，就像一个引人入胜的画外音引导观众完成叙述。
                4. 始终以问题或陈述开头，让观众想要了解更多信息。
                5. 您还必须在回复中包含主题和要点。
                6. 字幕值必须仅包含字幕，不能包含其他元数据或信息。

                以 JSON 格式输出回复：
                {
                    "topic": "topic",
                    "takeaway": "takeaway",
                    "captions": [
                        "caption1",
                        "caption2",
                        "caption3",
                        "caption4",
                        "caption5"
                    ]
                }
        '''
    )

    #创建音频的Agent
    voice_actor = AssistantAgent(
        name="voice_actor",
        model_client=model_client,
        tools=[generate_voiceovers],
        system_message='''
            您是一名乐于助人的代理，负责生成和保存画外音。
            您将获得一个字幕列表captions，其中包含 5 个字幕，每个字幕代表故事中的一个关键时刻。
            然后，您将使用字幕列表为每个提供的字幕生成画外音。
            仅在文件成功保存在本地后才响应“终止”。
        '''
    )

    # 创建图片的Agent
    graphic_designer = AssistantAgent(
        name="graphic_designer",
        model_client=model_client,
        tools=[generate_images],
        system_message='''
            您是一位乐于助人的代理，负责为短视频生成和保存图像。
            您将获得一个字幕列表。
            您将把每个字幕转换为图像生成工具的优化提示。
            您的提示尽可能详细描述出一幅完整的画面，同时确保图像之间的连续性。您的提示必须提到输出图像必须为：“科幻艺术风格/超高品质。”（包括在每个提示中）
            然后，您将使用提示列表为每个提供的字幕生成图像。
            仅在文件成功保存在本地后才响应“终止”。
        '''
    )

    #负责进行最后的合成，导演agent
    director = AssistantAgent(
        name="director",
        model_client=model_client,
        tools=[generate_video],
        system_message='''
            您是一位乐于助人的代理，负责制作一段短视频。
            您将获得一个字幕列表，您将使用这些字幕来制作短视频。
            从字幕中删除所有非字母数字或空格的字符。
            然后，您将使用字幕列表来生成视频。
            仅在成功生成视频并将其保存在本地后，才响应“终止”。
        '''
    )

    # 设置终止条件
    termination = TextMentionTermination("TERMINATE")

    # 创建顺序执行流程，组合Agent确保每个任务完成
    # RoundRobinGroupChat是 AutoGen 中一种经典的多智能体对话调度机制，
    # 其核心逻辑是让智能体按照预设顺序轮流参与对话，类似 “轮询” 模式。
    agent_team = RoundRobinGroupChat(
        [script_writer, voice_actor, graphic_designer, director],
        termination_condition=termination,
        # 每个Agent执行最大轮数
        max_turns=5
    )

    # 交互式控制台循环
    while True:
        user_input = input("Enter a message (type 'exit' to leave): ")
        if user_input.strip().lower() == "exit":
            break

        # 运行team并显示结果
        stream = agent_team.run_stream(task=user_input)
        await Console(stream)


# 运行主函数
if __name__ == "__main__":
    asyncio.run(main())

    """windows下安装ffmpeg:https://blog.csdn.net/qq_42663692/article/details/130915201"""

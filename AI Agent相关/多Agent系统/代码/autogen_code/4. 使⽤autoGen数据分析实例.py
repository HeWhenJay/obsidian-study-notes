from autogen_ext.models.openai import OpenAIChatCompletionClient
import os
from dotenv import load_dotenv
import asyncio

# 加载环境变量
load_dotenv()

async def main():
    try:
        model_client = OpenAIChatCompletionClient(
                model="qwen3-max",
                api_key=os.getenv("DASHSCOPE_API_KEY"),
                base_url=os.getenv("API_BASE_URL"),
                model_info={
                    "vision": True,
                    "function_calling": True,
                    "json_output": True,
                    "family": "unknown",
                    "structured_output": True
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
        from autogen_agentchat.agents import AssistantAgent, CodeExecutorAgent
        from autogen_ext.code_executors.docker import DockerCommandLineCodeExecutor
        from autogen_agentchat.teams import RoundRobinGroupChat
        from autogen_agentchat.ui import Console

        coder = AssistantAgent(
            name="Coder",
            model_client=model_client,
        )

        code_executor = DockerCommandLineCodeExecutor(work_dir="dataanalysis")
        await code_executor.start()
        executor = CodeExecutorAgent(
            name="Executor",
            code_executor=code_executor
        )

        critic = AssistantAgent(
            name="Critic",
            system_message="""评论家。您是一位乐于助人的助手，能够通过提供 1（差）- 10（好）的分数来评估给定可视化代码的质量，同时提供明确的理由。您必须为每次评估考虑可视化最佳实践。具体来说，您可以从以下维度仔细评估代码
    - 错误（bug）：是否存在错误、逻辑错误、语法错误或拼写错误？代码编译失败的原因是什么？应该如何修复？如果存在任何错误，错误分数必须小于 5。
    - 目标合规性（合规性）：代码与指定可视化目标的符合程度如何？
    
    您必须为上述每个维度提供分数。
    {bug：0，合规性：0}
    不建议代码。
    最后，根据上述批评，建议程序员应采取的具体行动清单，以改进代码。
    """,
            model_client=model_client,
        )

        team = RoundRobinGroupChat([coder, executor, critic], max_turns=20)
        stream = team.run_stream(task="从 https://raw.githubusercontent.com/vega/vega/main/docs/data/seattle-weather.csv 下载数据并告诉我每种天气的数量。将图保存到文件中。在可视化数据集之前打印数据集中的字段。接受评论者的反馈以改进代码。")
        await Console(stream)

    except Exception as e:
        print(f"发生错误: {str(e)}")
    finally:
        if 'code_executor' in locals():
            await code_executor.stop()

if __name__ == "__main__":
    asyncio.run(main())
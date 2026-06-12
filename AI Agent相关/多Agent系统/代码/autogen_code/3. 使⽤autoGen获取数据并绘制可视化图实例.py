from autogen_ext.code_executors.local import LocalCommandLineCodeExecutor
from autogen_ext.models.openai import OpenAIChatCompletionClient
import os
from dotenv import load_dotenv
import asyncio

# 加载环境变量
load_dotenv()

async def main():
    try:
        model_client = OpenAIChatCompletionClient(
                model="o1-preview-2024-09-12",
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

        model_coder_client = OpenAIChatCompletionClient(
                model="o1-preview-2024-09-12",
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

        model_coder_review_client = OpenAIChatCompletionClient(
                model="o1-preview-2024-09-12",
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

        #code_executor = LocalCommandLineCodeExecutor(work_dir="visualization")
        code_executor = DockerCommandLineCodeExecutor(work_dir="visualization")
        await code_executor.start()
        executor = CodeExecutorAgent(
            name="Executor",
            code_executor=code_executor
        )
        #这个Agent生成业务代码
        coder = AssistantAgent(
            name="Coder",
            model_client=model_coder_client,
        )
        # 这个Agent审核代码的执行结果，给出修改意见
        critic = AssistantAgent(
            name="Critic",
            system_message="""评论家。您是一位乐于助人的助手，能够通过提供 1（差）- 10（好）的分数来评估给定可视化代码的质量，同时提供明确的理由。您必须为每次评估考虑可视化最佳实践。具体来说，您可以从以下维度仔细评估代码
    - 错误（bug）：是否存在错误、逻辑错误、语法错误或拼写错误？代码编译失败的原因是什么？应该如何修复？如果存在任何错误，错误分数必须小于 5。
    - 数据转换（transformation）：数据是否针对可视化类型进行了适当的转换？例如，数据集是否根据需要进行了适当的过滤、聚合或分组？如果使用日期字段，是否先将日期字段转换为日期对象等？
    - 目标合规性（compliance）：代码与指定可视化目标的匹配程度如何？
    - 可视化类型 (type)：考虑最佳实践，可视化类型是否适合数据和意图？是否有更有效地传达见解的可视化类型？如果其他可视化类型更合适，则分数必须小于 5。
    - 数据编码 (encoding)：数据是否适合可视化类型编码？
    - 美学 (aestics)：可视化的美学是否适合可视化类型和数据？
    
    您必须为上述每个维度提供分数。
    {错误：0，转换：0，合规性：0，类型：0，编码：0，美观性：0}
    不建议代码。
    最后，根据上述批评，建议程序员应采取的具体行动清单，以改进代码。
    """,
            model_client=model_coder_review_client,
        )

        team = RoundRobinGroupChat(
            [coder, executor, critic],
            max_turns=20,
        )

        stream = team.run_stream(task="从 https://raw.githubusercontent.com/uwdata/draco/master/data/cars.csv 下载数据并绘制可视化图，告诉我们重量和马力之间的关系。将图保存到文件中。在可视化之前打印数据集中的字段。")
        await Console(stream)

    except Exception as e:
        print(f"发生错误: {str(e)}")
    finally:
        if 'code_executor' in locals():
            await code_executor.stop()

if __name__ == "__main__":
    asyncio.run(main())
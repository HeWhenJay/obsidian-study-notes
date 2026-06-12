from autogen_agentchat.teams import SelectorGroupChat
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


        from autogen_agentchat.agents import AssistantAgent, UserProxyAgent, CodeExecutorAgent
        from autogen_ext.code_executors.docker import DockerCommandLineCodeExecutor

        # 创建一个管理员Proxy
        user_proxy = UserProxyAgent(
            name="Admin",
            description="人类管理员. 与规划师互动，讨论计划。计划执行需要得到该管理员的批准。",
        )

        # 创建一个工程师assistant
        engineer = AssistantAgent(
            name="Engineer",
            model_client=model_client,
            system_message="""工程师。您遵循已批准的计划。您编写 python/shell 代码来解决任务。
            将代码包装在指定脚本类型的代码块中。用户无法修改您的代码。因此，不要建议需要其他人修改的不完整代码。
            如果代码块不打算由执行器执行，请不要使用它。
            不要在一个响应中包含多个代码块。不要要求其他人复制和粘贴结果。检查执行器返回的执行结果。
            如果结果表明存在错误，请修复错误并再次输出代码。建议使用完整代码而不是部分代码或代码更改。
            如果错误无法修复，或者即使代码成功执行后任务仍未解决，请分析问题，重新审视您的假设，
            收集您需要的其他信息，并考虑尝试其他方法。
            """,
        )

        # 创建一个科学家assistant
        scientist = AssistantAgent(
            name="Scientist",
            model_client=model_client,
            system_message="""科学家。你遵循一个已批准的计划。你可以在看到论文摘要后对论文进行分类。你不写代码。""",
        )

        # 创建一个计划员assistant
        planner = AssistantAgent(
            name="Planner",
            system_message="""规划师。提出计划。根据人类管理员和评论员的反馈修改计划，直到人类管理员批准。
            该计划可能涉及会写代码的工程师和不会写代码的科学家。
            首先解释一下计划。明确哪一步由工程师执行，哪一步由科学家执行。
            """,
            model_client=model_client,
        )

        code_executor = DockerCommandLineCodeExecutor(work_dir="paper")
        await code_executor.start()
        
        # 创建一个执行者Proxy
        executor = CodeExecutorAgent(
            name="Executor",
            description="执行器。执行工程师编写的代码并报告结果。",
            code_executor=code_executor,
            model_client=model_client
        )

        # 创建一个评论家assistant
        critic = AssistantAgent(
            name="Critic",
            system_message="""批评家。仔细检查其他智能体的计划、声明和代码并提供反馈。检查计划是否包括添加可验证信息，
            例如源 URL。 你的工作完成后请以'人类管理员'的称呼明确告知人类是否需要干预""",
            model_client=model_client,
        )

        from autogen_agentchat.teams import RoundRobinGroupChat
        from autogen_agentchat.ui import Console

        # 组合Agent确保每个任务完成
        # agent_team = RoundRobinGroupChat(
        #     [planner, user_proxy, engineer, executor, scientist, critic]
        # )
        agent_team = SelectorGroupChat(
            participants = [planner, user_proxy, engineer, executor, scientist, critic],
            model_client = model_client
        )

        print("\033[1;31m本程序因为要访问arxiv需要科学上网！请人类管理员检查是否开启了科学上网！\033[0m")

        stream = agent_team.run_stream(task="从arxiv上找到最新的5篇关于大语言模型的论文，保存到markdown表，并保存到本地文件。"
                                            "请问人类管理员对该计划是否有调整？如有，请告知我")
        await Console(stream)

    except Exception as e:
        print(f"发生错误: {str(e)}")
    finally:
        if 'code_executor' in locals():
            await code_executor.stop()

if __name__ == "__main__":
    asyncio.run(main())

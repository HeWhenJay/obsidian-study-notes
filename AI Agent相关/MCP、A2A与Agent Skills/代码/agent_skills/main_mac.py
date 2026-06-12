import os
import sys
import subprocess
from dotenv import load_dotenv
from deepagents import create_deep_agent
from langgraph.checkpoint.memory import MemorySaver
from langchain_community.chat_models.tongyi import ChatTongyi
from deepagents.backends.filesystem import FilesystemBackend
from langchain_core.tools import tool

load_dotenv()

# =========================================================================
# 1. 定义一个通用的执行工具
# =========================================================================
# 技巧：我们将工具命名为 "execute"。
# 这样，当 arxiv-search 的 SKILL.md 说 "请使用 execute 工具运行命令" 时，
# Agent 会自动匹配到这个工具，而不需要你在 Prompt 里特殊废话。
@tool("execute")
def custom_execute(command: str) -> str:
    """
    执行本地 Shell 命令或 Python 脚本。
    当技能说明（SKILL.md）要求运行命令时，使用此工具。
    """
    # 安全打印，让你知道它在干活
    print(f"\n⚡️ [AutoTool] 正在执行: {command}")
    
    try:
        # 设置超时为 120秒，防止脚本卡死
        result = subprocess.run(
            command,
            shell=True,
            capture_output=True,
            text=True,
            timeout=120
        )
        
        # 捕获标准输出和错误
        output = result.stdout
        if result.stderr:
            output += f"\n[STDERR]: {result.stderr}"
        
        # 处理空输出的情况
        if not output.strip():
            return "命令执行成功，但没有输出内容。"
            
        print(f"✅ 执行完成 (输出长度: {len(output)})")
        return output

    except subprocess.TimeoutExpired:
        return "Error: 命令执行超时 (超过120秒)。"
    except Exception as e:
        return f"Error: 执行失败 - {str(e)}"

# =========================================================================
# 2. 初始化环境
# =========================================================================
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
PYTHON_EXEC = sys.executable  # 获取当前 Python 路径

if not os.getenv("DASHSCOPE_API_KEY"):
    print("❌ 错误: 未找到 API KEY")
    sys.exit(1)

model = ChatTongyi(
    model="qwen3-max",
    api_key=os.getenv("DASHSCOPE_API_KEY")
)

# =========================================================================
# 3. 创建 Agent (全局注入工具)
# =========================================================================
print(f"📂 工作目录: {BASE_DIR}")

agent = create_deep_agent(
    model=model,
    # 依然挂载文件系统，让 Agent 能读写文件
    backend=FilesystemBackend(root_dir=BASE_DIR),
    
    # 这里会自动加载 skills 文件夹下所有的 Skill (arxiv, langgraph 等)
    skills=["skills"], 
    
    # 【关键】注入我们的自定义工具，它会覆盖系统默认的同名工具
    tools=[custom_execute], 
    
    checkpointer=MemorySaver(),
)

# =========================================================================
# 4. 执行
# =========================================================================

# 场景 A: 需要跑脚本的任务
user_input_arxiv = "搜索关于 'DeepSeek-R1' 的最新论文"

# 场景 B: 不需要跑脚本的任务 (假设你有一个纯文本处理的 skill)
# user_input_other = "总结一下 langgraph 的基本概念" 

# 构造一个通用的 System Prompt 风格的输入
# 我们只需要告诉 Agent 环境的基本事实，不需要针对特定任务写死逻辑
prompt = (
    f"当前任务: {user_input_arxiv}\n\n"
    f"【环境说明】\n"
    f"1. 你拥有一个名为 `execute` 的工具，拥有完全的本地执行权限。\n"
    f"2. 当前 Python 解释器路径: `{PYTHON_EXEC}`。\n"
    f"3. 如果某个技能的 SKILL.md 要求运行脚本，请毫不犹豫地使用 `execute` 工具，并带上 Python 路径。\n"
    f"4. 如果任务不需要运行代码，直接回答或使用其他工具即可。"
)

print("\nAgent 启动...")

result = agent.invoke(
    {
        "messages": [
            {
                "role": "user",
                "content": prompt,
            }
        ]
    },
    config={"configurable": {"thread_id": "mac_session"}},
)

print("\n" + "="*50)
print("最终结果:")
print("="*50)
print(result)
import os
import sys
import subprocess
from dotenv import load_dotenv

# =========================================================================
# 🛑 核心修复：Monkey Patch (在导入 Agent 之前执行)
# =========================================================================
# 我们需要拦截 deepagents 的路径检查函数
import deepagents.middleware.filesystem as fs_module

# 保存原版函数（备份）
_original_validate = fs_module._validate_path

# 定义一个“宽容版”的验证函数
def _windows_friendly_validate(path):
    # 如果是 Windows，直接放行，并统一把反斜杠转为正斜杠，防止后续拼接出错
    if os.name == 'nt':
        return path.replace("\\", "/")
    # 其他系统保持原样
    return _original_validate(path)

# ⚡️ 强行覆盖库的内部函数
print("🔧 应用路径兼容补丁...")
fs_module._validate_path = _windows_friendly_validate
print("✅ 补丁应用成功！")

# =========================================================================
# 正常导入其他模块
# =========================================================================
from deepagents import create_deep_agent
from langgraph.checkpoint.memory import MemorySaver
from langchain_community.chat_models.tongyi import ChatTongyi
from deepagents.backends.filesystem import FilesystemBackend
from langchain_core.tools import tool

load_dotenv()

# =========================================================================
# 1. 路径与工具定义
# =========================================================================
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
PYTHON_EXEC = sys.executable
SKILLS_DIR = os.path.join(BASE_DIR, "skills")

print(f"📂 物理根目录: {BASE_DIR}")

# 定义执行工具
@tool("execute")
def custom_execute(command: str) -> str:
    """
    执行本地命令。自动处理路径转换。
    """
    print(f"\n⚡️ [Agent命令] {command}")
    
    # 路径清理：把 Agent 可能混用的 /skills 替换为真实路径
    # 这一步是为了防止 Agent 传进来虚拟路径，而 subprocess 不认
    cmd_clean = command.replace("\\", "/")
    real_skills = SKILLS_DIR.replace("\\", "/")
    
    if real_skills in cmd_clean:
        print("▶️ [检测到绝对路径] 直接执行，不修改")
        
    # 情况 B: Agent 使用了虚拟绝对路径 (/skills/...)
    elif "/skills/" in cmd_clean:
        # 我们直接去掉开头的 "/"，变成相对路径 "skills/..."
        # 因为 subprocess 设置了 cwd=BASE_DIR，相对路径是最安全的
        cmd_clean = cmd_clean.replace("/skills/", "skills/")
        print(f"🔄 [转为相对路径] {cmd_clean}")
        
    else:
        print("▶️ [常规执行] 不修改")

    try:
        # cwd=BASE_DIR 让相对路径也能工作
        result = subprocess.run(
            cmd_clean,
            shell=True,
            capture_output=True,
            text=True,
            timeout=120,
            cwd=BASE_DIR,  # 关键：设置工作目录为项目根目录
            encoding='utf-8', 
            errors='replace'
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
# 因为我们打了补丁，Agent 现在不会报错了
agent = create_deep_agent(
    model=model,
    backend=FilesystemBackend(root_dir=BASE_DIR),
    skills=["skills"], 
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
    config={"configurable": {"thread_id": "win_patch_session"}},
)

print("\n" + "="*50)
print("最终结果:")
print("="*50)
print(result)
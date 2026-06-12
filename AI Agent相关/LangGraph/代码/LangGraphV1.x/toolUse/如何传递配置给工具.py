# 导入必要的模块和类
from typing import List  # 用于类型提示

from langchain.agents import create_agent
from langchain_core.tools import tool  # 用于创建工具的装饰器
from langchain_core.runnables.config import RunnableConfig  # 用于处理运行配置

# 全局字典，用于存储用户与宠物的关系
user_to_pets = {}


# 定义更新喜爱宠物的工具
@tool  # 装饰器将此函数标记为工具，并解析文档字符串
def update_favorite_pets(
    # 注意：config参数不需要添加到文档字符串中，因为我们不希望它出现在传给LLM的函数签名中
    pets: List[str],  # 用户喜爱的宠物列表
    config: RunnableConfig,  # 运行配置对象，包含用户ID等信息
) -> None:
    """添加喜爱的宠物列表。
    
    Args:
        pets: 要设置的喜爱宠物列表。
    """
    # 从配置中获取用户ID
    user_id = config.get("configurable", {}).get("user_id")
    # 更新用户喜爱的宠物列表
    user_to_pets[user_id] = pets


# 定义删除喜爱宠物的工具
@tool
def delete_favorite_pets(config: RunnableConfig) -> None:
    """删除喜爱的宠物列表。"""
    # 从配置中获取用户ID
    user_id = config.get("configurable", {}).get("user_id")
    # 如果用户存在，则删除其宠物列表
    if user_id in user_to_pets:
        del user_to_pets[user_id]


# 定义列出喜爱宠物的工具
@tool
def list_favorite_pets(config: RunnableConfig) -> None:
    """当被询问时列出喜爱的宠物。"""
    # 从配置中获取用户ID
    user_id = config.get("configurable", {}).get("user_id")
    # 返回用户喜爱的宠物列表，用逗号连接
    return ", ".join(user_to_pets.get(user_id, []))

# 将所有工具放入列表
tools = [update_favorite_pets, delete_favorite_pets, list_favorite_pets]

# 导入聊天模型
from langchain_openai import ChatOpenAI
from dotenv import load_dotenv
load_dotenv()  # 加载环境变量（包括API密钥）
import os

model = ChatOpenAI(
    model_name="deepseek-v3",
    api_key=os.getenv("DASHSCOPE_API_KEY"),
    base_url=os.getenv("API_BASE_URL"),
)

# 创建react代理图
graph = create_agent(model, tools)
graph.get_graph().draw_mermaid_png(output_file_path='../imgs/如何将配置传递给工具.png')
# 导入人类消息类
from langchain_core.messages import HumanMessage

# 清空用户宠物状态
user_to_pets.clear()

# 测试1：设置喜爱的宠物
print("测试1：设置喜爱的宠物:")
print(f"运行前的用户信息: {user_to_pets}")

# 创建输入消息
inputs = {"messages": [HumanMessage(content="我最喜欢的宠物是猫和狗")]}
# 流式处理输入
for chunk in graph.stream(
    inputs, {"configurable": {"user_id": "123"}}, stream_mode="values"
):
    chunk["messages"][-1].pretty_print()  # 打印最后一条消息

print(f"运行后的用户信息: {user_to_pets}")

print()

# 测试2：查询喜爱的宠物
print("测试2：查询喜爱的宠物:")
print(f"运行前的用户信息: {user_to_pets}")

inputs = {"messages": [HumanMessage(content="最喜欢的宠物是什么？")]}
for chunk in graph.stream(
    inputs, {"configurable": {"user_id": "123"}}, stream_mode="values"
):
    chunk["messages"][-1].pretty_print()

print(f"运行后的用户信息: {user_to_pets}")

print()

# 测试3：删除喜爱的宠物信息
print("测试3：删除喜爱的宠物信息:")
print(f"运行前的用户信息: {user_to_pets}")

inputs = {
    "messages": [
        HumanMessage(content="请忘记我告诉你的我最喜欢的动物")
    ]
}
for chunk in graph.stream(
    inputs, {"configurable": {"user_id": "123"}}, stream_mode="values"
):
    chunk["messages"][-1].pretty_print()

print(f"运行后的用户信息: {user_to_pets}")
print()
"""
上小节遗留知识点
「a」TypedDict与Pydantic BaseModel
「b」Schema图模式
「c」Reducers规约器
「d」Conditional Edges条件边
"""
# 导入必要的类型注解和模块
from typing import TypedDict, List  # 用于创建类型化的字典
from langchain_core.messages import AnyMessage, HumanMessage
from langgraph.graph import StateGraph, START, END  # LangGraph的状态图和起始/结束节点
from langchain_openai import ChatOpenAI  # OpenAI聊天模型
import os
from dotenv import load_dotenv  # 用于加载环境变量

load_dotenv()  # 加载.env文件中的环境变量
from pydantic import BaseModel, Field

# 定义状态类型，使用TypedDict来明确状态的结构
# class State(TypedDict):
#     # 消息列表，使用Annotated添加元数据（这里指定了消息处理方式）
#     messages: list[AnyMessage]

class State(BaseModel):
    messages: List[AnyMessage] = Field(default_factory=list)


"""
需求：需要基于LangGraph构建一张图、并且需要让这张图有与AI对话的能力
需求分析：
第一步：首先我需要有一张空白的图--------->构建一张图 「类和对象的关系」
from langgraph.graph import StateGraph
graph_builder = StateGraph(State)

第二步：构建状态-------->对于这张图来说，我可以接收哪些数据类型------->TypedDict「可以对相关性的数据类型进行声明」
class State(TypedDict):
    messages: list[AnyMessage]

第三步：构建相关性的Nodes与Edges
def chatbot(state: State):
    pass

graph_builder.add_node("chatbot", chatbot)

graph_builder.add_edge(START, "chatbot")
graph_builder.add_edge("chatbot", END)

第四步：编译图
graph = graph_builder.compile()


"""

# 创建状态图构建器，传入状态类型
graph_builder = StateGraph(State)


# print(llm.invoke('hi').content)
# exit()

# 定义聊天机器人节点函数
def chatbot(state: State):
    # 初始化OpenAI聊天模型
    llm = ChatOpenAI(
        model="deepseek-chat",
        api_key=os.getenv("DEEPSEEK_API_KEY"),
        base_url=os.getenv("DEEPSEEK_URL")
    )
    # 当 State 是 BaseModel 时，传入节点函数的 state 是一个 State 实例，应使用属性访问 state.messages，
    # 而不是 state['messages']（后者适用于 TypedDict）。
    print(f"聊天机器人节点接收状态：{state.messages}")
    message = llm.invoke(state.messages)
    print(f"大模型答复：{message.content}")
    return {"messages": [message.content]}


# 将聊天机器人节点添加到图中
graph_builder.add_node("chatbot", chatbot)

# 添加图的边（连接关系）：
# 从开始节点连接到聊天机器人节点
graph_builder.add_edge(START, "chatbot")
# 从聊天机器人节点连接到结束节点
graph_builder.add_edge("chatbot", END)

# 编译图，使其可执行
graph = graph_builder.compile()

# 主交互循环
while True:
    try:
        # 获取用户输入
        user_input = input("User: ")
        # 检查退出命令
        if user_input.lower() in ["quit", "exit", "q"]:
            print("Goodbye!")
            break
        # 处理用户输入并获取助手回复
        """在 graph.invoke({"messages": [{"role": "user", "content": user_input}]}) 中，您传入的是一个字典列表。
        虽然Pydantic可能尝试将其转换为 AnyMessage，但更可靠的方式是显式使用 LangChain 的消息类（如 HumanMessage）。"""
        graph.invoke({"messages": [HumanMessage(content=user_input)]})
    except:
        print("系统发生错误，停止!")
        break

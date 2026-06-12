# 导入必要的类型注解和模块
from typing import TypedDict  # 用于创建类型化的字典
from langchain_core.messages import AnyMessage
from langgraph.graph import StateGraph, START, END  # LangGraph的状态图和起始/结束节点
from langchain_openai import ChatOpenAI  # OpenAI聊天模型
import os
from dotenv import load_dotenv  # 用于加载环境变量
load_dotenv()  # 加载.env文件中的环境变量

# 定义状态类型，使用TypedDict来明确状态的结构
class State(TypedDict):
    # 消息列表，使用Annotated添加元数据（这里指定了消息处理方式）
    messages: list[AnyMessage]

# 创建状态图构建器，传入状态类型
graph_builder = StateGraph(State)
# 初始化OpenAI聊天模型
llm = ChatOpenAI(
    model_name="deepseek-chat",
    api_key=os.getenv("DEEPSEEK_API_KEY"),
    base_url=os.getenv("DEEPSEEK_URL")
)

# 定义聊天机器人节点函数
def chatbot(state: State):
    print(f"聊天机器人节点接收状态：{state['messages']}")
    message = llm.invoke(state["messages"])
    print(f"大模型答复：{message}" )
    return {"messages": [message]}

# 将聊天机器人节点添加到图中
graph_builder.add_node("chatbot", chatbot)

# 添加图的边（连接关系）：
# 从开始节点连接到聊天机器人节点
graph_builder.add_edge(START, "chatbot")
# 从聊天机器人节点连接到结束节点
graph_builder.add_edge("chatbot", END)

# 编译图，使其可执行
graph = graph_builder.compile()

# 定义流式处理图更新的函数
def stream_graph_updates(user_input: str):
    # 使用图的流式处理功能，传入用户输入作为初始消息
    for event in graph.stream({"messages": [{"role": "user", "content": user_input}]}):
        # 遍历事件中的值
        for value in event.values():
            print("value:", value)
            # 打印助手的最新回复（消息列表中的最后一条消息内容）
            print("Assistant:", value["messages"][-1].content)

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
        stream_graph_updates(user_input)
    except:
        print("系统发生错误，停止!")
        break
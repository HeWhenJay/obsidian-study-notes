from typing import TypedDict, Annotated, Sequence
from langchain_core.messages import HumanMessage, AIMessage, BaseMessage, SystemMessage, AnyMessage
from langchain_openai import ChatOpenAI
from langgraph.constants import START
from langgraph.graph import StateGraph, END
import operator
import os
from dotenv import load_dotenv
load_dotenv()

model = ChatOpenAI(
    model_name="deepseek-v3",
    api_key=os.getenv("DASHSCOPE_API_KEY"),
    base_url=os.getenv("API_BASE_URL")
)

# ================== 类型定义 ==================
class ChatState(TypedDict):
    messages: Annotated[Sequence[AnyMessage], operator.add]  # 自动合并消息的历史记录

# ================== 节点函数优化 ==================
# def handle_user_input(state: ChatState):
#     """处理用户输入节点"""
#     try:
#         print(f"handle_user_input_node state:{state}")
#         user_input = input("\n用户输入（输入'退出'结束）: ").strip()
#         if user_input.lower() == "退出":
#             print("正在结束对话...")
#             return END
#         # # 保留历史记录并追加新消息
#         # return {"messages": state["messages"] + [HumanMessage(content=user_input)]}
#         return {"messages": [HumanMessage(content=user_input)]}
#     except KeyboardInterrupt:
#         return END

def generate_ai_response(state: ChatState):
    """生成AI响应节点（增加错误处理）"""
    print(f"generate_ai_response_node state:{state}")
    # 使用最近6条消息保持上下文连贯性
    response = model.invoke(state["messages"])
    print("模型答复：",response)
    return {"messages": [response]}

# ================== 对话图构建 ==================
builder = StateGraph(ChatState)
# 节点注册
# builder.add_node("user_input", handle_user_input)
builder.add_node("ai_response", generate_ai_response)
# 流程设计
# builder.set_entry_point("user_input")
builder.add_edge(START, "ai_response")
builder.add_edge("ai_response", END)
# 编译对话图
conversation = builder.compile()
# ================== 运行逻辑优化 ==================
if __name__ == "__main__":
    # 初始化带时间戳的系统提示
    system_prompt = f""" 你好！"""
    state = ChatState(messages=[HumanMessage(content=system_prompt)])
    # 执行对话流程，invoke后图执行一次完成
    result = conversation.invoke(state)
    print("图执行一次后：",result)
        # 提取最新交互记录
    new_messages = result["messages"][len(state["messages"]):]
    # 打印AI响应
    for msg in new_messages:
        if isinstance(msg, AIMessage):
            print(f"\n【AI响应】\n{msg.content}\n")
            # 更新对话状态
    state = result

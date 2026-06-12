from typing import TypedDict
from langgraph.checkpoint.memory import MemorySaver
from langgraph.graph import StateGraph, START
from langgraph.types import Command, interrupt

# 新增模型相关导入
from langchain_core.messages import HumanMessage
from langchain_openai import ChatOpenAI
import os
from dotenv import load_dotenv
load_dotenv()

# 定义状态类型
class State(TypedDict):
    some_text: str

# 初始化大模型
model = ChatOpenAI(
    model_name="deepseek-v3",
    api_key=os.getenv("DASHSCOPE_API_KEY"),
    base_url=os.getenv("API_BASE_URL")
)

# 初始化检查点存储
checkpointer = MemorySaver()

def show_begin_node(state: State):
    print(f"=====>show_begin_node :{state}")

# 改造后的人类介入节点
def human_node(state: State):
    # 接收用户输入并构造新指令
    print(f"human_node :{state}")
    value = interrupt(
        {
            "text_to_revise": state["some_text"],
            "instructions": "human_node要求你输入修改要求："
        }
    )
    print(f"human_node value :{value}")
    # 返回用户输入的内容，而不是Command
    return {"some_text": value}


# 优化后的自动处理节点
def proceed_text(state: State):
    print(f"proceed_text :{state}")
    # 强化格式要求的提示词
    message = model.invoke([
        HumanMessage(content=f'''当前请求：{state["some_text"]}''')
    ])
    return {"some_text": message.content}


# 构建循环工作流
graph_builder = StateGraph(State)
graph_builder.add_node("proceed_text", proceed_text)
graph_builder.add_node("human_review", human_node)
graph_builder.add_node("show_begin_node", show_begin_node)

# 设置循环流程
graph_builder.add_edge(START, "show_begin_node")
graph_builder.add_edge("show_begin_node", "proceed_text")
graph_builder.add_edge("proceed_text", "human_review")
graph_builder.add_edge("human_review", "proceed_text")  # 新增循环连接

# 编译图表
graph = graph_builder.compile(
    checkpointer=checkpointer
)

# 使用示例
if __name__ == "__main__":
    thread_id = "thread_123"
    thread_config = {"configurable": {"thread_id": thread_id}}

    # 初始执行
    initial_state = {"some_text": "使用python语法生成三三乘法表"}
    result = graph.invoke(initial_state, config=thread_config)
    print("初始执行结果:\n", result)
    
    # 检查并显示中断信息
    interrupt_instructions = None
    if "__interrupt__" in result:
        interrupts = result["__interrupt__"]
        if interrupts:  # 确保中断列表不为空
            # 获取第一个中断的信息
            interrupt_value = interrupts[0].value
            interrupt_instructions = interrupt_value['instructions']
            print("中断信息:")
            print(f"  文本范例: {interrupt_value['text_to_revise']}")
            print(f"  提示信息: {interrupt_instructions}")
        else:
            print("中断列表为空")
    else:
        print("没有中断信息")

    # 人类输入环节 (使用Command.resume)
    # 使用中断中的提示信息
    prompt = interrupt_instructions if interrupt_instructions else "请输入修改要求："
    resume_result = graph.invoke(
        Command(resume=input(f"\n{prompt}")),
        config=thread_config
    )
    
    print("\n最终处理结果:\n", resume_result["some_text"])
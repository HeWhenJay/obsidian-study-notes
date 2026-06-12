from typing import Literal
from langchain_core.messages import SystemMessage, RemoveMessage
from langgraph.checkpoint.memory import MemorySaver
from langgraph.graph import MessagesState, StateGraph, START, END
from dotenv import load_dotenv
load_dotenv()
from langchain_openai import ChatOpenAI
import os

memory = MemorySaver()

class State(MessagesState):
    summary: str

from dotenv import load_dotenv
load_dotenv()

model = ChatOpenAI(
    model_name="deepseek-v3",
    api_key=os.getenv("DASHSCOPE_API_KEY"),
    base_url=os.getenv("API_BASE_URL")
)

def call_model(state: State):
    summary = state.get("summary", "")
    if summary:
        system_message = f"Summary of conversation earlier: {summary}"
        messages = [SystemMessage(content=system_message)] + state["messages"]
    else:
        messages = state["messages"]
    response = model.invoke(messages)

    return {"messages": [response]}

# 我们现在定义用于确定是结束还是总结对话的逻辑
def should_continue(state: State) -> Literal["summarize_conversation", END]:
    """返回下一个要执行的节点."""
    messages = state["messages"]
    # 如果有六条以上的消息，那么我们将对对话进行总结
    if len(messages) > 6:
        return "summarize_conversation"
    return END

def summarize_conversation(state: State):
    summary = state.get("summary", "")
    if summary:
        summary_message = (
            f"这是迄今为止的对话摘要: {summary}\n\n"
            "通过考虑上述新消息来扩展摘要:"
        )
    else:
        summary_message = "创建上述对话的摘要:"

    messages = state["messages"] + [HumanMessage(content=summary_message)]
    response = model.invoke(messages)
    delete_messages = [RemoveMessage(id=m.id) for m in state["messages"][:-2]]
    return {"summary": response.content, "messages": delete_messages}


workflow = StateGraph(State)
workflow.add_node("conversation", call_model)
workflow.add_node(summarize_conversation)
workflow.add_edge(START, "conversation")
workflow.add_conditional_edges(
    "conversation",
    should_continue,
)

workflow.add_edge("summarize_conversation", END)

app = workflow.compile(checkpointer=memory)
app.get_graph().draw_mermaid_png(output_file_path='../imgs/添加会话历史摘要.png')

def print_update(update):
    for k, v in update.items():
        for m in v["messages"]:
            m.pretty_print()
        if "summary" in v:
            print(v["summary"])

from langchain_core.messages import HumanMessage

config = {"configurable": {"thread_id": "4"}}
input_message = HumanMessage(content="你好，我是云帆")
input_message.pretty_print()
for event in app.stream({"messages": [input_message]}, config, stream_mode="updates"):
    print_update(event)

input_message = HumanMessage(content="我叫什么名字？")
input_message.pretty_print()
for event in app.stream({"messages": [input_message]}, config, stream_mode="updates"):
    print_update(event)

input_message = HumanMessage(content="我喜欢曼联！")
input_message.pretty_print()
for event in app.stream({"messages": [input_message]}, config, stream_mode="updates"):
    print_update(event)

values = app.get_state(config).values
print(values)

input_message = HumanMessage(content="我喜欢他们总是赢球")
input_message.pretty_print()
for event in app.stream({"messages": [input_message]}, config, stream_mode="updates"):
    print_update(event)

values = app.get_state(config).values
print(values)

input_message = HumanMessage(content="我叫什么名字？")
input_message.pretty_print()
for event in app.stream({"messages": [input_message]}, config, stream_mode="updates"):
    print_update(event)

input_message = HumanMessage(content="你觉得我喜欢哪支英超球队？")
input_message.pretty_print()
for event in app.stream({"messages": [input_message]}, config, stream_mode="updates"):
    print_update(event)
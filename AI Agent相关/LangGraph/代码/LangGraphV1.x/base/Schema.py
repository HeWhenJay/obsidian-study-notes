"""
注意：本程序运行无业务意义，仅展示知识点
"""
from langgraph.graph import StateGraph, START, END
from typing_extensions import TypedDict

"""
from typing import TypedDict, List
class AgentState(TypedDict):
    input: str
    chat_history: List[str]
    intermediate_steps: List[tuple]

from pydantic import BaseModel, Field
from typing import List
class AgentStatePydantic(BaseModel):
    input: str
    chat_history: List[str] = Field(default_factory=list) # 默认为空列表
    retry_count: int = 0 # 默认为0
"""

#定义输入Schema
class InputState(TypedDict):
    question: str

# 定义输出Schema
class OutputState(TypedDict):
    answer: str

# 结合输入和输出，定义总体模式
class OverallState(InputState, OutputState):
    pass

# 定义处理输入并生成答案的节点
# def answer_node(state: InputState):
#     return {"answer": "hello!", "question": state["question"]}

# # 这么使用会报错
def answer_node(state: OverallState):
    return {"answer": state["answer"], "question": state["question"]}


# 使用指定的输入和输出模式构建图形
builder = StateGraph(OverallState, input_schema=InputState, output_schema=OutputState)

builder.add_node(answer_node)

builder.add_edge(START, "answer_node")
builder.add_edge("answer_node", END)

graph = builder.compile()

# print(graph.invoke({"question": "hi"}))
# 可以运行，但是传入的"answer"值不会起作用
print(graph.invoke({"question": "hi","answer": "OK"}))
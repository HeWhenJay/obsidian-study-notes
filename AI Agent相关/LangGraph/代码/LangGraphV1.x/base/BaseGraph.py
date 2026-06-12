"""
注意：本程序运行无业务意义，仅展示知识点
"""
from typing import List
from langchain_core.messages import AnyMessage
from langchain_core.runnables import RunnableConfig
from pydantic import BaseModel, Field
from typing_extensions import TypedDict

# 定义State
class State(TypedDict):
    messages: list[AnyMessage]
    extra_field: int

# #定义State
# class AgentStatePydantic(BaseModel):
#     input: str
#     chat_history: List[str] = Field(default_factory=list) # 默认为空列表
#     retry_count: int = 0

from langgraph.graph import StateGraph, START, END
graph_builder = StateGraph(State)

#定义Node
def process_input_node(state: State, config: RunnableConfig):
    print(f"process_input_node :{state}")
    user_id = config.get("configurable", {}).get("user_id", "default_user")
    print(f"Node 'process_input_node' processing for user: {user_id}")
    return {"process_input": state["extra_field"]+2}

# 定义另一个Node
def another_node(state: State): # 这个节点没有 config 参数
    print(f"another_node :{state}")
    state["extra_field"] = 10
    return {"some_other_data": "done"}

def node_a(state: State):
    print("Called A")
    print(f"node_a :{state}")
    return {"extra_field": state["extra_field"] + 2}

def node_b(state: State):
    print("Called B")
    print(f"node_b :{state}")
    return {"extra_field": state["extra_field"] + 1}

# 路由选择
def route_tools(state: State):
    # 判断是否为偶数（最后一位二进制位为0表示偶数）
    if state["extra_field"] & 1 == 0:
        return "node_b"
    else:
        return "node_a"

graph_builder.add_node("processor", process_input_node) # 节点名为 "processor"
graph_builder.add_node("finalizer", another_node)     # 节点名为 "finalizer"
graph_builder.add_node("node_a", node_a)     # 节点名为 "finalizer"
graph_builder.add_node("node_b", node_b)     # 节点名为 "finalizer"

# 添加图的边（连接关系）：
# 从开始节点连接到业务节点
graph_builder.add_edge(START, "processor")

#Conditional Edges「条件边」:
graph_builder.add_conditional_edges('processor', route_tools, {"node_b": "node_b", "node_a": "node_a"})


graph_builder.add_edge("node_a", END)
graph_builder.add_edge("node_b", "finalizer")

# 从业务节点连接到结束节点
graph_builder.add_edge("finalizer", END)


#  顺序型的节点增加
# graph_builder = StateGraph(State).add_sequence([process_input_node, another_node])
# graph_builder.add_edge(START, "processor")

# 编译图
graph = graph_builder.compile()

print(graph.invoke({"messages": ["My", "name"], "extra_field": 2}))
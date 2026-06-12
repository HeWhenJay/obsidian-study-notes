from typing import Annotated, get_type_hints, get_origin, get_args
from typing_extensions import TypedDict
from operator import add  # 用于列表拼接的操作符函数
from langgraph.graph import StateGraph, START, END

# # 定义状态类型，使用TypedDict明确字段类型
# class StateWithoutAdd(TypedDict):
#     # foo字段为整数类型，更新时直接替换
#     foo: int
#     # bar字段为字符串列表
#     bar: list[str]

# def example_node(state: StateWithoutAdd):
#     return {"bar": ["done"]}

# graph_builder = StateGraph(StateWithoutAdd)

# 定义状态类型，使用TypedDict明确字段类型
class State(TypedDict):
    # foo字段为整数类型，更新时直接替换
    foo: int
    # bar字段为字符串列表，使用Annotated标注合并策略为add（列表拼接）
    bar: Annotated[list[str], add]  # map高阶函数


graph_builder = StateGraph(State)

# def example_node(state: State):
#     return {"bar": ["done"]}

def example_node(state: State):
    print(state)
    print(state["bar"] + ["OK"])
    return {"bar":state["bar"] + ["OK"]}

graph_builder.add_node("example_node", example_node)
graph_builder.add_edge(START, "example_node")
graph_builder.add_edge("example_node", END)
graph = graph_builder.compile()
print(graph.invoke({"bar": ["My", "name"], "foo": 1}))

# def get_reducers() -> dict[str, callable]:
#     """获取状态字段的合并策略映射表
#     通过解析State的类型注解，提取字段的合并函数（如add）
#     返回形如 {'foo': None, 'bar': operator.add} 的字典
#     """
#     reducers = {}
#     # 获取State的类型提示，包含元数据（Annotated信息）
#     type_hints = get_type_hints(State, include_extras=True)
#     print(type_hints)
#     for key, hint in type_hints.items():
#         origin = get_origin(hint)  # 获取类型注解的原始类型（如Annotated）
#         if origin is Annotated:
#             args = get_args(hint)  # 分解Annotated的参数
#             # 取第一个参数为实际类型，第二个为合并函数（如add）
#             if len(args) >= 2:
#                 reducers[key] = args[1]
#             else:
#                 reducers[key] = None
#         else:
#             reducers[key] = None  # 无合并策略则设为None
#     return reducers
#
# def update_state(current_state: State, update: dict) -> State:
#     """更新状态字典，支持字段级合并策略
#     根据get_reducers()中的策略：
#     - 若字段有合并函数（如add），则用该函数合并新旧值
#     - 否则直接替换为新值
#     注意：直接修改并返回current_state（需传入拷贝以避免副作用）
#     """
#     reducers = get_reducers()
#     for key, new_value in update.items():
#         if key in current_state:
#             current_value = current_state[key]
#             reducer = reducers.get(key)
#             if callable(reducer):
#                 # 使用合并函数（如add(current_value, new_value)）
#                 current_state[key] = reducer(current_value, new_value)
#             else:
#                 current_state[key] = new_value  # 直接替换
#         else:
#             current_state[key] = new_value  # 新增字段
#     return current_state
#
#
# # 测试示例
# if __name__ == "__main__":
#     # 初始化状态（注意TypedDict只是类型提示，实际仍为普通字典）
#     initial_state: State = {"foo": 1, "bar": ["hi"]}
#     print("初始状态:", initial_state)  # {'foo': 1, 'bar': ['hi']}
#
#     # 第一次更新：直接替换foo字段
#     update1 = {"foo": 2}
#     # 传入拷贝以避免修改原始状态
#     new_state = update_state(initial_state.copy(), update1)
#     print("第一次更新后:", new_state)  # {'foo': 2, 'bar': ['hi']}
#
#     # 第二次更新：使用add合并bar字段（列表拼接）
#     update2 = {"bar": ["bye"]}
#     new_state = update_state(new_state.copy(), update2)
#     print("第二次更新后:", new_state)  # {'foo': 2, 'bar': ['hi', 'bye']}
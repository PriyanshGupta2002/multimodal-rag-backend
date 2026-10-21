from langgraph.graph import START, END, StateGraph
from langgraph.checkpoint.base import BaseCheckpointSaver

from app.workflow.state import RAGState
from app.workflow.nodes import retrieve_node, generate_node


def build_workflow(
    checkpointer: BaseCheckpointSaver,
):
    builder = StateGraph(RAGState)

    builder.add_node("retrieve", retrieve_node)
    builder.add_node("generate", generate_node)

    builder.add_edge(START, "retrieve")
    builder.add_edge("retrieve", "generate")
    builder.add_edge("generate", END)

    return builder.compile(checkpointer=checkpointer)

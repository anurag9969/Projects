from typing import TypedDict, Dict, Any
from langgraph.graph import StateGraph, END

from agents.semantic_listner import semantic_analyze

from agents.listener import analyze_decision
from agents.simulator import simulate_future
from agents.critic import critique_decision
from agents.scorer import score_risk
from agents.gatekeeper import gate_decision

# ---------------------------
# GRAPH STATE
# ---------------------------

class GuardianState(TypedDict):
    decision: Any
    listener_output: Dict
    simulation_output: Dict
    critic_output: Dict
    scoring_output: Dict
    verdict: Dict


# ---------------------------
# NODE FUNCTIONS
# ---------------------------

def listener_node(state: GuardianState):
    decision = state["decision"]

    output = analyze_decision(decision)

    # ✅ Add semantic intelligence
    semantic = semantic_analyze(decision.decision_text)
    output.update(semantic)

    return {
        **state,
        "listener_output": output,
        "decision": decision,
    }



def simulator_node(state: GuardianState):
    output = simulate_future(
        state["decision"],
        state["listener_output"]
    )

    return {
        **state,
        "simulation_output": output,
    }


def critic_node(state: GuardianState):
    output = critique_decision(
        state["decision"],
        state["listener_output"],
        state["simulation_output"],
    )

    return {
        **state,
        "critic_output": output,
    }


def scorer_node(state: GuardianState):
    output = score_risk(
        state["listener_output"],
        state["critic_output"],
    )

    return {
        **state,
        "scoring_output": output,
    }


def gatekeeper_node(state: GuardianState):
    verdict = gate_decision(
        state["scoring_output"],
        state["listener_output"],   # <-- pass listener output
    )

    return {
        **state,
        "verdict": verdict,
    }



# ---------------------------
# BUILD GRAPH
# ---------------------------

def build_guardian_graph():
    graph = StateGraph(GuardianState)

    graph.add_node("listener", listener_node)
    graph.add_node("simulator", simulator_node)
    graph.add_node("critic", critic_node)
    graph.add_node("scorer", scorer_node)
    graph.add_node("gatekeeper", gatekeeper_node)

    graph.set_entry_point("listener")

    graph.add_edge("listener", "simulator")
    graph.add_edge("simulator", "critic")
    graph.add_edge("critic", "scorer")
    graph.add_edge("scorer", "gatekeeper")
    graph.add_edge("gatekeeper", END)

    return graph.compile()

from langgraph.graph import StateGraph, START, END
from typing import Optional, List, Dict, Any, TypedDict

from src.agents.flow_discovery_agent import FlowDiscoveryAgent
from src.agents.script_generator_agent import ScriptGeneratorAgent
from src.agents.execution_agent import ExecutionAgent
from src.agents.error_diagnosis_agent import ErrorDiagnosisAgent
from src.agents.adaptive_repair_agent import AdaptiveRepairAgent
from src.agents.regression_monitor_agent import RegressionMonitorAgent


# -------------------------
# State definition
# -------------------------
class WorkflowState(TypedDict, total=False):
    url: str
    flows: Optional[List[Dict[str, Any]]]
    selected_flow: Optional[Dict[str, Any]]
    script: Optional[str]
    execution_result: Optional[Dict[str, Any]]
    diagnosis: Optional[str]
    repaired_script: Optional[str]
    regression_result: Optional[Dict[str, Any]]
    error_count: int
    max_retries: int


# -------------------------
# Agent instances
# -------------------------
flow_agent = FlowDiscoveryAgent()
script_agent = ScriptGeneratorAgent()
exec_agent = ExecutionAgent()
diagnosis_agent = ErrorDiagnosisAgent()
repair_agent = AdaptiveRepairAgent()
regression_agent = RegressionMonitorAgent()


# -------------------------
# Node implementations
# -------------------------
def discover_flow_node(state: WorkflowState) -> Dict[str, Any]:
    result = flow_agent.discover(state["url"])
    updates = {"flows": result.get("flows", [])}

    if updates["flows"]:
        updates["selected_flow"] = updates["flows"][0]

    return updates


def generate_script_node(state: WorkflowState) -> Dict[str, Any]:
    flow = state.get("selected_flow")
    if not flow:
        return {}

    flow_description = (
        f"Name: {flow['name']}\n"
        f"Description: {flow['description']}\n"
        f"Steps: {', '.join(flow['steps'])}"
    )

    return {"script": script_agent.generate_script(flow_description)}


def execute_script_node(state: WorkflowState) -> Dict[str, Any]:
    if not state.get("script"):
        return {}

    result = exec_agent.execute(state["script"])

    updates = {"execution_result": result}

    if not result.get("success"):
        updates["error_count"] = state.get("error_count", 0) + 1

    return updates


def diagnose_error_node(state: WorkflowState) -> Dict[str, Any]:
    stderr = state.get("execution_result", {}).get("stderr", "")

    if stderr and is_non_repairable_error(stderr):
        return {
            "diagnosis": "Non-repairable syntax error detected",
        }

    if stderr:
        return {
            "diagnosis": diagnosis_agent.diagnose(stderr)
        }

    return {}


def repair_script_node(state: WorkflowState) -> Dict[str, Any]:
    if not state.get("diagnosis") or not state.get("script"):
        return {}

    repaired = repair_agent.repair(state["script"], state["diagnosis"])
    return {
        "script": repaired,
        "repaired_script": repaired
    }


def compare_regression_node(state: WorkflowState) -> Dict[str, Any]:
    # Optional placeholder
    return {}


# -------------------------
# Routing logic
# -------------------------
def route_after_execution(state: WorkflowState) -> str:
    result = state.get("execution_result", {})
    stderr = result.get("stderr", "")

    # ✅ Success → move forward
    if result.get("success") is True:
        return "compare"

    # ❌ Non-repairable → STOP
    if stderr and is_non_repairable_error(stderr):
        print("❌ Non-repairable error detected. Exiting workflow.")
        return "compare"

    # 🔁 Retry limit reached → STOP
    if state.get("error_count", 0) >= state.get("max_retries", 3):
        return "compare"

    # 🔧 Repairable failure → try fix
    return "diagnose"


def is_non_repairable_error(stderr: str) -> bool:
    NON_REPAIRABLE_ERRORS = [
        "IndentationError",
        "SyntaxError",
        "TabError",
        "ImportError",
        "ModuleNotFoundError"
    ]

    return any(err in stderr for err in NON_REPAIRABLE_ERRORS)


# -------------------------
# Build the graph
# -------------------------
workflow = StateGraph(WorkflowState)

workflow.add_node("discover", discover_flow_node)
workflow.add_node("generate", generate_script_node)
workflow.add_node("execute", execute_script_node)
workflow.add_node("diagnose", diagnose_error_node)
workflow.add_node("repair", repair_script_node)
workflow.add_node("compare", compare_regression_node)

workflow.add_edge(START, "discover")
workflow.add_edge("discover", "generate")
workflow.add_edge("generate", "execute")

workflow.add_conditional_edges(
    "execute",
    route_after_execution,
    {
        "compare": "compare",
        "diagnose": "diagnose"
    }
)

workflow.add_edge("diagnose", "repair")
workflow.add_edge("repair", "execute")
workflow.add_edge("compare", END)

graph = workflow.compile()

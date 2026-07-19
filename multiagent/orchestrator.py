# pipeline/orchestrator.py
# Copyright (c) 2026 Sergey Postnikov. All rights reserved.

import logging
import json
import time
from typing import Dict, Any, List, TypedDict
from langgraph.graph import StateGraph, END

from agents.classifier import ClassifierAgent
from agents.quality import QualityAgent
from agents.compliance import ComplianceAgent
from agents.summarizer import SummarizerAgent


# === Логирование ===
logger = logging.getLogger("orchestrator")


def log_agent_step(agent_name: str, input_data: Any, output_data: Any):
    """Логирование входа и выхода каждого агента в JSON-формате."""
    log_data = {
        "timestamp": time.time(),
        "agent": agent_name,
        "input_segments": len(input_data) if isinstance(input_data, list) else 1,
        "output_keys": list(output_data.keys()) if isinstance(output_data, dict) else type(output_data).__name__
    }
    logger.info(json.dumps(log_data, ensure_ascii=False))


# === Определение состояния ===
class AgentState(TypedDict):
    transcript: List[Dict[str, Any]]
    classification: Dict[str, Any]
    quality_score: Dict[str, Any]
    compliance: Dict[str, Any]
    summary: str
    action_items: List[str]


class AgentOrchestrator:
    """
    Оркестратор Multi-Agent системы на базе LangGraph.
    Поддерживает передачу llm_client (Groq / Ollama).
    """

    def __init__(self, llm_client):
        self.llm_client = llm_client

        # Инициализируем агентов
        self.classifier = ClassifierAgent(llm_client)
        self.quality = QualityAgent(llm_client)
        self.compliance = ComplianceAgent(llm_client)
        self.summarizer = SummarizerAgent(llm_client)

        self.graph = self._build_graph()

    def _build_graph(self) -> StateGraph:
        """Строит граф агентов."""
        workflow = StateGraph(AgentState)

        workflow.add_node("classifier", self._classifier_node)
        workflow.add_node("quality", self._quality_node)
        workflow.add_node("compliance", self._compliance_node)
        workflow.add_node("summarizer", self._summarizer_node)

        workflow.set_entry_point("classifier")
        workflow.add_edge("classifier", "quality")
        workflow.add_edge("quality", "compliance")
        workflow.add_edge("compliance", "summarizer")
        workflow.add_edge("summarizer", END)

        return workflow.compile()

    # === Узлы графа ===

    async def _classifier_node(self, state: AgentState) -> AgentState:
        result = await self.classifier.run(state["transcript"])
        log_agent_step("classifier", state["transcript"], result)
        state["classification"] = result
        return state

    async def _quality_node(self, state: AgentState) -> AgentState:
        result = await self.quality.run(state["transcript"])
        log_agent_step("quality", state["transcript"], result)
        state["quality_score"] = result
        return state

    async def _compliance_node(self, state: AgentState) -> AgentState:
        result = await self.compliance.run(state["transcript"])
        log_agent_step("compliance", state["transcript"], result)
        state["compliance"] = result
        return state

    async def _summarizer_node(self, state: AgentState) -> AgentState:
        result = await self.summarizer.run(state["transcript"])
        log_agent_step("summarizer", state["transcript"], result)
        state["summary"] = result["summary"]
        state["action_items"] = result["action_items"]
        return state

    async def run(self, transcript: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Запуск оркестрации."""
        initial_state: AgentState = {
            "transcript": transcript,
            "classification": {},
            "quality_score": {},
            "compliance": {},
            "summary": "",
            "action_items": [],
        }

        result = await self.graph.ainvoke(initial_state)
        return result

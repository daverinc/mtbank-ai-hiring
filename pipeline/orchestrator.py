# Copyright (c) 2026 Sergey Postnikov. All rights reserved.
# Данное решение выполнено исключительно для рассмотрения кандидатуры на вакансию.

from typing import Dict, Any, List, TypedDict
from langgraph.graph import StateGraph, END

from core.llm.base import LLMClient
from agents.classifier import ClassifierAgent
from agents.quality import QualityAgent
from agents.compliance import ComplianceAgent
from agents.summarizer import SummarizerAgent


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
    Оркестратор Multi-Agent системы.
    Получает готовый LLMClient (Groq или Ollama) и передаёт его агентам.
    """

    def __init__(self, llm_client: LLMClient):
        self.llm_client = llm_client

        # Создаём агентов, передавая им LLMClient
        self.classifier = ClassifierAgent(llm_client)
        self.quality = QualityAgent(llm_client)
        self.compliance = ComplianceAgent(llm_client)
        self.summarizer = SummarizerAgent(llm_client)

        self.graph = self._build_graph()

    def _build_graph(self) -> StateGraph:
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
        state["classification"] = result
        return state

    async def _quality_node(self, state: AgentState) -> AgentState:
        result = await self.quality.run(state["transcript"])
        state["quality_score"] = result
        return state

    async def _compliance_node(self, state: AgentState) -> AgentState:
        result = await self.compliance.run(state["transcript"])
        state["compliance"] = result
        return state

    async def _summarizer_node(self, state: AgentState) -> AgentState:
        result = await self.summarizer.run(state["transcript"])
        state["summary"] = result["summary"]
        state["action_items"] = result["action_items"]
        return state

    async def run(self, transcript: List[Dict[str, Any]]) -> Dict[str, Any]:
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

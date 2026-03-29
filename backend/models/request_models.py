from pydantic import BaseModel
from typing import Literal, Any

ScenarioId = Literal["S1", "S2", "S3", "S4", "S5", "S6", "S7"]


class AgentRunRequest(BaseModel):
    scenario_id: ScenarioId
    params: dict[str, Any] = {}

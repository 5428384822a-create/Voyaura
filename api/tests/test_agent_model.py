"""Explicit HTTP transport doubles, never evidence of live DeepSeek execution."""

import json

import httpx
import pytest

from app.agent.tools import AgentSettings, ToolTrace, model_intent


def test_optional_model_sends_only_current_goal_not_private_memory(monkeypatch):
    captured = []
    original_client = httpx.Client

    def handler(request):
        assert str(request.url) == "https://api.deepseek.com/chat/completions"
        captured.append(json.loads(request.content))
        return httpx.Response(
            200, json={"choices": [{"message": {"content": '{"keywords":["博物馆"]}'}}]}
        )

    monkeypatch.setattr(
        "app.agent.tools.httpx.Client",
        lambda **kwargs: original_client(transport=httpx.MockTransport(handler), **kwargs),
    )
    trace = ToolTrace()
    result = model_intent(
        {"city_name": "测试城市", "goal": "喜欢博物馆", "source_memories": "PRIVATE TEST MEMORY"},
        trace,
        AgentSettings(llm_enabled=True, llm_api_key="explicit-test-key"),
    )
    assert result == ["博物馆"]
    assert "PRIVATE TEST MEMORY" not in json.dumps(captured)
    assert all("longitude" not in item for item in result)
    assert trace.events[-1]["status"] == "succeeded"


@pytest.mark.parametrize(
    "content", ["[]", '{"keywords":[{"longitude":113}]}', '{"keywords":["a","b","c","d"]}']
)
def test_model_cannot_supply_unrestricted_structured_facts(monkeypatch, content):
    original_client = httpx.Client
    transport = httpx.MockTransport(
        lambda request: httpx.Response(200, json={"choices": [{"message": {"content": content}}]})
    )
    monkeypatch.setattr(
        "app.agent.tools.httpx.Client",
        lambda **kwargs: original_client(transport=transport, **kwargs),
    )
    trace = ToolTrace()
    result = model_intent(
        {"city_name": "测试城市", "goal": "测试目标"},
        trace,
        AgentSettings(llm_enabled=True, llm_api_key="explicit-test-key"),
    )
    assert result is None
    assert trace.events[-1]["status"] == "error"
    assert trace.events[-1]["details"]["code"] == "AGENT_TOOL_INVALID_RESPONSE"

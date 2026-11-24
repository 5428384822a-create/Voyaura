from __future__ import annotations

import json
import logging
from functools import lru_cache
from typing import Literal, Protocol

from langchain_core.prompts import ChatPromptTemplate
from langchain_deepseek import ChatDeepSeek
from pydantic import SecretStr

from app.config import Settings, settings
from app.errors import AppError
from app.xiaoxi_planning import ModelPlanningDraft

logger = logging.getLogger("voyaura.xiaoxi")

SYSTEM_PROMPT = """
你是 Voyaura 的旅行需求分析助手小曦。你的任务不是生成最终行程，而是：
1. 从用户原话和已确认上下文中提取结构化旅行需求；
2. 提出一小组需要交给高德地图核验的景点名称假设；
3. 生成覆盖不同主题的高德 POI 检索关键词。

严格规则：
- 已确认上下文的优先级高于用户本轮消息，不得擅自修改。
- 用户没有明确提供城市或天数时必须保留 null，不得猜测。
- 不输出坐标、行政区代码、开放时间、门票、排队时间、评分、交通耗时等事实。
- 景点名称只是待核验假设，不得宣称一定存在、开放或适合当天访问。
- 必去和排除项只来自用户明确表达，不能代替用户做决定。
- 兼顾热门、长尾和兴趣主题；不要只列网红景点。
- 城市或天数缺失时，attraction_hypotheses 和 search_themes 返回空数组。
- 使用简体中文，内容简洁、可解释。
""".strip()

PROMPT = ChatPromptTemplate.from_messages(
    [
        ("system", SYSTEM_PROMPT),
        (
            "human",
            (
                "已确认上下文（JSON，null 表示尚未确认）：\n{confirmed_context}\n\n"
                "用户本轮消息：\n{message}"
            ),
        ),
    ]
)


class TravelPlanningExtractor(Protocol):
    provider: Literal["deepseek"]
    model: str
    available: bool

    def extract(self, message: str, confirmed_context: dict[str, object]) -> ModelPlanningDraft: ...


class DeepSeekPlanningExtractor:
    provider: Literal["deepseek"] = "deepseek"

    def __init__(self, config: Settings) -> None:
        self.model = config.deepseek_model
        self.available = bool(config.deepseek_api_key.strip())
        self._chain = None
        if self.available:
            llm = ChatDeepSeek(
                model=config.deepseek_model,
                api_key=SecretStr(config.deepseek_api_key),
                base_url=config.deepseek_base_url,
                temperature=config.deepseek_temperature,
                timeout=config.deepseek_timeout_seconds,
                max_retries=config.deepseek_max_retries,
                max_tokens=2_500,
            )
            structured = llm.with_structured_output(
                ModelPlanningDraft,
                method="function_calling",
            )
            self._chain = PROMPT | structured

    def extract(self, message: str, confirmed_context: dict[str, object]) -> ModelPlanningDraft:
        if not self.available or self._chain is None:
            raise AppError(
                "DEEPSEEK_KEY_MISSING",
                "小曦尚未配置 DeepSeek API Key。",
                status_code=503,
                details={"setting": "VOYAURA_DEEPSEEK_API_KEY"},
            )
        try:
            result = self._chain.invoke(
                {
                    "message": message,
                    "confirmed_context": json.dumps(
                        confirmed_context,
                        ensure_ascii=False,
                        sort_keys=True,
                    ),
                }
            )
        except AppError:
            raise
        except Exception as exc:
            error_name = type(exc).__name__
            error_key = error_name.casefold()
            logger.warning("deepseek_planning_failed error_type=%s", error_name)
            if "authentication" in error_key or "permission" in error_key:
                code, message, status_code, retryable = (
                    "DEEPSEEK_AUTH_ERROR",
                    "DeepSeek 凭证无效或没有模型访问权限。",
                    503,
                    False,
                )
            elif "rate" in error_key:
                code, message, status_code, retryable = (
                    "DEEPSEEK_RATE_LIMIT",
                    "DeepSeek 请求过于频繁，请稍后重试。",
                    429,
                    True,
                )
            elif "timeout" in error_key:
                code, message, status_code, retryable = (
                    "DEEPSEEK_TIMEOUT",
                    "DeepSeek 响应超时，请稍后重试。",
                    504,
                    True,
                )
            elif "outputparser" in error_key or "validation" in error_key:
                code, message, status_code, retryable = (
                    "DEEPSEEK_OUTPUT_INVALID",
                    "DeepSeek 没有返回符合旅行规划契约的结构化结果。",
                    502,
                    True,
                )
            else:
                code, message, status_code, retryable = (
                    "DEEPSEEK_PROVIDER_ERROR",
                    "DeepSeek 当前无法完成旅行需求分析。",
                    502,
                    True,
                )
            raise AppError(
                code,
                message,
                status_code=status_code,
                retryable=retryable,
                details={"provider": self.provider, "error_type": error_name},
            ) from exc
        if not isinstance(result, ModelPlanningDraft):
            raise AppError(
                "DEEPSEEK_OUTPUT_INVALID",
                "DeepSeek 没有返回符合旅行规划契约的结构化结果。",
                status_code=502,
                retryable=True,
                details={"provider": self.provider},
            )
        return result


@lru_cache
def get_travel_planning_extractor() -> TravelPlanningExtractor:
    return DeepSeekPlanningExtractor(settings)

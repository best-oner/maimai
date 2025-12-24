"""
缩写翻译工具

提供中文网络缩写词汇翻译功能
"""

from typing import Any, Dict, List, Tuple

from src.common.logger import get_logger
from src.plugin_system import BaseTool, ToolParamType

from ..translators.nbnhhsh import NbnhhshTranslator

logger = get_logger("nbnhhsh_abbreviation_tool")


class AbbreviationTool(BaseTool):
    """独立的神奇海螺缩写翻译工具"""

    name: str = "abbreviation_translate"
    description: str = (
        "当遇到用户消息中出现难懂的网络用语、缩写、黑话、热词或流行语时，"
        "主动查询并翻译这些词汇以帮助理解。适用于各种类型的网络语言，包括字母缩写"
        "（如 yyds、u1s1）、网络黑话、当下热词、流行语等。应该识别消息中可能让人困惑的"
        "网络用语并自动查询其含义。"
    )
    parameters: List[Tuple[str, ToolParamType, str, bool, None]] = [
        ("term", ToolParamType.STRING, "从用户消息中识别出的网络用语、缩写或热词（如：yyds、躺平、内卷等）。", True, None),
        ("max_results", ToolParamType.INTEGER, "返回翻译结果数量，默认为 3。", False, None),
    ]
    available_for_llm: bool = True

    translator: NbnhhshTranslator

    def __init__(self, *args: Any, **kwargs: Any) -> None:
        super().__init__(*args, **kwargs)
        self._initialize_translator()

    def _initialize_translator(self) -> None:
        """初始化翻译器实例"""
        translation_config = self.plugin_config.get("translation", {})
        self.translator = NbnhhshTranslator(translation_config)

    async def execute(self, function_args: Dict[str, Any]) -> Dict[str, str]:
        """执行缩写翻译"""
        try:
            term = function_args.get("term", "").strip()
            max_results = function_args.get("max_results", 3)

            if not term:
                return {"name": self.name, "content": "未提供要翻译的词汇"}

            if not self.plugin_config.get("translation", {}).get("enabled", True):
                return {"name": self.name, "content": "翻译功能已禁用"}

            logger.info(f"[nbnhhsh] 主动翻译检测到的词汇: {term}")

            result = await self.translator.translate(term)
            if not result.translations:
                return {"name": self.name, "content": f"未找到「{term}」的翻译结果"}

            try:
                limit = int(max_results)
                if limit <= 0:
                    limit = 1
            except (TypeError, ValueError):
                limit = 3

            translations = result.translations[:limit]

            if len(translations) == 1:
                content = f"网络用语「{term}」的含义是：{translations[0]}"
            else:
                content = "网络用语「{term}」的可能含义：\n".format(term=term)
                content += "\n".join(f"• {trans}" for trans in translations)

            logger.info(f"[nbnhhsh] 主动翻译完成: {term} -> {len(translations)} 个结果")
            return {"name": self.name, "content": content}

        except Exception as exc:
            logger.error(f"缩写翻译执行异常: {exc}", exc_info=True)
            return {"name": self.name, "content": f"缩写翻译失败: {exc}"}


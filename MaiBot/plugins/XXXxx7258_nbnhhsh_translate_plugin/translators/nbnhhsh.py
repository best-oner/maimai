"""
神奇海螺缩写翻译器

基于神奇海螺 API 的中文网络缩写翻译服务：
https://lab.magiconch.com/api/nbnhhsh/
"""

import asyncio
import re
from typing import Any, Dict, List, Optional

import aiohttp

from src.common.logger import get_logger

from .base import BaseTranslator, TranslationResult

logger = get_logger("nbnhhsh_translator")


class NbnhhshTranslator(BaseTranslator):
    """神奇海螺缩写翻译器"""

    def __init__(self, config: Optional[Dict[str, Any]] = None):
        super().__init__(config)
        self.api_url = self.config.get("api_url", "https://lab.magiconch.com/api/nbnhhsh/guess")
        self.timeout = self.config.get("timeout", 10)
        self.max_retries = self.config.get("max_retries", 3)

    @property
    def name(self) -> str:
        return "nbnhhsh"

    async def translate(self, query: str) -> TranslationResult:
        """翻译缩写词"""
        if not query:
            return TranslationResult(query=query, translations=[], source=self.name)

        cached = self._get_from_cache(query)
        if cached:
            logger.info("从缓存获取翻译结果: %s", query)
            return cached

        translations = await self._call_api(query)
        result = TranslationResult(query=query, translations=translations, source=self.name)
        if translations:
            self._save_to_cache(result)

        logger.info("翻译完成: %s -> %s", query, translations)
        return result

    async def _call_api(self, query: str) -> List[str]:
        """调用神奇海螺 API"""
        payload = {"text": query}
        headers = {"Content-Type": "application/json"}
        client_timeout = aiohttp.ClientTimeout(total=self.timeout)

        for attempt in range(1, self.max_retries + 1):
            try:
                async with aiohttp.ClientSession(timeout=client_timeout) as session:
                    async with session.post(self.api_url, json=payload, headers=headers) as response:
                        if response.status != 200:
                            logger.warning("API 请求失败，状态码: %s", response.status)
                            continue

                        data = await response.json()
                        if not data:
                            return []

                        first_item = data[0]
                        translations = first_item.get("trans") or []
                        return [str(item) for item in translations]

            except asyncio.TimeoutError:
                logger.warning("API 请求超时，第 %s/%s 次尝试", attempt, self.max_retries)
            except aiohttp.ClientError as exc:
                logger.error("API 请求错误，第 %s/%s 次尝试: %s", attempt, self.max_retries, exc)
            except Exception as exc:  # noqa: BLE001
                logger.exception("API 请求异常，第 %s/%s 次尝试: %s", attempt, self.max_retries, exc)

            if attempt < self.max_retries:
                await asyncio.sleep(attempt)  # 简单的递增退避

        return []

    @staticmethod
    def is_abbreviation_query(query: str) -> bool:
        """判断查询是否匹配缩写询问模式"""
        pattern = r"^([a-z0-9]{2,})(?:是什么|是啥)$"
        return bool(re.match(pattern, query.lower().strip()))

    @staticmethod
    def extract_abbreviation(query: str) -> Optional[str]:
        """从查询语句中提取缩写"""
        pattern = r"^([a-z0-9]{2,})(?:是什么|是啥)$"
        match = re.match(pattern, query.lower().strip())
        return match.group(1) if match else None


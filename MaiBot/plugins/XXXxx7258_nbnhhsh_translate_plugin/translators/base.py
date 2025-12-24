"""
基础翻译器抽象类

定义所有翻译器的通用接口和基础功能。
"""

from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Any, Dict, List, Optional
import time


@dataclass
class TranslationResult:
    """翻译结果数据结构"""

    query: str
    translations: List[str]
    source: str
    cached: bool = False
    timestamp: float = 0.0

    def __post_init__(self) -> None:
        if self.timestamp == 0.0:
            self.timestamp = time.time()


class BaseTranslator(ABC):
    """翻译器基础抽象类"""

    def __init__(self, config: Optional[Dict[str, Any]] = None):
        self.config = config or {}
        self.cache: Dict[str, Any] = {}
        self.cache_ttl = self.config.get("cache_ttl", 3600)  # 默认缓存 1 小时
        self.max_cache_size = self.config.get("cache_size", 1000)

    @abstractmethod
    async def translate(self, query: str) -> TranslationResult:
        """执行翻译操作"""
        raise NotImplementedError

    @property
    @abstractmethod
    def name(self) -> str:
        """翻译器名称"""
        raise NotImplementedError

    def _get_from_cache(self, query: str) -> Optional[TranslationResult]:
        """从缓存获取结果"""
        entry = self.cache.get(query)
        if not entry:
            return None

        result, timestamp = entry
        if time.time() - timestamp > self.cache_ttl:
            del self.cache[query]
            return None

        return TranslationResult(
            query=result.query,
            translations=result.translations,
            source=result.source,
            cached=True,
            timestamp=result.timestamp,
        )

    def _save_to_cache(self, result: TranslationResult) -> None:
        """保存结果到缓存"""
        if len(self.cache) >= self.max_cache_size:
            oldest_key = min(self.cache, key=lambda key: self.cache[key][1])
            del self.cache[oldest_key]

        self.cache[result.query] = (result, time.time())

    def clear_cache(self) -> None:
        """清空缓存"""
        self.cache.clear()

    def get_cache_stats(self) -> Dict[str, Any]:
        """获取缓存统计信息"""
        return {
            "cache_size": len(self.cache),
            "max_cache_size": self.max_cache_size,
            "cache_ttl": self.cache_ttl,
        }


"""
神奇海螺缩写翻译插件入口

提供独立的神奇海螺缩写翻译工具，便于在主系统中按需启用或禁用。
"""

from typing import List, Tuple, Type

from src.plugin_system import (
    BasePlugin,
    register_plugin,
    ComponentInfo,
    ConfigField,
)
from src.common.logger import get_logger

from .tools.abbreviation_tool import AbbreviationTool

logger = get_logger("nbnhhsh_translate_plugin")


@register_plugin
class NbnhhshTranslatePlugin(BasePlugin):
    """神奇海螺缩写翻译插件"""

    plugin_name: str = "nbnhhsh_translate_plugin"
    enable_plugin: bool = True
    dependencies: List[str] = []
    python_dependencies: List[str] = ["aiohttp"]
    config_file_name: str = "config.toml"

    config_section_descriptions = {
        "plugin": "插件基本信息",
        "translation": "翻译服务配置",
    }

    config_schema = {
        "plugin": {
            "name": ConfigField(type=str, default="nbnhhsh_translate_plugin", description="插件名称"),
            "version": ConfigField(type=str, default="1.0.0", description="插件版本"),
            "enabled": ConfigField(type=bool, default=True, description="是否启用插件"),
        },
        "translation": {
            "enabled": ConfigField(type=bool, default=True, description="是否启用翻译功能"),
            "api_url": ConfigField(type=str, default="https://lab.magiconch.com/api/nbnhhsh/guess", description="神奇海螺 API 地址"),
            "timeout": ConfigField(type=int, default=10, description="请求超时时间（秒）"),
            "max_retries": ConfigField(type=int, default=3, description="请求最大重试次数"),
            "cache_ttl": ConfigField(type=int, default=3600, description="缓存有效期（秒）"),
            "cache_size": ConfigField(type=int, default=1000, description="缓存条目上限"),
        },
    }

    def on_plugin_load(self) -> None:
        """插件加载时输出配置摘要"""
        plugin_enabled = self.get_config("plugin.enabled", True)
        translation_enabled = self.get_config("translation.enabled", True)
        logger.info(
            "神奇海螺缩写翻译插件加载完成，插件启用：%s，翻译功能启用：%s",
            plugin_enabled,
            translation_enabled,
        )

    def get_plugin_components(self) -> List[Tuple[ComponentInfo, Type]]:
        """返回插件组件列表"""
        return [
            (AbbreviationTool.get_tool_info(), AbbreviationTool),
        ]


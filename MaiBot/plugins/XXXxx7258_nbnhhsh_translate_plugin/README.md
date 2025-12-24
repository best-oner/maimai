# 神奇海螺缩写翻译插件

独立的神奇海螺缩写翻译工具，封装自原谷歌搜索插件中的缩写翻译能力。插件提供一个可供 LLM 调用的工具 `abbreviation_translate`，用于查询中文网络缩写、黑话与热门词汇的含义。

## 功能特点

- 基于 [神奇海螺 API](https://lab.magiconch.com/api/nbnhhsh/) 的缩写翻译能力  
- 内置缓存与重试机制，提升稳定性  
- 可通过配置文件自定义接口地址、超时和重试次数  
- 与其它插件完全解耦，可独立启用或禁用

## 配置说明

编辑 `config.toml` 可调整下列参数：

```toml
[plugin]
enabled = true            # 是否启用插件

[translation]
api_url = "https://lab.magiconch.com/api/nbnhhsh/guess"  # 神奇海螺 API 地址
timeout = 10             # 请求超时时间（秒）
max_retries = 3          # 最大重试次数
cache_ttl = 3600         # 缓存有效期（秒）
cache_size = 1000        # 缓存条目上限
```

## 组件

- `abbreviation_translate`：网络缩写翻译工具，支持参数：
  - `term`（必填）：需要翻译的缩写或词语
  - `max_results`（选填）：返回的最大翻译条目数，默认 3

## 依赖

- Python 包：`aiohttp`

安装依赖：

```bash
pip install -r requirements.txt
```


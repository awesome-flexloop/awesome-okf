---
type: Reference
title: mdurl 源码路径映射
description: mdurl 核心源文件路径、职责与关键代码位置索引，覆盖全部6个Python模块
tags: [mdurl, markdown, url, source, reference]
generated: { by: "reference_agent/trae-cn", at: "2026-08-23T01:00:00Z" }
status: stable
stale_after: 2027-08-23
sources:
  - id: mdurl-repo
    resource: https://github.com/executablebooks/mdurl
    title: mdurl GitHub Repository
---

# mdurl 源码路径映射

本文档为 mdurl 源码的文件级索引，标注每个核心文件的路径、职责和关键代码。源路径相对于 `external/libs/ai/executablebooks/mdurl/`。

## 项目元数据

| 属性 | 值 |
|------|-----|
| 名称 | mdurl |
| 版本 | 0.1.2 |
| 描述 | Markdown URL utilities |
| 许可证 | MIT |
| Python 要求 | >=3.10 |
| 构建系统 | flit_core >=3.2.0,<4 |
| 第三方运行时依赖 | 无（仅标准库） |
| 项目主页 | https://github.com/executablebooks/mdurl |

## 核心文件清单

| 文件 | 行数 | 职责 | 关键代码 |
|------|------|------|---------|
| `src/mdurl/__init__.py` | 18 行 | 包入口，公共API导出 | `__all__` L1-11、`__version__` L12、导入重导出 L14-18 |
| `src/mdurl/_url.py` | 32 行 | URL 不可变数据结构定义 | `URL` namedtuple L20-31、TYPE_CHECKING类型标注 L9-17 |
| `src/mdurl/_decode.py` | 108 行 | URL 百分号解码 | `decode()` L37-40、`get_decode_cache()` L17-32、`repl_func_with_cache()` L43-108、`DECODE_DEFAULT_CHARS` L11、`DECODE_COMPONENT_CHARS` L12 |
| `src/mdurl/_encode.py` | 90 行 | URL 百分号编码 | `encode()` L50-89、`get_encode_cache()` L22-41、`ENCODE_DEFAULT_CHARS` L14、`ENCODE_COMPONENT_CHARS` L15 |
| `src/mdurl/_format.py` | 26 行 | URL namedtuple 格式化为字符串 | `format()` L8-25 |
| `src/mdurl/_parse.py` | 303 行 | URL 字符串解析为 URL namedtuple | `MutableURL` 类 L105-293、`url_parse()` L296-303、正则/常量表 L53-102 |

## 公共 API 一览

| API | 来源模块 | 签名 |
|-----|---------|------|
| `URL` | `_url.py` | `namedtuple`，字段：protocol, slashes, auth, port, hostname, hash, search, pathname |
| `parse` | `_parse.py` | `url_parse(url: URL \| str, *, slashes_denote_host: bool = False) -> URL` |
| `format` | `_format.py` | `format(url: URL) -> str` |
| `encode` | `_encode.py` | `encode(string: str, exclude: str = ENCODE_DEFAULT_CHARS, *, keep_escaped: bool = True) -> str` |
| `decode` | `_decode.py` | `decode(string: str, exclude: str = DECODE_DEFAULT_CHARS) -> str` |
| `ENCODE_DEFAULT_CHARS` | `_encode.py` | `str` = `";/?:@&=+$,-_.!~*'()#"` |
| `ENCODE_COMPONENT_CHARS` | `_encode.py` | `str` = `"-_.!~*'()"` |
| `DECODE_DEFAULT_CHARS` | `_decode.py` | `str` = `";/?:@&=+$,#"` |
| `DECODE_COMPONENT_CHARS` | `_decode.py` | `str` = `""` |

## 构建与配置文件

| 文件 | 说明 |
|------|------|
| `pyproject.toml` | 项目元数据、依赖声明、pytest/tox/mypy/coverage 配置 |
| `LICENSE` | MIT 许可证文本 |
| `README.md` | 项目简介 |

## 测试文件

| 文件 | 说明 |
|------|------|
| `tests/test_decode.py` | decode 函数测试 |
| `tests/test_encode.py` | encode 函数测试 |
| `tests/test_format.py` | format 函数测试 |
| `tests/test_parse.py` | parse 函数测试 |
| `tests/decode.js` | JavaScript 参考测试用例 |
| `tests/fixtures/url.py` | URL 测试固件数据 |

## 相关概念

- [mdurl 简介](/concepts/00-introduction.md)
- [URL 数据结构](/concepts/01-url-data-structure.md)
- [URL 解析与格式化](/concepts/02-parse-and-format.md)
- [URL 编码与解码](/concepts/03-encode-and-decode.md)

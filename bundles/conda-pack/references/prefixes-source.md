---
type: Reference
title: prefixes.py 前缀替换模块源码
description: conda-pack 前缀替换模块源码索引，包含文本/二进制前缀替换、shebang 正则、macOS codesign 处理、Windows distlib 入口点替换。
tags: [conda-pack, source, prefixes, binary-patching]
generated: { by: "reference_agent/trae-glm", at: "2026-08-21T05:40:00Z" }
verified: { by: "process:seven-concepts-v", at: "2026-08-21T06:00:00Z" }
status: stable
stale_after: 2027-12-31
sources:
  - id: conda-pack-prefixes
    resource: conda_pack/prefixes.py
    title: conda-pack prefixes.py
---

# prefixes.py 前缀替换模块源码

`conda_pack/prefixes.py` 是前缀替换模块（约196行），大部分代码借鉴自 `conda/core/portability.py`，实现了文本和二进制文件中的路径前缀替换。

## 关键定义

| 定义 | 行号 | 说明 |
|------|------|------|
| `on_win` | L44 | 平台检测：`sys.platform == 'win32'` |
| `SHEBANG_REGEX` | L47-L58 | shebang 正则（bytes），三个捕获组：完整shebang、可执行路径、选项 |
| `update_prefix(path, new_prefix, placeholder, mode)` | L61-L87 | 对外接口：读取文件→替换前缀→写回；macOS arm64 自动 codesign |
| `replace_prefix(data, mode, placeholder, new_prefix)` | L90-L106 | 调度函数：根据 mode 调用 text_replace 或 binary_replace |
| `text_replace(data, placeholder, new_prefix)` | L109-L122 | 文本模式前缀替换（简单 bytes.replace） |

## 二进制替换

### Unix 二进制替换（L135-L148）

- 使用正则 `re.escape(placeholder) + b'([^\0]*?)\0'` 匹配以 null 结尾的前缀字符串
- 替换后用 null 字节填充到原长度（`padding = (len(placeholder) - len(new_prefix)) * occurances`）
- **约束**：新前缀长度必须 ≤ 旧前缀长度（否则抛出 ValueError）
- 保证二进制文件中字符串偏移不变，避免破坏相对地址引用

### Windows 二进制替换（L126-L132）

- 检测 placeholder 是否存在，存在则调用 `replace_pyzzer_entry_point_shebang()`
- 也处理小写匹配的 placeholder
- 专门处理 distlib 生成的入口点 exe 文件

### replace_pyzzer_entry_point_shebang()（L151-L196）

- 代码源自 pyzzer（Vinay Sajip），处理 distlib 入口点 exe 格式：
  - 格式：`[launcher][shebang][zip archive]`
  - 通过 ZIP End of Central Directory Record (`PK\x05\x06`) 定位 zip 起始位置
  - 在 launcher 和 zip 之间找到 `#!` 开头的 shebang
  - 替换 shebang 中的前缀路径，重新拼接三部分

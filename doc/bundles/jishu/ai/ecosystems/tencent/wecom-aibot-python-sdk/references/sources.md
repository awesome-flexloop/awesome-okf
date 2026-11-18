---
type: reference
title: wecom-aibot-python-sdk 信源登记
description: 上游地址、固定 commit、许可证、文件清单、版本双口径与可复现的核对命令
tags: [wecom, aibot, python-sdk, sources]
generated: { by: okf-wiki/0.2, at: 2026-11-09 }
status: stable
verified: { by: "process:seven-concepts-v", at: "2026-11-09" }
stale_after: 2027-11-09
sources:
  - resource: vendor/WecomTeam/wecom-aibot-python-sdk/
---

# 信源登记

本知识包的全部技术断言只来自一处上游仓库的固定快照，不引入官方在线文档或二手转述。凡本包与上游不一致，以上游该 commit 的工作树为准。

## 上游坐标

| 项目 | 取值 |
|---|---|
| 上游仓库 | `git@github.com:WecomTeam/wecom-aibot-python-sdk.git` |
| 浏览地址 | `https://github.com/WecomTeam/wecom-aibot-python-sdk` |
| 固定 commit | `6bcb59a9a636c566f4c6ea5268b228e3def1611a` |
| 本包基线路径 | `vendor/WecomTeam/wecom-aibot-python-sdk/` |
| 许可证 | MIT（`LICENSE` 第 1 行 `MIT License`，第 3 行 `Copyright (c) 2026 WeCom`，F-005） |
| 受控文件数 | 19 个（排除 `.git`；根目录 8、`aibot/` 9、`examples/` 2，F-059） |
| 包名 | `wecom-aibot-python-sdk`（F-001） |
| 最低 Python | `>=3.8`，classifiers 覆盖 3.8 至 3.13（F-003） |
| 开发状态 | `Development Status :: 4 - Beta`（F-003） |

## 版本双口径

同一快照存在两个不相等的版本字符串，必须并置理解：

| 口径 | 位置 | 取值 | 适用场景 |
|---|---|---|---|
| 打包元数据 | `pyproject.toml:7` | `1.0.1` | `pip` / 构建产物 / 依赖解析（F-002） |
| 运行期自述 | `aibot/__init__.py:7` | `1.0.0` | `aibot.__version__` 探测（F-008） |
| 示例日志 | `examples/comparison_test.py:441` | `1.0.0` | 启动日志中的 `version` 字段（F-009） |

结论：`pip show wecom-aibot-python-sdk` 与 `python -c "import aibot; print(aibot.__version__)"` 会给出不同答案。撰写问题单或兼容性说明时，应同时注明两个值，不要只引用其一。

## 核对命令

以下命令均为只读操作，在仓库根目录执行；PowerShell 与 POSIX shell 均可复现。

```bash
# 1. 确认上游与固定点
git -C vendor/WecomTeam/wecom-aibot-python-sdk remote -v
git -C vendor/WecomTeam/wecom-aibot-python-sdk rev-parse HEAD

# 2. 确认版本双口径
grep -n '^version' vendor/WecomTeam/wecom-aibot-python-sdk/pyproject.toml
grep -n '__version__' vendor/WecomTeam/wecom-aibot-python-sdk/aibot/__init__.py

# 3. 确认受控文件数为 19（排除 .git）
find vendor/WecomTeam/wecom-aibot-python-sdk -type f -not -path '*/.git/*' | wc -l

# 4. 确认许可证
head -3 vendor/WecomTeam/wecom-aibot-python-sdk/LICENSE
```

PowerShell 等价写法：

```powershell
git -C vendor/WecomTeam/wecom-aibot-python-sdk rev-parse HEAD
Get-ChildItem -Recurse -Force vendor/WecomTeam/wecom-aibot-python-sdk -File |
  Where-Object { $_.FullName -notmatch '\\.git\\' } | Measure-Object
```

## 关键信源文件清单

| 文件 | 职责 | 本包主要引用的事实 |
|---|---|---|
| `pyproject.toml` | 包元数据、依赖、构建后端 | F-001 ~ F-007、F-010、F-011 |
| `requirements.txt` / `MANIFEST.in` | 运行依赖镜像与打包清单 | F-011 |
| `LICENSE` | MIT 许可证正文 | F-005 |
| `aibot/__init__.py` | 17 项公开导出与 `__version__` | F-008、F-009、F-012、F-013 |
| `aibot/types.py` | `WsCmd`、`MessageType`、`EventType`、`TemplateCardType`、`WSClientOptions`、`WsFrame`、`Logger` 协议 | F-015、F-016、F-029 ~ F-035、F-055 |
| `aibot/ws.py` | 连接、认证、心跳、重连、串行回复队列、回执处理 | F-019 ~ F-028、F-039 ~ F-043 |
| `aibot/client.py` | `WSClient` 门面：回复、流式、卡片、下载、事件注册 | F-014、F-036 ~ F-038、F-043 ~ F-046、F-050、F-056 |
| `aibot/message_handler.py` | 入站帧校验与事件分发 | F-047 ~ F-049 |
| `aibot/api.py` | `aiohttp` 文件下载、`Content-Disposition` 解析 | F-018、F-021、F-051、F-052 |
| `aibot/crypto_utils.py` | AES-256-CBC 解密与手写去填充 | F-053、F-054 |
| `aibot/utils.py` | `generate_req_id` / `generate_random_string` | F-032 |
| `aibot/logger.py` | 默认 stderr 日志实现 | F-017 |
| `examples/basic.py` | 连接事件、文本/图片/文件/事件回调示例 | F-057 |
| `examples/comparison_test.py` | 卡片、流式卡片、主动发送、三阶段流式示例 | F-058 |

未纳入信源：`README.md`、`COMPARISON.md`、`.env.example`、`.gitignore` 仅用于交叉印证配置与示例变量（F-056、F-059），其叙述性内容不作为独立技术断言来源。

## 引用与再分发

MIT 许可证允许复制、修改与再分发，但须保留版权与许可声明。本包正文为二次创作的技术解读，不复制上游大段源码；代码片段仅用于说明调用方式。若上游后续提交改变协议字段或默认值，本包以 `stale_after: 2027-11-09` 为复核期限，过期后应重新采集事实。
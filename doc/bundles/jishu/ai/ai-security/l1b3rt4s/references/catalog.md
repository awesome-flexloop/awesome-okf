---
type: reference
title: L1B3RT4S 档案编目参考
description: |
  L1B3RT4S 仓库 44 个文件的完整编目：34 个厂商 .mkd 档案的文件名、字节规模、主题锚点与
  攻击技术类别归属（T 编号），加 10 个杂项研究文件（README、LICENSE、glitch token 数据库、
  指令别名集、Unicode 隐写载体群）的用途注记，附核验深度标记与计数断言。
tags:
  - ai-security
  - jailbreak-research
  - archive-catalog
  - l1b3rt4s
sources:
  - elder-plinius/L1B3RT4S 上游仓库（https://github.com/elder-plinius/L1B3RT4S ，git HEAD 64960b783249d36f76a48a33103cc4b168332b9b，仅以只读 git 命令读取）
  - 本地事实清单 facts-l1b3rt4s.md（F-L1-001~055，2026-09-02 采集）
  - 跨仓库洞察 insights.md（洞察 1/3/6/7）
---

# L1B3RT4S 档案编目参考

本参考对 elder-plinius/L1B3RT4S 仓库（git HEAD `64960b7`）全部 44 个文件做一次性编目 (F-L1-008)。编目只登记**文件名、字节规模、结构形态与技术类别归属**，不收录任何条目正文；类别归属使用本束[攻击技术分类学](../concepts/attack-taxonomy.md)定义的 T1–T10 编号。

## 信源与读取方式

- **上游地址**：https://github.com/elder-plinius/L1B3RT4S （AGPL-3.0 许可，F-L1-004）
- **本地只读副本**：`external/dao/action/elder-plinius/L1B3RT4S`。注意：该工作树的 44 个文件在 git 状态中全部为已删除状态，内容仅存于 git 对象库 (F-L1-005)
- **读取方式**：`git ls-tree -r -l HEAD`（文件清单与字节数）、`git show HEAD:<file>`（内容）、`git rev-parse HEAD`（版本锚点）；全程未执行 checkout/restore/clean 等改变工作树的命令 (F-L1-006)
- **版本锚点**：HEAD commit `64960b783249d36f76a48a33103cc4b168332b9b`，近期提交主题含 “Update XAI.mkd”“Update synthetic dataset generation prompts” 等 (F-L1-001)

## 仓库总体构成

| 构成 | 数量 | 说明 |
|---|---|---|
| 厂商/实体 .mkd | 34 | 攻击面档案主体，逐厂商组织 (F-L1-009) |
| 非厂商 .mkd | 5 | `-MISCELLANEOUS-`、`1337`、`SYSTEMPROMPTS`、`TOKEN80M8`、`TOKENADE` |
| JSON | 2 | `!SHORTCUTS.json`、`*SPECIAL_TOKENS.json` |
| TXT | 1 | `#MOTHERLOAD.txt` |
| README.md | 1 | 隐写载体形态的仓库门面 (F-L1-002/003) |
| LICENSE | 1 | AGPL-3.0 全文 (F-L1-004) |
| **合计** | **44** | 与 `git ls-tree -r` 计数一致 (F-L1-008) |

其中 5 个文件名以 ASCII 特殊字符开头（`!`、`#`、`*`、`-` 与数字 `1`），在目录列表中前置排列 (F-L1-007)。

## 厂商档案清单（34 个 .mkd）

类别编号对照：T1 角色框架｜T2 虚构授权修辞｜T3 编码混淆｜T4 分词器层对抗｜T5 多轮递进与合成数据诱导｜T6 双响应与输出仪式｜T7 通道与工具中介｜T8 Unicode 隐写载体｜T9 模板复用与指纹｜T10 防御反转与提取。

核验深度标记：**D** = R 阶段逐文件深读（事实清单 D/E 节给出结构级登记）；**M** = 标记级核验（仅采集章节标题行与指纹标记计数，未读条目正文）；“独立条目” 指未命中任何已知指纹族的文件。

| # | 文件 | 字节 | 主题锚点 | 类别归属 | 核验 |
|---|---|---|---|---|---|
| 1 | `AAA.mkd` | 147 | 通用多模态条目（图像内嵌指令提取） | T7 | D (F-L1-041) |
| 2 | `ALIBABA.mkd` | 6,178 | QWEN 系列逐版本 8 章节 | T9、T6、T3 | M (F-L1-045) |
| 3 | `AMAZON.mkd` | 981 | Nova/Rufus 产品条目 | T9、T3 | M |
| 4 | `ANTHROPIC.mkd` | 35,290 | Claude 逐版本 14 章节 | T1、T3、T5、T6、T9 | D (F-L1-020~024) |
| 5 | `APPLE.mkd` | 889 | Apple Intelligence（经系统写作工具中转） | T7 | D (F-L1-042) |
| 6 | `BRAVE.mkd` | 1,645 | Leo 浏览器 | T9、T6 | M |
| 7 | `CHATGPT.mkd` | 897 | ChatGPT 产品（无章节标题） | T9、T6 | M |
| 8 | `COHERE.mkd` | 256 | Command R+ | T9、T3 | M |
| 9 | `CURSOR.mkd` | 751 | Composer（IDE 代理） | T9、T6 | M |
| 10 | `DEEPSEEK.mkd` | 5,455 | V3.2/V3.1/R1 等 6 章节 | T3、T6 | D (F-L1-036/037) |
| 11 | `FETCHAI.mkd` | 869 | ASI1-Mini | T9 | M |
| 12 | `GOOGLE.mkd` | 20,354 | Gemini/Gemma 15 章节 | T6、T9、T3、T7 | D (F-L1-029~031) |
| 13 | `GRAYSWAN.mkd` | 515 | Cygnet 1.0 | 独立条目（未命中已知指纹族） | M |
| 14 | `GROK-MEGA.mkd` | 97,121 | Grok 系多重编码变体集 | T3、T9 | D (F-L1-040) |
| 15 | `HUME.mkd` | 530 | Hume EVI | 独立条目（未命中已知指纹族） | M |
| 16 | `INCEPTION.mkd` | 809 | Mercury | T9 | M |
| 17 | `INFLECTION.mkd` | 191 | Pi 产品 | T9（三行最简样本） | D (F-L1-044) |
| 18 | `LIQUIDAI.mkd` | 302 | LiquidAI | T1（最小化构造样本） | D (F-L1-043) |
| 19 | `META.mkd` | 3,834 | Llama 逐版本 5 章节 | T10、T6 | D (F-L1-034) |
| 20 | `MICROSOFT.mkd` | 173 | Copilot | T3（二进制编码） | D (F-L1-035) |
| 21 | `MIDJOURNEY.mkd` | 1,104 | Midjourney V6 | 独立条目（未命中已知指纹族） | M |
| 22 | `MISTRAL.mkd` | 1,641 | Mistral Large 系 3 章节 | T9、T6 | M |
| 23 | `MOONSHOT.mkd` | 1,493 | Kimi K2 | T9、T3 | D (F-L1-038) |
| 24 | `MULTION.mkd` | 11,564 | MultiOn 浏览器代理 | T10、T9、T6 | M |
| 25 | `NOUS.mkd` | 1,802 | Hermes 3/4 | T9、T6、T3 | M |
| 26 | `NVIDIA.mkd` | 1,821 | Nemotron 系 | T9、T3 | M |
| 27 | `OPENAI.mkd` | 13,336 | GPT 系 21 条目 | T5、T2、T7、T3、T9 | D (F-L1-025~028) |
| 28 | `PERPLEXITY.mkd` | 1,040 | Perplexity | T9、T6 | M |
| 29 | `REFLECTION.mkd` | 943 | Reflection 70B | T9、T6 | M |
| 30 | `REKA.mkd` | 563 | Reka Core | T3、T6 | M |
| 31 | `WINDSURF.mkd` | 1,051 | SWE-1（IDE 代理） | T9、T6 | M |
| 32 | `XAI.mkd` | 7,443 | Grok 系 8 章节 | T9、T2、T7 | D (F-L1-032/033) |
| 33 | `ZAI.mkd` | 4,179 | GLM 系 6 章节 | T9、T6 | D (F-L1-039) |
| 34 | `ZYPHRA.mkd` | 481 | Zamba 7B | T9 | M |

**分布观察**：命中 `T9`（模板复用指纹族）的文件占绝对多数；`T3`（编码混淆）为第二普遍要素 (F-L1-048)；三个 “独立条目”（GRAYSWAN/HUME/MIDJOURNEY）规模均在 1.2KB 以下，说明小文件既可能是极简模板也可能是完全独立的构造——不能以文件大小推断归属。

## 杂项与特殊文件（10 个）

| 文件 | 字节 | 用途注记 | 类别/性质 |
|---|---|---|---|
| `README.md` | 24,071 | 可见内容仅约 51 字符（标签、社区链接、署名），其余为不可见 Unicode 字符——门面文件本身即隐写载体 | T8 (F-L1-002/003) |
| `LICENSE` | 34,523 | GNU AGPL-3.0 全文，含第 13 条远程网络交互条款 | 许可 (F-L1-004) |
| `*SPECIAL_TOKENS.json` | 55,437 | 自称 “AGGREGLITCH v1.0.0” 的 glitch token 编目数据库：登记 7,895 个 token、8 类异常行为、5 类分词器，附学术/工业引源列表 | T4（结构化研究数据库）(F-L1-014/015) |
| `!SHORTCUTS.json` | 10,859 | `!` 前缀指令别名集，元素三键 name/definition/category，类别含 “Core Liberation” 等；含系统提示词提取类与动态指令生成类条目 | T10 (F-L1-016) |
| `#MOTHERLOAD.txt` | 2,239 | 无害叙事短文 + 词间嵌入大量不可见 Unicode 变体选择符——载体与无害内容混合交付形态 | T8 (F-L1-013) |
| `-MISCELLANEOUS-.mkd` | 20,327 | 通用模板集三章：虚构图书馆框架的 JSON 角色模板、预测追问的递进应答模板、XML 结构化情绪角色框架 | T1、T9 (F-L1-019) |
| `1337.mkd` | 35 | 单行 leetspeak 转换元指令（不含具体目标）——编码混淆的最小微件 | T3 (F-L1-018) |
| `SYSTEMPROMPTS.mkd` | 37,059 | 各厂商产品系统提示词原文汇编（Mistral Le Chat、OpenAI o1、Anthropic UserStyle 等）——提取成果档案，非攻击模板 | T10（提取档案）(F-L1-012) |
| `TOKEN80M8.mkd` | 23,448,666 | 单行 emoji + 海量 Unicode Tag 字符（U+E0000–E007F），可见文本近零——最大隐写载体 | T8 (F-L1-017) |
| `TOKENADE.mkd` | 1,867,310 | 与 TOKEN80M8 同构的第二载体（单行 emoji + Unicode Tag） | T8 (F-L1-017) |

## 已知指纹要素速查

| 指纹要素 | 形态描述 | 分布证据 |
|---|---|---|
| `LOVE PLINY` divider | 作者署名式装饰分隔串，含反斜杠/竖线等分隔符变体 | F-L1-047；V 阶段以 `git grep -E "LOVE[ \|/\\\\-]*PLINY" HEAD` 复核：34 个厂商 .mkd 中 16 个命中（另 `-MISCELLANEOUS-.mkd` 亦命中，共 17 文件，2026-09-02） |
| `GODMODE` 开关声明 | 以 “开关已启用” 仪式化措辞出现的术语，衍生 GODMODE MINI/Universal 等变体 | F-L1-020/047 |
| `{Z}` 变量占位符 | 目标查询的参数化占位，使模板成为可复用框架 | F-L1-028/047 |
| `<|vq_*|>` 伪 token | 仿特殊标记语法的伪 token 字样 | F-L1-028/047 |
| `RESET_CORTEX` + `!OMNI` | 模板前奏与虚构平行宇宙协议，跨厂商同源 | F-L1-030/038/039/046 |
| 拒绝禁令句式 | 要求模型不得输出道歉/拒绝类语句的规则行 | F-L1-043/047/050 |
| 字数/字符下限 | 强制应答长度（如 >420 词、>3000 字符等） | F-L1-050 |

## 计数断言

以下数量陈述均经独立命令复核，供 V 阶段比对：

1. 仓库文件总数 **44** = 34 厂商 .mkd + 5 非厂商 .mkd + 2 JSON + 1 TXT + README + LICENSE (F-L1-008，`git ls-tree -r` 计数复核一致)
2. 最大文件 `TOKEN80M8.mkd` **23,448,666 字节**；次大 `TOKENADE.mkd` **1,867,310 字节** (F-L1-010)
3. `*SPECIAL_TOKENS.json` 登记编目 token **7,895** 个、行为分类 **8** 类、分词器覆盖 **5** 类 (F-L1-014/015)
4. `README.md` blob **24,071 字节**、可见字符约 **51** 个（不可见占比 >99%）(F-L1-003)
5. `LICENSE` 为 AGPL-3.0 全文 **34,523 字节** (F-L1-004)
6. 以 `#` 开头行数（含代码块内）：SYSTEMPROMPTS 46、GOOGLE 28、OPENAI 21、ANTHROPIC 20、GROK-MEGA 20 等 (F-L1-011)

## 相关文档

- [攻击技术分类学](../concepts/attack-taxonomy.md) — T1–T10 类别定义与机制
- [攻击面研究定位与档案形态](../concepts/mission-attack-research.md) — 仓库定位与两大形态
- [束索引](../index.md) — 本束导航与用途限定声明

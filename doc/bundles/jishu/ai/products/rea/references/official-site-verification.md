---
type: Reference
title: "REA 中文官网第四轮验证记录"
description: "官网覆盖、固定版本命令与数量回验，以及公开教学算法的本机验证边界"
sources:
  - id: site
    resource: official-site-source.md
  - id: facts
    resource: facts.md
  - id: source
    resource: https://github.com/morluto/rea/tree/eaf88aca2af2b8ad7a277c09d0b45f6e2de8ac4a
generated: {by: "process:seven-concepts-v", at: "2026-10-12"}
status: draft
---

# REA 中文官网第四轮验证记录

## 证据分层

官网为 2026-10-12 在线快照，技术文档与公开教学模块固定到 REA 6.4.0 提交 `eaf88aca2af2b8ad7a277c09d0b45f6e2de8ac4a`。多数历史案例使用 REA 4.1.0，Aegis 使用 6.1.0；网页与该仓库的证据文件属于同一上游，不算独立来源。

本轮未安装 REA、反编译器、Electron 或求解器，未执行被分析的 APK、Windows Calculator、CTF 二进制、原游戏或 Notion。下面的算法验证只运行公开教学 JavaScript 与独立 Python 计算，不能替代原目标验证。

## 覆盖与固定版本回验

| 对象 | 手段与结果 | 限制 |
|---|---|---|
| 中文官网 | W01~W17 台账；sitemap 与逐页内部链接去重集合均为 17，双向差集为空 | 排除其他语言、图片与下载资源；未 OCR 图片，未操作网页实验 |
| docs 文件 | 固定提交 `git ls-tree -r --name-only <commit> docs` 筛选 `.md`，结果 48 | 文件数不自动证明每文件逐字通读；旧 49 已纠正 |
| 客户端 | 固定 `SupportedClients.ts` 定义数组：name 匹配 18、唯一 18、unsupported 1 | 17 文件型配置；Grok Bot 为手动账户连接器 |
| Node 与 CI | engines 为 `^22.19.0 \|\| ^24.11.0 \|\| >=26.0.0`；多数 CI job 读 `.nvmrc` 24.18.0，路径专项 22.19.0 | package 是 Linux/macOS x64/arm64 平台矩阵，不是三个 Node 主版本矩阵 |
| MCP profile | `docs/mcp-contracts.md` 默认 full；compact 每个广告输入 schema 预算 13,312 字节 | 不压缩 Evidence，不改变 canonical 验证、输出 schema、工具全集 |
| 引擎轨道 | F-124 分开记录 Ghidra 12.1.x、Hopper 6.1.0-demo FAT 工作流、IDA Windows/macOS headless 轨道 | 不泛化到全部 loader、版本或架构；真实 HTTP supervisor 未验证 |

官网 IDA 页面称 Linux/macOS headless 未验证；固定 6.4.0 文档另列 macOS arm64 IDA Professional 9.1 build 9.1.250226。两者分别归因（F-139/F-124），不静默合并。

## 命令形态回验

| 调用或字段 | 核对依据 | 本轮修正 |
|---|---|---|
| setup / doctor | 官网 W02/W03、固定 installation 文档 | latest、确认计划、重启；setup 不等于全局 PATH 安装 |
| function / decompile | `src/cli/coreBinaryCommands.ts` | 目标 path 加 address 或 --procedure；删除无依据 --function |
| analyze JavaScript 与后续投影 | JS 技术文档、对应 CLI 注册 | 完整成功 Evidence 输入，先生成再调用；去除虚构 from 请求 |
| Web source location | `docs/web-source-location.md` | 六位置参数；map URL 是解析上下文，不触发网络获取 |
| Electron inspect | `src/cli/electronCommands.ts` | endpoint 与 targetId 必填；与主动场景分开 |
| Electron capture | Electron 文档、inputJson 注册 | 内联 JSON 或文件；启动目标并管理生命周期，当前示例输入未构造 |
| Harmony projection | `docs/harmony-analysis.md` | 包装完整 inventory Evidence，不能只取 normalized_result |
| Firmware extract | 固件文档、`src/cli/firmwareCommands.ts` | offset/length 成对；输出不存在、父目录存在；写文件与 complete 范围明确 |
| 空义务台账 | `docs/reconstruction-obligation-ledger.md` | 合法空请求只演示接口；预期 unknown 未本机执行，digest 不证明闭合 |
| 工具发现 | `docs/mcp-contracts.md` | tools/list 返回定义/schema；binary_session 返回身份、绑定及可用性 |

Apple projection 与 Electron scenario 仅作接口示意；未提供目标、生产级 Evidence 或场景请求时，不声称是独立可复现的完整工程。

## 本机教学验证

2026-10-12 使用既有 py314 与 Node，复跑教学验证脚本，观察到：

```text
speed rule passed
percentage summary passed
public OTP vectors passed
id,title
1,"Hello, ""REA"""
CTF=26 equations; Numeric=PASS; OTP=133 Python/WebCrypto; Dino=5; TutorialJS=4 PASS
```

- TOTP：独立 Python HMAC-SHA1 对照官网 WebCrypto；0~120 秒的 121 项，加六项 RFC SHA1 八位向量及六项六位结果，共 133 项一致。只使用公开测试 key。
- 恐龙：五个更新次数输入 0/1000/4000/7000/10000，对照 `simulateSpeed`；最后值 13.000999999997896，保留浮点与先比较后相加语义。
- 教学代码：官网实验页三块 JavaScript 与 Notes formatter 一块均执行成功；未启动 Electron。
- CTF：AST 读取公开 solve.py 的 RUNS/TARGETS，不导入或运行 solver；36 字符候选满足 26 个方程，不证明唯一解或原程序接受。
- 数量算术：DX-Ball 641×5=3205 与 63 字节闭区间、TH04 两范围 503/包围 517/extent 2139 字节、CTF 624/104 字节等均通过断言；不等于重新编译或重新运行原目标。

## 文档门禁

2026-10-12 导航完成后的实施者自验：

- UTF-8 无 BOM、YAML、sources 与官方 toctree 扫描通过：`Markdown=31 Facts=180 Unique=180`。
- 在子项目工作目录运行主仓链接检查器，实际扫描 31 文件、169 内联链接，其中 155 本地引用全部存在；14 外链未在该检查器中测试。主仓工作目录第一次扫描被 projects 排除规则滤为 0，不计通过证据。
- 以原 `doc/conf.py`、include_patterns 限定本束、root_doc/master_doc 指向本束根索引，Sphinx 9.1.0 dummy `-E -W` 构建 31 文档成功，零警告。它验证解析与导航，不声称 HTML 视觉测试或全库构建通过。
- HTMLParser 按每份缓存来源 URL 解析链接：HTML=17、Internal=17、差集为空。公开 `Invoke-WebRequest` 取得实时 sitemap：Sitemap=17，与缓存集合差集为空。Python urllib 请求返回403，不计成功。
- `git diff --check` 通过；所有文件保留未暂存状态，未提交。

最终独立 Review 与这些实施者自验分开记录。

## 相关概念

- [官网逐页台账](official-site-source.md)
- [编号事实与勘误](facts.md)
- [重建验证与比较器风险](../concepts/13-reconstruction-verification.md)

---
type: Guide
title: "导入说明：把本知识包挂载到 OKF 库、文档站或 Agent 工作区"
description: "skylinevpn-proxylist 知识包的导入与再同步指南——包清单、三条导入路径（独立 bundle / MyST 站点 / Agent 上下文）、上游更新后的重新导入流程、验收命令与常见问题"
tags: [导入, OKF, Sphinx, MyST, 知识包挂载, 再同步, 验收]
generated: { by: "seven-concepts-cmd", at: "2026-11-21T17:00:00+08:00" }
status: stable
stale_after: 2027-05-31
---

# 导入说明

> **适用对象**：要把本包导入另一个 OKF 库、Sphinx/MyST 站点或 Agent 工作区的人；以及源仓库更新后需要重新导入的维护者。
> **不适用**：只想阅读本包内容——直接回 [知识包首页](index.md) 按身份选路线即可。

## 一、包清单与外部依赖

```text
skylinevpn-proxylist/
├── index.md                  bundle 根：元数据、性质声明、四条阅读路线、toctree
├── import.md                 本文件：导入与再同步
├── log.md                    生成日志：R→I→E→C、G1~G4/V 门自评
├── concepts/                 index + 6 篇（定位→格式→消化→归约→发布→边界）
├── examples/                 index + 3 篇（本地复现 / 消费方接入 / 维护者 Runbook）
└── references/               index + facts（F-001~F-068）+ verification（C/D 清单）+ import-verification（导入后验证报告）
```

| 依赖 | 是否必需 | 说明 |
|------|---------|------|
| OKF v0.2 | 必需 | 根 `index.md` 的 `okf_version: "0.2"`；其余文件只需非空 `type` |
| Mermaid 渲染 | 建议 | 概念层共 3 处 `mermaid` 代码块；纯 Markdown 阅读器可忽略 |
| Sphinx + MyST | 可选 | 仅在并入文档站时需要；toctree 语法为 MyST 冒号围栏 |
| 中文搜索词典 | 可选 | 需要连写检索时，把本包新增词条并入站点 `okf-userdict.txt` |

本包**不含**图片、脚本、数据文件与外部网络依赖，复制目录即可移植。

## 二、三条导入路径

### 路径 A：作为独立 bundle 挂载到同级 OKF 库（最常见）

以本库为参照，共 6 个落点，缺一即被门禁拦截：

| 步骤 | 动作 | 落点 |
|------|------|------|
| 1 | 复制整个 `skylinevpn-proxylist/` 目录 | `<目标库>/doc/bundles/<域>/<组>/skylinevpn-proxylist/` |
| 2 | 在组索引登记一行 | `<域>/<组>/index.md` 的束清单表 + toctree |
| 3 | 在域索引更新组计数与简介 | `<域>/index.md`（若按组计数） |
| 4 | 更新总索引五面计数 | `<域>/index.md` 与 `doc/bundles/index.md`：frontmatter、正文计数行、域节标题、分组表束数列、toctree |
| 5 | 视需要登记搜索词 | `doc/_search/okf-userdict.txt`（本包新增：proxylist、gfwlist、AutoProxy、规则归约、父后缀吸收、叠加层并集等） |
| 6 | 跑门禁 | 见第四节 |

**注意**：总索引的计数必须与目录树一致（本库以目录树为地面真值）。若目标库此前已有计数漂移，先按门禁报错逐项归位，再叠加本包，否则会误判为本次导入引起。

### 路径 B：并入既有 Sphinx/MyST 站点

1. 把本包放在源目录下的任意层级（推荐 `bundles/<域>/<组>/`，与库内相对链接假设一致）。
2. 在上级 `index.md` 的 toctree 中挂 `skylinevpn-proxylist/index`。
3. 保持包内相对链接不变：包内全部链接都是**相对路径**（`../concepts/...`、`/references/...`），只有整体移动目录时才需要改。
4. 确认 Mermaid 扩展已启用（如 `sphinxcontrib-mermaid`）；未启用时图表退化为代码块，正文仍可读。
5. 若站点用中文搜索，合并第五步的词条并重建索引。

### 路径 C：作为 Agent 知识上下文

按以下顺序装载，避免上下文被事实表占满：

```text
index.md → concepts/00 → 按角色取 1~3 篇概念 → references/verification.md
（仅在需要引用数字或复核时再读 references/facts.md）
```

装载时必须同时告知 Agent 三条边界（与根页性质声明一致）：

1. 未联网执行 `build.sh`，构建行为属**源码口径**；
2. 未访问 GitHub Release，发布行为属**配置口径**；
3. 未接入任何客户端，规则的匹配语义是**从归约代码反推**，不代表任何消费端实现。

否则 Agent 容易把「脚本这么写」当成「线上跑过」。

## 三、上游更新后的重新导入

源仓库：`\\10.16.11.3\ai\notebook\libs\skylinevpn\skylinevpn-proxylist`。更新时按「先事实、后概念、再索引」的顺序：

| 步骤 | 读什么 | 改什么 |
|------|--------|--------|
| 1 | `git log` / `git tag` / `HEAD` | `references/facts.md` A 节（F-001~F-012）与根页 HEAD 标注 |
| 2 | `proxy.list` 分段计数与抽样 | facts B 节、concepts/01 的规模表 |
| 3 | `scripts/build.sh` | concepts/02、facts C 节 |
| 4 | `scripts/merge.py` | concepts/02、concepts/03、facts C 节 |
| 5 | `release.yml` | concepts/04、facts D 节 |
| 6 | `README.md`、`LICENSE`、`.gitignore` | facts E 节、concepts/05 |

**编号纪律**：`F-` 编号只追加、不复用、不重排；已删除的事实标注「作废」而非删除，保证正文引用不悬空。同理，`C-`（口径歧义）与 `D-`（对抗意见）只增不改号。

**收尾**：在 `log.md` 追加一节「再同步记录」（日期、上游 commit、变更范围），并按需顺延 `stale_after`。

## 四、验收清单

在目标库根目录执行：

```bash
python scripts/check-bundles-index.py                 # 总索引五面对账
python scripts/check-utf8.py doc/bundles/<域>/<组>/skylinevpn-proxylist
python scripts/check-toctrees.py doc/bundles/<域>/<组>/skylinevpn-proxylist
```

| 检查 | 通过标志 | 本次导入的实际结果 |
|------|---------|------------------|
| 总索引对账 | `9 域 / 65 组 / 748 束 …五面一致` | 见 [log.md](log.md) 第六节 |
| UTF-8 | `UTF-8 检查通过: 18 个文件均为有效 UTF-8` | 见 [log.md](log.md) 第六节 |
| 包内 toctree | `引用有效，所有内容文档均可达` | 见 [log.md](log.md) 第六节 |

**只认这三条硬信号**：计数一致、编码合法、内容可达。三者任一失败都不要合并。

## 五、常见问题

| 现象 | 原因 | 处理 |
|------|------|------|
| `计数漂移 … 差 +1` | 只改了 frontmatter，没改节标题或表行 | 按报错逐面补齐；先核对是否为本包引起 |
| `断链 … 链接不存在或越界` | 用了 `../` 越出 bundles 根，或改了目录名 | 包内链接一律改为相对 bundle 根的形式 |
| `所有内容文档均可达` 失败 | 新增了未挂 toctree 的 `.md`（如本文件遗漏登记） | 在所属 `index.md` 的 toctree 中登记 |
| 包被计成 0 束或 2 束 | 目录同时含 `concepts/` 与带 `index.md` 的子目录，触发锚点/导航歧义 | 保持三层结构：`concepts/`、`examples/`、`references/` 同级，不再嵌套内容束 |
| `type` 大小写不一致 | 根页写 `Bundle` 而非 `bundle` | 统一小写；子文档用 `Concept`/`Example`/`Reference`/`Guide`/`Log` |
| 中文连写搜不到 | 未合并搜索词条 | 追加 `proxylist`、`gfwlist`、`AutoProxy` 等词条并重建索引 |

## 六、导入时不可越界的声明

导入到任何载体后，以下表述都不应出现：

1. 「这份清单能翻墙」——本仓只为 SkylineVPN 自有产品供数，且许可为 AS IS；
2. 「构建脚本已实测」——本包未联网执行；
3. 「Release 资产已核验」——本包未访问 Release 页面；
4. 「规则语法是行业标准」——三节格式只由 `merge.py` 定义，仓内无格式规范文档（见 [核验报告](references/verification.md) C-4）。

如需改变这些边界，正确做法是补充实测并在 `facts.md` 追加新事实，而不是修改措辞。

## 主题关联

- 包内总览：[index.md](index.md)
- 生成过程与质量门：[log.md](log.md)
- 引用前必读：[references/facts.md](references/facts.md)、[references/verification.md](references/verification.md)

---
type: Reference
title: "导入后验证报告：skylinevpn-proxylist 知识包"
description: "知识包挂载到 awesome-okf-xs 后的验收记录——变更清单、五面计数对账、三条门禁原样输出、结构与内容完整性抽查、遗留项"
generated: { by: "seven-concepts-cmd", at: "2026-11-21T18:00:00+08:00" }
status: stable
---

# 导入后验证报告

> **验证对象**：`doc/bundles/jishu/dev/skylinevpn-proxylist/`（知识包本体）及其在总索引、域索引、组索引中的登记。
> **验证时间**：2026-11-21。
> **验证方式**：静态核对（目录清点、frontmatter 与正文比对）+ 三条仓库自带门禁脚本。**未执行** Sphinx 构建，**未执行**全库 `check-section-anchors.py`（耗时原因见第六节）。

## 一、变更清单

| 类别 | 变更 | 数量 |
|------|------|------|
| 新增知识包文件 | 根 3 + concepts 7 + examples 4 + references 3（本报告计入后为 4） | 18 |
| 总索引 | `doc/bundles/index.md`：frontmatter `total_bundles`、正文计数行、jishu 域节标题、mermaid 行、dev 分组表行与简介 | 5 处 |
| 库首页 | `doc/index.md`：导语计数、关于知识包计数 | 2 处 |
| 域索引 | `doc/bundles/jishu/index.md`：dev 行束数与简介 | 1 处 |
| 组索引 | `doc/bundles/jishu/dev/index.md`：description、束清单表行、学习路径第 5 条、toctree | 4 处 |
| 搜索词典 | `doc/_search/okf-userdict.txt`：新增 8 个词条 | 8 行 |

计数变化：总库 **747 → 748**；jishu 域 **550 → 551**；dev 组 **8 → 9**；域数与组数不变（9 域 / 65 组）。

## 二、五面对账

总索引的计数在五个面同时存在，任一面遗漏都会被门禁判为「计数漂移」：

| 面 | 位置 | 导入前 | 导入后 |
|----|------|--------|--------|
| frontmatter | `doc/bundles/index.md` 第 6 行 | 747 | **748** |
| 正文计数行 | 同文件「当前共 **N 个知识包**」 | 747 | **748** |
| 域节标题 | 同文件 `### ⚙️ [技术](jishu/index.md) · N 束 · 19 组` | 550 | **551** |
| 分组表束数列 | 同文件 dev 行 | 8 | **9** |
| toctree | 域/组层 toctree（总索引只挂域） | — | 组内新增 `skylinevpn-proxylist/index` |

对照地面真值：`doc/bundles/jishu/dev/` 下现有 9 个含 `index.md` 的子目录（dingtalk-workspace-cli、git、git-advanced、git-baidu-sync、github、opensource、plane、skylinevpn-cli、skylinevpn-proxylist），与 dev 组声明一致。

## 三、门禁结果（原样输出）

```text
$ python scripts/check-bundles-index.py
bundles 总索引对账通过: 9 域 / 65 组 / 748 束，frontmatter、计数行、节标题、分组表、toctree 五面一致。

$ python scripts/check-utf8.py doc/bundles/jishu/dev/skylinevpn-proxylist
UTF-8 检查通过: 18 个文件均为有效 UTF-8。

$ python scripts/check-toctrees.py doc/bundles/jishu/dev/skylinevpn-proxylist
toctree 检查通过: 全部 index.md 引用有效，所有内容文档均可达。
```

判定：三条硬信号（计数一致、编码合法、内容可达）全部通过。

## 四、结构与内容完整性

| 检查项 | 期望 | 实测 |
|--------|------|------|
| 三层结构 | `concepts/`、`examples/`、`references/` 同级，无嵌套内容束 | 符合 |
| 根 frontmatter | `okf_version: "0.2"`、`type: bundle`（小写）、`delegates_to` 指向三层索引 | 符合 |
| 概念篇数 | 6 篇 + 索引 | 6 + 1 |
| 演练篇数 | 3 篇 + 索引 | 3 + 1 |
| 事实条数 | F-001 ~ F-068 连续无缺号 | 68 条（脚本计数 68） |
| 口径歧义 | C-1 ~ C-5 | 5 条 |
| 对抗意见 | D-1 ~ D-8，四视角覆盖 | 8 条 |
| 事实性质标注 | 每条含 `事实 / 清点 / 文档口径` | 全部标注 |
| 包内链接 | 全部相对路径，不越出 bundle 根 | toctree 门禁已覆盖 |
| 新增根级 `.md` | 必须登记进根 toctree | `import.md` 已登记；本报告位于 `references/`，由信源索引登记 |

## 五、索引可达性抽查

| 入口 | 期望内容 | 结果 |
|------|---------|------|
| 总索引 dev 行 | 束数 9，简介含「SkylineVPN 规则清单仓」 | 符合 |
| 域索引 dev 行 | 束数 9，简介同步 | 符合 |
| 组索引束清单表 | 新增「SkylineVPN 规则清单仓」行，入口指向 `skylinevpn-proxylist/index.md` | 符合 |
| 组索引 toctree | 含 `skylinevpn-proxylist/index` | 符合 |
| 学习路径 | 第 5 条由「产品发布」扩为「产品与数据发布」，串起两个 SkylineVPN 束 | 符合 |
| 搜索词典 | `skylinevpn-proxylist`、`proxylist`、`gfwlist`、`AutoProxy`、`规则清单`、`父后缀吸收`、`叠加层并集`、`固定下载地址` | 8 条已追加 |
| 反向链接 | 根索引「与同组知识包的关系」指向 `../skylinevpn-cli/index.md` | 目标存在 |

## 六、遗留项与边界

| 项 | 状态 | 说明 |
|----|------|------|
| Sphinx `-W` 构建 | 未执行 | SMB 侧全站构建耗时过长；包内 toctree 语法已由门禁校验 |
| 全库 `check-section-anchors.py` | 未执行 | 扫描整库，本包未新增跨文档锚点引用，风险低 |
| 运行时验证 | 未执行 | 知识包性质为「只读研读」，未联网构建、未访问 Release、未接入客户端；该边界已写入根页性质声明与 `verification.md` 第五节 |
| 内容时效 | 有保质期 | `stale_after: 2027-05-31`；`proxy.list` 分段计数每周会变，引用前须按 `facts.md` 口径重测 |

## 七、结论

**通过（有条件）**。导入在结构、计数、编码、可达性四个维度均满足 OKF v0.2 与仓库门禁要求；条件项为「未做 Sphinx 全站构建」与「未做运行时验证」，二者均不影响知识包入库，但发布到对外站点前应补做一次 `-W` 构建。

## 关联

- 知识包首页：[index.md](../index.md)
- 导入说明：[import.md](../import.md)
- 生成日志：[log.md](../log.md)
- 事实与核验：[facts.md](facts.md)、[verification.md](verification.md)

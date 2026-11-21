---
type: Log
title: "skylinevpn-proxylist 知识包生成日志（七概念链路）"
description: "R→I→E→C 执行记录：事实采集、四元组洞察、可复用模式、质量门自评与对抗审查汇总"
generated: { by: "seven-concepts-cmd", at: "2026-11-21T17:00:00+08:00" }
status: stable
---

# 生成日志

## 0. 任务与场景判定

- **输入**：`\\10.16.11.3\ai\notebook\libs\skylinevpn\skylinevpn-proxylist`（HEAD `9c6567c`，2026-11-16）。
- **产出**：OKF 知识包 `doc/bundles/jishu/dev/skylinevpn-proxylist/`。
- **场景**：知识沉淀（R → I → E；V 与 C 按需）。理由：用户要求「全面学习 + 洞察」并产出教程，非故障处置或重构。
- **边界**：只读研读；不联网执行构建、不访问 Release 页面、不接入客户端。

## 1. R：事实采集（G1）

- 采集范围：`git log / tag / remote / branch / status`、`README.md`、`LICENSE`、`.gitignore`、`proxy.list`（结构、分段计数、抽样、编码）、`scripts/build.sh`、`scripts/merge.py`、`.github/workflows/release.yml`、目录清点。
- 产出：[facts.md](references/facts.md)，F-001 ~ F-068，分 A 仓库与版本 / B 数据文件 / C 编译管线 / D 发布工作流 / E 治理与边界五节。
- 性质分布：`[事实]` 主要来自脚本源码、工作流配置与 git 元数据；`[清点]` 为本次对数据文件的分段统计与抽样。
- **G1 自评：通过**。68 条 ≥ 20；每条附依据文件、行号或命令；未把推断写成事实（推断一律落在 I / D 节）。

## 2. I：洞察（G2，四元组）

| # | 现象 | 根因 | 影响 | 建议 |
|---|------|------|------|------|
| I-1 | 仓库只有 7 个文件，却是一个持续 5 周、每周发版的在运行系统 | 产品只要一份可下载的规则表，工程复杂度被压在上游与 CI | 「数据仓」的最小形态：无依赖、无测试、无构建产物目录 | 任何「只交付一个文件」的产品都可用此模板，但必须补上本仓缺失的校验层 |
| I-2 | 规则用三节而非全正则表达 | 最小表达力原则：后缀覆盖绝大多数，精确项处理 IP 与特例，正则只兜底 | 匹配快、可读、体积小；但把「匹配语义」的责任推给了消费端 | 交付规则表时同步交付一份格式契约，或在客户端固化语义 |
| I-3 | 归约不是简单去重，而是父后缀吸收子域 | 后缀语义天然包含子域，保留子域条目只是冗余 | 条目数下降、匹配结果等价；代价是消费端必须实现「后缀含子域」 | 归约逻辑与消费端语义必须成对交付，否则「优化」会变成行为变更 |
| I-4 | 每次构建把现有 `proxy.list` 读进来一起合并 | 清单是本仓的**叠加层**，上游只是增量源 | 本地策展条目（金融/AI/流媒体等）永不丢失；但上游删除不传播，规模单调增长 | 需要「删除传播」时，应引入来源标记或分文件，而不是靠并集 |
| I-5 | 工作流每次都发 Release，即使 `proxy.list` 没变 | 发布节拍由 cron 决定，内容节拍由上游决定 | `v20261109` 指向 11-02 的提交，tag 日期 ≠ 内容日期 | 把「无变化则跳过发版」写成显式分支，或让 tag 携带内容摘要 |
| I-6 | 全链路没有校验和、没有签名、没有内容量下界 | 定位是内部供数，而非面向不可信网络的软件分发 | 上游异常或仓库失陷可静默产出近空表/污染表 | 至少加「条目数下界 + 文件摘要」两道断言，成本极低 |

**G2 自评：通过**。6 条 ≥ 3，均含现象、根因、影响、建议四项。

## 3. E：模式萃取（G3）

| 模式 | 触发 | 步骤 | 反模式 | 迁移 |
|------|------|------|--------|------|
| 最小表达力分层 | 需要表达一批「主机/域名」规则 | 先按后缀归类 → 再抽精确项 → 剩余才用正则 | 一上来全部写正则 | 防火墙、广告拦截、抓取白名单、CDN 回源规则 |
| 父级吸收归约 | 规则集含层级关系（域 → 子域） | 定义包含语义 → 自顶向下吸收 → 全集排序输出 | 只做字符串去重 | 任何树状命名空间的规则压缩 |
| 叠加层并集 | 本地有策展条目、外部有增量源 | 读取现有产物 → 与上游并集 → 归约 → 覆写 | 每次从上游全量重建（会冲掉策展） | 词典、黑名单、种子库、配置基线 |
| 静默幂等提交 | 定时任务每天/每周跑一次 | 生成 → `git diff --cached --quiet` → 有差异才提交 | 无条件提交产生空提交噪声 | 任何定时生成产物的仓库 |
| 日期 tag + 固定地址 | 需要给消费端一个永不变的下载 URL | 每次发布打日期 tag → 另设 `latest` 别名 → 文档只写 latest | 让用户追最新 tag 名 | 数据订阅、模型权重、证书包分发 |

**G3 自评：通过**。5 个模式，每个 3~4 步，均含 ≥1 反模式与迁移场景。

## 4. V：对抗审查（V 门）

四视角意见已写入 [verification.md](references/verification.md) 第二节：D-1（无签名/无摘要）、D-2（无内容量下界）、D-3（`@@` 白名单被丢弃）、D-4（只增不减导致膨胀）、D-5（消费端语义未定义）、D-6（同日重发改变资产）、D-7（README 不描述格式）、D-8（合规与适用性）。

处置结果：

- D-1、D-2 → 在 [05](concepts/05-boundaries-and-risk-model.md) 与 [演练 01](examples/01-consumer-integration.md) 明确降级表述，并给出接入侧自保措施；
- D-3、D-4、D-5 → 在 [02](concepts/02-upstream-digestion-pipeline.md)、[03](concepts/03-reduction-algorithm.md) 记录为「设计取舍」与语义契约缺口；
- D-6、D-7 → 在 [04](concepts/04-release-channel-and-fixed-url.md) 与 [演练 02](examples/02-maintainer-runbook.md) 写明核对清单；
- D-8 → 根索引「适用与不适用」与 [05](concepts/05-boundaries-and-risk-model.md) 同时声明。

**V 门自评：通过**。8 条 ≥ 5，四视角覆盖（魔鬼 D-1/D-2、新人 D-7、老板 D-4/D-8、未来 D-3/D-5/D-6）。

## 5. A / C：原子化与交付

- 原子化：按「概念 / 演练 / 信源」三分层；数字集中在 facts，歧义集中在 verification，正文只引用编号。
- 交付清单（知识包内 18 个文件）：
  - 根：`index.md`、`import.md`、`log.md`
  - concepts：`index.md` + 00 ~ 05 共 7 个
  - examples：`index.md` + 00 ~ 02 共 4 个
  - references：`index.md`、`facts.md`、`verification.md`、`import-verification.md` 共 4 个
  - 索引更新：`jishu/dev/index.md`、`jishu/index.md`、`doc/bundles/index.md`、`doc/index.md`、`doc/_search/okf-userdict.txt`
- **G4 自评：通过**。每个文件单一职责；事实编号可追溯；索引计数与实际文件同步（748 束 / 551 束 / 9 束）。

## 6. 门禁记录

| 门禁 | 命令 | 结果 |
|------|------|------|
| 总索引对账 | `python scripts/check-bundles-index.py` | 通过：9 域 / 65 组 / 748 束，五面一致 |
| 编码 | `python scripts/check-utf8.py doc/bundles/jishu/dev/skylinevpn-proxylist` | 通过：18 个文件均为有效 UTF-8 |
| 可达性 | `python scripts/check-toctrees.py doc/bundles/jishu/dev/skylinevpn-proxylist` | 通过：引用有效，所有内容文档均可达 |

## 7. 后续维护

触发更新见 [verification.md](references/verification.md) 第四节。优先关注：上游 `SRC_URL` 变更、`merge.py` 的归约规则变更、工作流调度或 tag 策略变更、`proxy.list` 分段计数显著漂移。

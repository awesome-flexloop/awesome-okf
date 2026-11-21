---
type: Log
title: "skylinevpn-cli 知识包生成日志（七概念链路）"
description: "R→I→E→C 执行记录：事实采集、四元组洞察、可复用模式、质量门自评与对抗审查汇总"
generated: { by: "seven-concepts-cmd", at: "2026-11-21T12:00:00+08:00" }
status: stable
---

# 生成日志

## 0. 任务与场景判定

- **输入**：[skyline-projext/skylinevpn-cli](https://github.com/skyline-projext/skylinevpn-cli)（HEAD `415d0bb`，v3.0.1）。
- **产出**：OKF 知识包 `doc/bundles/jishu/dev/skylinevpn-cli/`。
- **场景**：知识沉淀（R → I → E；V 与 C 按需）。理由：用户要求「全面学习 + 洞察」并产出教程，非故障处置或重构。
- **边界**：只读研读；不执行二进制、不运行安装器、不访问服务端与 Release 页面。

## 1. R：事实采集（G1）

- 采集范围：`git log/tag/remote/branch`、6 份 README、`CHANGELOG.md`、`LICENSE`、`.gitignore`、`.gitattributes`、`tools/` 下 4 脚本 + `RELEASING.md`、目录清点。
- 产出：[facts.md](references/facts.md)，F-001 ~ F-072，分 A ~ E 五节。
- 性质分布：`[事实]` 主要来自脚本与 git 元数据；`[文档口径]` 来自 README/RELEASING；`[清点]` 为本次目录清点。
- **G1 自评：通过**。72 条 ≥ 20；每条附依据文件或命令；无因果推断混入。

## 2. I：洞察（G2，四元组）

| # | 现象 | 根因 | 影响 | 建议 |
|---|------|------|------|------|
| I-1 | 仓库无产品源码，却有一套完整的发布工程 | 专有二进制 + 公开发行仓的分层组织 | 学习价值集中在「交付链」而非「实现」 | 以「可审计交付」为主线阅读，勿越界评价协议安全 |
| I-2 | 构建立处使用 `sub()`/`var()`/`one()` 并带命中次数断言 | 安装器由上游生成，本仓只能做外科式改写 | 上游格式漂移时失败而非产出坏包 | 任何对外部格式的假设都写成带期望命中数的替换 |
| I-3 | 禁止词清单放在仓库外，缺失即拒绝运行 | 清单本身即敏感信息 | 保密性提升、可复现性下降，换机易卡 | 清单纳入密钥管理；文档把「恢复清单」列为发布前置 |
| I-4 | 泄漏扫描递归解包到 zip/tar/ar/xar 与 UTF-16 | 二进制包任意层级都可能夹带身份信息 | 扫描成本高，但覆盖真实泄漏面 | 二进制交付门禁以「解到最后一层文件」为标准 |
| I-5 | 身份锁允许 GitHub 作为提交者 | 平台 squash merge 会重写提交者 | 正常 PR 流程不被自己的门禁误杀 | 门禁以作者为主键、提交者为白名单 |

**G2 自评：通过**。5 条 ≥ 3，均含现象、根因、影响、建议四项。

## 3. E：模式萃取（G3）

| 模式 | 触发 | 步骤 | 反模式 | 迁移 |
|------|------|------|--------|------|
| 断言式改写 | 需要修改上游生成的产物 | 定位变量 → 提取 → 带命中数替换 → 复查残留 | 用无断言的 `replace` 静默漏改 | 任何「模板/安装器/配置由他人生成」的场景 |
| 双校验分工 | 同时存在安装期与发布期哈希 | 区分「包内容校验」与「下载完整性」→ 各自锚定 → 不互相替代 | 把 `SHA256SUMS` 当成安装器校验 | 软件分发、固件、模型权重分发 |
| 递归内容门禁 | 交付物含压缩/归档 | 解容器 → 递归归档 → 多编码匹配 → 生成物与上游分级处置 | 只 `grep` 顶层文件 | 发布前保密扫描 |
| 身份主键分离 | 平台会重写提交元数据 | 作者强校验 + 提交者白名单 + 全历史扫描 | 只查当前工作区 | 任何 squash-only 仓库 |
| 单版本保留 | 用户只应装最新 | 新 Release 晋升 → 核验 → 删旧 Release 留 tag | 把「删旧资产」写成纯优点 | 需要明确回滚代价的产品 |

**G3 自评：通过**。5 个模式，每个 3~4 步，均含 ≥1 反模式与迁移场景。

## 4. V：对抗审查（V 门）

四视角意见已写入 [verification.md](references/verification.md) 第二节：D-1（无签名）、D-2（一键安装信任面）、D-3（清单在仓库外）、D-4（正则误伤/漏检）、D-5（本地钩子可缺）、D-6（单版本牺牲回滚）、D-7（运行时缺席）。

处置结果：

- D-1、D-2 → 在 [06](concepts/06-trust-model-and-boundaries.md) 与 [演练 00](examples/00-install-verify-uninstall.md) 明确降级表述；
- D-3、D-5 → 在 [05](concepts/05-identity-and-leak-gates.md) 列为「设计取舍」并给前置清单；
- D-4、D-6 → 在 [04](concepts/04-release-staging-pipeline.md)、[02](concepts/02-distribution-topology.md) 记录代价；
- D-7 → 根索引与三篇演练顶部统一标注「未实机执行」。

**V 门自评：通过**。7 条 ≥ 5，四视角覆盖（魔鬼 D-1/D-4、新人 D-2、老板 D-5/D-6、未来 D-3/D-7）。

## 5. A / C：原子化与交付

- 原子化：按「概念 / 演练 / 信源」三分层；数字集中在 facts，冲突集中在 verification，正文只引用编号。
- 交付清单（知识包内 18 个文件）：
  - 根：`index.md`、`import.md`、`log.md`
  - concepts：`index.md` + 00 ~ 06 共 8 个
  - examples：`index.md` + 00 ~ 02 共 4 个
  - references：`index.md`、`facts.md`、`verification.md` 共 3 个
  - 索引更新：`jishu/dev/index.md`、`jishu/index.md`、`doc/bundles/index.md`、`doc/index.md`、`doc/_search/okf-userdict.txt`
- **G4 自评：通过**。每个文件单一职责；事实编号可追溯；索引计数与实际文件同步。

## 6. 后续维护

触发更新见 [verification.md](references/verification.md) 第四节。优先关注：新 tag、`LEAK_PATTERNS` 变更、`sub()` 期望计数变更、发布策略变化。

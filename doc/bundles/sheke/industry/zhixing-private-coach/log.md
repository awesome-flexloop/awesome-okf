# 变更日志

## 2026-10-24

### R/I/E/V 阶段（方法论编排 sc-20261024-zhixing-private-coach）

- 场景识别：知识沉淀（会议纪要转教程），链路 R→I→E→V→C。
- R：从腾讯会议录制（会议号 855792273）获取智能纪要与逐字稿（165 个发言段），登记 F-001~F-095 事实清单（references/meeting-source.md），通过 G1（事实带时间戳+发言人归属，无 recorder 因果推断）。
- I：提炼 4 条四元组洞察（concepts/00-overview.md 第二节），通过 G2。
- E：萃取 concepts 5 页教程 + examples 2 份工作表，通过 G3（触发边界/步骤/反模式/检验标准/跨场景迁移齐备；单案例标注 flagged 不标 verified）。
- V：四视角对抗审查（魔鬼代言人/新人/老板/未来）共 13 条意见，采纳 4 条修正：
  1. 「提价不是为了多赚」的动机归因修正为「现场推演共识（道动哥重新定价示范）」，避免把个人悟道说成主讲主张（00-overview 洞察 2、01 页）。
  2. 「一半让利」在教程与工作表中补注「主讲人个人口径，非验证过的结构」（01 页、examples 工作表）。
  3. 02 页第五动作补「初学可先跳过前四动作照常执行」的入周提示（新人视角）。
  4. 04 页迁移节补「以下迁移为本包整理者推演，会上未涉及」声明；examples 对赌勾选补对赌定义（未来视角/新人视角）。
- 未执行 `invoke gates.*`，改执行手动等效门禁（C 阶段记录）。

（C 阶段提交证据见下）

### C 阶段：门禁 + 索引对账 + 原子提交

- 索引对账（三级）：industry 33→34 束、sheke 79→80 束、bundles 676→677 束；新增知识包导航表行、阅读建议条目与 toctree 条目。
- 门禁三态递进（手动等效门禁，未执行 `invoke gates.*`）：
  1. 暂存区快照（`git checkout-index --all --prefix=`）：toctrees / bundles-index / utf8 三门禁全绿，677 束五面一致；
  2. 提交态（`git archive <sha>`）：同三门禁复跑预期 677 束（见提交后验证）。
- **并发隔离提交**：工作区存在他方会话未提交 WIP（personal-growth 组 wechat-psychology-value-and-bias 新束），共享索引 doc/bundles/index.md 与 doc/bundles/sheke/index.md 已被双方同行混合修改（混合态 678/81 束）。
  - 共享索引用 crafted blob 法：基线取 `git cat-file blob HEAD:<path>`，仅叠加本束增量后 `git hash-object -w --path=<path>` + `git update-index --cacheinfo`，工作区保留混合态不动；
  - 本提交只含本束 14 个文件 + industry/index.md（独占）+ 两个共享索引的 crafted blob（提交口径 677 束），不含他方 WIP；
  - 计数口径以纯净树/暂存区为准（677），不采用混合态（678）。
- 提交：见 git log（conventional commits，中文说明「为什么」）。

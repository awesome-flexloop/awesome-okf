---
type: Reference
title: "核验报告：口径歧义、对抗审查与不可核验边界"
description: "C-1 ~ C-5 口径歧义、D-1 ~ D-8 四视角对抗意见、本次未执行的验证项，以及需要重新复核的触发条件"
generated: { by: "seven-concepts-cmd", at: "2026-11-21T17:00:00+08:00" }
status: stable
---

# 核验报告

## 一、核验方法与边界

| 项 | 做法 | 结论 |
|----|------|------|
| 版本锚定 | `git rev-parse`、`git log`、`git tag` | 全部事实对应 `HEAD 9c6567c` |
| 源码阅读 | 逐行读 `build.sh`、`merge.py`、`release.yml` | 已覆盖全部逻辑分支 |
| 数据统计 | 按节切分统计条目数、抽样三类条目、检查非 ASCII | 见 F-015 ~ F-021 |
| 运行时验证 | **未执行** | 未联网跑构建、未访问 Release、未接入客户端 |

**不可核验（本次）**：

1. `build.sh` 在真实上游上的执行结果（上游内容随时间变化）；
2. GitHub Release 页面上的资产存在性与下载可用性；
3. 任一消费端的实际匹配行为与代理效果；
4. `v20261109` 当时的工作流日志（只能从 tag 指向推断「无内容变化」）。

## 二、口径歧义（C）

| 编号 | 歧义 | 说明 | 影响 |
|------|------|------|------|
| C-1 | 「latest」三重指代 | GitHub Release 的 latest 标记、真实 git tag `latest`、README 的 `/releases/latest/download/` 是三种不同机制（F-057、F-058、F-064） | 只成功一半时两条下载通道会分叉 |
| C-2 | 版本节拍 ≠ 内容节拍 | tag 按 `vYYYYMMDD` 命名，但 `v20261109` 指向 11-02 的提交（F-006） | 不能把 tag 日期当成内容日期或内容指纹 |
| C-3 | 「继承 gfwlist」的口径 | `@@` 例外与非 blogspot 的 URL 正则被丢弃（F-035、F-036） | 准确说法是「取其主机级规则」，不是完整继承 |
| C-4 | 格式无文档 | 三节语义只存在于 `merge.py`，README 不解释格式（F-064、F-068） | 消费端必须读代码或本包才能正确实现 |
| C-5 | 「Rules: N」的统计口径 | Release notes 用 `grep -vcE` 统计（F-055），与「条目数」在存在空行/注释时口径一致，但不含三节拆分信息 | 无法从 notes 判断是哪个节增长 |

## 三、对抗审查（D）

四视角：魔鬼（找最坏情况）、新人（第一次接触会误解什么）、老板（成本与收益）、未来（半年后会坏在哪）。

| 编号 | 视角 | 意见 | 处置 |
|------|------|------|------|
| D-1 | 魔鬼 | 全链路无签名、无摘要、无发布者校验，仓库或账号失陷即可让所有客户端拿到污染清单 | 在 [05](../concepts/05-boundaries-and-risk-model.md) 明确写入信任链表；接入侧建议补摘要（[演练 01](../examples/01-consumer-integration.md)） |
| D-2 | 魔鬼 | 无内容量下界：上游返回 200 但内容异常时，可产出仅剩两行表头的清单并照常提交发布 | 列入 [05](../concepts/05-boundaries-and-risk-model.md) 第 2 节，给出三道低成本断言 |
| D-3 | 魔鬼 | `@@` 例外规则被静默丢弃，造成过覆盖（本应直连的站点被代理） | [02](../concepts/02-upstream-digestion-pipeline.md) 第 4 节标为设计取舍，不宣称「完整继承」 |
| D-4 | 老板 | 只增不减：上游删除不传播，清单单调膨胀，长期维护成本上升 | [03](../concepts/03-reduction-algorithm.md) 第 7 节给出「来源分文件」的演进方向 |
| D-5 | 未来 | 消费端语义未定义；若客户端把后缀实现成严格相等，归约会变成行为变更 | [01](../concepts/01-rule-file-format.md) 第 6 节给出最低实现要求，列为隐式契约 |
| D-6 | 未来 | 同日重发删除并重建 Release/tag，资产 ID 与时间戳变化，客户端缓存判断失效 | [04](../concepts/04-release-channel-and-fixed-url.md) 第 3 节说明；建议内容比对而非元数据比对 |
| D-7 | 新人 | README 只有下载地址，新人会以为「下载即完成」，不知道还要实现三节匹配 | 根索引与 [01](../concepts/01-rule-file-format.md) 均强调「仓内无匹配器」 |
| D-8 | 老板 | 许可为 AS IS 且清单覆盖敏感类别站点，对外分发存在合规与适用性风险 | 根索引「适用与不适用」与 [05](../concepts/05-boundaries-and-risk-model.md) 第 4 节同时声明 |

**覆盖率**：8 条 ≥ 5；四视角均有覆盖（魔鬼 D-1/D-2/D-3、老板 D-4/D-8、未来 D-5/D-6、新人 D-7）。

## 四、复核触发条件

出现以下任一情况时，本包需要重新核对（按 [import.md](../import.md) 第三节流程）：

| 触发 | 需重读 | 预期影响 |
|------|--------|---------|
| `proxy.list` 分段计数偏离 F-015 超过 10% | 数据文件 | concepts/01 的规模表、facts B 节 |
| `merge.py` 的归约或语法判定改动 | 编译管线 | concepts/02、concepts/03、facts C 节 |
| `build.sh` 的 `SRC_URL` 或解码方式改动 | 取料 | concepts/02、facts C 节 |
| `release.yml` 的触发、tag 策略、发布步骤改动 | 发布 | concepts/04、facts D 节 |
| 新增 tag 且其指向与提交日期错位 | 版本 | concepts/04 第 7 节、C-2 |
| 新增格式文档或 README 说明 | 文档 | C-4、import.md 第六节 |
| 仓库转为归档或更换许可 | 治理 | 根索引性质声明、concepts/05 |

## 五、引用本包时的五条禁令

1. 不得声称本包验证了任何站点的可达性；
2. 不得声称构建脚本「已实测」；
3. 不得声称 Release 资产「已核验」；
4. 不得把三节格式称为「行业标准」或「gfwlist 官方格式」；
5. 不得把「每周一个版本」表述为「每周都有内容更新」。

## 关联

- 事实来源：[facts.md](facts.md)
- 风险正文：[05 风险与边界](../concepts/05-boundaries-and-risk-model.md)
- 再同步流程：[import.md](../import.md)

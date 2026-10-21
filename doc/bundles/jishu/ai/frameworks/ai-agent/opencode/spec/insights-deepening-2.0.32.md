---
type: spec
title: "OpenCode 同快照深化洞察与学习地图"
source: "facts-deepening-2.0.32.md"
sources:
  - id: deepening-facts
    resource: facts-deepening-2.0.32.md
    title: F-115～F-151
  - id: deepening-source
    resource: ../references/source-deepening-2.0.32.md
    title: 固定源码与阅读范围
---

# OpenCode 同快照深化洞察与学习地图

本轮于2026-10-21深化同一`2.0.32`快照，以[新增事实](facts-deepening-2.0.32.md)为依据。以下是对代码关系的解释与学习建议，不是运行实验结论。[前轮洞察](insights-2.0.32.md)保留原有覆盖范围。

## 五条洞察

### 一：配置优先级属于消费链

- **陈述**：来源发现、有序entries与领域消费分离，同一序列分别转化为技能、指令和压缩设置。
- **证据**：F-115～F-122。
- **反常识**：“最后配置覆盖一切”不能代替字段选取、技能同ID覆盖、指令组合各自的语义。
- **行动**：先查discovery，再查插件消费循环，最后查Session状态；逐层记录实际输入。

### 二：复用执行环境不自动启用预算与校验

- **陈述**：codemode复用prepared runtime，逐次新建执行状态；预算需要显式接线，输入校验取决于schema形态。
- **证据**：F-123～F-130。
- **反常识**：解释器不是宿主eval，但也不是进程级隔离证明；存在limits类型不表示Core传入；JSON Schema呈现不表示运行时解码。
- **行动**：并列核对runtime生命周期、make参数、decodeInput、hooks与结果裁剪，不把局部限制写成整体安全保证。

### 三：扩展可见信息、加载许可与释放是不同契约

- **陈述**：Schema提供插件信息；module policy/activation控制加载；Scope/cleanup承载生命周期。
- **证据**：F-131～F-135。
- **反常识**：active/failed信息不说明重载顺序；失败插件重排也不必触发相同revision重试。
- **行动**：从Info追到module、activate、hook与finalizer，分别理解pending、failed、健康fallback。

### 四：“完成”要标注是哪一层确认

- **陈述**：TUI写成功后更新状态，App先变状态后延迟写，Desktop ACK后仍有SQLite write-behind。
- **证据**：F-136～F-140。
- **反常识**：响应式状态更新、RPC resolve或某层flush resolve不能通用地等价为持久保存；下层失败排队可能仍在。
- **行动**：逐端标注确认点与失败归属，先问“哪层返回成功”，再找最终写入证据。

### 五：可复现与可交付分别有失败边界

- **陈述**：simulation控制请求流，recorder回放固定交互；proxy、统计、文件服务、updater各自处理不同失败与确认。
- **证据**：F-141～F-151。
- **反常识**：终端JSONL不是HTTP cassette；CI auto replay不是全模式禁网；代理源码不证明计费正确；ready不等于installed。
- **行动**：按模型驱动、HTTP匹配、终端时间线选择验证对象；读云端与更新时分别查代理响应、统计降级、etag保护、暂存及安装交接。

## 增量学习路径

新增六篇概念与一篇静态导读，续接既有编号，不重复旧入口篇。

| 顺序 | 教程 | 读者与前置 | 事实 |
|---|---|---|---|
| 1 | [10 配置与上下文](../concepts/10-config-context-resolution.md) | 配置学习者；先读05包地图 | F-115～F-122 |
| 2 | [11 Codemode执行边界](../concepts/11-codemode-runtime-boundaries.md) | 工具开发者；建议先读07扩展 | F-123～F-130 |
| 3 | [12 插件契约与生命周期](../concepts/12-plugin-contract-lifecycle.md) | 插件开发者；先读08 API边界 | F-131～F-135 |
| 4 | [13 三端状态持久化](../concepts/13-product-state-persistence.md) | 客户端排查；先读09产品入口 | F-136～F-140 |
| 5 | [14 模拟与录制回放](../concepts/14-simulation-record-replay.md) | 验证学习者；建议先读06会话 | F-141～F-146 |
| 6 | [15 云端与更新边界](../concepts/15-cloud-update-boundaries.md) | 工程视角收束；先读09与14 | F-147～F-151 |
| 7 | [03 状态与回放阅读实验](../examples/03-state-and-replay-reading-lab.md) | 对照源码核验；先读13～15 | F-136～F-151 |

每篇教程给出定位顺序、容易误解的确认点与未读范围。阅读实验只要求查代码，不运行真实请求、安装或更新。

## 相关概念

- [六主题范围矩阵](../references/source-deepening-2.0.32.md)
- [前轮知识地图](insights-2.0.32.md)

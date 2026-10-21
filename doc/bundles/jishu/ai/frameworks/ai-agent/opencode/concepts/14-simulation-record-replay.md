---
type: Concept
title: "OpenCode 模拟、录制与回放边界"
description: "区分Drive控制的模型流、终端时间线及HTTP cassette匹配与领取"
source: "../spec/facts-deepening-2.0.32.md"
tags: [opencode, simulation, recorder, replay, testing]
status: draft
sources:
  - id: source
    resource: ../references/source-deepening-2.0.32.md
    title: 同快照深化信源
---

# OpenCode 模拟、录制与回放边界

OpenCode的模拟和回放不是一个统一“录屏后重放”的功能。模型驱动、终端时间线与HTTP交互各有数据及生命周期。依据[F-141～F-146](../spec/facts-deepening-2.0.32.md)，本篇阅读代码和测试定义，没有运行模型或回放实验。

## Simulation替换哪一层

`simulationReplacements`替换HTTP layer。未设`OPENCODE_DRIVE`时安装模拟网络；设值后解析Drive manifest，并安装`SimulatedProvider`与OpenAI route，安装失败经`Layer.orDie`中止启动，不静默继续成真实运行。（F-141）

`SimulatedProvider.layerDrive`为每个invocation建立容量256的responses queue；stream的`acquireRelease`在释放时关闭queue、清除pending。`llm.attach`替换旧订阅；chunk、finish、disconnect分别对应入队、结束或失败。（F-142）

这些是可控请求流的机制，不是“真实模型行为已经复现”的证明。控制驱动产生什么事件、哪些网络路由可用，还要查对应协议与driver；完整Drive UI/controller不在本轮穷尽范围。

## Terminal Timeline记录什么

`Timeline.create`先写version=1/base64 header，随后output与resize写JSONL，pointer写sidecar，共享`performance.now`单调时钟。`finish`等待自身和子流完成并传播失败。（F-143）

终端输出字节、尺寸和指针时间线描述交互呈现；它不是HTTP cassette，也不自动还原服务端请求或模型副作用。完成判断需等待finish，而不是仅看到JSONL文件已生成。

## HTTP录制保留两种响应视图

record路径先调用真实upstream，捕获response snapshot，再把脱敏副本写入cassette。Deferred序列让append按请求开始顺序执行，实际调用返回未脱敏响应快照。live response与存储内容不同，不能把cassette中的`[REDACTED]`当作应用实际收到的值。（F-144）

cassette store默认目录为当前工作目录的`test/fixtures/recordings`，拒绝绝对name与`..`；append在semaphore内检查possible secrets，临时文件写入后rename。这个检查是实现保护，不是所有秘密必被识别的安全保证。（F-146）

## 回放的匹配与使用量检查

replay对脱敏request从未领取交互中匹配；pool缓存读取，以`SynchronizedRef`原子claim。不同请求可按匹配关系乱序回放，同请求对应的记录依次领取；测试定义分别覆盖乱序和并发。（F-144～F-146）

`auto`在CI非空且非`false/0`时选replay；非CI则按cassette是否存在选replay或record。这个条件只说明auto，不是所有显式record/passthrough都禁网。record可能访问真实网络，读者不要把本篇静态导读当作运行授权。（F-145）

成功Scope收尾会检查未用记录，但failure exit、尝试而零领取、missing cassette有例外。不能称“所有执行路径都要求cassette耗尽”；一次请求未匹配也不等于它消耗了记录。

## 夹具导读

`http/multi-step.json`定义step=1/2对应first/second。先看JSON，再看HTTP测试的mismatch、distinct order、concurrent claim、unused与CI missing断言，最后回到recorder/state实现。全部仅作为测试已存在的证据。

完整redaction/matching内部、WebSocket recorder及Drive控制器不在穷尽范围。需要真实验证时必须另外选择模式、凭据和网络边界，不以文档构建通过代替源码测试。

## 相关概念

- [会话执行生命周期](06-session-execution-lifecycle.md)
- [云端与更新边界](15-cloud-update-boundaries.md)
- [状态与回放阅读实验](../examples/03-state-and-replay-reading-lab.md)

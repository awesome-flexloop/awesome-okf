---
type: Concept
title: "OpenCode 2.0.32 配置与上下文解析"
description: "沿来源发现、有序配置及领域插件追踪技能、指令与压缩设置"
source: "../spec/facts-deepening-2.0.32.md"
tags: [opencode, config, skill, instruction, compaction]
status: draft
sources:
  - id: source
    resource: ../references/source-deepening-2.0.32.md
    title: 同快照深化信源
---

# OpenCode 2.0.32 配置与上下文解析

本篇补充[包地图](05-monorepo-package-map.md)与[会话生命周期](06-session-execution-lifecycle.md)，说明配置怎样成为模型上下文。对象是固定`2.0.32`源码，不是历史配置教程的无条件延伸。事实依据为[F-115～F-122](../spec/facts-deepening-2.0.32.md)。

## 先找来源，再看消费

`ConfigDiscovery`区分system、global、explicit、direct、project、Claude与agents来源；project walk排除已经识别的global roots/files，direct/project列表经反转返回。接着`Config.entries()`给出有序序列：

```text
managed policies → wellknown → global supplementary → explicit
→ direct → project supplementary → content → managed settings
```

这是来源顺序，不是已经替每个领域完成通用深合并的对象。`Config.latest(entries,key)`找到最后一个该字段非`undefined`的document，返回其字段值`info[key]`；其他领域由插件自行消费entries。理解某字段时，必须继续找它的消费方，不能停在配置文件列表。（F-115、F-116）

## 技能发现与同名覆盖

`ConfigSkillPlugin`从directory entry的`skill/skills`和document的`skills`字段构造来源；后读来源的同ID技能覆盖前者，watcher经100ms debounce后rescan/reload。（F-118）

`SkillScan`遇到目录内`SKILL.md`便停止继续下探；没有`SKILL.md`的扫描根会采集普通`.md`，递归depth上限为6。`SkillFile.parse`从文件名或父目录名派生ID，`metadata["opencode/autoinvoke"]`优先于`disable-model-invocation`。（F-119）

“文件存在”“被扫描”“最终ID保留”“允许autoinvoke”是不同问题。排查技能未出现时依次查来源、扫描停止条件、ID冲突和frontmatter解析；不要先假定深目录一定会被扫描。

## 指令的刷新与去重

配置指令插件组合global/project/configured内容。HTTP URL获取有5秒timeout；获取失败保留最后成功副本，没有旧副本则跳过该URL。URL不可达本身不会使整个指令集unavailable，三个来源都是空数组仍可产生available；`editor.unavailable()`对应不可用状态或激活失败。因此远程暂时不可用与此前缓存仍可使用并不矛盾。（F-117）

会话侧`SessionInstructions`另有两种去重：`inFlight`仅防同Session/path并发发布，`ensuring`负责释放claim；持久去重看模型可见synthetic metadata中的`instruction.paths`。不能把进程内Set扩写为跨重启持久状态，也不能忽略模型可见性条件。（F-120）

## 压缩不是单一阈值开关

`SessionCompaction`默认`auto=true`、`keep=15000`；配置插件逐document消费auto、buffer与keep.tokens。触发原因区分manual与非manual，关闭auto会跳过非manual路径，包括overflow，而不是只关闭某个定时行为。（F-121）

压缩还分summary/native。native路径要求稳定provenance，路由后的provenance必须compatible；仅在`model.request`改写endpoint不能替代配置来源一致性。`calculateCeiling`有显式buffer直接扣除与默认窗口保留分支；默认保留15%，足够大的窗口至少保留16000。这里的数字是计算分支，不应转述为固定可用上下文或质量保证。（F-122）

## 阅读练习与边界

依次打开discovery、config entries、对应插件，再打开Session消费者，分别回答：来源是否进入序列、同ID/同字段怎样处理、状态怎样刷新、失败回退在哪里。配置压缩测试使用mock LLM；本轮仅阅读其定义，没有验证真实Provider压缩。normalize/variable及全部指令测试不在穷尽范围。

## 相关概念

- [会话执行生命周期](06-session-execution-lifecycle.md)
- [Codemode运行时边界](11-codemode-runtime-boundaries.md)
- [新增事实与源码链接](../spec/facts-deepening-2.0.32.md)

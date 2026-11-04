---
type: Concept
title: 五个创造模式案例的设计与证据
description: 倒计时、主题、Transformer、建筑和体素海岛分别训练哪些设计能力，以及哪些只是需求。
source: ../references/creator-mode-facts.md
sources:
  - { id: facts, resource: ../references/creator-mode-facts.md }
  - { id: article, resource: "https://mp.weixin.qq.com/s/pslQaWATxQDlhBBAZROEwg" }
generated: { by: "process:seven-concepts-cmd", at: "2026-11-04T10:01:28+08:00" }
status: draft
stale_after: 2026-12-04
---

# 五个创造模式案例的设计与证据

原文五个案例从小组件扩展到全局样式、教学场景、文化展示和建造交互。[F-021](../references/creator-mode-facts.md) 下列“建议验证”均为本教程提出的验收设计，不是作者已经执行的测试。

## 倒计时与边界状态

`offwork-countdown` 要求挂在聊天输入区右上角，以 `HH:MM:SS` 显示距下班的时间，默认目标为 `18:30`，允许调整；还有百分比进度和归零变色、标题切换。[F-028 至 F-030](../references/creator-mode-facts.md) 作者明确报告看到归零后的状态，没有提供所有跨日与时间修改测试。[F-032](../references/creator-mode-facts.md)

这个案例的学习价值是把一句愿望分成位置、时间输入、显示格式、状态迁移和恢复行为。百分比还需要工作日开始时间，源文没有完整给出计算口径，不能直接猜一个值。

建议验证：目标时间早于现在时不显示负数；修改目标时间立即更新；回到聊天不妨碍输入；停用插件后计时器不再重复运行。首次尝试可以暂不实现百分比，先验收倒计时，详见[练习](../examples/creator-first-plugin.md)。

## Style Lab 与全局变更

需求列出五套皮肤：8-Bit Pixel、Neon Grid、Green Terminal、Paper Press、Zen Glass。范围覆盖侧栏、聊天、输入区、代码卡和菜单，还要求实时切换、本地保存与恢复默认。8-Bit Pixel 指定圆角 `0px`。[F-033 至 F-036](../references/creator-mode-facts.md)

作者报告五张主题卡出现，Green Terminal 即时切成黑底绿字，8-Bit Pixel 去掉圆角。[F-037](../references/creator-mode-facts.md) 这些描述不能替代其余主题、代码块可读性、窄屏布局、重启持久化及卸载恢复测试。

建议验证：先选择单一主题覆盖一个面板，再检查全局覆盖；恢复默认后既有聊天仍能使用；同一按钮只注册一次；切换主题不清空会话。设计方案应说明样式作用域与持久化位置，避免将全局改动隐藏在普通视觉要求里。

## Transformer Lab 与教学准确性

需求使用 `the cat sat on the`，展示五个 Token 和 Embed、Q K V、Attention、Mix、FFN、Logits 六阶段；四维向量与两层 FFN 是作者指定的教学简化。[F-038 至 F-040](../references/creator-mode-facts.md)

作者还指定末尾 `the` 关注 `cat`、`sat`，并给出五个候选概率。[F-041、F-042](../references/creator-mode-facts.md) **这些数值与关注对象不是读取真实模型所得。** 五个概率加总为 `0.97`，缺失部分没有来源，不能擅自分配给其他词。[核验记录](../references/verification.md)保留了计算。

| 展示对象 | 可以说明 | 不能据此证明 |
|---|---|---|
| 五个 Token | 作者设计的教学输入序列 | 任意真实 tokenizer 都得到相同分词 |
| 四维向量 | 为视觉理解压缩后的示意 | DeepSeek 实际隐藏维度是四维 |
| 六阶段镜头 | 场景播放与讲解次序 | 完整模型计算图、真实计算结果 |
| Q K V 与弧线 | 作者希望表达的注意力关系 | 某次真实推理中的注意力权重 |
| 候选条形图 | 固定演示数据 | 模型预测的正确率与校准程度 |

作者报告旋转、缩放、Inspector、阶段播放和返回聊天可用。[F-043](../references/creator-mode-facts.md) 建议把“交互验收”与“学科内容验收”分开：前者测试按钮和视角，后者请懂模型原理的人审核公式、符号、遗漏结构与演示标签。该场景适合作为交互教学原型，不作为真实推理可视化工具。

## 建筑场景与资料真实性

需求展示埃菲尔铁塔、长城、太和殿和斗兽场，支持 Day、Dusk、Night 三档光照、旋转、标注、重置和返回。长城、太和殿的结构术语及三层台基描述来自提示词。[F-044 至 F-046](../references/creator-mode-facts.md)

作者报告查看白天慕田峪长城与黄昏太和殿，没有逐项证明四座建筑与全部标注的准确性。[F-047](../references/creator-mode-facts.md) 原文“热度很高”没有数据，本教程不沿用排名或热度结论。[F-048](../references/creator-mode-facts.md)

建议验证：每个地标可切换、镜头重置可回到起点、标签可关闭；资料来源与几何示意分开标注。若用于正式历史或建筑教学，需补权威测绘与建筑史来源，不能凭生成模型的外观判断真实性。

## FUYU 与状态一致性

需求为等轴测体素海岛，带数量统计、一键建亭及八格建造工具栏；初始七棵树、三只小羊，夜景有双层飞檐木亭和发光灯笼。[F-049 至 F-052](../references/creator-mode-facts.md)

作者报告 SUNNY NOON 起步，可通过建造或 STARRY NIGHT 按钮进入夜景。[F-053](../references/creator-mode-facts.md) 全工具建造、删除、计数、保存、重复建亭等仍缺独立证据。

建议验证：放置对象后统计变化，删除后恢复；一键建亭连续点击的行为有定义；日夜切换只改变环境，不意外重置世界；返回聊天后原会话可用。先做单一对象的放置与移除，再增加完整工具栏，较容易定位状态问题。

## 从案例选择学习任务

| 想学习的能力 | 起点 | 延后到基本流程通过后 |
|---|---|---|
| 描述挂载位置与状态 | 倒计时 | 百分比与跨日规则 |
| 全局外观与恢复 | 单面板主题 | 五主题与全局持久化 |
| 教学信息与交互同步 | 固定数据的单阶段面板 | 三维镜头与完整讲解 |
| 内容真实性与展示分离 | 一个带来源的地标 | 多建筑与结构标签 |
| 交互数据一致性 | 一个对象的增删与计数 | 完整体素建造世界 |

这一学习顺序是执行者建议，没有实验数据证明其必然更快或更省 Token。

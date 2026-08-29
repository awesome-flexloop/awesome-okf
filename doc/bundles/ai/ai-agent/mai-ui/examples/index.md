# 实战示例（Examples）

本目录收录基于 MAI-UI 仓库自带 cookbook 的两个可复现 notebook 教程。两者只需 vLLM 服务与仓库自带示例图即可复现，是仓库内仅有的"跑一遍"素材；所有步骤与 API 调用均来自事实台账（F-049、F-050），未添加 notebook 之外的步骤。

## 示例列表

| 序号 | 文档 | 场景 | 核心内容 |
|------|------|------|---------|
| 01 | [Grounding Notebook 复现](01-grounding-notebook.md) | 单图单元素定位 | figure1.png → predict → 归一化坐标换算绝对像素 → 红圈可视化 |
| 02 | [Run Agent Notebook 复现](02-navigation-trajectory-notebook.md) | 5 张连续截图多步导航 | figure1~5 循环 predict、同一实例轨迹累积、save_traj 检查轨迹 |

### 路径建议

先跑 01（grounding 无基类依赖，最低成本验证 vLLM 链路），再跑 02（观察轨迹累积与消息回放的增长）。

```{toctree}
:hidden:
:maxdepth: 2

01-grounding-notebook
02-navigation-trajectory-notebook
```

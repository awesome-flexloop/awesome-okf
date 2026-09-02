# 信源登记簿（References）

本目录是 ROS 2 知识包的信源登记，收录简书连载《☠️无人驾驶(停止维护)》中介绍 ROS 2 概念的文章。所有 concepts 文档中引用的事实均可追溯到此处的原始信源。

## 信源清单

| 信源ID | 文档 | 原始来源 | 覆盖事实范围 |
|--------|------|---------|-------------|
| jianshu-86377a66ecef | [source-01.md](source-01.md) | 《ROS2 概念》（2020 年前后） | F-324 ~ F-332（ROS 2 核心概念） |

## 事实编号索引

| 编号段 | 主题 | 登记位置 |
|-------|------|---------|
| F-324 ~ F-326 | 发布订阅中间件、ROS graph、基本概念、节点 | [source-01.md](source-01.md) |
| F-327 ~ F-328 | 客户端库（rclcpp/rclpy）、节点发现过程 | [source-01.md](source-01.md) |
| F-329 ~ F-330 | DDS/RTPS 中间件、DDS 实现与 rmw | [source-01.md](source-01.md) |
| F-331 ~ F-332 | QoS History 策略、Topic Statistics | [source-01.md](source-01.md) |

## 信源可信度说明

- 文章内容为 ROS 2 官方概念的转述整理（节点/话题/消息/发现/DDS/QoS），非作者独创观点，属**概念综述**；
- 内容时点为 2020 年前后，涉及 ROS 2 Dashing/Foxy 早期版本，部分细节（如 Topic Statistics 的 Foxy 实现范围）可能已过时，仅作历史方法与概念参考；
- 文章 URL 为简书公开链接，未做第三方交叉核验（非 P0 成效数字类声明），按"仅博文单源"处理。

```{toctree}
:hidden:
:maxdepth: 7

source-01
```

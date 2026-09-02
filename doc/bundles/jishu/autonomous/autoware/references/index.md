# 信源登记簿（References）

本目录是 Autoware 知识包的信源登记，收录简书连载《☠️无人驾驶(停止维护)》中与 Autoware/Autoware.Auto 搭建直接相关的 4 篇文章。所有 concepts 文档中引用的事实均可追溯到此处的原始信源。

## 信源清单

| 信源ID | 文档 | 原始来源 | 覆盖事实范围 |
|--------|------|---------|-------------|
| jianshu-7218542ae424 | [source-01.md](source-01.md) | 《Ubuntu 搭建 AutowareAuto》（2020 年前后） | F-319 ~ F-323（ADE 开发环境） |
| jianshu-8f97786e1631 | [source-02.md](source-02.md) | 《AutowareAuto 基础》（2020 年前后） | F-333 ~ F-340（Autoware 三系与演示） |
| jianshu-a95f95276fec | [source-03.md](source-03.md) | 《WSL2 之 autoware.auto》（2020 年前后） | F-349 ~ F-353（WSL2 环境一） |
| jianshu-dfc1df4eb6ee | [source-04.md](source-04.md) | 《WSL2 安装和配置无人驾驶系统 autoware.auto》（2020 年前后） | F-357 ~ F-361（WSL2 环境二） |

## 事实编号索引

| 编号段 | 主题 | 登记位置 |
|-------|------|---------|
| F-319 ~ F-323 | ADE 开发环境原理与构建测试命令 | [source-01.md](source-01.md) |
| F-333 ~ F-340 | Autoware 三系、能力范围、ADE 安装与目标检测演示 | [source-02.md](source-02.md) |
| F-349 ~ F-353 | WSL2 X 桌面、docker/conda/ade-cli、免 sudo、构建测试 | [source-03.md](source-03.md) |
| F-357 ~ F-361 | Ubuntu 子系统远程桌面、初始化、VcXsrv 显示转发 | [source-04.md](source-04.md) |

## 信源可信度说明

- 四篇均为作者一手实测教程（"水之心"），描述自己环境中的实际安装与演示命令，属**一手实操记录**，无厂商自宣数据；
- 内容时点均为 2020 年前后，涉及 Autoware.Auto 早期版本、ROS2 Dashing、WSL2 早期版本，命令细节可能已过时，仅作历史方法与概念参考；
- 文章 URL 均为简书公开链接，未做第三方交叉核验（非 P0 成效数字类声明），按"仅博文单源"处理。

```{toctree}
:hidden:
:maxdepth: 7

source-01
source-02
source-03
source-04
```

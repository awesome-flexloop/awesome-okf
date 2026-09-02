# 概念文档（Concepts）

本目录包含 Autoware 知识包的核心概念文档，按"环境 → 基础"的递进路径排列：先解决环境问题，再理解 Autoware 生态本身。

## 学习路径

| 序号 | 文档 | 核心问题 |
|------|------|---------|
| 00 | [WSL2 环境搭建 Autoware.Auto](00-wsl2-environment.md) | 在 Windows WSL2 中如何搭建 Autoware.Auto 开发环境（两条路径 + 显示转发） |
| 01 | [Ubuntu 与 ADE 开发环境](01-ubuntu-ade-environment.md) | ADE 开发环境是什么？adehome 主目录与构建测试命令如何工作 |
| 02 | [Autoware.Auto 基础](02-autoware-auto-basics.md) | Autoware 三系是什么？2020 年 Autoware.Auto 能做什么，如何安装与演示 |

### 路径建议

```
00 WSL2 环境（Windows 用户入口）
   ↓
01 ADE 开发环境（环境公共底座）
   ↓
02 Autoware.Auto 基础（生态与能力总览）
```

三篇文档均可独立阅读；Windows 用户建议从 00 开始，Ubuntu 用户可直接读 01 与 02。

```{toctree}
:hidden:
:maxdepth: 7

00-wsl2-environment
01-ubuntu-ade-environment
02-autoware-auto-basics
```

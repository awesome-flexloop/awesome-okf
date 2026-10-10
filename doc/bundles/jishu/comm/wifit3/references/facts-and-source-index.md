---
type: reference
title: "事实与来源索引：SRC-001 / SRC-002"
description: "WiFiT3 文章的 F 编号、定位与核验边界"
tags: [provenance, facts, single-source, wifi, security]
status: draft
stale_after: 2027-10-07
generated:
  by: process:seven-concepts-wifit3-okf
  at: 2026-10-10T12:00:00Z
sources:
  - id: src-001
    resource: https://mp.weixin.qq.com/s/ufDnlN7grRoYzNT5LxY26A
    title: "kali笔记：离了大谱! 这款WiFi工具太强了"
  - id: src-002
    resource: https://github.com/derv82/wifit3
    title: "derv82/wifit3 - A standalone USB Wi-Fi auditor"
---

# 事实与来源索引

| F 编号 | 类型 | 摘要 | 定位 | 状态 |
|---|---|---|---|---|
| F-001 | 页面事实 | 文章标题为"离了大谱! 这款WiFi工具太强了" | 页面标题 | observed |
| F-002 | 页面事实 | 作者/账号为"kali笔记"（大表哥吆），发布于 2026-10-07 | 作者与发布时间区域 | observed |
| F-003 | 页面事实 | 文章以 kali Linux 环境演示 WiFiT3 安装 | 快速上手章节 | observed |
| F-004 | 作者观点 | 程序扫描网络并提示安装缺少模块 | 快速上手章节 | author-claim/src-001 |
| F-005 | 作者观点 | 信息收集展示信道、信号强度、设备厂商等信息 | 快速上手章节 | author-claim/src-001 |
| F-006 | 作者观点 | 文章评价工具"太强""有很多值得学习的地方" | 总结章节 | author-claim/src-001 |
| F-007 | 作者观点 | 选择目标网络、回车进入控制台 | 快速上手章节 | author-claim/src-001 |
| F-008 | 作者观点 | 选择 `AutoDeauth` 可在日志中查看握手/找回进度 | 快速上手章节 | author-claim/src-001 |
| F-009 | 页面事实 | 官方定位为 standalone USB Wi-Fi auditor，跨 Linux/Windows/macOS | 官方 README（src-002） | observed |
| F-010 | 页面事实 | 支持多卡聚合、多网卡同时抓包、指定卡注入 | 官方 README（src-002） | observed |
| F-011 | 页面事实 | 2.4/5GHz 实时信道跳频扫描，跟踪信号强度与加密套件、WPA3/SAE | 官方 README（src-002） | observed |
| F-012 | 页面事实 | AP 与客户端识别、指纹厂商、WPS 信标提取路由器型号 | 官方 README（src-002） | observed |
| F-013 | 页面事实 | VAP Decloaking 识别隐藏网络 | 官方 README（src-002） | observed |
| F-014 | 页面事实 | 数据包仪表盘可视化信标/数据/注入/取消认证速率 | 官方 README（src-002） | observed |
| F-015 | 页面事实 | WPA/WPA2 握手被动嗅探 + 定向取消认证，导出 .pcap/.hc22000 | 官方 README（src-002） | observed |
| F-016 | 页面事实 | PMKID Harvesting 主动/被动采集 | 官方 README（src-002） | observed |
| F-017 | 页面事实 | 零运行时依赖（无 aircrack-ng/reaver），纯 Python+PyUSB+Textual | 官方 README（src-002） | observed |
| F-018 | 页面事实 | EvilTwin WPA3 降级，克隆 AP 并通过 CSA/BTM/de-auth 捕获握手 | 官方 README（src-002） | observed |
| F-019 | 页面事实 | WPS 恢复套件：PixieDust(2 模式)/PBC/PIN 爆破 | 官方 README（src-002） | observed |
| F-020 | 页面事实 | 内置轻量无线协议栈（mini-drivers），USB 控制无线芯片 | 官方 README（src-002） | observed |
| F-021 | 页面事实 | 避开 Windows NDIS 与 Linux 内核驱动锁限制 | 官方 README（src-002） | observed |
| F-022 | 页面事实 | 需要至少一块受支持 USB 网卡，维护支持硬件清单 | 官方 README（src-002） | observed |
| F-023 | 页面事实 | WEP 套件：ARP 重放 / ChopChop / 伪装认证 / PTW | 官方 README（src-002） | observed |
| F-024 | 页面事实 | 提供 Linux/Windows/macOS 三平台预编译二进制 | 官方 README（src-002） | observed |
| F-025 | 页面事实 | 一次性驱动设置流程（Linux pkexec/sudo、Windows UAC/WinUSB、macOS 授权） | 官方 README（src-002） | observed |
| F-026 | 页面事实 | 卸载流程（删除 udev/modprobe 规则或卸载 WinUSB） | 官方 README（src-002） | observed |
| F-027 | 页面事实 | 合法授权边界与使用风险声明 | 官方 README（src-002） | observed |
| F-028 | 页面事实 | 仓库状态：v0.3.3 BETA、约 2449 commits、672 stars、74 forks | 官方仓库（src-002，2026-10-10 观察） | observed |

## 核验边界

- **文章评价（F-004-F-008）**：为 `kali笔记` 作者的单源观点与操作演示描述，无独立评测/基准数据，仅能作为作者观点引用，不可作为工具能力的确凿证据。
- **工具能力（F-009-F-027）**：以官方仓库 README 为核验基准；仓库为公开、活跃维护（该束观察时 GPL-2.0，`src-002`）。能力清单未逐一在真实网卡上演测，属于"官方自述"而非独立第三方验证。
- **版本漂移（F-028）**：仓库处于活跃开发，star/commit/release 数字会随时间变化；本束以 2026-10-10 观察快照为准，`stale_after` 已设 2027-10-07。
- 原始链接由 `src-001`、`src-002` 提供，未复制文章全文或构建镜像。
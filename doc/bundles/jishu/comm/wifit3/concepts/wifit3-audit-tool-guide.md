---
type: concept
title: "WiFiT3 使用教程：前期侦察、密码找回与快速上手"
description: "基于公开文章与官方仓库，原创改写的 WiFiT3 跨平台 WiFi 安全审计工具教程"
tags: [wifi, security, audit, reconnaissance, password-recovery]
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

# WiFiT3 使用教程

## 一、先把文章观点放回原位

公众号文章（`kali笔记`，2026-10-07 发布）把 WiFiT3 描述为"离了大谱""太强"的 WiFi 工具（F-001-F-006）。这些是作者的推荐与修辞。工具的实际能力以官方仓库 README（`SRC-002`）为核验基准：官方将其定位为 standalone USB Wi-Fi auditor（独立 USB Wi-Fi 审计工具），跨 Linux / Windows / macOS 三平台（F-009）。

## 二、工具定位：Userland 独立协议栈

WiFiT3 的核心设计不同于传统工具（如 aircrack-ng / wifite2）依赖系统内核无线驱动：

- 它内置一套 **Python 移植的轻量无线协议栈**（mini-drivers），直接通过 USB bulk/control 传输控制无线芯片（F-020）。
- 因此**不需要**系统原生 WiFi 驱动进入 monitor 模式，可规避 Windows NDIS 与 Linux 内核驱动锁的限制（F-021）。
- 运行时**零外部依赖**（不依赖 aircrack-ng / reaver），纯 Python + PyUSB + Textual（F-017）。
- **硬件前置条件**：至少需要一块**受支持的 USB 无线网卡**，官方维护支持硬件清单（Atheros / MediaTek / Realtek / Ralink 等芯片组，F-022）。

## 三、两大能力模块（原创改写）

### 1. 前期侦察与分析

- **多网卡聚合**：可同时用多块网卡抓包，并指定其中一块用于注入（F-010）。
- **实时扫描**：2.4GHz / 5GHz 频段跳频扫描（多卡可拆分），跟踪信号强度、加密套件、WPA3/SAE 过渡模式（F-011）。
- **AP 与客户端识别**：指纹识别设备厂商与类别；从 WPS 信标提取路由器品牌与型号（F-012）。
- **VAP 隐网揭露**：通过关联 BSSID 与已知可见网络，识别隐藏网络（F-013）。
- **数据包仪表盘**：可视化实时信标、数据、注入与取消认证的数据包速率（F-014）。

### 2. 密码找回与握手捕获

- **WPA/WPA2 握手**：被动嗅探 + 定向取消认证；校验可破解的握手对；导出 `.pcap` 与 `.hc22000`（F-015）。其中 `.hc22000` 为 **hashcat 的破解输入格式**，可直接交给 hashcat 离线破解；`.pcap` 是标准抓包格式。
- **PMKID 收割**：主动关联收割与被动嗅探 WPA/WPA2 的 PMKID 密钥材料（`.hc22000`）（F-016）。
- **EvilTwin WPA3 降级**：克隆 AP，通过 CSA / BTM / 取消认证逐出客户端以捕获握手（支持单/多网卡）（F-018）。
- **WPS 恢复套件**：PixieDust（空秘密 / 静态秘密 PRNG 弱点）、PBC 按键捕获、可断点续传的 PIN 爆破（F-019）。
- **WEP 套件**：纯 Python ARP 重放、ChopChop、伪装认证与 PTW 密钥恢复（F-023）。

> **能力边界提示**：WEP 属已过时的弱加密，教程仅作协议原理介绍，不鼓励在现实网络中使用。

## 四、快速上手（按文章流程改写）

文章以 kali Linux 环境演示安装（F-003）；官方提供三平台预编译二进制（F-024）。通用流程：

```bash
# 1. 下载对应系统预编译可执行文件（Windows / Linux / macOS）
#    Linux 示例：
chmod +x wifit3-linux-x64 && ./wifit3-linux-x64

# 2. 首次启动，程序会引导一次性驱动设置：
#    - Linux：提示用 pkexec/sudo 写入 udev 权限与 modprobe 黑名单
#    - Windows：UAC 提权安装 WinUSB
#    - macOS：无需安装，授权窗口点允许即可
#    （F-025）
```

进入界面后：

1. 插入受支持网卡，程序扫描网络（F-004）。
2. 在扫描结果中查看信道、信号强度、加密方式、设备厂商等（F-005）。
3. 选择目标网络，进入控制台（F-007）。
4. 使用 `AutoDeauth` 自动找回密码，在日志中查看握手获取进度（F-008）。

也可以从源码运行（需要 `uv`）：

```bash
uv sync
uv run wifit3
```

## 五、驱动设置与卸载

- **一次性驱动设置**：启动后按 `START`，程序会自动处理硬件配置（udev 权限 / WinUSB / macOS 授权）（F-025）。
- **卸载**：在启动界面选择网卡 → 点击 `Uninstall` → 确认提权 → 拔插网卡。Linux 会删除其 udev 与 modprobe 规则，Windows 会卸载 WinUSB 绑定并触发 PnP 重扫（F-026）。

## 六、使用限制与风险

- **合法授权**：官方明确声明仅用于自有机或经授权审计的网络与设备，且工具直接操作 USB 硬件寄存器、绕过内核护栏，风险自担（F-027）。
- **单源评价**：文章对工具的"太强""值得学习"等评价（F-006）为作者观点，非评测机构的结论；星级、性能对比等未经独立基准验证。
- **版本漂移**：本教程能力以官方仓库 README 为锚，工具处于活跃开发（该束核验时仓库 version v0.3.3 BETA、约 2449 commits、672 stars，F-028），特性可能快速变化，`stale_after` 已设 2027-10-07。

## 来源映射

具体页面事实与观点请参阅 [事实与来源索引](../references/facts-and-source-index.md)。
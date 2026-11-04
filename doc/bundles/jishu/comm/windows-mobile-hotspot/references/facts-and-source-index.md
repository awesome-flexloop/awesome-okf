---
type: reference
title: "事实登记簿 F-001~F-038"
description: "Windows 11 移动热点知识包的事实登记——38 条编号事实，按来源族分组，标注口径类型与证据层级，供逐声明溯源"
tags: [windows-11, mobile-hotspot, facts, source-index, evidence-grading]
status: draft
stale_after: "2027-05-04"
generated: { by: "seven-concepts-cmd", at: "2026-11-04" }
sources:
  - id: s1-wx-article
    resource: "https://mp.weixin.qq.com/s/IG0HnN7HxCjgMkFJLBLh2g"
    title: "微信公众号图文《把 Windows 11 变成无线路由器！电脑也能发 Wi-Fi》"
  - id: s2-ms-support-hotspot
    resource: "https://support.microsoft.com/en-us/windows/experience/connectivity-networking/use-your-windows-device-as-a-mobile-hotspot"
    title: "Microsoft 支持：Use your Windows device as a mobile hotspot"
  - id: s3-ms-learn-sr2003-network
    resource: "https://learn.microsoft.com/zh-cn/previous-versions/windows/it-pro/windows-server-2003/cc728250(v=ws.10)"
    title: "Microsoft Learn：Home and small office networking features"
  - id: s4-ms-learn-embedded-ics
    resource: "https://learn.microsoft.com/en-my/previous-versions/windows/embedded/aa940309(v=winembedded.5)"
    title: "Microsoft Learn：Windows Firewall/Internet Connection Sharing (ICS)"
---

# 事实登记簿 F-001~F-038

## 登记规则

- **口径类型**：`article_claim` 源文主张 · `official_doc` 官方支持文档 · `official_learn` 官方学习文档 · `official_qa` 官方社区答复 · `official_spec` 官方兼容性规范 · `community` 第三方社区口径 · `secondary` 二手报道 · `package_inference` 本包推断
- **证据层级**：L1 官方支持/产品文档 · L2 官方技术学习文档 · L3 官方社区答复 · L4 官方兼容性规范 · L5 第三方社区口径（多源交叉） · L6 二手媒体报道
- **本表只登记陈述**，不含因果推断——因果判断归入概念层与 [核验报告](verification.md)。
- **来源缩写**：`s1-wx-article` ~ `s14-community-ics-subnet`，完整 URL 见本包根 [index.md](../index.md) 的 `sources` 段。

## 一、源文主张（s1-wx-article，`article_claim`）

| 编号 | 事实陈述 | 口径类型 | 层级 |
|---|---|---|---|
| F-001 | 源文设定的场景是：手中只有一根可上网的网线与一台 Windows 电脑，旁边设备没有网线接口、只能走 Wi-Fi | article_claim | — |
| F-002 | 源文主张：带无线网卡的 Windows 电脑可把有线网络共享为 Wi-Fi 热点，电脑充当临时无线路由器 | article_claim | — |
| F-003 | 源文的入口路径为：开始菜单 →「设置」→「网络和 Internet」→「移动热点」 | article_claim | — |
| F-004 | 源文要求在「共享我的以下 Internet 连接」中选择有线网络（以太网） | article_claim | — |
| F-005 | 源文的属性步骤为：点「编辑」设置 Wi-Fi 名称、密码、频段，保存后打开右上角开关 | article_claim | — |
| F-006 | 源文建议网络名称采用英文字符，不使用中文，理由是避免部分设备识别乱码 | article_claim | — |
| F-007 | 源文标注密码要求至少 8 个字符 | article_claim | — |
| F-008 | 源文列出频段可单独指定 5GHz 或 2.4GHz，并称 5GHz 速度更快但兼容性稍差、2.4GHz 兼容性强但速度略慢，设备混杂时建议选「任何可用频率」 | article_claim | — |
| F-009 | 源文称 Windows 11 移动热点最多可连接 8 台设备 | article_claim | — |
| F-010 | 源文称终端接入后可在 Windows 属性中看到设备名称、IP 地址与 MAC 地址，多台设备接入时信息与连接数量一目了然 | article_claim | — |
| F-011 | 源文称关闭开关即可停止共享，下次开启无需重新设置 | article_claim | — |
| F-012 | 源文建议电脑用有线网卡共享网络，硬件上至少一块有线网卡加一块无线网卡；两块无线网卡（一块连 Wi-Fi、一块发热点）也可行，源文举例为网络测试场景 | article_claim | — |
| F-013 | 源文注意事项列出：电脑不能关机，关机后热点消失 | article_claim | — |
| F-014 | 源文注意事项列出：需关闭自动休眠，休眠后热点可能无法继续使用 | article_claim | — |
| F-015 | 源文注意事项称：真正的路由器可长期运行并支持防火墙、DHCP、端口转发等功能，Windows 11 移动热点更适合临时应急共享网络，不建议作为长期方案替代路由器 | article_claim | — |

## 二、官方支持文档（s2 / s13，`official_doc`，L1）

| 编号 | 事实陈述 | 口径类型 | 层级 |
|---|---|---|---|
| F-024 | 官方支持文档给出的入口为「设置 > 网络和 Internet > 移动热点」，并提供 `ms-settings:network-mobilehotspot` 快捷 URI | official_doc | L1 |
| F-025 | 官方支持文档列出的「共享我的 Internet 连接来源」可选 Wi-Fi、以太网或蜂窝数据 | official_doc | L1 |
| F-026 | 官方支持文档列出的「共享方式」可选 Wi-Fi 或蓝牙，并说明 Wi-Fi 通常更快且是默认项 | official_doc | L1 |
| F-027 | 官方支持文档说明：展开「属性」后点「编辑」可设置网络名称、密码与网络频段 | official_doc | L1 |
| F-028 | 官方支持文档说明：其他设备可通过输入密码或扫描 QR 码连接到热点 | official_doc | L1 |
| F-029 | 官方支持文档说明：任务栏快速设置中含「移动热点」快捷操作，可能需翻到快速操作第二页；点击可开关热点并沿用默认或上次在设置中使用的属性；开启时该快捷操作显示已连接设备数；可右键「转到设置」 | official_doc | L1 |
| F-030 | 官方支持文档说明：设备具备蜂窝数据时可远程开启移动热点，需 Windows 电脑与控制端设备双方具备蓝牙且已完成配对 | official_doc | L1 |
| F-031 | 官方支持文档标注：Windows 10 的支持已于 2025-10-14 结束，此后不再提供免费软件更新、技术支持与安全修复 | official_doc | L1 |
| F-038 | 官方学习中心载明的使用场景：把有线上网的电脑共享为热点供其他设备使用；在只允许单台设备付费上网的场景（如航司机上 Wi-Fi）中，用笔记本热点把联网能力分享给手机或平板；带 5G 的笔记本可把蜂窝数据作为共享来源 | official_doc | L1 |

## 三、官方学习文档与兼容性规范（s3 / s4 / s5 / s9）

| 编号 | 事实陈述 | 口径类型 | 层级 |
|---|---|---|---|
| F-016 | 官方学习文档载明：ICS 通过提供本地私有网络服务（名称解析与地址分配）简化小网络配置 | official_learn | L2 |
| F-017 | 官方学习文档载明：启用 ICS 时只有 ICS 主机对 Internet 可见，ICS 客户端的地址对 Internet 隐藏 | official_learn | L2 |
| F-018 | 官方学习文档载明：ICS 组件提供 DHCP 与 DNS 服务到私网，并对发往公网的报文做修改，使其在公网看来发自 ICS 机器本身 | official_learn | L2 |
| F-019 | 官方兼容性规范载明：ICS 扮演 DHCP 服务器并充当 DNS 代理；主机防火墙须放行 DHCP（入向 UDP 68→67，出向 UDP 67→68）与 DNS（UDP 53）流量 | official_spec | L4 |
| F-020 | 官方 schema 文档载明：WPA2-PSK / WPA2PSK 在 TKIP 或 AES 下的 passphrase 有效值为 8 到 63 个 ASCII 字符，即码位 32 到 126 的 ANSI 字符；无法映射到 ANSI 或 ASCII 的 Unicode 字符将被拒绝 | official_learn | L2 |

## 四、官方社区答复（s6 / s7 / s8 / s12，`official_qa`，L3）

| 编号 | 事实陈述 | 口径类型 | 层级 |
|---|---|---|---|
| F-021 | 官方社区中文答复载明：Windows 11/10 系统暂不支持「限制移动热点设备连接数量」的功能，连接上限为 8 部设备；建议设置复杂密码并轻易不要向他人共享密码 | official_qa | L3 |
| F-022 | 官方社区英文答复载明：Windows 10/11 内置移动热点没有超出默认值的设备数上限设置项 | official_qa | L3 |
| F-023 | 官方社区答复载明：在 `HKEY_LOCAL_MACHINE\SYSTEM\CurrentControlSet\Services\icssvc\Settings` 下新建 DWORD 值 `WifiMaxPeers` 可调整热点最大连接数，重启后生效 | official_qa | L3 |
| F-032 | 官方社区答复载明：出现「已连接但无网络」时，常见成因是共享了错误的 Internet 连接或客户端未取得正确 IP；给出的处置为改选另一网络接口，以及重置网络 | official_qa | L3 |

## 五、第三方社区口径（s14，`community`，L5）

| 编号 | 事实陈述 | 口径类型 | 层级 |
|---|---|---|---|
| F-036 | 社区口径（3 源一致）：ICS 默认把共享网卡 IP 设为 `192.168.137.1`，客户端经 DHCP 从 `192.168.137.0/24` 取址；`HKLM\SYSTEM\CurrentControlSet\Services\SharedAccess\Parameters` 下的 `ScopeAddress` / `ScopeAddressBackup` / `StandaloneDhcpAddress` 用于调整该网段 | community | L5 |
| F-037 | 社区口径：`netsh wlan show drivers` 的 `Hosted network supported` 行探测的是 Hosted Network（Windows 7 时代技术），与当前移动热点的可用性不属同一判据；微软官方移动热点文档全文不含 Hosted Network 与 `netsh wlan` | community | L5 |

## 六、6 GHz 证据冲突组（s10 / s11 / 媒体报道）

| 编号 | 事实陈述 | 口径类型 | 层级 |
|---|---|---|---|
| F-033 | 官方 KB5050094 更新条目清单中未列出「移动热点 6 GHz 支持」条目 | official_doc | L1 |
| F-034 | 官方社区答复载明：KB5050094 原预期启用 6 GHz 移动热点功能，微软随后澄清该功能尚未开始推出 | official_qa | L3 |
| F-035 | 二手媒体报道：Windows 11 24H2 的 KB5050094 为移动热点引入 6 GHz 支持，需 Wi-Fi 6E 设备 | secondary | L6 |

## 七、来源索引

| 编号 | 来源 | 类型 | 层级 |
|---|---|---|---|
| s1 | 《把 Windows 11 变成无线路由器！电脑也能发 Wi-Fi》（公众号「红头发蓝胖纸」，2026-11-03 09:58 北京） | 公众号图文 | — |
| s2 | Microsoft 支持：Use your Windows device as a mobile hotspot | official_doc | L1 |
| s3 | Microsoft Learn：Home and small office networking features（Windows Server 2003 家族文档） | official_learn | L2 |
| s4 | Microsoft Learn：Windows Firewall/Internet Connection Sharing (ICS)（Windows Embedded 组件文档） | official_learn | L2 |
| s5 | Windows Hardware Compatibility Program（ICS 的 DHCP / DNS 代理防火墙放行要求） | official_spec | L4 |
| s6 | Microsoft Learn Answers：win10 专业版 如何限制热点连接数量 | official_qa | L3 |
| s7 | Microsoft Learn Answers：Limiting the number of phones to access my PC hotspot | official_qa | L3 |
| s8 | Microsoft Answers：注册表 `icssvc\Settings\WifiMaxPeers` | official_qa | L3 |
| s9 | Microsoft Learn：keyMaterial（WLAN 配置文件的密钥材料规范） | official_learn | L2 |
| s10 | Microsoft 支持：KB5050094 预览版更新条目清单 | official_doc | L1 |
| s11 | Microsoft Learn Answers：KB5050094 wifi 6GHz hotspot | official_qa | L3 |
| s12 | Microsoft Learn Answers：Network/wifi sharing | official_qa | L3 |
| s13 | Microsoft Windows 学习中心：How to use your laptop as a hotspot on the go | official_doc | L1 |
| s14 | 第三方社区源族（3 源一致）：ICS 默认共享网段与 `SharedAccess\Parameters` 注册表键 | community | L5 |

**s14 的三个佐证源**（本包仅以其中之一作为 `resource` 锚点，其余两处供交叉核对）：

1. `https://www.cnblogs.com/adam-ma/p/17851659.html` —— 博客园《Win10 修改共享网卡 IP》
2. `https://blog.csdn.net/weixin_45535344/article/details/163636339` —— CSDN《通过让电脑充当"路由器"，将有线局域网内的设备流量转发到无线网卡上》
3. `https://tsight.io/articles/16623229` —— TrueSight《深挖网络共享的"幽灵"：192.168.137.1 的技术本质与排障逻辑》

## 八、统计

| 分组 | 条数 | 编号 |
|---|---|---|
| 源文主张（`article_claim`） | 15 | F-001 ~ F-015 |
| 官方支持文档（L1） | 9 | F-024 ~ F-031、F-038 |
| 官方学习文档 / 兼容性规范（L2、L4） | 5 | F-016 ~ F-020 |
| 官方社区答复（L3） | 4 | F-021、F-022、F-023、F-032 |
| 第三方社区口径（L5） | 2 | F-036、F-037 |
| 6 GHz 冲突组（L1 + L3 + L6） | 3 | F-033、F-034、F-035 |
| **合计** | **38** | F-001 ~ F-038 |

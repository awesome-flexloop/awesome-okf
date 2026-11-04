---
type: concept
title: "频段与兼容性：2.4 / 5 GHz、密码规范与驱动约束"
description: "移动热点的频段取舍与兼容性边界——2.4/5 GHz 选择、6 GHz 的证据冲突与不作断言的理由、WPA2-PSK 8–63 字符规范、8 台设备上限的三层证据、SoftAP 与 STA 并发的驱动约束、Hosted Network 辨析"
tags: [windows-11, mobile-hotspot, wifi, 2ghz, 5ghz, 6ghz, passphrase, wpa2, softap, hosted-network, compatibility]
status: draft
stale_after: "2027-05-04"
generated: { by: "seven-concepts-cmd", at: "2026-11-04" }
sources:
  - id: s2-ms-support-hotspot
    resource: "https://support.microsoft.com/en-us/windows/experience/connectivity-networking/use-your-windows-device-as-a-mobile-hotspot"
    title: "Microsoft 支持：Use your Windows device as a mobile hotspot"
  - id: s9-ms-learn-keymaterial
    resource: "https://learn.microsoft.com/en-us/uwp/schemas/mobilebroadbandschema/wlan/element-keymaterial"
    title: "Microsoft Learn：keyMaterial（WPA2-PSK passphrase 8–63 ASCII）"
  - id: s10-ms-kb5050094
    resource: "https://support.microsoft.com/kb/5050094"
    title: "Microsoft 支持：KB5050094 预览版更新条目清单"
  - id: s11-ms-answers-6ghz
    resource: "https://learn.microsoft.com/en-us/answers/a/8002416"
    title: "Microsoft Learn Answers：KB5050094 wifi 6GHz hotspot"
---

# 频段与兼容性：2.4 / 5 GHz、密码规范与驱动约束

## 一、频段选择

源文给出的三个选项与取舍（F-008，`article_claim`）：**5GHz** 速度更快但兼容性稍差；**2.4GHz** 兼容性强但速度略慢；设备杂时选**「任何可用频率」**，兼容性最强。

这个取舍本身是**通用 Wi-Fi 常识**，成立且实用：

| 频段 | 覆盖 | 速率 | 抗干扰 | 典型问题 |
|---|---|---|---|---|
| **2.4 GHz** | 远、穿墙好 | 较低 | 差（拥挤，微波炉/蓝牙干扰重） | 老设备只能连这个；近处速率不够用 |
| **5 GHz** | 近、穿墙差 | 较高 | 好（频段空旷） | 隔墙衰减明显；部分老设备不支持 |
| **任何可用频率** | 交给系统判断 | 视实现 | 最稳 | 具体落到哪个频段不可控 |

**实用建议**：设备构成确定时显式指定频段（性能可控）；构成不确定或要现场救急时选「任何可用频率」（兼容性优先）。

> **口径提示**：微软官方支持文档只写了「网络频段（network band）」这一项，**并未列举具体可选值**（F-027，L1）。三个具体取值来自源文经验与界面实测约定，官方文档未逐项确认——引用时按 `article_claim` 层级对待。

## 二、6 GHz：证据冲突，本包不作断言

<a id="band-6ghz-conflict"></a>

这是本包唯一一处**多方报道互相矛盾**的技术点，单列一节说明理由。

### 2.1 冲突内容

| 立场 | 主张 | 来源与层级 |
|---|---|---|
| **二手报道** | Windows 11 24H2 的 KB5050094 为移动热点**引入 6 GHz 支持**，需 Wi-Fi 6E 设备 | F-035（L6，`secondary`）——多家科技媒体转载同一则消息 |
| **官方 KB 条目清单** | KB5050094 的官方更新条目中**未列出**「移动热点 6 GHz」项 | F-033（L1，`official_doc`） |
| **官方社区答复** | 该更新原计划启用 6 GHz 热点功能，但**微软已澄清此功能尚未开始推出** | F-034（L3，`official_qa`） |

### 2.2 本包的处置

**不写「Windows 11 支持 6 GHz 移动热点」，也不写「不支持」**。理由：

1. 官方 KB 条目清单是 L1 证据，其**沉默**不能直接等同于「不支持」——微软的更新条目常不含完整功能矩阵；
2. 但它同样**不足以支撑肯定断言**；
3. 官方社区答复（L3）明确说「尚未推出」，且时间点晚于二手报道；
4. 三方证据的净结论是：**状态未定，且至少存在一条与肯定断言冲突的官方侧证据**。

**处置方式**：登记为**未闭环项 U-1**，并给出复核触发条件（见 [边界与风险](boundaries-and-risks.md#open-items)）。若读者要在生产环境依赖 6 GHz 热点，**唯一的可靠办法是实机验证**——打开「编辑」看频段下拉里是否出现 6 GHz 选项。

## 三、密码规范：8–63 个 ASCII 字符

微软官方 schema 文档明示（WPA2-PSK / TKIP 或 AES 组合下，F-020，L2）：

> passPhrase：包含 **8 到 63 个 ASCII 字符**的口令，即码位 **32 到 126** 的 ANSI 字符。密钥值须符合 802.11i 的规定。

三条实操含义：

1. **下限 8**：源文说「至少 8 个字符」是对的（F-007），但**只说了下限**；
2. **上限 63**：超长密码会被拒；
3. **必须是 ASCII 可打印字符**：中文、emoji、某些全角符号**无法映射到 ASCII 时会被拒绝**（官方原文明确：不能映射的 Unicode 字符将导致密钥材料被拒）。

> **源文小贴士的价值定位**：源文「网络名称最好用英文字符」（F-006）没有官方背书，但它指向的正是上面这条**硬约束**所在的编码问题域。采纳它作为实践建议，但要知道它**不是**官方规则。

**另一个常见误解**：密码复杂度（大小写混用、符号、数字）**不是**协议要求——8 个 `a` 在协议上合法。官方对复杂度的建议出现在**降低 8 台上限带来的滥用风险**的语境里：设置复杂密码并**不轻易分享**（F-021，L3）。

## 四、设备上限的三层证据

<a id="device-limit-evidence"></a>

### 4.1 官方社区答复：默认 8 台，设置界面无调整入口

- 中文答复：Windows 11/10 系统暂不支持「限制移动热点设备连接数量」的功能，**连接上限为 8 部设备**；建议设置复杂密码并**轻易不要向他人共享密码**（F-021，L3）。
- 英文答复：Windows 10/11 内置的移动热点**没有超出默认值的设备数上限设置项**（F-022，L3）。

**这两条答复互相印证**，且是**官方账号**在官方社区给出的口径。但请注意证据层级：**产品文档从未写过这个数字**（`s2-ms-support-hotspot` 全文不含设备数量）。

### 4.2 注册表调整键：说明 8 是默认值，不是协议硬上限

官方社区的另一条答复给出了调整方法：在

```
HKEY_LOCAL_MACHINE\SYSTEM\CurrentControlSet\Services\icssvc\Settings
```

下新建 **DWORD** 值 `WifiMaxPeers`，改为目标数量，重启后生效（F-023，L3）。

**这条证据的价值**：注册表键的存在本身说明 **8 是一个可配置的默认值**，而不是写死在协议里的硬上限——如果是硬上限，就不会存在这个参数。

### 4.3 本包的审慎表述

<a id="cautious-wording"></a>

> 移动热点的**默认连接上限为 8 台设备**，Windows 设置界面**不提供**调整入口。存在官方社区答复提及的注册表调整项 `icssvc\Settings\WifiMaxPeers`，但其**跨版本、跨驱动的实际效果未获微软官方文档确认**（未闭环项 U-3），因此本包**不建议**将其作为常规操作推荐。

### 4.4 还有第二道天花板

无论用哪种方式建热点，**无线网卡驱动自身还有并发连接上限**（F-037，L5）。这个上限由驱动决定，且不受 ICS 侧的参数影响——换句话说，`WifiMaxPeers` 调大了，也不代表驱动会放行。

**遇到「第 9 台连不上」时的正确解读**：Windows 不给提示，症状通常是第 9 台显示「无法加入」或长时间停在「正在获取 IP 地址」；也可能表现为「昨天能连的设备今天连不上了」——因为它占了别人的名额位。**先在快速设置面板看一眼已连接设备数**（F-029），若显示已满，则问题定位完毕，不必再动注册表。

## 五、驱动约束：SoftAP 与 STA 并发

移动热点要求无线网卡支持 **SoftAP**（自身作为接入点）。当前 Windows 的开启路径是设置界面开关，走的是 Wi-Fi Direct 体系（官方支持文档全文不含 `netsh wlan`、不含 Hosted Network，F-024 ~ F-029）。

**兼容性约束集中在两种场景**：

| 场景 | 约束 | 表现 |
|---|---|---|
| 共享来源 = **Wi-Fi** | 同一适配器同时承担 STA（连上游）与 AP（发热点），需驱动支持并发模式 | 开关打不开、开了又断、上游一断热点跟着断 |
| 共享来源 = **以太网 / 蜂窝** | 无线网卡专职当 AP，无并发压力 | 稳定 |

**排查建议**：遇到「移动热点开关灰色不可用」或「开了立刻断」，**先看无线网卡驱动版本**，再考虑是否换共享来源。官方支持文档本身未列出驱动要求清单，这是**未覆盖的空白**（缺口 G4）。

## 六、Hosted Network 辨析

<a id="hosted-network"></a>

`netsh wlan show drivers` 的输出里有一行 `Hosted network supported`。这行探测的是 **Hosted Network**——Windows 7 时代的承载网络技术，与当前的移动热点**是两套独立机制**。

| 维度 | Hosted Network | 移动热点（Mobile Hotspot） |
|---|---|---|
| 时代 | Windows 7 时代 | Windows 10 起，Windows 11 主力 |
| 技术栈 | 承载网络（Hosted Network） | Wi-Fi Direct / SoftAP |
| 官方开启路径 | `netsh wlan` 命令 | 设置界面 + 快速设置（F-024、F-029） |
| `Hosted network supported: No` 的含义 | 该驱动不支持承载网络 | **与移动热点能否使用不是同一判据** |

**本包的立场**（F-037，L5）：

- 微软官方的移动热点文档**从头到尾没有提到 Hosted Network，也没有提到 `netsh wlan`**（F-024 ~ F-031）——这是「二者不是一回事」的最强间接证据；
- 社区普遍观察到：许多现代无线适配器 `Hosted network supported` 显示为 `No`，而移动热点**照常可用**；
- 但本包**未找到微软官方文档正面声明「`Hosted network supported` 与移动热点可用性无关」**——因此这条为 **L5 社区口径**，登记为未闭环项 U-4。

**操作结论**：

> 判断本机能否开热点，看**移动热点开关是否可用**，以及**无线网卡驱动是否支持 SoftAP**。不要拿 `Hosted network supported` 那一行当判据——这是中文教程里最普遍的一条错误判据。

## 七、网络名称的编码问题

源文建议「网络名称最好采用英文字符，不要用中文，避免部分设备识别乱码」（F-006）。

结合密码的 ASCII 硬约束（F-020），可以给出一条更一般的原则：

> **SSID 与密码都优先使用 ASCII 可打印字符。** 两者都是要跨设备广播/比对的标识串，任何超出 ASCII 的字符都会在某一端遇到编码转换问题。SSID 层面是「部分设备显示乱码」，密码层面则直接是**被拒绝**（F-020 官方原文）。

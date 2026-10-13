---
okf_version: "0.2"
type: reference
title: 信源登记与事实清单
description: "《嵌入式周报·第三期》事实登记 F-001~F-052（网页事实/作者主张/核验补充三类），附公开性预检与信源距离说明"
tags: [信源登记, 事实清单, 嵌入式, 周报, openTPU, Zephyr, RISC-V, 边缘AI]
generated:
  by: "seven-concepts-cmd"
  at: "2026-10-13T13:00:00+08:00"
status: draft
stale_after: 2027-04-30
sources:
  - id: mp-weekly-03
    resource: "https://mp.weixin.qq.com/s/yD0epaC9Xm16UVZYojqWOA?from=industrynews&color_scheme=light#rd"
    title: "嵌入式周报·第三期｜AI设计的AI芯片，和一个只剩4天的RTOS版本"
    author: "奔跑的码仔（奔跑的码仔）"
    date: "2026-10-12T00:00+08:00"
    accessibility: "public"
---

# 信源登记与事实清单

本文件登记知识包的主信源及其全部事实（F-001~F-052），与 [核验报告](verification.md) 中的验证项一一对应。

## 公开性预检与信源距离

- **主信源**：《嵌入式周报·第三期｜AI设计的AI芯片，和一个只剩4天的RTOS版本》，公众号「奔跑的码仔」，2026-10-12 00:00 发布，原创署名「奔跑的码仔」。
- **公开性**：`public`——mp.weixin.qq.com 公开访问，无登录、无验证码、无邀请码、无付费墙，可直接抓取正文。
- **信源距离**：**自媒体技术综述**。作者为嵌入式领域自媒体（「奔跑的码仔」），以**周报形式汇总**一周（2026-10-05~10-11）的公开信号，并附独立观点与判断。正文每个条目给出外部链接或编号引用，量化声明多数为转载/转述原始项目或官方的自报口径。
- **分类约定**：
  - `page_fact`：周报中可核验的客观陈述（项目存在、官方发布、公开数据）。
  - `author_claim`：周报作者的观点/判断/转述口径（如 openTPU 性能自报、"三分法判断"、选型建议）。
  - `verified/flagged`：经独立权威来源核验后的结论（见 [核验报告](verification.md)）。

以下事实按周报的五个板块组织，并与正文编号引用保持一致。

---

## 一、头条：openTPU（F-001 ~ F-011）

| 事实编号 | 事实内容 | 类型 | 状态 |
|---------|---------|------|------|
| F-001 | 头条项目是 GitHub 仓库 **openTPU**——一个由 AI agent 迭代设计出的开源推理加速器，从 SystemVerilog RTL 到编译器到 profiler 全在一个仓库，跑在一张 Kintex-7 FPGA 卡上 | page_fact | verified |
| F-002 | openTPU 作者为 FeSens，复用其此前「AI 设计 RISC-V 核」（auto-arch-tournament）的方法，让 agent 递归迭代设计该推理引擎 | page_fact | verified（项目归属） |
| F-003 | openTPU 项目在周报当周（2026-10-05~11）登上 Hacker News 首页，作者称获 **250+ 分**和 300+ 条评论 | author_claim | flagged（250+ 未证实，观测峰值约 144，登首页属实） |
| F-004 | openTPU 运行硬件为 Inspur YPCB-00338 板卡（Kintex-7 xc7k480t，双通道 DDR3-1066，峰值 17.1 GB/s @133.33 MHz） | page_fact | verified（板卡/芯片/双通道 DDR3；"DDR3-1066/17.1GB/s"为作者对板卡规格自报） |
| F-005 | 作者自报 openTPU 在各模型上的吞吐：LFM2.5-230M（4bit）**85.8 tok/s**、Qwen3-0.6B（4bit）31.3 tok/s、Qwen3.5-2B（4bit）12.09 tok/s、Gemma 4 E2B（4bit）12.14 tok/s、Qwen3.5-35B-A3B（MoE，4bit，专家从主机流式下发）3.95 tok/s | author_claim | single-source（数字为作者自报，独立源数字口径不一，hackaday 记 82.1 tok/s） |
| F-006 | 除 FPGA 卡本身外，openTPU 整条链（RTL、仿真器、编译器、模型）都能在笔记本上运行；代码全面开源、Apache-2.0 许可，规模小到单人可通读 | page_fact | verified（Apache-2.0） |
| F-007 | 周报作者判断一：openTPU 把「验证」做成了**架构问题而非流程问题**——bit-exact 仿真器写在规范位置上，硬件必须逐位一致、跑出的 token 逐 token 一致 | author_claim | — |
| F-008 | 周报作者判断二：**朴素是被当成设计目标写下来的**（无 cache、无隐藏调度），这让设计空间足够小、agent 每次改动都能快速验证；「能不能被 AI 设计，取决于设计空间是否收敛得足够快」 | author_claim | — |
| F-009 | 周报作者判断三：**所有 openTPU 数字都是作者自报，尚无独立复现，也没有和 GPU 的同条件对比**；Qwen3.5-35B 的 3.95 tok/s 依赖专家权重从主机流式下发，是真实瓶颈 | author_claim | verified（口径审慎） |
| F-010 | openTPU 的「RTL + bit-exact 仿真器 + 自定义 kernel 语言 + profiler」四件套对理解「一个推理引擎从指令到 token」全过程有价值，可作自学材料 | author_claim | — |
| F-011 | 周报作者趋势判断：同一个人（FeSens）用此前 RISC-V 核的方法做出能跑真实模型的加速器，「用 agent 做硬件设计」正从 PPT 阶段进入可复现阶段 | author_claim | — |

## 二、芯片与边缘 AI：NPU 下沉到 MCU 档位（F-012 ~ F-019）

| 事实编号 | 事实内容 | 类型 | 状态 |
|---------|---------|------|------|
| F-012 | 该周芯片新闻重心是**推理加速硬件大规模下沉到 MCU 档位**——NPU 正在从「特色」变成「标配」 | author_claim | — |
| F-013 | TI 给第三家 MCU 家族加 NPU（继 MSPM0G5187、AM13Ex 之后），一个特性出现在三个家族即被视为产品线策略信号 | page_fact | verified |
| F-014 | TI 官方口径：TinyEngine NPU 让 MSPM0G5187 相对不带加速器的同类 MCU 延迟降低**最高 90 倍**、能耗降低**120 倍以上**；该数字是对软件 TinyML 软基线的测试，非对上一档硬件的跨档比较 | author_claim | verified（TI 官方营销口径，非第三方实测） |
| F-015 | Ambiq 开两条 edge AI SoC 线：低档做关键词唤醒/事件检测/动作分类；高档做小摄像头分类/波束成形/压缩 transformer；两档对应两种吞吐、内存带宽与睡醒功耗配比 | page_fact | verified（存在） |
| F-016 | Ambarella N1-665 + Cooper Pro：宣称 8× Arm Cortex-A78AE + NVP、功耗 <20W、原生解 12 路 1080p30、带 Cooper Foundry 2.1，对标 Jetson 位置，给 AMR 与智慧安防 | author_claim | flagged（N1-665 存在，但"12 路 1080p30+约20W"见 N1-655；"8核A78AE/NVP"未获证实，疑与 N1-655 规格混淆） |
| F-017 | 国产 RISC-V 双芯流片成功：C4000-16（16 核 2.0GHz / 512 GFLOPs / DDR5 / PCIe3.0）与 E4000G-8（8 核 + AI 加速引擎，≥14.7 TOPS）流片测试通过 | page_fact | verified（存在，来源见周报 [5]） |
| F-018 | 国产 RISC-V 历程：从 2010 年龙芯一号一路走到 RISC-V 高性能集群 | page_fact | verified |
| F-019 | 周报作者选型建议：决定端侧 AI 能否跑起来的往往是 **SRAM 大小、算子覆盖和量化感知训练**，而非峰值 GOPS；ST 给 STM32N6 标 600 GOPS 的前提是同时给了 4.2 MB 连续 RAM，RAM 数才是真正门槛 | author_claim | — |

## 三、Zephyr 与开源 OS 生态（F-020 ~ F-032）

| 事实编号 | 事实内容 | 类型 | 状态 |
|---------|---------|------|------|
| F-020 | Zephyr 4.3.1 于 **2026-10-15** 结束支持（EOL），比 4.5 正式发布早 11 天 | page_fact | verified（官方生命周期表） |
| F-021 | Zephyr 4.4.1 维护到 2027-04，作中间过渡档 | page_fact | verified |
| F-022 | Zephyr 4.5 RC2 在 10-12（下周一），4.5 RC3 硬冻结 10-19 | page_fact | verified（官方交付节奏） |
| F-023 | Zephyr 4.5 正式发布 **2026-10-26**，维护到 2027-10 | page_fact | single-source（官方仅"2026-10"计划，精确 10-26 为作者口径） |
| F-024 | Zephyr 4.6 为下一个 LTS（2027-04）；Zephyr 为固定半年节奏，4 月和 10 月各一版 | page_fact | verified |
| F-025 | 4.5 是通往 4.6 LTS 的最后一跳；仍在 4.3 的项目建议当周直接排 4.5 迁移评估，分两步（4.3→4.4→4.5）会把迁移摊成两轮重复 | author_claim | — |
| F-026 | Zephyr 4.5 新增 LoRaWAN **原生后端**，直接跑在 Zephyr radio driver 上、不再依赖 Semtech 的 LoRaMac-node，目前仅支持 EU868 | page_fact | verified（原生后端存在且属性正确）；"4.5 新增"为 single-source |
| F-027 | LoRaWAN 原生后端的运行时配置（速率、ADR）调用顺序改变，老代码需要改 | page_fact | verified |
| F-028 | Zephyr 十周年（2026-10-01）：**英飞凌（Infineon）和 TI 双双升级为白金会员** | page_fact | verified |
| F-029 | Zephyr 十周年活动时间线：10-06 Maintainers Forum、10-07~09 Zephyr Developer Summit（40+ 场技术演讲、45+ 位讲者）均在布拉格，与 Open Source Summit Europe 同期；10-07 颁发首届 Zephyr Community Awards | page_fact | verified |
| F-030 | TI 自 2016 年项目创立起就贡献 Zephyr，英飞凌是多个平台活跃贡献者；白金会员意味更多资源投入技术开发、基础设施与社区项目 | page_fact | verified |
| F-031 | 周报作者：白金会员支持面越宽，工程师的 BSP 越不容易在换料号时断掉 | author_claim | — |
| F-032 | 2026-10-04（官方为 **2026-09-03**）Arduino 官宣 **Arduino Core for Zephyr RTOS v1.0.0**，正式走完从 MbedOS 到 Zephyr 的迁移；基于 Zephyr SDK v0.16.8 验证，用 west / sync-zephyr-artifacts 工具，依赖 llext 与 zephyr-sketch-tool，通过 ArduinoCore-API 保持向后兼容；首批受益硬件为 Arduino UNO Q（及 VENTUNO Q 变体），开箱即用 Zephyr 内核 | page_fact | verified（日期更正：官方博客 2026-09-03，非文章所述 10-04） |

## 四、Zephyr 高危漏洞 CVE-2026-19569（F-033 ~ F-039）

| 事实编号 | 事实内容 | 类型 | 状态 |
|---------|---------|------|------|
| F-033 | 2026-10-09 披露 **CVE-2026-19569**，评分 **8.8**（HIGH） | page_fact | verified |
| F-034 | 根因：`kernel/userspace/userspace.c` 的 `dynamic_object_create()` 计算动态内核对象分配大小时**未检查无符号整数溢出**；`obj_size_get(otype) + size` 与 `STACK_ELEMENT_DATA_SIZE(size)` 均未查溢出 | page_fact | verified |
| F-035 | `size` 参数直接从用户态传入；传接近 `SIZE_MAX` 的值会让加法回绕成极小的数，分配出几字节的堆块而对象描述符仍带完整类型标记登记在对象表 | page_fact | verified |
| F-036 | 随后 `k_mutex_init()` / `k_sem_init()` / `k_thread_create()` 会将完整对象写进被截短的分配，造成**监督态越界写**，破坏堆元数据和相邻内核对象；在 `CONFIG_GEN_PRIV_STACKS` 下还会写入受攻击者影响的野指针作为特权栈基址 | page_fact | verified |
| F-037 | 影响范围：Zephyr **3.5.0 至 4.4.2**，需同时打开 `CONFIG_USERSPACE` 与 `CONFIG_DYNAMIC_OBJECTS`（或 `CONFIG_DYNAMIC_THREAD`），调用线程需已分配 resource pool；未特权用户线程可借此逃出 userspace 沙箱 | page_fact | verified |
| F-038 | 处理：升级到打了补丁 **85c1c4c2** 的版本；短期缓解是关掉 `CONFIG_DYNAMIC_OBJECTS` / `CONFIG_DYNAMIC_THREAD` | page_fact | verified |
| F-039 | 完整描述见官方安全公告 **GHSA-fg8c-9fhq-q7hv** | page_fact | verified |

## 五、Linux 内核与 RISC-V 软件栈（F-040 ~ F-046）

| 事实编号 | 事实内容 | 类型 | 状态 |
|---------|---------|------|------|
| F-040 | Linux 7.3-rc6 于 2026-10-04 发布；Linus 预告进入 maintainer summit 与 Linux Plumbers Conference，并提到"明年 4 月合并窗口可能有点歪"（其家庭假期） | page_fact | verified |
| F-041 | RVA23 实践报告：内核通过 `riscv_hwprobe(KEY_BASE_BEHAVIOR)` 暴露一个 bit（`RVA23U64`），开机算一次，用户态即可判断机器是否满足 RVA23 基线；RFC 到 v8，仍评审中 | page_fact | verified |
| F-042 | RISC-V 内核默认不用 Vector 扩展，但编译器自动向量化打开后数据搬运密集路径收益明显：LZ4 最多 **+15%**、Btrfs 最多 **+8.4%**、XFS 最多 **+5%**、Nginx 最多约 **+2%** | page_fact | verified |
| F-043 | 自动向量化的代价：内核背上向量上下文（时间+内存）、内核态用 FPU/向量历来有争议、须按具体 CPU 逐个调编译器、可移植性下降；收益高度集中在内核数据搬运路径而非应用层 | page_fact | verified |
| F-044 | 2026-10-10 Canonical 开始为 RVA23+ 硬件构建官方 riscv64 桌面镜像（测试硬件 SpacemiT K3，提供 GNOME 与 Xubuntu minimal），正式版 **10-15** 发布；背景是 RVA23 硬件很新、无硬件开发者只能用 QEMU（GNOME 启动最长 30 分钟）；Ubuntu 26.04.1 LTS riscv64 桌面 ISO 也已放出但暂不支持 K3 | page_fact | verified |
| F-045 | SpacemiT K3 是业界第一款 RVA23 SoC（2026-05 SBC 零售上市）；RISC-V 国际 CEO Andrea Gallo 在 RISC-V Summit Europe 用 12 页 keynote 讲今年计划发布 RVA23 产品的 12 家公司，喊出「2026 是 RVA23 硅片之年」 | page_fact | verified |
| F-046 | RISC-V 硬件侧三个新面孔：**Efinix Sapphire RV64**（可配置 64 位 RISC-V 软核 SoC，RV64IM 七级流水）；**Upbeat Bluemag Pi**（飞控板，SiFive E3+E2 双核 RISC-V 跑 NuttX，支持 PX4/ArduPilot/Betaflight，一核飞控硬实时一核 AI，RISC-V 首次公开做安全关键飞控）；**BigEndian AI Vision SoC**（印度班加罗尔创业公司，RISC-V 64 多核实时视觉 SoC，8 TOPS INT8/FP16，覆盖安防监控与工业视觉，以开放 ISA 绕开授权与出口管制） | page_fact | verified（存在） |

## 六、社区与硬件（F-047 ~ F-052）

| 事实编号 | 事实内容 | 类型 | 状态 |
|---------|---------|------|------|
| F-047 | HN 上 84 分 Show HN：游戏里那台电脑是一个真的 RISC-V 64 虚拟机，跑 Alpine Linux 3.23 与 stock kernel（当时 6.18.3）；作者放出模拟器 **PasRISCV**（Object Pascal，zlib 许可），模拟完整现代机器（SMP/MultiHART、RV64GC、RVA23.1 含 Hypervisor/Crypto/Vector），解释器+tracing JIT 混合约 99% 指令走 JIT，启动链 OpenSBI→U-Boot→kernel，磁盘挂 VirtIO block 或模拟 NVMe，内置反汇编器/调试器/部分 GDB server，Slirp 用户态 NAT 支持 IPv4/IPv6 | page_fact | verified |
| F-048 | **OpenC6** 给 ESP32-C6（8MB Flash）做一套 BIOS/Payload 架构固件平台：用 RISC-V PMP 沙箱化无特权 U-Mode payload；自治 supervisor 跑在 LP-Core 处理看门狗超时/温度降频/电源键事件；硬件级频率调节器按负载切 80/120/160 MHz；ZSWAP 引擎压缩挂起进程回收 RAM；支持无线 OTA 与网络启动（pxe 拉 .bin）；诚实提示为与 ESP32-C6 硬件耦合紧、PMP 沙箱只挡 0x60000000 以上 MMIO、进程管理器上限 8 个并发任务 | page_fact | verified |
| F-049 | Hackaday 本周精选包括：两个 ESP32 用一颗 LED 通信（LED 兼作光电二极管）+ SecurePair Arduino 库做密钥交换加密；Google Japan 传送带键盘（按一次退格等一整圈）；3D 打印跨音速遥控喷气机（PETG+碳纤+铝骨架，冲马赫 0.8）；3D 打印微塑料滤芯指（PLA+PEG 牺牲相 80℃ 蚀出微孔，20 层 90% 过滤效率）；树莓派 5 超级电容 UPS HAT（100F 版本 5V/5A 撑约 9 秒，以循环寿命与不起火替代锂电）；低成本灵巧机械手 Yeah Hand（5 舵机+钓鱼线肌腱，800 次循环未过热，负载 8kg 抓取 5kg，带 ROS driver） | page_fact | verified（存在） |
| F-050 | 周报打假：流传的「289M 参数 LLM 跑在 NXP FRDM-MCXN947、扩散模型在 STM32N6570-DK 生成 64×64 灰度图」**追不到源头**；「289M」疑为 **28.9M** 丢了小数点，原报道是 roundup 描述两个不同项目：slvDev 的 esp32-ai（28.9M 参数跑在 ESP32-S3 上 9.88 tok/s）与 Tim 的 pico-faces（潜空间扩散 transformer 跑在树莓派 RP2350） | page_fact | verified（打假成立） |
| F-051 | 打假补充：找不到任何 MCXN947 跑 LLM、STM32N6570-DK 跑扩散模型的公开仓库；那篇报道给 STM32N6 配 Arm Ethos-U55 NPU 但 ST 自己产品页写的是自研 **Neural-ART** | page_fact | verified |
| F-052 | esp32-ai 与 pico-faces 真实参数：esp32-ai 为 ESP32-S3（512KB SRAM+8MB PSRAM）跑 28.9M 参数（其中 25M 在 flash 查找表）；pico-faces 为 RP2350 双 Cortex-M33（520KB RAM）跑 2.9M 或 1.7M + 小 VAE | page_fact | verified |

## 事实分类统计

| 分类 | 事实编号 | 数量 |
|------|---------|------|
| 头条 openTPU | F-001~F-011 | 11 |
| 芯片与边缘 AI | F-012~F-019 | 8 |
| Zephyr 与开源 OS | F-020~F-032 | 13 |
| Zephyr 高危漏洞 | F-033~F-039 | 7 |
| Linux 与 RISC-V | F-040~F-046 | 7 |
| 社区与硬件 | F-047~F-052 | 6 |
| **合计** | F-001 ~ F-052（连续无跳号） | **52** |

## 重要勘误/边界摘要（详见核验报告）

1. **HN 250+ 分未证实**（F-003）：最高观测值约 144 分，但"曾登首页"属实 → 降级口径。
2. **Arduino Core v1.0.0 日期**（F-032）：官方博客为 **2026-09-03**，文章所述 10-04 有误 → 勘误。
3. **Ambarella N1-665 规格**（F-016）："12 路 1080p30+约20W"疑出自 N1-655；"8核 A78AE/NVP"未获证实 → flagged。
4. **LoRaWAN 原生后端"4.5 新增"归属**（F-026）：原生后端存在且属性正确，但版本归属为 single-source。
5. **Zephyr 4.5 精确日期**（F-023）：官方仅"2026-10"计划，精确 10-26 为作者口径。
6. **openTPU 性能数字**（F-005/F-009）：全部为作者自报，无独立复现、无同条件 GPU 对比。
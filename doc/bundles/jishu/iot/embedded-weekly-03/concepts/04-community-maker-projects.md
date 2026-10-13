---
okf_version: "0.2"
type: concept
title: "社区动手能量：模拟器、微内核与打假"
description: "游戏内真 RISC-V 虚拟机（PasRISCV）、ESP32-C6 BIOS/微内核平台（OpenC6）、Hackaday 精选，以及一条不实数字的完整打假链"
tags: [RISC-V模拟器, PasRISCV, ESP32-C6, OpenC6, Hackaday, 打假, 端侧AI]
generated:
  by: "seven-concepts-cmd"
  at: "2026-10-13T13:20:00+08:00"
status: draft
stale_after: 2027-04-30
sources:
  - id: mp-weekly-03
    resource: "https://mp.weixin.qq.com/s/yD0epaC9Xm16UVZYojqWOA"
    title: "嵌入式周报·第三期"
---

# 社区动手能量：模拟器、微内核与打假

## 一个太空游戏里跑着真的 Linux（F-047）

HN 上 84 分 Show HN：游戏里那台电脑**不是终端特效，是一个真的 RISC-V 64 虚拟机**，跑着 Alpine Linux 3.23 和 stock kernel（当时 6.18.3）。作者放出自己的模拟器 **PasRISCV**（Object Pascal，zlib 许可），规格相当认真：

- 模拟的是**完整的现代机器**，不只是用户态：**SMP/MultiHART、RV64GC、RVA23.1**（含 Hypervisor、Crypto、Vector）
- 解释器 + tracing JIT 混合，约 **99% 的指令走 JIT**，FPU 直通给 guest
- 启动链 **OpenSBI → U-Boot → kernel**，磁盘挂 VirtIO block 或 PCIe 上的模拟 NVMe
- 内置反汇编器、调试器和部分 GDB server，能当 gdb server 用
- Slirp 风格的用户态 NAT，IPv4/IPv6 都支持

> 🧰 **对嵌入式工程师的价值**（作者）：一个能跑 stock kernel 的完整 VM，意味着你可以**在笔记本上做 MIPS/RISC-V 的固件回归测试**，不必每次都等硬件回来。

## ESP32-C6 上跑 BIOS + 微内核（F-048）

**OpenC6** 给 ESP32-C6（8MB Flash）做了一套 **BIOS/Payload 架构**的固件平台：

- 用 RISC-V **PMP** 沙箱化无特权的 U-Mode payload，硬件初始化与用户态执行分离
- 一个**自治 supervisor** 跑在低功耗 LP-Core 核上，处理看门狗超时、温度降频、电源键事件
- **硬件级频率调节器**按负载在 80/120/160 MHz 之间切 HP 核；**ZSWAP 引擎**压缩挂起进程回收 RAM
- 配置页在 `http://192.168.4.1`，支持无线 OTA；`make setup` 一条命令配好 ESP-IDF v6.1 工具链并刷写
- 支持网络启动：起个 HTTP server，BIOS 用 **pxe** 拉 `.bin`

**诚实提示**：它和 ESP32-C6 硬件耦合得紧，不是通用 MCU 即插即用方案；PMP 沙箱目前只挡 `0x60000000` 以上的 MMIO，外设密集设计可能要自己补驱动；进程管理器上限 **8 个并发任务**。

## Hackaday 本周精选（F-049）

| 项目 | 看点 |
|------|------|
| **两个 ESP32 只用一颗 LED 通信** | 靠 LED 本身也是光电二极管这个特性收发；配套 SecurePair Arduino 库做密钥交换+加密，可跑 ESP-NOW/LoRa——"可见光做配对、无线做数据" |
| **Google Japan 传送带键盘** | 源码/STL/构建指南全开，按一次退格等一整圈；关键构建步还标着 TBD |
| **3D 打印跨音速遥控喷气机** | PETG+碳纤杆+铝骨架冲马赫 0.8；PPS-CF 段套碳布扛热；目标破 626 km/h 四轴纪录 |
| **3D 打印微塑料滤芯** | PLA 掺 PEG 做牺牲相、80℃ 热水蚀掉留微孔，20 层过滤效率达 90%（论文数据） |
| **树莓派 5 超级电容 UPS HAT** | 明确只撑几秒~几分钟好让你安全关机别写坏 SD 卡；100F 版本 5V/5A 称约 9 秒——但循环寿命和"不起火"才是替代锂电的理由 |
| **低成本灵巧机械手 Yeah Hand** | 每手 5 舵机+钓鱼线肌腱、PTFE 导绳减摩擦；800 次开合未过热、负载 8kg 抓取 5kg；带 ROS driver |

## 一条需要打假的数字：289M 参数的真相（F-050 ~ F-052）

网上流传：「有 **289M** 参数的 LLM 跑在 NXP FRDM-MCXN947 上，还有扩散模型在 STM32N6570-DK 上生成 64×64 灰度图」。周报团队逐条核了一遍，**这条追不到源头**：

1. **「289M」疑为「28.9M」丢了小数点**（F-050）：原报道源头是一篇 roundup，描述的是两个不同项目——**slvDev 的 esp32-ai**（28.9M 参数跑在 ESP32-S3 上，9.88 tok/s）和 **Tim 的 pico-faces**（潜空间扩散 transformer 跑在树莓派 RP2350 上）。
2. **找不到任何 MCXN947 跑 LLM、STM32N6570-DK 跑扩散模型的公开仓库**（F-051）。
3. **那篇报道还给 STM32N6 配了 Arm Ethos-U55 NPU，但 ST 自己的产品页写的是自研 Neural-ART**（F-051）。

那两个真实项目虽小得多，技术上其实更有意思（F-052）：esp32-ai 为 ESP32-S3（512KB SRAM + 8MB PSRAM）跑 28.9M 参数（其中 25M 在 flash 查找表里）；pico-faces 为 RP2350 双 Cortex-M33（520KB RAM）跑 2.9M 或 1.7M + 小 VAE。

> 🔍 **打假方法论**：① 对"惊人数字"先溯源（find the source）；② 检查是否小数点/单位错位（289M→28.9M）；③ 用公开仓库存在性做证伪（找不到 MCXN947 仓库则声明不成立）；④ 交叉核对产品页原文（Ethos-U55 vs Neural-ART）。这是对付 AI/自媒体时代漂移数字的通用流程。

---

## 工程启示

1. **完整 VM 是固件回归利器**：能跑 stock kernel 的 PasRISCV 让你在笔记本上回归 RISC-V 固件，不必等硬件（F-047）。
2. **BIOS/Payload 解耦硬件初始化与用户态**：OpenC6 用 PMP 沙箱 + 独立 supervisor，是可借鉴的 MCU 固件架构（F-048）。
3. **对 i 数据先打假再传播**：29 => 289 这种小数点漂移极常见；用存在性证伪 + 产品页原文核对拦截（F-050~F-052）。

```{toctree}
:hidden:
:maxdepth: 1

../references/index
```
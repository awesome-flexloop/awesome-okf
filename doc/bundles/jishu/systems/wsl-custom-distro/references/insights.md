---
type: Insights
title: "WSL 自定义发行版：五条洞察、四段式分发契约与文档覆盖矩阵"
description: "I/E 阶段产物：从 81 条官方事实中提炼五条四元组洞察（四件套契约、OOBE 单点否决、配置时点分层、三档分发控制权、去宿主耦合），并沉淀可跨领域迁移的『四段式分发契约』模式"
tags: [wsl, custom-distro, insight, pattern, distribution-contract, oobe]
generated: { by: "reference_agent/trae-solo", at: "2026-11-06T00:00:00Z" }
verified: { by: "process:seven-concepts-v", at: "2026-11-06T00:00:00Z" }
status: draft
stale_after: "2027-05-31"
sources:
  - id: facts
    resource: /references/facts.md
    title: WSL 自定义发行版构建事实清单（81 条）
  - id: ms-zh
    resource: https://learn.microsoft.com/zh-cn/windows/wsl/build-custom-distro
    title: 为 WSL 生成自定义 Linux 分发版（中文）
---

# 洞察、模式与覆盖矩阵

> 本文件建立在 [81 条编号事实](facts.md)之上。洞察中的每条判断均标注事实编号；「反常识」是对默认假设的挑战，「行动」是可执行建议。工程推断与官方口径的分界见 [验证报告](verification.md)。

## 一、五条核心洞察（四元组）

### I-1：交付物不是「一个镜像」，而是「载荷 + 首次启动契约 + 安装入口 + 分发元数据」四件套
- **陈述**：官方定义只把 WSL 发行版拆成「rootfs tar + 清单条目」两部分（F-003），但可安装、可双击、可上架的最小完整交付实际由四层构成：①tar 载荷（F-007~F-010）；②rootfs 内的首次启动契约 `/etc/wsl-distribution.conf`（F-015~F-026）；③安装入口——`.wsl` 扩展名加 `oobe.defaultName`（F-043~F-045）；④分发元数据——`ModernDistributions` 清单条目（F-050~F-057）。
- **证据**：F-003、F-007、F-015、F-019、F-043、F-045、F-052。
- **反常识**：直觉认为 `.wsl` 是类似 `.appx` 的特殊封装格式；官方口径是「tar 文件重命名」（F-043）。真正的复杂度和失败点不在格式转换，而在四层契约是否齐全——缺 `defaultName` 时双击安装失效（F-045），缺清单时 `wsl --install <distro>` 不可达（F-048）。
- **行动**：构建流水线按四段分别验收：`tar -tzf` 查载荷 → 解析两份 conf 查契约 → 检查扩展名与 `defaultName` → 校验清单 JSON 与 SHA256；任一段缺失不得进入发布。

### I-2：OOBE 是「单点否决」的安装期钩子，脚本失败等于发行版不可用
- **陈述**：`oobe.command` 在用户首次打开交互式 shell 时运行，返回非零即判定失败，用户无法打开 shell（F-020）。示例脚本用 `getent passwd` 做幂等短路（F-030），并用 `adduser → usermod → deluser` 组成创建与回滚链（F-031）。
- **证据**：F-020、F-021、F-029、F-030、F-031。
- **反常识**：直觉把首次启动当成「打开一个 shell」，实际它是维护者注入的**唯一一次用户创建窗口**；这个窗口没有重试 UI，失败表现为「装好了但进不去」。同时 `oobe.defaultUid`（F-021）与脚本内 `uid` 必须同锚到 1000（F-074），否则「先有 UID、后有人」的假设不成立。
- **行动**：OOBE 脚本按「幂等检查 → 创建 → 加组 → 失败回滚 → 明确错误输出」五段写；本地安装测试至少覆盖「已存在 UID」「用户名非法」「中途失败」三条路径。

### I-3：两份配置文件的差异不是位置，而是「作用时点 + 责任主体」
- **陈述**：`/etc/wsl-distribution.conf` 由发行版维护者创建，控制首次启动时的配置（F-016），可交互建用户、显示许可（F-018）；`/etc/wsl.conf` 承载用户相关的全局系统设置并控制启动方式（F-017），其中 `[boot] systemd` 由发行版作者设定默认值（F-039、F-040）。
- **证据**：F-015~F-018、F-038~F-042、F-073。
- **反常识**：两个文件都在 rootfs 里、都在 `/etc` 下，容易被当成同类配置一起维护；实际一个是**安装期契约**（只跑一次），一个是**每次启动契约**（可被用户/发行版共同影响）。把用户偏好写进发行版配置会把一次性决策固化成所有用户的默认。
- **行动**：维护者只把「发行版身份、OOBE、快捷方式、终端模板、systemd 默认开关」放进 `wsl-distribution.conf`；其余运行期设置进 `wsl.conf`；两者都以 `root:root 0644` 交付（F-073）。

### I-4：分发渠道有三档，控制权与门槛依次递增
- **陈述**：①直传 `.wsl`，用户用 `wsl --install --from-file` 或双击安装（F-049）；②企业/团队用注册表 `DistributionListUrl` 覆盖或 `DistributionListUrlAppend` 追加清单（F-061~F-064），WSL 2.4.4 起支持 `file://` 本地测试（F-065）；③公开上架需满足分发邮件列表成员资格（F-058、F-059）并向 microsoft/WSL 提交 PR（F-060）。
- **证据**：F-049、F-061~F-065、F-058~F-060。
- **反常识**：`wsl --list --online` 的列表不是编译进 WSL 的固定集合，而是**可被注册表覆盖的清单 URL**（F-061~F-063）。这意味着企业内分发不必等官方收录，也不必改 WSL 二进制；反之，公开上架的门槛不在技术，而在成员资格与安全标准（F-058、F-059）。
- **行动**：按受众选档——内部测试走 `file://` + `DistributionListUrl`；企业内部走 HTTPS 清单 + `DistributionListUrlAppend`；面向公众先过成员资格再提 PR。每档都保留「删除注册表值恢复官方清单」的回退路径（F-072）。

### I-5：质量底线是「去掉宿主耦合」，而不是「把现有系统打包」
- **陈述**：官方建议明确要求排除 `/etc/resolv.conf`（F-076）、内核与 initramfs（F-079），`/etc/shadow` 不保留密码哈希（F-078），`/etc/passwd` 保留 UID 0 的 root（F-077）；启用 systemd 时须禁用或屏蔽 9 个单元（F-080、F-081），且两份配置归 `root:root 0644`（F-073）。
- **证据**：F-073~F-081。
- **反常识**：把一台已运行系统的根目录直接 tar 看似最省事，但会把宿主网络配置、内核、账号口令等**环境身份**一起带入；WSL 需要的是可移植的 rootfs，而不是宿主快照。官方清单本质是一张「去宿主化」黑名单。
- **行动**：打包前跑「去宿主化检查」：`resolv.conf` 不存在、无 `vmlinuz`/`initrd`、shadow 无哈希、passwd 有 root、两份 conf 权限正确、systemd 单元已 mask；检查结果作为发布门禁证据留档。

## 二、E 阶段：可迁移模式「四段式分发契约」

### 模式卡

| 项 | 内容 |
|---|---|
| 模式名称 | 四段式分发契约（Four-Segment Distribution Contract） |
| 成熟度 | L1（单案例来源，已做三类跨域对照，待第二个真实案例验证） |
| 适用场景 | 把「一个可运行环境」交付成「可被平台安装的发行单元」：WSL 发行版、容器基础镜像、IDE 扩展包、语言运行时安装包 |
| 不适用场景 | 仅在本机导入一次性环境（用 `wsl --import` 即可，不必做发行版）；平台已托管全部安装语义的 SaaS 插件 |

**核心五步**

1. **冻结载荷**：确定 rootfs 内容边界，排除宿主身份（内核、initramfs、`resolv.conf`、密码哈希）。
2. **写首次启动契约**：把「装完第一次要做什么」写成幂等、可回滚、失败可见的钩子（WSL 的 `oobe.command`）。
3. **写运行期契约**：把「每次启动的默认行为」与「安装期一次性行为」分文件、分责任人。
4. **定安装入口**：选择平台识别的扩展名/包格式，并确保入口所需的最小元数据齐全（WSL 的 `oobe.defaultName`）。
5. **挂分发元数据**：为每个平台/架构提供可校验的下载地址与摘要，并保留本地覆盖与回退通道。

**四条反模式（均来自本案例的源页面约束）**

| # | 反模式 | 后果 | 正确做法 |
|---|---|---|---|
| A-1 | 把 `.wsl` 当成需要专用工具生成的镜像格式 | 引入不必要的打包工具链，忽略「tar 重命名」这一事实（F-043） | 用标准 tar + gzip，改名即入口 |
| A-2 | 把 OOBE 写成「尽力而为」的脚本 | 命令非零即拒绝 shell（F-020），发行版装好却进不去 | 幂等短路 + 失败回滚 + 明确错误输出 |
| A-3 | 把用户偏好写进发行版配置 | 一次性决策固化为所有用户默认（F-016 vs F-017） | 安装期契约与运行期契约分文件 |
| A-4 | 直接打包运行中的宿主系统 | 带入内核、网络配置、口令哈希（F-076、F-078、F-079） | 先做去宿主化检查再打包 |

**检验标准（做完怎么知道做对了）**

- [ ] `tar -tzf` 能列出 rootfs 顶层，且不含内核/initramfs/`resolv.conf`；
- [ ] 两份 conf 存在、`root:root 0644`、字段可解析；
- [ ] 本地 `wsl --install --from-file` 能完成安装并进入 shell；
- [ ] `wsl --list --online` 在覆盖清单后能看到测试条目（F-070）；
- [ ] 删除注册表值后恢复官方清单（F-072）。

**跨域迁移示例**

- **容器基础镜像**：载荷 = rootfs 层；首次启动契约 = entrypoint 初始化；运行期契约 = 环境变量与配置挂载；分发元数据 = 镜像 tag + digest。反模式 A-4 对应「不要把运行中的容器 commit 成基础镜像」。
- **IDE 扩展包**：载荷 = 扩展代码；首次启动契约 = 激活时的依赖安装；运行期契约 = 用户 settings；分发元数据 = marketplace 的版本与校验和。
- **Python 运行时安装包**：载荷 = 解释器与标准库；首次启动契约 = 安装后编译字节码；运行期契约 = `pyvenv.cfg`；分发元数据 = wheel 的 `RECORD` 与哈希。

## 三、文档覆盖矩阵

| 文档 | 覆盖事实 | 主题 |
|---|---|---|
| [00-overview](../concepts/00-overview.md) | F-001~F-006 | 全景、术语、路径选择 |
| [01-rootfs-tar](../concepts/01-rootfs-tar.md) | F-007~F-014、F-076、F-079 | rootfs 准备与打包 |
| [02-wsl-distribution-conf](../concepts/02-wsl-distribution-conf.md) | F-015~F-027、F-073~F-075 | 发行版配置文件字段 |
| [03-oobe](../concepts/03-oobe.md) | F-020、F-021、F-028~F-032、F-074 | OOBE 用户创建 |
| [04-wsl-conf-systemd](../concepts/04-wsl-conf-systemd.md) | F-038~F-042、F-080、F-081 | `/etc/wsl.conf` 与 systemd |
| [05-terminal-profile](../concepts/05-terminal-profile.md) | F-033~F-037 | Windows Terminal 配置生成 |
| [06-wsl-file-install](../concepts/06-wsl-file-install.md) | F-043~F-049 | `.wsl` 入口与安装方式 |
| [07-manifest-local-test](../concepts/07-manifest-local-test.md) | F-050~F-057、F-061~F-072 | 清单结构与本地测试 |
| [08-enterprise-and-publishing](../concepts/08-enterprise-and-publishing.md) | F-058~F-065 | 三档分发与公开上架 |
| [09-recommendations-checklist](../concepts/09-recommendations-checklist.md) | F-073~F-081 | 建议清单与发布门禁 |

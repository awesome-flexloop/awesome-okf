---
type: Facts
title: "WSL 自定义发行版构建事实清单（81 条）"
description: "基于 Microsoft Learn 中英文官方页面的 R 阶段事实采集：版本门槛、rootfs tar、两份配置文件、OOBE、终端配置、.wsl 安装、分发清单、企业注册表覆盖与发布建议"
tags: [wsl, custom-distro, rootfs, tar, oobe, systemd, manifest, windows-terminal]
generated: { by: "reference_agent/trae-solo", at: "2026-11-06T00:00:00Z" }
status: draft
stale_after: "2027-05-31"
sources:
  - id: ms-zh
    resource: https://learn.microsoft.com/zh-cn/windows/wsl/build-custom-distro
    title: 为 WSL 生成自定义 Linux 分发版（中文）
    last_modified: "2025-10-04"
  - id: ms-en
    resource: https://learn.microsoft.com/en-us/windows/wsl/build-custom-distro
    title: Build a Custom Linux Distribution for WSL（英文）
---

# WSL 自定义发行版构建事实清单

> **R 阶段口径**：本文件只记录官方页面可核对的客观陈述，不写因果推断与工程建议；建议与推断集中在 [洞察与模式](insights.md)，核验过程见 [验证报告](verification.md)。
> **双源对照**：每条事实同时取自中文页（S1）与英文页（S2）；两页表述不一致处单列为「疑点」，不擅自选定一方。

## 一、文档定位与版本门槛

### F-001 — 官方页面标题与地址
- 来源：S1 页面标题「为 WSL 生成自定义 Linux 分发版」；S2 页面标题 "Build a Custom Linux Distribution for WSL"
- 细节：中文页 `https://learn.microsoft.com/zh-cn/windows/wsl/build-custom-distro`；英文页 `https://learn.microsoft.com/en-us/windows/wsl/build-custom-distro`

### F-002 — 指南目标是创建并分发 `.wsl` 文件
- 来源：S1/S2 开篇段
- 细节：S1「本指南将演练创建和分发 WSL 分发（文件 `.wsl` ）的步骤」；S2 "This guide will walk through the steps to create and distribute a WSL distribution, which is a `.wsl` file."

### F-003 — WSL 分发由两个部分组成
- 来源：S1/S2 开篇列表
- 细节：①根文件系统（以 tar 文件形式分发）；②清单条目（包含分发元数据）

### F-004 — 指南仅适用于 WSL 2.4.4 及更高版本
- 来源：S1/S2 开篇段
- 细节：S1「本指南仅适用于 WSL 版本 2.4.4 及更高版本」，链接指向 `https://github.com/microsoft/WSL/releases`

### F-005 — 旧的 appx 打包说明位于另一个仓库
- 来源：S1/S2 的 Note 段
- 细节：旧方式说明见 `https://github.com/microsoft/WSL-DistroLauncher`

### F-006 — 中文页脚注最后更新时间为 2025/10/04
- 来源：S1 页面末尾 "Last updated on 2025/10/04"
- 细节：该日期为页面级元数据，不代表其中引用的 WSL 版本或终端文档同步更新

## 二、根文件系统 tar 文件

### F-007 — WSL 分发由带 `.wsl` 扩展名的 tar 文件定义
- 来源：S1「什么是 WSL 根文件系统 tar 文件？」；S2 "What are WSL root filesystem tar files?"
- 细节：S1「WSL 分发版由具有 Windows 文件扩展名的 `.wsl` tar 文件定义」；S2 "WSL distributions are defined by a tar file with a `.wsl` file extension on Windows."

### F-008 — TAR 是 Tape Archive 的缩写
- 来源：S1/S2 同节
- 细节：TAR 是一种存档文件格式，用于把多个文件存入单个文件，便于分发或备份

### F-009 — TAR 文件包含 Linux 发行版根文件系统与 WSL 配置文件
- 来源：S1/S2 同节
- 细节：S1「TAR 文件包含 Linux 分发版（所有分发文件）以及 WSL 配置文件的根文件系统」

### F-010 — WSL 配置文件告知 Windows 如何安装和启动发行版
- 来源：S1/S2 同节
- 细节：S1「WSL 配置文件告知 WIndows 操作系统如何安装和启动分发版」

### F-011 — 推荐的 tar 创建命令
- 来源：S1「创建 tar 文件」；S2 "Create the tar file"
- 细节：`cd /path/to/rootfs` 后执行 `tar --numeric-owner --absolute-names -c * | gzip --best > ../install.tar.gz`

### F-012 — tar 的根应为文件系统根，而不是包含根文件系统的目录
- 来源：S1/S2 同节
- 细节：S1「tar 的根目录应该是文件系统的根（而不是包含根文件系统的目录）」；S2 "The root of the tar should be the root of the filesystem (not a directory containing the root filesystem)."

### F-013 — 推荐压缩格式为 gzip
- 来源：S1/S2 同节
- 细节：S1「建议的压缩格式为 gzip。其他压缩格式可能会破坏与旧版 WSL 版本的兼容性」；S2 "Other compression formats run the risk of breaking compatibility with older WSL versions."

### F-014 — 现有 Linux 发行版的 tar 获取方式：参考导入任意发行版文档
- 来源：S1/S2 同节
- 细节：S1 指向「导入要用于 WSL 的任何 Linux 分发版」页面，其中含导出 Docker 容器的指导；目标页为 `https://learn.microsoft.com/zh-cn/windows/wsl/use-custom-distro`

## 三、两份 WSL 配置文件与 OOBE

### F-015 — 发行版应包含两份配置文件
- 来源：S1「创建 WSL 配置文件」；S2 "Create WSL configuration files"
- 细节：`/etc/wsl-distribution.conf` 与 `/etc/wsl.conf`

### F-016 — `/etc/wsl-distribution.conf` 由发行版维护者创建
- 来源：S1/S2 同节
- 细节：S1「由分发维护者创建的文件，负责控制首次使用 WSL 启动时应如何配置 Linux 分发版」；S2 "A file created by the distribution maintainer responsible for controlling how the Linux distribution should be configured when first launched with WSL."

### F-017 — `/etc/wsl.conf` 承载用户相关的全局系统设置
- 来源：S1/S2 同节
- 细节：S1「包含特定于用户的全局系统设置的文件，并控制分发的启动方式」；S2 "A file containing global system settings that are specific to the user and control how the distribution is launched."

### F-018 — 分发配置文件可用于交互式创建用户账户、显示许可协议
- 来源：S1/S2「添加 WSL 分发配置文件」
- 细节：S1「此文件可用于以交互方式创建用户帐户、显示许可协议等」

### F-019 — 示例配置含三个节与七个键
- 来源：S1/S2 示例 `/etc/wsl-distribution.conf`
- 细节：`[oobe]` 下 `command`、`defaultUid`、`defaultName`；`[shortcut]` 下 `enabled`、`icon`；`[windowsterminal]` 下 `enabled`、`ProfileTemplate`

### F-020 — `oobe.command`：首次打开交互式 shell 时运行
- 来源：S1/S2 配置选项表
- 细节：类型字符串，默认 None；OOBE 代表 out of box experience；命令返回非零即视为失败，用户将无法打开 shell

### F-021 — `oobe.defaultUid`：发行版启动时的默认 UID
- 来源：S1/S2 配置选项表
- 细节：类型整数，默认 None；当 `oobe.command` 脚本创建新用户时该键有用

### F-022 — `oobe.defaultName`：发行版注册的默认名称
- 来源：S1/S2 配置选项表
- 细节：类型字符串，默认 None；可用 `wsl.exe --install <distro> --name <name>` 命令替换该默认名称

### F-023 — `shortcut.icon`：开始菜单快捷方式图标
- 来源：S1/S2 配置选项表
- 细节：类型字符串，默认 WSL 默认图标；必须为 `.ico` 格式，最大大小 10MB

### F-024 — `shortcut.enabled`：是否创建开始菜单快捷方式
- 来源：S1/S2 配置选项表
- 细节：类型布尔，默认 true

### F-025 — `windowsterminal.profileTemplate`：终端配置文件 JSON 模板
- 来源：S1/S2 配置选项表
- 细节：类型字符串，默认 None；用于为该发行版生成 Windows Terminal 配置文件

### F-026 — `windowsterminal.enabled`：是否创建终端配置文件
- 来源：S1/S2 配置选项表
- 细节：类型布尔，默认 true；未设置 `profileTemplate` 时将生成默认配置文件

### F-027 — 配置选项表中 `windowsterminal.profileTemplate` 出现两次且默认值不同
- 来源：S1/S2 配置选项表原文
- 细节：第一次默认值为 None，第二次默认值为 "Path to a terminal template file"（S1 译为「终端模板文件的路径」）；两行的 Notes 文本相同

### F-028 — OOBE 全称为 out of box experience
- 来源：S1/S2 配置选项表与示例脚本段
- 细节：S1 译作「现装体验」，S2 原文 "OOBE stands for out of box experience"

### F-029 — 示例 OOBE 脚本假定 `defaultUid` 为 1000
- 来源：S1/S2「示例 bash 脚本」
- 细节：脚本定义 `DEFAULT_GROUPS='adm,cdrom,sudo,dip,plugdev'` 与 `DEFAULT_UID='1000'`

### F-030 — 示例脚本以 `getent passwd` 检查默认 UID 是否已存在
- 来源：S1/S2 示例脚本
- 细节：若 `getent passwd "$DEFAULT_UID"` 命中，则输出「User account already exists, skipping creation」并 `exit 0`

### F-031 — 示例脚本的用户创建与回滚流程
- 来源：S1/S2 示例脚本
- 细节：循环 `read -p 'Enter new UNIX username: '` 读取用户名；`adduser --uid "$DEFAULT_UID" --quiet --gecos '' "$username"` 成功后执行 `usermod "$username" -aG "$DEFAULT_GROUPS"`；`usermod` 失败则执行 `deluser "$username"` 后继续循环

### F-032 — 中英文页面的示例脚本代码块均存在换行丢失
- 来源：S1/S2 示例脚本呈现
- 细节：抓取到的代码块中 `DEFAULT_UID='1000'` 与后续 `echo` 语句在同一行；`fi while true; do` 合并；`fi done` 合并。两语言页面表现一致，属源页面渲染问题

## 四、Windows Terminal 配置文件

### F-033 — 安装发行版时 WSL 自动生成 Windows Terminal 配置文件
- 来源：S1「生成 Windows 终端配置文件」；S2 "Generate a Windows Terminal profile"
- 细节：S1「安装分发版时，WSL 自动生成Windows 终端配置文件」

### F-034 — 维护者可通过 `windowsterminal.profileTemplate` 自定义生成结果
- 来源：S1/S2 同节
- 细节：模板路径写入 `/etc/wsl-distribution.conf` 的 `windowsterminal.profileTemplate`

### F-035 — 模板 JSON 遵循终端配置文件 JSON 格式
- 来源：S1/S2 同节
- 细节：链接指向 `https://learn.microsoft.com/zh-cn/windows/terminal/json-fragment-extensions#structure-of-the-json-files`

### F-036 — 示例模板设置抗锯齿、字重与配色方案
- 来源：S1/S2 示例 JSON
- 细节：`profiles[0]` 含 `"antialiasingMode": "aliased"`、`"fontWeight": "bold"`、`"colorScheme": "Postmodern Tango Light"`；`schemes[0]` 定义同名方案并列出 black/red/green/yellow/blue/purple/cyan/white 及对应 bright 共 16 个颜色键

### F-037 — 模板无需指定配置文件 `name` 与 `commandLine`
- 来源：S1/S2 示例 JSON 之后说明
- 细节：S1「此文件不需要指定配置文件 `name`，也 `commandLine`不需要指定配置文件。生成终端配置文件时，WSL 会自动添加这些配置文件」

## 五、`/etc/wsl.conf` 与 systemd

### F-038 — 建议在 `/etc/wsl.conf` 中按发行版配置 systemd 设置
- 来源：S1「为每个分布区添加本地设置的 WSL 配置」；S2 "Add a WSL configuration for local settings on a per-distribution basis"
- 细节：S1「我们建议你配置系统设置，包括默认是否以按分布方式在本地设置中`/etc/wsl.conf`启动系统设置」

### F-039 — 示例配置为 `[boot]` 节下的 `systemd=true|false`
- 来源：S1/S2 示例 `/etc/wsl.conf`
- 细节：代码块正文为 `[boot]` 与 `systemd=true|false`

### F-040 — 发行版作者决定 systemd 是否默认启用
- 来源：S1/S2 同节
- 细节：S1「分发作者通过将值设置为 `boot.systemd` `true`（enabled）或 `false`（未启用）来确定系统是默认启用的」

### F-041 — 若默认启用 systemd，须参考 Systemd 建议
- 来源：S1/S2 同节
- 细节：链接指向本文「WSL 自定义 Linux 分发建议」的 Systemd 小节

### F-042 — `/etc/wsl.conf` 的全部受支持设置见 WSL 高级设置文档
- 来源：S1/S2 同节
- 细节：链接指向 `https://learn.microsoft.com/zh-cn/windows/wsl/wsl-config`

## 六、`.wsl` 扩展名与安装入口

### F-043 — 将 `.tar` 重命名为 `.wsl` 即标记为 WSL 分发
- 来源：S1「创建 .wsl 文件扩展名」；S2 "Create a .wsl file extension"
- 细节：S1「通过重命名从 `.tar` 文件扩展名更改为 `.wsl` 文件扩展名。重命名此文件扩展名会将它标记为 WSL 分发版」

### F-044 — 重命名后在文件资源管理器中双击可安装
- 来源：S1/S2 同节
- 细节：S1「文件将在文件资源管理器中打开（双击）时正确安装在 Windows 上」

### F-045 — 双击安装要求配置中存在 `oobe.defaultName`
- 来源：S1/S2 同节
- 细节：S1「要使此双击操作能够正常工作，`oobe.defaultName`文件中需要一个`/etc/wsl-distribution.conf`条目」

### F-046 — 用户可通过 `wsl --list --online` 查看可用发行版
- 来源：S1「分发 WSL 分发」；S2 "Distribute your WSL distribution"
- 细节：S1「WSL 用户可以通过运行 `wsl --list --online` 查看可用的发行版」

### F-047 — 可直接用 `wsl --install <distroName>` 安装
- 来源：S1/S2 同节
- 细节：S1「可以直接使用 `wsl --install <distroName>` 安装它们」

### F-048 — 该过程由分发清单文件控制
- 来源：S1/S2 同节
- 细节：S1「此过程由分发清单文件控制。可以将此清单文件添加到客户 Linux 分发版，以便将其包含在命令选项中 `wsl --install`」

### F-049 — 自定义 `.wsl` 文件可任意分发，用户可用 `--from-file` 安装或双击打开
- 来源：S1/S2 同节
- 细节：S1「可以按照您的意愿分发。下载后，用户可以使用命令行 `wsl --install --from-file <fileLocation>` 直接安装它」

## 七、分发清单结构

### F-050 — 分发清单位于 microsoft/WSL 仓库
- 来源：S1「分发清单详细信息」；S2 "Distribution manifest details"
- 细节：`https://github.com/microsoft/WSL/blob/master/distributions/DistributionInfo.json`

### F-051 — 正文称 `ModernDistribution`，JSON 键为 `ModernDistributions`
- 来源：S1/S2 同节
- 细节：S1 正文「下面列出了 `ModernDistribution`基于 tar 的 Linux 分发版」；紧随其后的 JSON 代码块根键为 `"ModernDistributions"`

### F-052 — 清单条目字段集
- 来源：S1/S2 清单 JSON 示例
- 细节：`Name`、`FriendlyName`、`Default`（true 或 false）、`Amd64Url`（含 `Url` 与 `Sha256`）、`Arm64Url`（含 `Url` 与 `Sha256`）

### F-053 — 每个 flavor 条目包含一个可安装发行版列表
- 来源：S1/S2 同节
- 细节：S1「每个 `flavor` 条目都包含一个可安装分发版的列表」

### F-054 — 可通过 flavor 名（安装默认条目）或版本名安装
- 来源：S1/S2 同节
- 细节：S1「可以通过风格名称（即安装默认条目）或版本名称来安装分发版」

### F-055 — 示例清单中 `my-distro-v3` 为默认项，`my-distro-v2` 为非默认项
- 来源：S1/S2 示例清单
- 细节：`"Name": "my-distro-v3"` 配 `"Default": true`；`"Name": "my-distro-v2"` 配 `"Default": false`

### F-056 — 三条示例安装命令分别对应 flavor、v3、v2
- 来源：S1/S2 示例命令
- 细节：`wsl --install my-distro`（安装默认的 v3）、`wsl --install my-distro-v3`、`wsl --install my-distro-v2`

### F-057 — 清单为每个条目同时提供 AMD64 与 ARM64 两个下载对象
- 来源：S1/S2 清单 JSON 示例
- 细节：两个对象均含 `Url` 与 `Sha256`

## 八、公开上架 `wsl --install`

### F-058 — 进入 `wsl --list --online` 需满足分发邮件列表的成员资格条件
- 来源：S1「将您的分发添加到 `wsl --install` 以供所有 WSL 用户使用」；S2 "Adding your distribution to `wsl --install` for all WSL users"
- 细节：条件链接为 `https://oss-security.openwall.org/wiki/mailing-lists/distros#membership-criteria`

### F-059 — 成员资格条件的目的是确保列出的发行版遵循必要安全标准
- 来源：S1/S2 同节
- 细节：S1「这可确保所有列出的分发版都遵循必要的安全标准」

### F-060 — 上架需向 microsoft/WSL 提交更新 DistributionInfo.json 的 PR
- 来源：S1/S2 同节
- 细节：S1「请在 WSL GitHub 存储库上提交拉取请求……以使用分发的详细信息更新 DistributionInfo.json 文件。WSL 团队将审查此拉取请求」

## 九、企业分发与本地清单覆盖

### F-061 — 注册表覆盖位置为 HKLM 下的 Lxss 键
- 来源：S1「将您的分发添加到 `wsl --install` 用于您的企业或业务团队」；S2 对应小节
- 细节：`HKEY_LOCAL_MACHINE\SOFTWARE\Microsoft\Windows\CurrentVersion\Lxss`

### F-062 — `DistributionListUrl` 覆盖分发清单 URL
- 来源：S1/S2 同节
- 细节：S1「重写分发清单 URL」

### F-063 — `DistributionListUrlAppend` 向可安装列表追加清单中的发行版
- 来源：S1/S2 同节
- 细节：S1「将清单 URL 中的分发版添加到可安装分发版列表」

### F-064 — 两个注册表值均为 REG_SZ 字符串
- 来源：S1/S2 同节
- 细节：S1「这两个注册表值都是字符串（REG_SZ），应采用 URL 格式」

### F-065 — 从 WSL 2.4.4 起支持 `file://` 协议
- 来源：S1/S2 同节
- 细节：S1「从 WSL 版本 2.4.4 开始，`file://` 支持协议，以便更轻松地进行本地测试。预期格式为：`file:///C:/path/to/file`」

### F-066 — 本地测试脚本要求管理员权限
- 来源：S1/S2「在本地测试分发」
- 细节：脚本首行 `#Requires -RunAsAdministrator`

### F-067 — 脚本参数
- 来源：S1/S2 示例 `override-manifest.ps1`
- 细节：`TarPath` 为必填字符串；`Flavor` 默认 `test-distro`；`Version` 默认 `test-distro-v1`；`FriendlyName` 默认 `Test distribution version 1`

### F-068 — 脚本计算 SHA256 并写入本地 manifest.json，再设置注册表值
- 来源：S1/S2 示例脚本
- 细节：`Get-Filehash $TarPath -Algorithm SHA256`；`ConvertTo-Json -Depth 5`；`Out-File -encoding ascii`；`Set-ItemProperty -Path "HKLM:SOFTWARE\Microsoft\Windows\CurrentVersion\Lxss" -Name DistributionListUrl -Value "file://$manifestFile" -Type String -Force`

### F-069 — 运行方式为带 `-TarPath` 参数执行脚本
- 来源：S1/S2 同节
- 细节：`.\override-manifest.ps1 -TarPath /path/to/tar`

### F-070 — 覆盖后 `wsl --list --online` 会显示测试条目
- 来源：S1/S2 同节
- 细节：示例输出表头为 `NAME FRIENDLY NAME`，条目为 `test-distro-v1  Test distribution version 1`

### F-071 — 随后可执行 `wsl.exe --install test-distro-v1`
- 来源：S1/S2 同节
- 细节：S1「然后，可以运行 `wsl.exe --install test-distro-v1` 以尝试安装新分发版」

### F-072 — 删除 `DistributionListUrl` 注册表值即可恢复官方清单
- 来源：S1/S2 同节
- 细节：路径为 `HKEY_LOCAL_MACHINE\SOFTWARE\Microsoft\Windows\CurrentVersion\Lxss\DistributionListUrl`

## 十、官方建议（配置与 systemd）

### F-073 — 两份配置文件都应归 root:root 所有，权限 0644
- 来源：S1「配置文件建议」；S2 "Configuration file recommendations"
- 细节：涉及 `/etc/wsl.conf` 与 `/etc/wsl-distribution.conf`

### F-074 — 若由 `oobe.command` 创建新用户，`uid` 与 `oobe.defaultUid` 都应设为 1000
- 来源：S1/S2 同节
- 细节：S1「用于创建新用户的`oobe.command`设置时，`uid`和`oobe.defaultUid`应同时设置为`1000`」

### F-075 — 应同时设置 `oobe.defaultName` 与 `shortcut.icon`
- 来源：S1/S2 同节
- 细节：两者均位于 `/etc/wsl-distribution.conf`

### F-076 — 不要在根文件系统中包含 `/etc/resolv.conf`
- 来源：S1/S2 同节
- 细节：S1「不要在根文件系统中包含该文件 `/etc/resolv.conf`」

### F-077 — `/etc/passwd` 中应包含 root 用户，其 UID 为 0
- 来源：S1/S2 同节
- 细节：S1「在 `/etc/passwd` 中包含根用户。此 `uid` 根用户应为 `0`」

### F-078 — `/etc/shadow` 中不应有密码哈希
- 来源：S1/S2 同节
- 细节：S1「在 `/etc/shadow` 中不应有密码哈希」

### F-079 — 存档不应包含内核或 initramfs
- 来源：S1/S2 同节
- 细节：S1「存档不应包含内核或 initramfs」

### F-080 — 启用 systemd 时应禁用或屏蔽 9 个已知问题单元
- 来源：S1「系统建议」；S2 "Systemd recommendations"
- 细节：systemd-resolved.service、systemd-networkd.service、NetworkManager.service、systemd-tmpfiles-setup.service、systemd-tmpfiles-clean.service、systemd-tmpfiles-clean.timer、systemd-tmpfiles-setup-dev-early.service、systemd-tmpfiles-setup-dev.service、tmp.mount

### F-081 — 该单元清单同时适用于 system 与 user 单元
- 来源：S1/S2 同节
- 细节：S2 "applies to both system and user units"；S1「适用于系统和用户单位」

## 十一、疑点与源页面瑕疵

### D-01 — `windowsterminal.profileTemplate` 在配置表中重复且默认值冲突
- 证据：F-027
- 说明：一行默认 None，另一行默认「终端模板文件的路径」。两行 Notes 相同，无法据此判断哪行为准；本库在教程中以「默认未设置」为主口径，并把第二行登记为源页面重复条目

### D-02 — 正文单数 `ModernDistribution` 与 JSON 键复数 `ModernDistributions` 不一致
- 证据：F-051
- 说明：以 JSON 代码块的实际键名为实现口径；正文单数形式视为行文误差

### D-03 — 中英文示例 OOBE 脚本代码块均存在换行丢失
- 证据：F-032
- 说明：`DEFAULT_UID` 定义行与后续语句合并、`fi while` 合并、`fi done` 合并；本库教程按 Bash 语法重建等价脚本，并明确标注「非逐字复制」

### D-04 — 中文页存在多处机器翻译痕迹，且示例键名与配置表大小写不一致
- 证据：F-028「现装体验」、F-040「按分布方式」、配置表「密钥/价值/违约」分别对应 Key/Value/Default；F-019 示例写 `ProfileTemplate`，F-025 配置表写 `profileTemplate`
- 说明：本库以英文页作为术语校正基准，中文页用于对照；涉及字段名与命令时一律保留英文原样；大小写差异官方未说明，登记为未验证项

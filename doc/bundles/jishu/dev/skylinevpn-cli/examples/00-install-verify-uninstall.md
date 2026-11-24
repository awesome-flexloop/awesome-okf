---
type: Example
title: "演练 00：安装、校验与卸载（三平台）"
description: "按 README 口径走通一键安装、离线安装、--check 校验与两档卸载；每步标注「文档口径 / 自行可验证」，本包未实跑"
tags: [安装, 离线安装, 校验和, 卸载, purge, 演练]
generated: { by: "seven-concepts-cmd", at: "2026-11-21T12:00:00+08:00" }
status: stable
stale_after: 2027-05-31
---

# 演练 00：安装、校验与卸载

> **性质**：本演练全部命令取自 `README.zh-CN.md`（F-019 ~ F-025），**未在任何实机执行**。命令本身可按文档直接使用；涉及「安装后行为」的描述属于文档口径，未经本包复现。
> **前置**：已在官网 `www.skylinevpn.com` 购买订阅（CLI 内不能购买，F-016）。

## 第 1 步：选路径——一键还是离线

| 场景 | 建议路径 | 理由 |
|------|---------|------|
| 个人电脑、网络正常 | 一键安装 | 最短路径，安装器自带校验 |
| 服务器 / 高风险环境 | 离线包 + `--check` | 可先验包再执行，减少远端脚本直接落地的环节 |
| 内网 / 无外网 | 离线包 | 唯一可行路径 |
| 自动化部署 | 一键安装 + `--lang` | 免交互（F-020） |

## 第 2 步：一键安装

**Linux**

```bash
curl -fsSL https://github.com/skyline-projext/skylinevpn-cli/releases/latest/download/skyline-linux-install.sh | sudo bash
```

**macOS**

```bash
curl -fsSL https://github.com/skyline-projext/skylinevpn-cli/releases/latest/download/skyline-macos-install.sh | sudo bash
```

**Windows**（管理员 PowerShell）

```powershell
$u = "https://github.com/skyline-projext/skylinevpn-cli/releases/latest/download/skyline-windows-install.ps1"
$f = "$env:TEMP\skyline-install.ps1"
Invoke-WebRequest -UseBasicParsing $u -OutFile $f
powershell -ExecutionPolicy Bypass -File $f
```

Windows 之所以先落盘再执行，是为了让脚本可见（可打开检查），也避免 `iex` 管道执行。

安装器会依次：检测架构 → 下载对应包 → 校验 SHA-256 → 安装后台服务 → 询问语言（F-019）。指定语言时追加 `-Lang en`（PowerShell）或 `--lang en`（bash）。

## 第 3 步：离线安装 + 独立校验

从同一个 Release 下载资产与 `SHA256SUMS.txt`，先做**文件级**校验：

```bash
sha256sum -c SHA256SUMS.txt          # macOS 用 shasum -a 256 -c
```

再做**包级**校验（不安装、不提权）：

```bash
# Linux：解压 universal 束后
bash install.sh --check ./skyline-linux-cli_3.0.1_amd64.deb

# macOS：.pkg 与安装脚本放同一目录
bash skyline-macos-install.sh --check ./SkylineVPN-CLI-3.0.1.pkg
```

两套校验的分工见 [03 安装期校验链](../concepts/03-installer-verification-chain.md)：`SHA256SUMS` 证明下载未损坏，`--check` 证明包符合安装器预期。

最后执行安装：

```bash
# Linux
tar -xzf skyline-linux-cli-universal-*.tar.gz
sudo bash install.sh

# macOS
sudo bash skyline-macos-install.sh

# Windows：解压 zip 后，管理员 PowerShell 运行
.\install.cmd
```

## 第 4 步：让命令生效

| 平台 | 动作 | 原因 |
|------|------|------|
| Windows | 开一个新终端 | PATH 在当前会话未刷新（F-028） |
| Linux | 注销并重新登录一次 | 使非 root 用户进入 `skyline` 用户组（F-028） |
| macOS | 若无提示，直接使用 | — |

验证：

```bash
skyline version
skyline --help
```

## 第 5 步：卸载

| 平台 | 普通卸载 | 彻底卸载（含数据与日志） |
|------|---------|------------------------|
| Linux（deb） | `sudo apt-get remove skyline-cli` | `sudo apt-get purge skyline-cli` |
| macOS | `sudo /usr/local/lib/skyline/uninstall.sh` | 追加 `--purge` |
| Windows | `uninstall.ps1` | 追加 `-Purge` |

卸载前建议先 `skyline logout`，再按需保留 `/var/log/skyline/` 等日志用于排障（F-025、F-026）。

## 常见偏差

| 偏差 | 纠正 |
|------|------|
| 用 `releases/download/v3.0.0/` 但装完报版本不符 | 安装器内地址与 tag 绑定；应使用该 tag 目录下的安装器（F-034） |
| 把第三方镜像的安装器当官方 | 只从 `github.com/skyline-projext/skylinevpn-cli/releases` 取；`getskyline.org` 为钓鱼站（F-017） |
| 跳过上传者核对 | `SHA256SUMS` 只能证明完整性，来源需另看上传者（[06](../concepts/06-trust-model-and-boundaries.md)） |

## 主题关联

- [01 产品面](../concepts/01-product-surface.md)
- [演练 01 日常使用与排障](01-daily-usage-and-troubleshooting.md)

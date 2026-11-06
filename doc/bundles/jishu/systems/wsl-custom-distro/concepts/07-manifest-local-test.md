---
type: Tutorial
title: "07 分发清单结构与本地测试"
description: "ModernDistributions 清单字段、flavor 与版本选择、双架构 URL/SHA256、注册表覆盖、file:// 本地测试脚本与恢复官方清单"
tags: [wsl, manifest, distribution-list, registry, file-protocol, custom-distro]
generated: { by: "reference_agent/trae-solo", at: "2026-11-06T00:00:00Z" }
status: draft
stale_after: "2027-05-31"
sources:
  - id: facts
    resource: /references/facts.md
    title: 事实清单（81 条）
  - id: ms-zh
    resource: https://learn.microsoft.com/zh-cn/windows/wsl/build-custom-distro
    title: 为 WSL 生成自定义 Linux 分发版（中文）
---

# 07 分发清单结构与本地测试

`wsl --install <distro>` 能装什么，不由 WSL 二进制决定，而由**分发清单**决定（F-048）。官方清单在 microsoft/WSL 仓库（F-050），企业可以用注册表覆盖或追加自己的清单（F-061~F-064）。本节讲清清单结构，并给出本地测试闭环。

## 一、清单位置与结构

官方清单：`https://github.com/microsoft/WSL/blob/master/distributions/DistributionInfo.json`（F-050）。

基于 tar 的发行版写在根键 `ModernDistributions` 下（F-051）：

```json
{
  "ModernDistributions": {
    "<flavor>": [
      {
        "Name": "<version name>",
        "FriendlyName": "<friendly name>",
        "Default": true,
        "Amd64Url": {
          "Url": "<tar url>",
          "Sha256": "<tar sha256 hash>"
        },
        "Arm64Url": {
          "Url": "<tar url>",
          "Sha256": "<tar sha256 hash>"
        }
      }
    ]
  }
}
```

| 字段 | 必填性（按示例） | 含义 |
|---|---|---|
| `<flavor>` | 是 | 发行版系列名，作为对象键 |
| `Name` | 是 | 版本名，可被 `wsl --install <Name>` 直接使用 |
| `FriendlyName` | 是 | 展示名 |
| `Default` | 是 | 该 flavor 下的默认版本 |
| `Amd64Url.Url` / `.Sha256` | 是 | x64 下载地址与摘要（F-052、F-057） |
| `Arm64Url.Url` / `.Sha256` | 是 | ARM64 下载地址与摘要（F-052、F-057） |

> **源页面瑕疵（S-02）**：正文写作 `ModernDistribution`（单数），JSON 根键是 `ModernDistributions`（复数）（F-051、D-02）。**唯一正确的根键是复数形式 `ModernDistributions`**；官方正文的单数写法不可照抄，本教程所有示例与自检项均按复数书写。

## 二、flavor 与版本的选择语义

官方示例（F-055、F-056）：

```json
{
  "ModernDistributions": {
    "my-distro": [
      {
        "Name": "my-distro-v3",
        "Default": true,
        "FriendlyName": "My distribution version 3 (latest)"
      },
      {
        "Name": "my-distro-v2",
        "Default": false,
        "FriendlyName": "My distribution version 2"
      }
    ]
  }
}
```

对应安装行为：

```powershell
wsl --install my-distro      # 安装 my-distro-v3（flavor 的 Default）
wsl --install my-distro-v3   # 显式安装 v3
wsl --install my-distro-v2   # 显式安装 v2
```

规则：用 flavor 名安装时取 `Default: true` 的条目；用版本名安装时直接命中该条目（F-054）。

## 三、本地测试：用注册表覆盖清单

适用 WSL 2.4.4+，`file://` 协议可用于本地测试（F-065）。注册表位置（F-061）：

```text
HKEY_LOCAL_MACHINE\SOFTWARE\Microsoft\Windows\CurrentVersion\Lxss
```

两个值（F-062、F-063、F-064）：

| 值名 | 作用 |
|---|---|
| `DistributionListUrl` | 覆盖清单 URL |
| `DistributionListUrlAppend` | 把该清单中的发行版追加到可安装列表 |

两者都是 `REG_SZ`，值为 URL 格式（F-064）。

### 3.1 覆盖脚本（语义重建版 + 本库修正）

> 官方示例脚本同样存在换行丢失（`$TarPath = Resolve-Path $TarPath $hash = ...` 合并）。以下按 PowerShell 语法重建，参数、字段与写入逻辑与原文一致（F-066~F-068）；唯一改动是把 `file://` 地址统一为正文要求的 `file:///C:/...` 形式（S-06，说明见代码块之后）。

```powershell
#Requires -RunAsAdministrator

[cmdletbinding(PositionalBinding = $false)]
param (
    [Parameter(Mandatory = $true)][string]$TarPath,
    [string]$Flavor = "test-distro",
    [string]$Version = "test-distro-v1",
    [string]$FriendlyName = "Test distribution version 1"
)

Set-StrictMode -Version latest

$TarPath = (Resolve-Path $TarPath).Path
$hash = (Get-FileHash $TarPath -Algorithm SHA256).Hash

# 统一成正文要求的 file:///C:/path/to/file 形式（S-06 修正）
$tarUri = 'file:///' + ($TarPath -replace '\\', '/')

$manifest = @{
    ModernDistributions = @{
        "$Flavor" = @(
            @{
                "Name" = "$Version"
                Default = $true
                FriendlyName = "$FriendlyName"
                Amd64Url = @{
                    Url = $tarUri
                    Sha256 = "0x$hash"
                }
            }
        )
    }
}

$manifestFile = Join-Path $PSScriptRoot 'manifest.json'
$manifest | ConvertTo-Json -Depth 5 | Out-File -encoding ascii $manifestFile
$manifestFileUri = 'file:///' + ($manifestFile -replace '\\', '/')
Set-ItemProperty -Path "HKLM:SOFTWARE\Microsoft\Windows\CurrentVersion\Lxss" `
    -Name DistributionListUrl -Value $manifestFileUri -Type String -Force
```

> **与官方脚本的差异（S-06）**：官方正文要求 `file:///C:/path/to/file` 格式（F-065），但官方脚本用 `"file://$TarPath"` 直接拼接，在 Windows 上会得到 `file://C:\...`（反斜杠且少一道斜杠）。上面的重建版把路径统一为「正斜杠 + 三斜杠」，使清单 `Url` 与注册表值都符合正文格式。
>
> 该修正**未实跑验证**：目前只能确认正文口径，不能确认两种写法的运行时兼容性。若你的 WSL 拒绝此写法而接受官方写法，把 `$tarUri` 改回 `"file://$TarPath"` 即可。若路径含空格或非 ASCII 字符，上述拼接不会做百分号转义（官方脚本同样不做），建议把 `.wsl` 放在无空格、纯 ASCII 的路径下再做本地测试。

**执行**（F-069）：

```powershell
.\override-manifest.ps1 -TarPath /path/to/tar
```

**预期输出**（F-070）：

```text
The following is a list of valid distributions that can be installed.
Install using 'wsl.exe --install <Distro>'.

NAME            FRIENDLY NAME
test-distro-v1  Test distribution version 1
```

**安装测试**（F-071）：

```powershell
wsl.exe --install test-distro-v1
```

### 3.2 恢复官方清单

删除注册表值即可（F-072）：

```powershell
Remove-ItemProperty -Path "HKLM:\SOFTWARE\Microsoft\Windows\CurrentVersion\Lxss" `
    -Name DistributionListUrl
```

> `Remove-ItemProperty` 是本库按「删除注册表值」语义给出的命令；官方原文只说可以删除该值。

## 四、企业内分发：覆盖还是追加

| 需求 | 用哪个值 | 影响 |
|---|---|---|
| 完全用内部清单替代官方清单 | `DistributionListUrl` | 用户只能看到内部清单中的发行版 |
| 保留官方清单，额外增加内部发行版 | `DistributionListUrlAppend` | 官方 + 内部并存 |
| 只在单机做本地测试 | `DistributionListUrl` + `file://` | 仅影响该机（F-065） |

选择建议（**本库判断**）：企业内部优先用 `DistributionListUrlAppend`，避免用户失去官方发行版；测试机可用 `DistributionListUrl` 做完全隔离。

## 五、清单条目自检

- [ ] 根键是 `ModernDistributions`（复数）
- [ ] 每个 flavor 下至少一个 `Default: true`
- [ ] `Name` 与 `FriendlyName` 均非空
- [ ] `Amd64Url` 与 `Arm64Url` 都有 `Url` 与 `Sha256`
- [ ] `Sha256` 与实际文件一致（脚本用 `Get-FileHash` 计算）
- [ ] `Url` 对内部清单可使用 HTTPS 或 `file://`（本地测试，F-065）
- [ ] 清单文件编码为 ASCII/UTF-8 且 JSON 可解析

## 六、常见错误

| 现象 | 可能原因 | 修复 |
|---|---|---|
| `wsl --list --online` 看不到测试条目 | 注册表值未写入/权限不足（F-066） | 以管理员重跑脚本 |
| 看到条目但安装 404 | `Url` 指向的文件不可访问 | 核对路径与 `file://` 格式（F-065） |
| 安装报摘要不匹配 | `Sha256` 与文件不一致 | 重新计算并更新清单（F-068） |
| 官方发行版全消失 | 用了 `DistributionListUrl` 覆盖 | 改用 `DistributionListUrlAppend`，或删除值恢复（F-072） |
| 写了 `ModernDistribution` | 根键拼写错误（正文单数 vs JSON 复数，F-051） | 改为 `ModernDistributions` |

## 七、小结

- 清单是 `wsl --install` 的数据源（F-048），结构为 `ModernDistributions` → flavor → 版本（F-051~F-057）。
- 本地测试靠 `HKLM\...\Lxss` 的 `DistributionListUrl` + `file://`（F-061、F-065）。
- 企业分发优先 `DistributionListUrlAppend`；测试完删除值恢复官方清单（F-072）。

下一步：[08 企业分发与公开上架](08-enterprise-and-publishing.md)。

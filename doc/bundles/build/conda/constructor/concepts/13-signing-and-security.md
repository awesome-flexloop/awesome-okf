---
type: concept
title: "签名与安全"
description: "constructor 的代码签名机制（Windows signtool/AzureSignTool、macOS codesign/productsign）、frozen 环境保护、路径安全检查和安装时安全验证。"
tags: [签名, 安全, codesign, signtool, AzureSignTool, frozen, CEP-22, UAC]
status: stable
stale_after: 2027-12-31
level: intermediate
prerequisites: ["03-construct-yaml-schema", "09-platform-installers"]
reading_time: 10
generated: { by: "concept_agent/trae-cn", at: "2026-08-21T00:00:00Z" }
sources:
  - id: constructor-signing
    resource: "constructor/signing.py"
---

# 签名与安全

constructor 支持对生成的安装程序进行代码签名，并提供多种安全机制保护安装的环境。

## Windows 代码签名

Windows 安装程序（.exe/.msi）支持两种签名工具：

### 签名工具选择

通过 `windows_signing_tool` 配置：

| 工具 | 值 | 说明 |
|------|---|------|
| Windows SDK SignTool | `signtool`（默认） | 使用本地安装的 Windows SDK signtool.exe |
| Azure SignTool | `azuresigntool` | 使用 Azure Key Vault 签名（云签名） |

### SignTool（本地证书）

```yaml
windows_signing_tool: signtool
signing_certificate: "C:/certs/my-cert.pfx"   # 证书路径
```

签名命令（由 `signing.WindowsSignTool` 执行）：
```cmd
signtool.exe sign /f <certificate.pfx> /p <password> /tr http://timestamp.digicert.com /td sha256 /fd sha256 <installer.exe>
```

环境变量配置密码：
- `CONSTRUCTOR_SIGNTOOL_CERT_PASSWORD`：PFX 文件密码

### AzureSignTool（Azure Key Vault）

适用于企业 CI/CD 场景，证书存储在 Azure Key Vault 中，不暴露到本地：

```yaml
windows_signing_tool: azuresigntool
```

需要通过环境变量配置 Azure 凭据：
- `AZURE_KEY_VAULT_URL`：Key Vault URL
- `AZURE_CERT_NAME`：证书名称
- `AZURE_CLIENT_ID` / `AZURE_CLIENT_SECRET` / `AZURE_TENANT_ID`：服务主体凭据

签名命令（由 `signing.AzureSignTool` 执行）：
```cmd
azuresigntool sign -kvu <vault-url> -kvc <cert-name> -kvi <client-id> -kvs <client-secret> -kvt <tenant-id> -tr http://timestamp.digicert.com <installer.exe>
```

### SigningTool 类体系

```python
class SigningTool:               # 抽象基类
    def sign(self, file_path): ...
    def verify(self, file_path): ...

class WindowsSignTool(SigningTool):   # signtool.exe
    def __init__(self, certificate_path=None, password=None): ...

class AzureSignTool(SigningTool):     # Azure Key Vault
    def __init__(self, **azure_kwargs): ...

class CodeSign(SigningTool):          # macOS codesign
    def __init__(self, identity_name=None): ...
```

所有签名工具通过 `subprocess.check_call()` 调用外部命令行工具执行签名。

## macOS 代码签名与公证

### PKG 安装程序签名

macOS pkg 安装程序使用 Apple 的 `productsign` 进行签名：

```yaml
signing_identity_name: "Developer ID Installer: Your Name (TEAMID1234)"
```

签名命令：
```bash
productsign --sign "Developer ID Installer: Your Name (TEAMID1234)" \
  unsigned.pkg signed.pkg
```

需要在 Keychain 中安装"Developer ID Installer"证书（.p12 文件）。

### conda-standalone 公证签名

在 macOS 上，安装程序内嵌的 conda-standalone 二进制也需要签名才能通过 Gatekeeper 检查：

```yaml
notarization_identity_name: "Developer ID Application: Your Name (TEAMID1234)"
```

使用 `codesign` 签名内嵌的二进制：
```bash
codesign --sign "Developer ID Application: Your Name (TEAMID1234)" \
  --options runtime --timestamp PREFIX/_conda
```

### 公证（Notarization）

签名后的 pkg 需要提交 Apple 公证服务（`xcrun notarytool`）才能在 Catalina+ 上无警告运行。constructor 本身不执行公证（公证需要网络和 Apple 账号），但正确签名是公证的前提。

## Frozen 环境保护（CEP-22）

### 什么是 Frozen 环境？

Frozen 环境是 CEP-22（conda Enhancement Proposal）定义的环境保护机制。当 conda 环境目录中存在 `conda-meta/frozen` 文件时，conda 将拒绝在该环境中执行 `install`/`update`/`remove`/`create` 等修改操作。

### 配置方式

```yaml
freeze_base:
  conda:
    message: "This base environment is managed by the installer and cannot be modified."
    # 可选字段：
    # override_channels: [...]
    # allowed_commands: [...]
```

base 环境的 frozen 标记由 `preconda.write_frozen()` 写入：
```json
{
  "conda": {
    "message": "This base environment is managed by the installer..."
  }
}
```

对于额外环境：

```yaml
extra_envs:
  myenv:
    specs: [python, numpy]
    freeze_env:
      conda:
        message: "This environment is frozen."
```

### Frozen 行为

- 用户尝试 `conda install xyz` → 报错，显示 message
- 用户尝试 `pip install xyz` → 不受 frozen 限制（frozen 仅保护 conda 操作）
- 更新安装程序（`-u`）可以绕过 frozen（构造函数在升级时自动移除 frozen 标记）
- 需要 conda-standalone >= 版本支持 CEP-22

### 适用场景

1. **企业标准化环境**：确保所有用户使用完全相同的包版本
2. **面向非技术用户**：防止用户意外破坏环境
3. **软件打包**：将 conda 环境作为软件的运行时，不希望用户修改

## 路径安全检查

### 路径长度检查（Windows MAX_PATH）

constructor 在 FCP 阶段计算所有包中文件的最大路径长度：

```python
# fcp.py check_duplicates_files()
for pc_rec in pc_recs:
    for path_data in paths_data["paths"]:
        relative_path = f"envs/{env_name}/{path_data['_path']}"
        length = len(relative_path)
        if length > max_length:
            max_length = length
info["_max_relative_path_length"] = max_length
```

安装程序在安装时检查：安装路径长度 + `_max_relative_path_length` < 260（Windows MAX_PATH 限制），否则报错提示用户选择更短的路径。

### 路径空格检查

`check_path_spaces: true`（默认）在安装时检查路径是否包含空格。空格可能导致某些包的脚本出错：

```yaml
check_path_spaces: true   # 默认，含空格时报错
check_path_spaces: false  # 允许空格（需要 conda >=22.11.1，且 base 不能包含 conda）
```

### 默认路径设计

constructor 根据平台选择安全的默认安装路径：
- Linux：`$HOME/<name>`（或 `/opt/<name>` 当 HOME 不存在）
- macOS：`~/<name>`（Just Me）或 `/<name>`（All Users）
- Windows Just Me：`%USERPROFILE%\<name>`
- Windows All Users：`%ALLUSERSPROFILE%\<name>`
- Windows 域用户：`%LOCALAPPDATA%\<name>`（避免漫游配置文件问题）

## UAC 和权限管理

### Windows UAC

Windows EXE 安装程序通过 NSIS 的 `UAC.nsh` 宏处理权限提升：
- Just Me 模式：不请求 UAC，安装到用户目录
- All Users 模式：自动请求 UAC 提升，安装到系统目录

### macOS 权限

PKG 安装程序根据 `pkg_domains` 决定权限需求：
- `enable_currentUserHome`：不需要 root
- `enable_localSystem`：需要 root 权限
- `enable_anywhere`：用户选择卷时可能需要 root

## 安装时完整性验证

### MD5/SHA256 校验

每个包的 `urls` 文件包含 MD5 哈希，conda-standalone 在安装时验证包完整性：

```
https://.../python-3.14.6-h...tar.bz2#<md5>
```

conda 在安装过程中：
1. 检查 tarball 是否存在于 `pkgs/` 目录
2. 计算 MD5 并与 urls 中的哈希比对
3. 不匹配则报错

### initial-state.explicit.txt

`preconda.write_initial_state_explicit_txt()` 写入精确的包 URL 和 MD5，用于 `conda list --explicit` 和环境验证。这确保安装后可以验证环境与构建时一致。

## 预构建安全检查

constructor 在构建时执行以下安全检查：

1. **重复文件检测**：跨包同路径文件冲突（可能导致安装时文件被覆盖）
2. **大小写冲突**：macOS/Windows 上的大小写不敏感重复文件
3. **conda-standalone 版本检查**：确保版本满足最低要求（>=24.1.0）
4. **frozen 版本兼容性**：25.5.x 的 conda-standalone 有 frozen bug 警告
5. **Schema 校验**：不允许未声明的配置字段（`extra="forbid"`）
6. **依赖求解失败**：specs 无法满足时立即报错，不生成损坏的安装程序

## 安全建议

1. **始终签名发布版本**：Windows 使用 signtool/AzureSignTool，macOS 使用 codesign
2. **使用 hash 构建产物**：发布时附带 SHA-256 校验文件
3. **企业分发启用 freeze_base**：防止用户意外修改标准化环境
4. **使用 channels_remap**：不在安装程序中暴露内部通道 URL
5. **启用 check_path_spaces**：默认开启，避免路径空格导致的问题
6. **许可证审计**：使用 `build_outputs: [licenses]` 收集许可证信息

## 下一步

- [11-多环境与通道配置](../11-multi-env-and-channels.md)：了解 channels_remap 等隐私相关配置
- [09-平台安装器实现](../09-platform-installers.md)：了解签名在各平台模块中的调用点

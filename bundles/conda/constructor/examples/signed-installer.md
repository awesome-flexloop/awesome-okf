---
type: example
title: "签名安装程序"
description: "为 Windows 和 macOS 安装程序配置代码签名，包括本地证书签名、Azure Key Vault 云签名和 Apple Developer 证书签名。"
tags: [签名, signtool, AzureSignTool, codesign, productsign, 公证, 证书]
status: stable
stale_after: 2027-12-31
level: advanced
prerequisites: ["custom-installer", "../concepts/13-signing-and-security"]
reading_time: 12
generated: { by: "example_agent/trae-cn", at: "2026-08-21T00:00:00Z" }
sources:
  - id: constructor-signing
    resource: "constructor/signing.py"
---

# 签名安装程序

签名的安装程序在 Windows SmartScreen 和 macOS Gatekeeper 中不会被拦截，用户不会看到"未知发布者"警告。本例演示三种签名方案：Windows 本地证书、Windows Azure Key Vault 云签名、macOS Apple Developer 签名。

## Windows 签名：本地证书（signtool.exe）

### 前提条件

1. 获得代码签名证书（.pfx/.p12 格式）：
   - 从 DigiCert、Sectigo 等 CA 购买 EV 或 OV 代码签名证书
   - 或使用内部 CA 签发的证书（企业内部分发）
2. 安装 Windows SDK（包含 signtool.exe）
3. 证书密码（如果 PFX 文件有密码）

### construct.yaml

```yaml
name: MyApp
version: "1.0"

channels:
  - conda-forge
specs:
  - python=3.14
  - pip

installer_type: exe  # [win]

# Windows 签名配置
windows_signing_tool: signtool     # [win]
signing_certificate: "C:/certs/mycompany-cert.pfx"  # [win]

# 其他 Windows 配置
company: "MyCompany Inc."
```

### 构建

设置证书密码环境变量后构建：

```cmd
:: 设置证书密码
set CONSTRUCTOR_SIGNTOOL_CERT_PASSWORD=your_cert_password_here

:: 构建（constructor 自动签名）
constructor . -o dist
```

constructor 执行的签名命令大致为：

```cmd
signtool.exe sign ^
  /f "C:\certs\mycompany-cert.pfx" ^
  /p %CONSTRUCTOR_SIGNTOOL_CERT_PASSWORD% ^
  /tr http://timestamp.digicert.com ^
  /td sha256 ^
  /fd sha256 ^
  "dist\MyApp-1.0-Windows-x86_64.exe"
```

### 验证签名

```cmd
:: 验证文件签名
signtool verify /pa /v dist\MyApp-1.0-Windows-x86_64.exe

:: 查看签名信息
powershell -Command "Get-AuthenticodeSignature 'dist\MyApp-1.0-Windows-x86_64.exe' | Format-List *"
```

右键 exe 文件 → 属性 → 数字签名 标签中可看到签名信息。

## Windows 签名：Azure Key Vault（云签名）

适用于 CI/CD 流水线，证书私钥不离开 Azure Key Vault 硬件安全模块（HSM）。

### 前提条件

1. Azure 账号和 Key Vault
2. 在 Key Vault 中导入或生成代码签名证书
3. 创建服务主体（Service Principal）并授予证书签名权限
4. 安装 [AzureSignTool](https://github.com/vcsjones/AzureSignTool)

### Azure Key Vault 设置

```bash
# 安装 Azure CLI
az login

# 创建服务主体
az ad sp create-for-rbac --name constructor-signing --role "Key Vault Crypto User" \
  --scopes /subscriptions/<sub-id>/resourceGroups/<rg>/providers/Microsoft.KeyVault/vaults/<vault-name>
```

记录输出的 `appId`（clientId）、`password`（clientSecret）、`tenant`。

### construct.yaml

```yaml
name: MyApp
version: "1.0"
channels:
  - conda-forge
specs:
  - python=3.14

installer_type: exe                       # [win]
windows_signing_tool: azuresigntool       # [win]
```

### 构建（CI 环境变量）

在 CI/CD 系统（GitHub Actions、Azure DevOps 等）中设置环境变量：

```bash
# Azure Key Vault 配置（CI 环境变量）
export AZURE_KEY_VAULT_URL="https://myvault.vault.azure.net"
export AZURE_CERT_NAME="mycompany-codesign-cert"
export AZURE_CLIENT_ID="xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx"
export AZURE_CLIENT_SECRET="xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx"
export AZURE_TENANT_ID="xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx"

# 构建
constructor . -o dist
```

constructor 执行的 AzureSignTool 命令大致为：

```cmd
azuresigntool sign ^
  -kvu %AZURE_KEY_VAULT_URL% ^
  -kvc %AZURE_CERT_NAME% ^
  -kvi %AZURE_CLIENT_ID% ^
  -kvs %AZURE_CLIENT_SECRET% ^
  -kvt %AZURE_TENANT_ID% ^
  -tr http://timestamp.digicert.com ^
  -v ^
  "dist\MyApp-1.0-Windows-x86_64.exe"
```

### GitHub Actions 集成

```yaml
name: Build and Sign Windows Installer
on:
  push:
    tags: ["v*"]

jobs:
  build-windows:
    runs-on: windows-latest
    steps:
      - uses: actions/checkout@v4

      - name: Setup Conda
        uses: conda-incubator/setup-miniconda@v3
        with:
          channels: conda-forge
          python-version: "3.14"

      - name: Install constructor
        run: conda install -y constructor conda-standalone

      - name: Install AzureSignTool
        run: dotnet tool install --global AzureSignTool

      - name: Build and sign
        env:
          AZURE_KEY_VAULT_URL: ${{ secrets.AZURE_KEY_VAULT_URL }}
          AZURE_CERT_NAME: ${{ secrets.AZURE_CERT_NAME }}
          AZURE_CLIENT_ID: ${{ secrets.AZURE_CLIENT_ID }}
          AZURE_CLIENT_SECRET: ${{ secrets.AZURE_CLIENT_SECRET }}
          AZURE_TENANT_ID: ${{ secrets.AZURE_TENANT_ID }}
        run: constructor . -o dist/

      - name: Upload artifact
        uses: actions/upload-artifact@v4
        with:
          name: installer-windows
          path: dist/*.exe
```

## macOS 签名和公证

### 前提条件

1. Apple Developer 账号（$99/年）
2. 两个证书：
   - **Developer ID Installer**（用于签名 .pkg）
   - **Developer ID Application**（用于签名内嵌的 conda-standalone 二进制）
3. 证书已导入 Keychain（.p12 文件）
4. Xcode 命令行工具（`xcode-select --install`）

### 获取证书

1. 登录 [Apple Developer Portal](https://developer.apple.com/account)
2. Certificates → 创建两个证书：
   - Developer ID Installer（类型：Developer ID - Installer）
   - Developer ID Application（类型：Developer ID - Application）
3. 下载 .cer 文件，双击导入 Keychain Access
4. 导出为 .p12 文件（含私钥）

证书的 Common Name 格式：
- Installer: `Developer ID Installer: Your Name (TEAMID)`
- Application: `Developer ID Application: Your Name (TEAMID)`

### construct.yaml

```yaml
name: MyApp
version: "1.0"
channels:
  - conda-forge
specs:
  - python=3.14
  - conda

installer_type: [sh, pkg]             # [osx] macOS 构建两种类型

# macOS 签名配置
signing_identity_name: "Developer ID Installer: Your Name (TEAMID)"         # [osx]
notarization_identity_name: "Developer ID Application: Your Name (TEAMID)"  # [osx]

company: "MyCompany Inc."
```

> 注意：sh 安装程序不需要签名，但 pkg 需要。`notarization_identity_name` 用于签名 pkg 内部的 conda-standalone 二进制。

### 构建

```bash
# 解锁 keychain（CI 环境需要）
security unlock-keychain -p "${KEYCHAIN_PASSWORD}" login.keychain-db

# 构建
constructor . -o dist/
```

constructor 自动执行：

1. `codesign --sign "Developer ID Application: ..." --options runtime --timestamp _conda`
   - 签名内嵌的 conda-standalone 二进制（启用 hardened runtime）
2. `pkgbuild --sign "Developer ID Installer: ..." ...` 或 `productsign --sign ...`
   - 签名 .pkg 安装程序

### 公证（Notarization）

签名后必须提交 Apple 公证服务，否则 macOS Catalina+ 会拦截：

```bash
# 提交公证
xcrun notarytool submit dist/MyApp-1.0-MacOSX-x86_64.pkg \
  --apple-id "your-apple-id@example.com" \
  --password "${APP_SPECIFIC_PASSWORD}" \
  --team-id "TEAMID" \
  --wait

# 公证成功后，附加公证票据到 pkg
xcrun stapler staple dist/MyApp-1.0-MacOSX-x86_64.pkg

# 验证
spctl --assess --type install dist/MyApp-1.0-MacOSX-x86_64.pkg
# 应该输出: dist/...: accepted
```

> **注意**：constructor 本身不执行公证步骤（公证需要网络和 Apple ID 凭据），必须在构建后手动或在 CI 中执行。

### macOS CI/CD（GitHub Actions）

```yaml
jobs:
  build-macos:
    runs-on: macos-latest
    steps:
      - uses: actions/checkout@v4

      - name: Setup Conda
        uses: conda-incubator/setup-miniconda@v3
        with:
          channels: conda-forge
          python-version: "3.14"

      - name: Install constructor
        run: conda install -y constructor conda-standalone

      - name: Import certificates
        uses: apple-actions/import-codesign-certs@v3
        with:
          p12-file-base64: ${{ secrets.MACOS_CERTIFICATE_P12_BASE64 }}
          p12-password: ${{ secrets.MACOS_CERTIFICATE_PASSWORD }}

      - name: Build and sign
        run: constructor . -o dist/

      - name: Notarize
        uses: apple-actions/notarize-macos-artifact@v1
        with:
          path: dist/*.pkg
          apple-id: ${{ secrets.APPLE_ID }}
          app-password: ${{ secrets.APPLE_APP_PASSWORD }}
          team-id: ${{ secrets.APPLE_TEAM_ID }}
```

## 不签名的后果

### Windows SmartScreen

- 未签名的 exe：首次运行显示"Windows 已保护你的电脑"蓝色警告
- 无签名的安装程序：Windows Defender SmartScreen 可能标记为不安全
- EV 签名证书：立即获得 SmartScreen 信誉
- OV 签名证书：需要时间积累信誉

### macOS Gatekeeper

- 未签名的 pkg：右键→打开才能绕过，普通用户双击会显示"无法验证开发者"
- 未签名的二进制：触发"恶意软件"检查，可能被隔离
- 未公证的 pkg：macOS Catalina (10.15)+ 直接拒绝

## 签名检查清单

在发布前验证签名：

### Windows
```cmd
:: 检查 exe 签名
signtool verify /pa /v MyApp-1.0-Windows-x86_64.exe
:: 检查卸载程序签名（如果有独立卸载程序）
```

### macOS
```bash
# 检查 pkg 签名
pkgutil --check-signature MyApp-1.0-MacOSX-x86_64.pkg
# 检查内嵌二进制签名
codesign --verify --deep --verbose=2 /path/to/installed/_conda
# Gatekeeper 评估
spctl --assess --type install MyApp-1.0-MacOSX-x86_64.pkg
```

## 时间戳服务

签名时必须使用时间戳服务器（RFC 3161），确保签名在证书过期后仍然有效。constructor 默认使用公共时间戳服务：

| 服务 | URL |
|------|-----|
| DigiCert | `http://timestamp.digicert.com` |
| Sectigo | `http://timestamp.sectigo.com` |
| GlobalSign | `http://timestamp.globalsign.com/scripts/timestamp.dll` |

## 下一步

- [自定义品牌安装程序](./custom-installer.md)：构建待签名的安装程序
- [基础 Miniconda 风格安装程序](./basic-miniconda.md)：入门示例
- [13-签名与安全](../concepts/13-signing-and-security.md)：签名机制的底层实现

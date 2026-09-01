---
type: example
title: "自定义品牌安装程序"
description: "为安装程序添加自定义许可证、品牌图片、安装前后脚本、自定义 NSIS 页面和默认配置，打造完全品牌化的安装体验。"
tags: [自定义, 品牌, 许可证, 图片, 脚本, NSIS, 品牌化]
status: stable
stale_after: 2027-12-31
level: intermediate
prerequisites: ["basic-miniconda", "../concepts/03-construct-yaml-schema", "../concepts/09-platform-installers"]
reading_time: 12
generated: { by: "example_agent/trae-cn", at: "2026-08-21T00:00:00Z" }
sources:
  - id: constructor-winexe
    resource: "constructor/winexe.py"
---

# 自定义品牌安装程序

本例演示如何创建一个完全品牌化的安装程序，包括自定义许可证、公司 Logo、欢迎/完成页面、安装脚本和 Windows 特定自定义。

## 项目结构

```
mycompany-python/
├── construct.yaml
├── LICENSE.txt
├── assets/
│   ├── welcome.bmp        # Windows 欢迎图 (164x314)
│   ├── header.bmp         # Windows 头图 (150x57)
│   ├── icon.ico           # Windows 图标 (256x256)
│   ├── background.png     # macOS 背景 (1227x600)
│   └── post_install.bat   # Windows 安装后脚本
├── scripts/
│   └── post_install.sh    # Unix 安装后脚本
└── nsis/
    └── custom_finish.nsi  # 自定义完成页面（Windows）
```

## construct.yaml

```yaml
name: MyCompanyPython
version: "3.14.0"
company: "MyCompany Inc."
reverse_domain_identifier: "com.mycompany.python"

channels:
  - https://repo.anaconda.com/pkgs/main
  - conda-forge

specs:
  - python=3.14
  - conda
  - pip
  - mycompany-internal-cli  # 公司内部工具

# === 品牌与外观 ===

# 许可证文件
license_file: LICENSE.txt

# Windows 图片
welcome_image: assets/welcome.bmp   # [win]
header_image: assets/header.bmp     # [win]
icon_image: assets/icon.ico         # [win]
default_image_color: blue           # [win] 默认图片颜色（无自定义图时使用）

# macOS 图片和文本
welcome_image: assets/background.png  # [osx]
welcome_text: "欢迎安装 MyCompany Python 环境"  # [osx]
conclusion_text: |                     # [osx]
  安装完成！
  请访问 https://docs.mycompany.com 查看使用文档。
readme_text: |                         # [osx]
  MyCompany Python 包含 Python 3.14、conda 和公司内部 CLI 工具。

# Windows 卸载显示名称
uninstall_name: "MyCompany Python 3.14 (64-bit)"  # [win]

# === 安装路径 ===
default_prefix: "%USERPROFILE%\\MyCompany\\Python"  # [win]
default_prefix_all_users: "%ALLUSERSPROFILE%\\MyCompany\\Python"  # [win]
default_prefix: "$HOME/mycompany/python"             # [unix]

# === 安装行为 ===
initialize_conda: classic
initialize_by_default: true
register_python: true                # [win]
register_python_default: false       # [win]
write_condarc: true
conda_default_channels:
  - https://repo.anaconda.com/pkgs/main
  - https://conda.anaconda.org/conda-forge

# === 自定义脚本 ===

# 安装后脚本
post_install: scripts/post_install.sh   # [unix]
post_install: assets/post_install.bat   # [win]
post_install_desc: "配置 MyCompany 开发环境"  # 显示复选框让用户选择是否运行

# 传递给脚本的环境变量
script_env_variables:
  MYCOMPANY_LICENSE_SERVER: "https://license.mycompany.com"
  MYCOMPANY_DOCS_URL: "https://docs.mycompany.com"

# Windows 卸载前脚本
pre_uninstall: assets/pre_uninstall.bat  # [win]

# === 额外文件注入 ===
extra_files:
  - assets/mycompany-env.sh           # 注入环境变量脚本
  - src: assets/settings.yaml
    dst: etc/mycompany/settings.yaml

# === Windows 自定义 NSIS 页面 ===
conclusion_file: nsis/custom_finish.nsi  # [win] 自定义完成页面

# === 构建产物 ===
build_outputs:
  - hash
  - info.json
  - licenses
  - pkgs_list
```

## 安装后脚本示例

### scripts/post_install.sh（Unix）

```bash
#!/bin/bash
# post_install.sh - MyCompany Python 安装后配置
# 可用环境变量: $PREFIX, $INSTALLER_NAME, $INSTALLER_VER, $INSTALLER_TYPE

echo "=== MyCompany Python 后安装配置 ==="

# 配置公司内部 pip 镜像
mkdir -p "$PREFIX/pip"
cat > "$PREFIX/pip/pip.conf" << EOF
[global]
index-url = https://pypi.mycompany.com/simple
trusted-host = pypi.mycompany.com
EOF

# 配置 conda 通道
"$PREFIX/bin/conda" config --add channels https://conda.mycompany.com/internal \
  --file "$PREFIX/.condarc"

echo "后安装配置完成。"
echo "文档地址: ${MYCOMPANY_DOCS_URL:-https://docs.mycompany.com}"
```

### assets/post_install.bat（Windows）

```batch
@echo off
REM post_install.bat - MyCompany Python Windows后安装配置
REM 可用环境变量: %PREFIX%, %INSTALLER_NAME%, %INSTALLER_VER%, %MYCOMPANY_LICENSE_SERVER%

echo === MyCompany Python 后安装配置 ===

REM 配置 pip 镜像
if not exist "%PREFIX%\pip" mkdir "%PREFIX%\pip"
echo [global] > "%PREFIX%\pip\pip.ini"
echo index-url = https://pypi.mycompany.com/simple >> "%PREFIX%\pip\pip.ini"
echo trusted-host = pypi.mycompany.com >> "%PREFIX%\pip\pip.ini"

REM 配置内部 conda 通道
"%PREFIX%\Scripts\conda.exe" config --add channels https://conda.mycompany.com/internal ^
  --file "%PREFIX%\.condarc"

echo 后安装配置完成。
```

## 自定义 NSIS 完成页面

### nsis/custom_finish.nsi

```nsis
; 自定义完成页面
; 这个文件会被插入到 NSIS 安装程序的最后

!define MUI_FINISHPAGE_TITLE "MyCompany Python 安装完成"
!define MUI_FINISHPAGE_TEXT "MyCompany Python 3.14 已成功安装到 $\r$\n$INSTDIR"

!define MUI_FINISHPAGE_SHOWREADME "$INSTDIR\README.txt"
!define MUI_FINISHPAGE_SHOWREADME_TEXT "查看 README"
!define MUI_FINISHPAGE_RUN "$INSTDIR\Scripts\anaconda-promt.bat"
!define MUI_FINISHPAGE_RUN_TEXT "打开 MyCompany Python 终端"
!define MUI_FINISHPAGE_LINK "访问文档中心"
!define MUI_FINISHPAGE_LINK_LOCATION "https://docs.mycompany.com"
```

## LICENSE.txt 示例

```
MyCompany Python 最终用户许可协议

版权所有 (C) 2026 MyCompany Inc.

本软件受 MyCompany 软件许可协议约束。
...
```

## 图片准备

### Windows 图片要求

| 图片 | 尺寸 | 格式 | 位置 |
|------|------|------|------|
| 欢迎图 | 164x314 px | BMP (24-bit) | NSIS 左侧面板 |
| 头图 | 150x57 px | BMP (24-bit) | NSIS 顶部栏 |
| 图标 | 256x256 px | ICO | 安装程序/卸载程序/开始菜单 |

可以使用 Pillow 生成简单图片：
```python
from PIL import Image, ImageDraw, ImageFont
img = Image.new("RGB", (164, 314), "#0066CC")
draw = ImageDraw.Draw(img)
# 添加文字...
img.save("assets/welcome.bmp")
```

constructor 的 `imaging.py` 会自动将任意格式图片缩放到正确尺寸。

### macOS 图片要求

| 图片 | 尺寸 | 格式 | 位置 |
|------|------|------|------|
| 背景图 | 1227x600 px | PNG/TIFF/JPG | 安装向导背景 |

## 构建

```bash
constructor . -o ./dist
```

输出文件：
```
dist/
├── MyCompanyPython-3.14.0-Windows-x86_64.exe
├── MyCompanyPython-3.14.0-Windows-x86_64.exe.sha256
├── MyCompanyPython-3.14.0-Windows-x86_64.exe.info.json
├── MyCompanyPython-3.14.0-Windows-x86_64.exe-licenses/
│   └── index.txt
└── MyCompanyPython-3.14.0-Windows-x86_64.exe-pkgs_list.csv
```

## 提示与技巧

1. **图片测试**：不提供自定义图片时，constructor 会自动生成带 `name` 文字的默认蓝色图片，可以先构建确认流程，再替换品牌图片。
2. **脚本调试**：post_install 脚本中添加 `set -x`（bash）或 `echo on`（batch）可调试安装时的问题。
3. **post_install_desc**：提供描述后，GUI 安装程序会显示复选框让用户选择是否运行脚本；不提供则强制运行。
4. **extra_files 路径**：相对路径相对于 construct.yaml 所在目录；目标路径相对于安装前缀。
5. **script_env_variables**：Unix 下值自动单引号包裹（支持空格），Windows 下不支持单/双引号和 # 字符。

## 下一步

- [签名安装程序](signed-installer.md)：为 Windows/macOS 安装程序添加代码签名
- [多环境安装程序](multi-env-installer.md)：添加额外的 conda 环境

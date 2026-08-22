---
okf_version: "0.2"
type: Example
title: "单文件打包"
description: "使用--onefile模式将程序打包为单个压缩可执行文件，便于分发"
tags: ["nuitka", "onefile", "single-file", "distribution", "portable"]
difficulty: intermediate
time_to_complete: "10分钟"
prerequisites:
  - "standalone-build.md"
  - "../concepts/10-freezer-distribution.md"
related_concepts:
  - "../concepts/09-c-compilation-backend.md"
related_references:
  - "../references/scons-backend-api.md"
verified: true
status: active
---

# 示例：单文件打包（Onefile）

`--onefile`模式在standalone基础上，将整个dist目录压缩并嵌入到单个EXE文件中。运行时自动解压到临时目录，执行完毕后清理。

## 1. Onefile vs Standalone

| 特性 | Standalone | Onefile |
|------|-----------|---------|
| 产物 | dist目录（多文件） | 单个EXE文件 |
| 分发方式 | 压缩目录分发 | 直接发送EXE |
| 启动速度 | 快（直接运行） | 稍慢（需解压） |
| 体积 | 原体积 | 压缩后更小（通常小30-50%） |
| 运行时写入 | 无（在原位运行） | 写入临时目录 |
| 适合场景 | 专业部署、频繁运行 | 便携式分发、偶尔运行 |

## 2. 基本Onefile编译

```bash
nuitka --onefile app.py
```

编译产物：`app.exe`（单个文件）。

运行：
```bash
app.exe
```

背后发生的事情：
1. 先执行完整的standalone编译→生成`dist/app.dist/`目录
2. 编译`OnefileBootstrap.c`为引导程序
3. 用zstandard压缩`dist/app.dist/`整个目录
4. 将压缩数据附加到引导程序EXE末尾
5. 输出最终的`app.exe`

## 3. 运行时行为

当用户运行onefile EXE时：

```
用户双击 app.exe
  │
  ├── 1. OnefileBootstrap启动（C程序，不依赖Python）
  ├── 2. 读取EXE自身末尾的压缩数据
  ├── 3. 创建临时目录: %TEMP%\ONE_TEMP_<hash>\
  ├── 4. zstandard解压所有文件到临时目录
  ├── 5. CreateProcess/execv 启动解压后的 app.exe
  ├── 6. 等待子进程退出
  └── 7. 删除临时目录（默认行为）
```

## 4. 临时目录控制

使用`--onefile-tempdir-spec`控制临时目录位置：

```bash
# 使用系统临时目录（默认）
nuitka --onefile --onefile-tempdir-spec=%TEMP% app.py

# 使用用户缓存目录（跨运行保留缓存，启动更快）
nuitka --onefile --onefile-tempdir-spec=%CACHE_DIR% app.py

# 使用指定目录
nuitka --onefile --onefile-tempdir-spec=C:\temp\myapp app.py

# 不清理临时目录（调试用）
nuitka --onefile --onefile-tempdir-spec=./temp app.py
```

`%CACHE_DIR%`模式适合：
- 需要快速启动的应用
- 包含大量数据文件解压慢的场景
- 用户首次启动后，后续启动几乎和standalone一样快

## 5. 压缩选项

### 压缩级别

```bash
# 默认压缩（级别约15，平衡速度和压缩率）
nuitka --onefile app.py

# 最小压缩（最快启动）
nuitka --onefile --onefile-compression-level=1 app.py

# 最大压缩（最小体积，压缩/解压慢）
nuitka --onefile --onefile-compression-level=22 app.py

# 不压缩（最快打包/启动，体积最大）
nuitka --onefile --onefile-no-compression app.py
```

压缩级别参考：
- 1-5：快速压缩，压缩率低
- 6-15：平衡（默认约12-15）
- 16-22：高压缩率，压缩慢但解压速度差不多

### 压缩效果

典型压缩效果：
- 纯Python应用：压缩率50-70%（20MB→8-10MB）
- 含C扩展应用：压缩率40-60%（50MB→20-30MB）
- 含大型DLL（如Qt）：压缩率30-50%（200MB→100-140MB）

## 6. 完整Onefile示例（GUI应用）

```bash
nuitka --onefile \
       --windows-disable-console \
       --windows-icon-from-ico=app.ico \
       --windows-product-name="My Tool" \
       --windows-file-version=2.1.0.0 \
       --enable-plugin=tk-inter \
       --include-data-dir=assets=assets \
       --onefile-tempdir-spec=%CACHE_DIR% \
       --onefile-compression-level=15 \
       --output-filename=MyTool \
       my_tool.py
```

产物：`MyTool.exe`（单个文件），包含：
- Tkinter GUI运行时
- 应用图标和版本信息
- assets资源目录
- 无控制台窗口
- 首次启动解压到缓存，后续启动快速

## 7. Splash Screen（Windows闪屏）

大型Onefile应用解压需要时间，可以显示闪屏：

```bash
nuitka --onefile \
       --onefile-windows-splash-screen-image=splash.png \
       app.py
```

解压过程中显示splash.png图片，解压完成后自动关闭。

## 8. Onefile常见问题

### 启动慢

Onefile启动需要解压，如果体积大解压时间明显：
- 使用`%CACHE_DIR%`模式避免每次解压
- 降低压缩级别
- 对频繁运行的工具考虑standalone模式

### 杀毒软件误报

Onefile的自解压行为可能被杀毒软件标记：
- 使用代码签名证书签名EXE（`--windows-certificate-*`选项）
- 提交到杀毒软件厂商白名单
- 考虑standalone模式（不修改自身、不写临时目录）

### 临时目录权限问题

如果`%TEMP%`目录权限不足：
- 指定其他临时目录：`--onefile-tempdir-spec=./temp`
- 确保用户对临时目录有写权限

### 子进程找不到资源

如果程序启动子进程，子进程的工作目录是临时目录：
- 使用`sys._MEIPASS`（PyInstaller兼容）或Nuitka的`__compiled__`常量获取解压路径
- 或使用`--onefile-tempdir-spec`指定固定路径

```python
import sys
import os

# 获取onefile解压目录
if hasattr(sys, '_MEIPASS'):
    # PyInstaller/Nuitka onefile兼容
    base_path = sys._MEIPASS
elif '__compiled__' in dir():
    # Nuitka编译环境
    base_path = os.path.dirname(sys.executable)
else:
    base_path = os.path.dirname(__file__)

# 加载数据文件
data_path = os.path.join(base_path, 'data', 'config.json')
```

### 从Onefile读取打包文件

Onefile模式下，程序自身的exe文件包含打包数据。可以读取：

```python
def get_resource_path(relative_path):
    """获取onefile/standalone模式下的资源路径"""
    if getattr(sys, 'frozen', False):
        # 编译后运行
        base_path = os.path.dirname(sys.executable)
    else:
        # 脚本运行
        base_path = os.path.dirname(os.path.abspath(__file__))
    return os.path.join(base_path, relative_path)
```

## 9. 跨平台Onefile

Onefile在三大平台都支持：

| 平台 | 产物 | 临时目录 |
|------|------|---------|
| Windows | `app.exe` | `%TEMP%\ONE_<hash>\` |
| Linux | `app.bin` | `/tmp/ONE_<hash>/` |
| macOS | `app.bin`（或.app内） | `$TMPDIR/ONE_<hash>/` |

### macOS .app Bundle

在macOS上可以生成.app包：

```bash
nuitka --onefile \
       --macos-create-app-bundle \
       --macos-app-icon=app.icns \
       --macos-app-name="My App" \
       app.py
```

产物：`My App.app`（标准macOS应用包，内含onefile二进制）。

---
okf_version: "0.2"
type: Example
title: "独立可执行文件构建"
description: "使用--standalone模式生成包含所有依赖的dist目录，可在未安装Python的机器上运行"
tags: ["nuitka", "standalone", "distribution", "deployment", "dll"]
difficulty: intermediate
time_to_complete: "10分钟"
prerequisites:
  - "basic-compilation.md"
  - "../concepts/10-freezer-distribution.md"
related_concepts:
  - "../concepts/06-module-import-system.md"
  - "../concepts/11-plugin-system.md"
related_references:
  - "../references/plugin-base-api.md"
verified: true
status: active
---

# 示例：独立可执行文件构建（Standalone）

`--standalone`模式将Python程序和所有依赖（Python运行时、C扩展、DLL、数据文件）打包到一个目录中，该目录可以复制到未安装Python的机器上直接运行。

## 1. 准备项目

创建一个使用第三方库的示例程序 `app.py`：

```python
# app.py
import sys
import json
from pathlib import Path

def main():
    print(f"Python版本: {sys.version}")
    print(f"运行路径: {Path.cwd()}")
    
    # 使用json模块（标准库）
    data = {"name": "Nuitka App", "version": "1.0", "modules": ["json", "sys", "pathlib"]}
    print(json.dumps(data, indent=2, ensure_ascii=False))
    
    # 计算
    result = sum(i * i for i in range(10000))
    print(f"sum of squares (0..9999) = {result}")

if __name__ == "__main__":
    main()
```

## 2. 编译命令

```bash
nuitka --standalone --output-dir=dist app.py
```

### 关键选项

- `--standalone`：启用独立分发模式
- `--output-dir=dist`：输出到dist目录

### 编译输出

```
Nuitka V4.1rc11 on Python 3.11

[CC]   编译模块...
[CC]   编译static_src...
[LINK] app.exe
[DLL]  检测DLL依赖...
[FREE]  收集模块...
       ├── 包含: python311.dll (Python运行时)
       ├── 包含: encodings/ (编码模块)
       ├── 包含: json/ (JSON模块)
       ├── 包含: pathlib.py
       └── 共包含约50-100个文件...

Successfully created 'dist/app.dist/app.exe'.
```

## 3. 产物结构

`dist/app.dist/` 目录包含：

```
dist/app.dist/
├── app.exe                    # 编译后的主程序
├── python311.dll              # Python运行时DLL
├── vcruntime140.dll           # MSVC运行时
├── msvcp140.dll               # MSVC C++运行时
├── ucrtbase.dll               # Universal CRT
├── api-ms-win-*.dll           # Windows API集（如需要）
├── lib/
│   └── python311/
│       ├── encodings/         # 编码模块
│       ├── importlib/         # importlib模块
│       ├── json/              # json包
│       ├── collections/       # collections包
│       ├── lib-dynload/       # C扩展模块
│       └── ...                # 其他标准库模块
└── ...                        # 其他依赖文件
```

## 4. 运行Standalone程序

```bash
# 进入dist目录
cd dist/app.dist

# 运行（无需Python环境！）
app.exe
```

**分发到其他机器**：将整个`app.dist/`目录压缩复制即可。目标机器不需要安装Python。

## 5. GUI应用（Windows）

对于GUI程序（如tkinter/PyQt），添加`--windows-disable-console`隐藏控制台窗口：

```bash
# 简单tkinter示例
nuitka --standalone --windows-disable-console --enable-plugin=tk-inter gui_app.py
```

### 设置EXE图标和版本信息

```bash
nuitka --standalone \
       --windows-disable-console \
       --windows-icon-from-ico=app.ico \
       --windows-product-name="My App" \
       --windows-file-version=1.0.0.0 \
       --windows-product-version=1.0.0 \
       --windows-file-description="My Application" \
       --windows-company-name="My Company" \
       app.py
```

## 6. 包含额外数据文件

如果程序需要数据文件（配置、资源等）：

```bash
# 包含单个文件
nuitka --standalone \
       --include-data-files=config.json=config.json \
       app.py

# 包含整个目录
nuitka --standalone \
       --include-data-dir=resources=resources \
       app.py

# 包含包的数据文件
nuitka --standalone \
       --include-package-data=mypackage \
       app.py
```

## 7. 控制模块包含

### 包含特定包/模块

```bash
# 包含整个包（即使没被import检测到）
nuitka --standalone --include-package=mypackage app.py

# 包含单个模块
nuitka --standalone --include-module=mypackage._hidden app.py
```

### 排除模块（减小体积）

```bash
# 不跟随特定模块导入
nuitka --standalone --nofollow-import-to=tests,debug_tools app.py

# 不跟随标准库（默认行为，除非--follow-stdlib）
# 默认不编译标准库，只包含必要的字节码
```

### 反膨胀（减小dist大小）

```bash
# anti-bloat插件默认启用，自动移除测试代码和debug模块
# 可以额外排除不需要的DLL
nuitka --standalone --noinclude-dlls=libpng16.dll app.py
```

## 8. 使用第三方库的完整示例

以使用`requests`库为例：

```bash
# 安装requests（如果没装）
pip install requests

# 编译（Nuitka自动检测requests及其依赖）
nuitka --standalone --follow-imports web_app.py
```

Nuitka会自动：
1. 检测到`import requests`
2. 跟随导入requests、urllib3、certifi、charset_normalizer、idna
3. 收集requests所需的CA证书（certifi的cacert.pem）
4. 打包所有DLL依赖

对于更复杂的库（NumPy、PyTorch、Qt等），需要启用对应插件：

```bash
# PyQt6应用
nuitka --standalone \
       --enable-plugin=pyqt6 \
       --include-qt-plugins=sensible,multimedia \
       qt_app.py

# NumPy/Pandas应用
nuitka --standalone \
       --enable-plugin=numpy \
       data_app.py
```

## 9. 常见问题排查

### 运行时 ModuleNotFoundError

如果运行时提示某模块找不到：
1. 检查是否用了动态导入（`__import__()`、`importlib.import_module()`）
2. 使用`--include-module=MOD`手动包含
3. 使用`--follow-import-to=MOD`强制跟随
4. 查看`--explain-imports`输出了解包含决策

### DLL缺失错误

```
ImportError: DLL load failed while importing _xxx: 找不到指定的模块。
```

1. 确保使用了正确的插件（`--enable-plugin=xxx`）
2. 使用`--include-data-dir`包含DLL所在目录
3. Windows上可能需要安装Visual C++ Redistributable

### dist目录太大

- 使用`--noinclude-data-files=*.pyc`排除.pyc
- 排除不需要的模块：`--nofollow-import-to=tkinter,test,tests`
- 启用UPX压缩：`--upx-bin=upx.exe`
- 考虑使用[Onefile模式](onefile-build.md)（不减小体积但更方便分发）

### 编译时间过长

- 使用`-j N`并行编译（N=CPU核心数）
- 安装ccache加速增量编译
- 首次编译后，增量编译会快很多
- 避免`--follow-stdlib`（编译标准库会大幅增加时间）

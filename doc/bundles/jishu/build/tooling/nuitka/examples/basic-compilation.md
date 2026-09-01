---
okf_version: "0.2"
type: Example
title: "基本编译"
description: "使用Nuitka将Python脚本编译为可执行文件——最基础的编译命令和输出说明"
tags: ["nuitka", "basic", "compilation", "hello-world"]
difficulty: beginner
time_to_complete: "5分钟"
prerequisites:
  - "../concepts/00-introduction.md"
  - "../concepts/01-compilation-pipeline.md"
related_concepts:
  - "../concepts/13-cli-options.md"
related_references:
  - "../references/main-control-entry.md"
verified: true
status: active
---

# 示例：基本编译

本示例演示最基础的Nuitka编译流程——将一个简单的Python脚本编译为本地可执行文件。

## 1. 准备Python脚本

创建一个简单的Python脚本 `hello.py`：

```python
# hello.py
def greet(name):
    return f"Hello, {name}!"

def main():
    names = ["World", "Nuitka", "Python"]
    for name in names:
        print(greet(name))
    
    # 计算斐波那契数列
    def fib(n):
        if n <= 1:
            return n
        return fib(n - 1) + fib(n - 2)
    
    print(f"fib(20) = {fib(20)}")

if __name__ == "__main__":
    main()
```

## 2. 基本编译命令

最简单的编译命令：

```bash
nuitka hello.py
```

### 编译过程输出

```
Nuitka V4.1rc11 on Python 3.11
│
│ ......
│
[CC]   constants_1.c
[CC]   helpers.c
[CC]   hello.py  (main module)
[CC]   __main__.c
[LINK] hello.exe

Successfully created 'hello.exe'.
```

## 3. 编译产物

编译完成后，当前目录下会产生：

| 文件 | 说明 |
|------|------|
| `hello.exe`（Windows）/`hello.bin`（Linux/macOS） | 编译后的可执行文件 |
| `hello.build/` | 构建目录（C源码、目标文件、SCons缓存） |
| `hello.dist/`（standalone模式才会有） | 依赖分发目录 |
| `hello.cmd`（Windows） | 启动辅助脚本 |

### 运行编译后的程序

```bash
# Windows
hello.exe

# Linux/macOS
./hello.bin
```

输出：
```
Hello, World!
Hello, Nuitka!
Hello, Python!
fib(20) = 6765
```

## 4. 编译过程解析

基本编译命令`nuitka hello.py`在背后执行了：

```
1. 解析hello.py为CPython AST（ast.parse）
2. 构建Nuitka IR树（buildParseTree）
3. 执行优化遍（常量折叠、类型推断、函数内联）
4. 生成C代码到 hello.build/ 目录
5. 调用C编译器（MSVC/gcc/clang）编译链接
6. 输出 hello.exe
```

由于没有指定`--standalone`，生成的`hello.exe`是**依赖Python环境**的——运行时需要系统安装相同版本的Python和Python DLL。

## 5. 常用选项组合

### 查看编译详情

```bash
nuitka --verbose --show-scons --show-progress hello.py
```

- `--verbose`：输出详细的编译过程信息
- `--show-scons`：显示C编译器的完整命令行
- `--show-progress`：显示编译进度百分比

### 指定输出目录和文件名

```bash
nuitka --output-dir=build --output-filename=greeting hello.py
```

产物将位于 `build/greeting.exe`。

### 生成仅C代码（不编译）

```bash
nuitka --generate-c-only hello.py
```

生成C代码到 `hello.build/` 目录，但不调用C编译器。适合学习Nuitka生成的C代码长什么样。

### 只重新编译C代码

```bash
nuitka --recompile-c-only hello.py
```

如果只修改了C代码（如手动patch），跳过Python→C生成阶段，直接重新编译C。

### 调试模式编译

```bash
nuitka --debug hello.py
```

- 无优化（-O0）
- 包含调试符号（-g）
- 启用运行时断言检查
- 适合调试Nuitka编译器本身或排查崩溃

## 6. 性能对比

编译后的程序 vs CPython解释执行：

```bash
# CPython解释执行
time python hello.py

# Nuitka编译后执行
time ./hello.exe
```

对于fib(20)这种计算密集型递归函数，Nuitka编译版本通常快2-5倍。对于I/O密集型程序，性能提升较小（因为I/O本身是瓶颈）。

## 7. 常见问题

### Q: 编译报错"找不到C编译器"

Windows上需要安装Visual Studio Build Tools或MinGW64。Nuitka会自动检测并提示安装：
```
Nuitka will automatically download MinGW64 if no MSVC is found.
```

### Q: hello.exe运行时提示"找不到python311.dll"

这是正常的——基本编译模式不包含Python DLL。需要：
1. 将python311.dll所在目录加入PATH，或
2. 使用`--standalone`模式

### Q: 编译很慢

- 首次编译需要编译static_src（100+个C文件），约1-3分钟
- 后续编译使用ccache缓存会快很多
- 可使用`-j N`增加并行编译数
- 使用`--no-pgo`跳过PGO分析

## 下一步

- 学习 [独立可执行文件构建](standalone-build.md) 来生成不依赖Python环境的可执行文件
- 学习 [单文件打包](onefile-build.md) 来生成单个EXE文件
- 查看 [命令行选项](../concepts/13-cli-options.md) 了解更多选项

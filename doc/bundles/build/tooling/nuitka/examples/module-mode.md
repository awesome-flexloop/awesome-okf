---
okf_version: "0.2"
type: Example
title: "编译为扩展模块"
description: "使用--module模式将Python代码编译为C扩展模块（.pyd/.so），可被其他Python脚本import使用"
tags: ["nuitka", "module", "extension", "pyd", "so", "import"]
difficulty: intermediate
time_to_complete: "5分钟"
prerequisites:
  - "basic-compilation.md"
related_concepts:
  - "../concepts/01-compilation-pipeline.md"
  - "../concepts/08-c-code-generation.md"
verified: true
status: active
---

# 示例：编译为扩展模块

`--module`模式将Python代码编译为Python C扩展模块（Windows下`.pyd`，Linux/macOS下`.so`），可以被其他Python脚本用`import`语句导入使用，就像普通Python模块一样，但运行速度更快。

## 1. 什么时候用Module模式

| 场景 | 推荐模式 |
|------|---------|
| 发布独立应用 | `--standalone`/`--onefile` |
| 加速Python库的核心计算函数 | `--module` |
| 保护Python源码（分发二进制扩展） | `--module` |
| 替换项目中性能瓶颈模块 | `--module` |
| 创建可pip安装的C扩展包 | `--module` + setuptools |

Module模式编译的扩展模块：
- ✅ 可以被CPython正常import
- ✅ 性能比纯Python快（计算密集型函数2-5倍）
- ✅ 不需要修改调用方代码
- ❌ 不能独立运行（需要Python解释器）
- ❌ 不包含Python运行时（使用宿主Python的运行时）

## 2. 基本Module编译

创建一个数学工具模块 `mymath.py`：

```python
# mymath.py
"""高性能数学工具模块 - 将被Nuitka编译为C扩展"""

def fibonacci(n):
    """计算第n个斐波那契数"""
    if n <= 1:
        return n
    a, b = 0, 1
    for _ in range(n - 1):
        a, b = b, a + b
    return b

def prime_sieve(limit):
    """埃拉托斯特尼筛法 - 找出所有小于limit的素数"""
    sieve = bytearray([1]) * (limit + 1)
    sieve[0] = sieve[1] = 0
    for i in range(2, int(limit ** 0.5) + 1):
        if sieve[i]:
            sieve[i*i : limit+1 : i] = bytearray(len(range(i*i, limit+1, i)))
    return [i for i in range(2, limit + 1) if sieve[i]]

def matrix_multiply(a, b):
    """矩阵乘法"""
    rows_a, cols_a = len(a), len(a[0])
    rows_b, cols_b = len(b), len(b[0])
    if cols_a != rows_b:
        raise ValueError("Matrix dimensions incompatible")
    result = [[0.0] * cols_b for _ in range(rows_a)]
    for i in range(rows_a):
        for j in range(cols_b):
            for k in range(cols_a):
                result[i][j] += a[i][k] * b[k][j]
    return result
```

编译命令：

```bash
nuitka --module mymath.py
```

### 编译产物

| 文件 | 说明 |
|------|------|
| `mymath.pyd`（Windows）/ `mymath.cpython-311-x86_64-linux-gnu.so`（Linux） | 编译后的C扩展模块 |
| `mymath.build/` | 构建目录（可删除） |

注意：Linux/macOS下的文件名包含Python版本和架构信息（如`cpython-311-x86_64-linux-gnu`），这是Python C扩展的命名规范。

## 3. 使用编译后的模块

创建一个调用脚本 `use_mymath.py`：

```python
# use_mymath.py
import mymath
import time

# 测试fibonacci
start = time.time()
result = mymath.fibonacci(100000)
elapsed = time.time() - start
print(f"fibonacci(100000) = {result}")
print(f"耗时: {elapsed*1000:.2f}ms")

# 测试素数筛
start = time.time()
primes = mymath.prime_sieve(1000000)
elapsed = time.time() - start
print(f"\n100万以内素数个数: {len(primes)}")
print(f"耗时: {elapsed*1000:.2f}ms")
print(f"前10个素数: {primes[:10]}")

# 测试矩阵乘法
import random
size = 100
a = [[random.random() for _ in range(size)] for _ in range(size)]
b = [[random.random() for _ in range(size)] for _ in range(size)]
start = time.time()
c = mymath.matrix_multiply(a, b)
elapsed = time.time() - start
print(f"\n{size}x{size}矩阵乘法耗时: {elapsed*1000:.2f}ms")
```

运行：

```bash
python use_mymath.py
```

性能对比（fibonacci(100000)）：
- 纯Python：约15-25ms
- Nuitka编译模块：约5-10ms（2-3x加速）

## 4. 编译整个包

对于多文件Python包：

```
mypackage/
├── __init__.py
├── core.py
├── utils.py
└── advanced.py
```

编译整个包：

```bash
nuitka --module mypackage/
```

Nuitka会：
1. 识别包目录结构
2. 编译包中的所有.py模块
3. 生成包含所有模块的单个扩展文件
4. 保持包的import结构不变

使用：
```python
import mypackage
from mypackage.core import my_function
```

## 5. 常用Module选项

### 指定输出文件名

```bash
nuitka --module --output-filename=mymath_accel mymath.py
```

### 包含包数据

```bash
nuitka --module \
       --include-package-data=mypackage \
       mypackage/
```

### 启用LTO优化

```bash
nuitka --module --lto=yes mymath.py
```

### 调试版本

```bash
nuitka --module --debug mymath.py
```

生成带调试符号的扩展，可用gdb/Visual Studio调试。

## 6. 与setuptools集成

可以在setup.py中使用Nuitka编译扩展：

```python
# setup.py
from setuptools import setup
from setuptools.command.build_ext import build_ext
import subprocess
import sys
import os

class NuitkaBuildExt(build_ext):
    def build_extension(self, ext):
        # 获取源文件和输出路径
        source = ext.sources[0]
        output = self.get_ext_fullpath(ext.name)
        output_dir = os.path.dirname(output)
        
        # 调用nuitka编译
        cmd = [
            sys.executable, "-m", "nuitka",
            "--module",
            "--output-dir", output_dir,
            "--output-filename", os.path.basename(output),
            source
        ]
        subprocess.check_call(cmd)

setup(
    name="mymath",
    version="1.0",
    ext_modules=[
        Extension("mymath", ["mymath.py"]),
    ],
    cmdclass={"build_ext": NuitkaBuildExt},
)
```

安装：
```bash
pip install .
```

## 7. Module模式的限制

1. **与Python版本绑定**：编译的.pyd/.so只能在编译它的Python版本上使用（如Python 3.11编译的不能在3.12上用）
2. **与架构绑定**：64位编译的不能在32位Python上使用
3. **不支持pickle某些自定义类**：Nuitka编译的类名/模块名可能与纯Python略有不同
4. **源码中`__file__`指向.pyd路径**：如果代码依赖.py文件路径，需要注意
5. **inspect模块限制**：`inspect.getsource()`无法获取编译后函数的源码
6. **不能热重载**：修改代码后需要重新编译

## 8. 性能优化建议

要获得最佳Module模式性能：

1. **将热点代码放在小函数中**：Nuitka的函数内联和类型特化在小函数上效果最好
2. **避免在热路径中使用动态类型**：在计算密集型函数中尽量保持变量类型稳定
3. **使用局部变量**：局部变量访问比全局变量快得多
4. **使用for循环而非map/filter**：Nuitka对for循环优化更好
5. **启用--lto**：链接时优化可额外提升10-20%性能
6. **使用整数运算**：整数运算的优化路径最成熟

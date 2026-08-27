---
type: Example
title: 使用 C++ 内核交互式编程
description: 配置 xeus-cpp 内核，在 JupyterLite 中进行交互式 C++ 编程和算法演示
tags: [cpp, xeus-cpp, interactive-cpp, algorithms, cling]
generated: { by: "agent:source-code-to-okf-wiki", at: "2026-08-22T20:05:00+08:00" }
status: stable
stale_after: 2027-08-22
sources:
  - id: readme
    resource: /references/readme-source.md
    title: README 使用说明信源
---

## 目标

在 JupyterLite 中配置 C++ 交互式内核（xeus-cpp），支持即时编译和运行 C++ 代码。

## 步骤1：配置 environment.yml

编辑 `environment.yml`：

```yaml
name: xeus-kernel
channels:
  - https://repo.prefix.dev/emscripten-forge-dev
  - https://repo.prefix.dev/conda-forge
dependencies:
  - xeus-cpp
```

也可以与 Python 内核共存：

```yaml
name: xeus-kernel
channels:
  - https://repo.prefix.dev/emscripten-forge-dev
  - https://repo.prefix.dev/conda-forge
dependencies:
  - xeus-python
  - xeus-cpp
  - numpy
```

## 步骤2：提交并等待构建

1. Commit changes 到 main 分支
2. 等待 GitHub Actions 构建完成
3. 刷新站点

## 步骤3：创建 C++ Notebook

1. **File** → **New** → **Notebook**
2. 内核选择 **XCpp**（C++ 内核）
3. 等待内核启动

## 步骤4：测试 C++ 代码

### Hello World

```cpp
#include <iostream>

std::cout << "Hello, JupyterLite C++!" << std::endl;
```

### 变量和算术

```cpp
int a = 10;
int b = 20;
std::cout << "a + b = " << a + b << std::endl;
std::cout << "a * b = " << a * b << std::endl;
```

与传统 C++ 不同，xeus-cpp 中变量在 cell 之间持久化：

```cpp
// 在另一个 cell 中可以使用之前定义的变量
std::cout << "Previous a = " << a << std::endl;
a = 100;
std::cout << "Updated a = " << a << std::endl;
```

### 循环和条件

```cpp
for (int i = 1; i <= 5; i++) {
    std::cout << "Number: " << i << ", Square: " << i * i << std::endl;
}
```

```cpp
int x = 15;
if (x > 10) {
    std::cout << "x is greater than 10" << std::endl;
} else {
    std::cout << "x is not greater than 10" << std::endl;
}
```

### 函数定义

```cpp
int factorial(int n) {
    if (n <= 1) return 1;
    return n * factorial(n - 1);
}

std::cout << "5! = " << factorial(5) << std::endl;
std::cout << "10! = " << factorial(10) << std::endl;
```

### 使用 STL

```cpp
#include <vector>
#include <algorithm>

std::vector<int> numbers = {5, 2, 8, 1, 9, 3, 7, 4, 6, 0};

std::sort(numbers.begin(), numbers.end());

std::cout << "Sorted: ";
for (int n : numbers) {
    std::cout << n << " ";
}
std::cout << std::endl;
```

### 斐波那契数列算法演示

```cpp
#include <iostream>

// 递归方法
int fib_recursive(int n) {
    if (n <= 1) return n;
    return fib_recursive(n - 1) + fib_recursive(n - 2);
}

// 迭代方法（更高效）
int fib_iterative(int n) {
    if (n <= 1) return n;
    int a = 0, b = 1;
    for (int i = 2; i <= n; i++) {
        int temp = a + b;
        a = b;
        b = temp;
    }
    return b;
}

std::cout << "Fibonacci numbers (first 15):" << std::endl;
for (int i = 0; i < 15; i++) {
    std::cout << "fib(" << i << ") = " << fib_iterative(i) << std::endl;
}
```

## xeus-cpp 特性

- **交互式**：无需编写 main 函数，cell 中的代码直接执行
- **持久状态**：变量、函数、类定义在 cell 间保持
- **即时编译**：基于 cling C++ 解释器，代码即时编译执行
- **标准 C++**：支持 C++17 标准特性
- **错误反馈**：编译错误即时显示，附带行号和错误信息
- **自动打印**：变量值可以直接输出（类似 Python 的 REPL 体验）

## 教学场景示例

### 数据结构演示

```cpp
#include <iostream>
#include <map>
#include <string>

std::map<std::string, int> scores;
scores["Alice"] = 95;
scores["Bob"] = 87;
scores["Charlie"] = 92;

// 遍历 map
for (const auto& pair : scores) {
    std::cout << pair.first << ": " << pair.second << std::endl;
}
```

### 面向对象编程

```cpp
class Rectangle {
private:
    double width;
    double height;
public:
    Rectangle(double w, double h) : width(w), height(h) {}
    
    double area() const { return width * height; }
    double perimeter() const { return 2 * (width + height); }
};

Rectangle r(5.0, 3.0);
std::cout << "Area: " << r.area() << std::endl;
std::cout << "Perimeter: " << r.perimeter() << std::endl;
```

## 注意事项

1. **编译速度**：C++ 代码需要即时编译，执行速度比 Python/R 慢一些
2. **包体积**：xeus-cpp 内核体积较大，会增加站点加载时间
3. **STL 可用性**：标准模板库（STL）基本可用，但某些 I/O 和系统调用受 WASM 限制
4. **第三方库**：C++ 第三方库（如 Eigen、Boost）的 WASM 可用性有限
5. **无文件系统访问**：WASM 环境中无法访问传统文件系统，输入输出通过 Jupyter 协议
6. **内存限制**：同样受浏览器内存限制
7. **编译器错误**：C++ 模板错误可能很长，需要一定的 C++ 经验来解读

## 适用场景

- C++ 入门教学（交互式学习，无需配置编译器）
- 算法演示和验证
- 数据结构可视化教学
- C++ STL 用法学习
- 编程面试准备（在浏览器中练习 C++ 算法题）

## 相关概念

- [多语言内核支持](../concepts/07-kernel-options.md) — 所有可用内核
- [运行时环境配置](../concepts/04-runtime-env-config.md) — 环境配置详解
- [Python 科学计算环境](02-numpy-matplotlib.md) — Python 配置
- [R 内核配置](03-r-kernel.md) — R 语言配置

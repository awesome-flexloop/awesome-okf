---
type: example
title: 消费 LLVM SDK
description: 在 CMake 项目与裸命令中正确引用 mlc-llvm-static 的完整做法
tags:
  - mlc-ai
  - llvm
  - cmake
  - example
generated: true
verified: false
status: stable
stale_after: "2027-05-01"
sources:
  - "external/dev/libs/mlc-ai/package/packages/mlc-llvm-static/README.md"
  - "external/dev/libs/mlc-ai/package/packages/mlc-llvm-static/verify/CMakeLists.txt"
---

# 消费 LLVM SDK

## 场景

你有一个 C++ 项目，需要链接 LLVM 做 IR 解析、优化或 JIT，但不想在自己的环境里编译 LLVM。目标：用 pip 安装 SDK，让 CMake 正确定位静态库、头文件与导入目标。

## 安装

```bash
# 只要本机后端
python -m pip install mlc-llvm-static

# 需要全部标准后端（跨目标代码生成）
python -m pip install 'mlc-llvm-static[all]'
```

`[all]` extra 会把 add-on 精确钉到同一版本（`mlc-llvm-static-extra-targets==23.1.1`）。

若你拿到的是两个 `.whl` 文件而不是从索引安装，**两个必须一起显式安装**：

```bash
python -m pip install mlc_llvm_static-23.1.1-py3-none-manylinux_2_28_x86_64.whl \
                     mlc_llvm_static_extra_targets-23.1.1-py3-none-manylinux_2_28_x86_64.whl
```

## 第一步：确认路径

```bash
python -m mlc_llvm_static.config --prefix
python -m mlc_llvm_static.config --cmake-dir
python -m mlc_llvm_static.config --llvm-config
```

Python 侧等价：

```python
import mlc_llvm_static as llvm

print(llvm.get_prefix())
print(llvm.get_cmake_dir())
print(llvm.get_include_dir())
print(llvm.get_library_dir())
print(llvm.get_llvm_config())
print(llvm.metadata()["targets"])
print(llvm.metadata()["profile"])       # native / all
print(llvm.metadata()["archive_count"])
```

`metadata()` 的 `profile` 字段是你判断"当前是否是 all 档"的依据。

## 第二步：CMake 配置

关键是把 `LLVM_DIR` 显式指到 wheel 内的 CMake 目录，并打开静态 zlib：

```bash
cmake -S . -B build \
  -DLLVM_DIR="$(python -m mlc_llvm_static.config --cmake-dir)" \
  -DCMAKE_PREFIX_PATH="$(python -m mlc_llvm_static.config --prefix)" \
  -DZLIB_USE_STATIC_LIBS=ON
```

`LLVM_DIR` 为什么必须显式传？该包 README 的解释：否则系统或 conda 里的 LLVM 可能悄悄提供不同的头文件、库与导出，产生难以定位的版本混用。

`ZLIB_USE_STATIC_LIBS=ON` 也是必须的：SDK 的 CMake 导出会调用 `find_package(ZLIB)`，默认可能找到共享 zlib，导致"链接了静态 LLVM 却依赖动态 zlib"。

### 最小 CMakeLists.txt

```cmake
cmake_minimum_required(VERSION 3.31)
project(my_llvm_consumer LANGUAGES C CXX)

set(ZLIB_USE_STATIC_LIBS ON)
find_package(LLVM CONFIG REQUIRED)

llvm_map_components_to_libnames(LLVM_LIBS
  Core OrcJIT Support native IRReader BitWriter Linker Passes Object DebugInfoDWARF)

add_executable(my_consumer main.cpp)
target_include_directories(my_consumer SYSTEM PRIVATE ${LLVM_INCLUDE_DIRS})
separate_arguments(LLVM_FLAGS NATIVE_COMMAND "${LLVM_DEFINITIONS}")
target_compile_options(my_consumer PRIVATE ${LLVM_FLAGS})
target_compile_features(my_consumer PRIVATE cxx_std_17)
target_link_libraries(my_consumer PRIVATE ${LLVM_LIBS})
```

四个细节：

- `SYSTEM PRIVATE`：把 LLVM 头文件当系统头，避免它们触发你项目的警告。
- `separate_arguments(... NATIVE_COMMAND ...)`：`LLVM_DEFINITIONS` 是空格分隔的字符串，直接传会当成一个参数。
- `cxx_std_17`：该包 README 的示例用 17；SDK 本身按 RTTI/异常关闭构建，你的代码要与之一致。
- `ZLIB_USE_STATIC_LIBS` 要在 `find_package(LLVM)` **之前**设置。

### 最小 main.cpp

```cpp
#include <llvm/ExecutionEngine/Orc/LLJIT.h>
#include <llvm/IR/IRBuilder.h>
#include <llvm/IR/Module.h>
#include <llvm/Support/TargetSelect.h>
#include <llvm/Support/raw_ostream.h>

int main() {
  llvm::InitializeNativeTarget();
  llvm::InitializeNativeTargetAsmPrinter();

  auto jit = llvm::orc::LLJITBuilder().create();
  if (!jit) { llvm::consumeError(jit.takeError()); return 1; }

  auto context = std::make_unique<llvm::LLVMContext>();
  auto module = std::make_unique<llvm::Module>("demo", *context);
  llvm::IRBuilder<> builder(*context);
  auto *fn = llvm::Function::Create(
      llvm::FunctionType::get(builder.getInt32Ty(), false),
      llvm::Function::ExternalLinkage, "answer", *module);
  auto *bb = llvm::BasicBlock::Create(*context, "entry", fn);
  builder.SetInsertPoint(bb);
  builder.CreateRet(builder.getInt32(42));

  module->setDataLayout((*jit)->getDataLayout());
  module->setTargetTriple((*jit)->getTargetTriple());
  if (auto err = (*jit)->addIRModule(llvm::orc::ThreadSafeModule(std::move(module), std::move(context)))) {
    llvm::consumeError(std::move(err));
    return 2;
  }
  auto sym = (*jit)->lookup("answer");
  if (!sym) { llvm::consumeError(sym.takeError()); return 3; }
  llvm::outs() << "answer() = " << sym->toPtr<int (*)()>()() << "\n";
  return 0;
}
```

预期输出 `answer() = 42`。

## 第三步：不用 CMake 的裸链接

若你的构建系统不是 CMake，用 `llvm-config` 兼容前端取旗标：

```bash
LLVM_CONFIG="$(python -m mlc_llvm_static.config --llvm-config)"

$LLVM_CONFIG --quote-paths --link-static --cxxflags
$LLVM_CONFIG --quote-paths --link-static --ldflags
$LLVM_CONFIG --quote-paths --link-static --libfiles Core OrcJIT Support native
$LLVM_CONFIG --quote-paths --link-static --system-libs
```

一条可用的编译命令骨架（顺序敏感）：

```bash
g++ -std=c++17 \
  $($LLVM_CONFIG --quote-paths --link-static --cxxflags) \
  main.cpp \
  $($LLVM_CONFIG --quote-paths --link-static --libfiles Core OrcJIT Support native) \
  $($LLVM_CONFIG --quote-paths --link-static --system-libs) \
  $($LLVM_CONFIG --quote-paths --link-static --ldflags) \
  -o my_consumer
```

顺序规则（`DEPENDENCIES.md` 明确）：

```text
对象文件 → LLVM 归档（依赖顺序）→ zlib/zstd → 平台库（rt/dl/pthread/m）
```

常见错误是"字母序列归档"——普通 ELF 单遍链接下会报未定义符号。

## 与上游工具链集成

该包 README 给出两个具体对接点：

```bash
# TIRx 的命令式发现
export TVM_TIRX_USE_LLVM="$($LLVM_CONFIG --llvm-config) --link-static"

# FFI ORC JIT addon
export LLVM_PREFIX="$(python -m mlc_llvm_static.config --prefix)"
```

Linux 上 ORC 运行时归档位于 `lib/clang/<LLVM-major>/lib/`，与 addon 的发现约定一致。

## 显式选择 profile

```bash
# 装了 [all] 但只想用本机后端
MLC_LLVM_STATIC_PROFILE=native cmake -S . -B build ...

# CMake 变量方式
cmake -S . -B build -DMLC_LLVM_STATIC_PROFILE=native
```

验证当前生效档位：

```bash
$LLVM_CONFIG --targets-built   # native 档只有一个架构
$LLVM_CONFIG --has-rtti        # 本 SDK 恒为 NO
```

## 常见错误与排查

| 症状 | 原因 | 处理 |
|---|---|---|
| `Could not find a package configuration file provided by "LLVM"` | 未传 `LLVM_DIR` | 显式传 `--cmake-dir` 的结果 |
| 链接期大量 `undefined reference to llvm::...` | 库顺序错误或漏组件 | 用 `--libs` 的既有顺序；不要手工重排 |
| 运行期依赖 `libz.so` | 未设 `ZLIB_USE_STATIC_LIBS=ON` | 在 `find_package(LLVM)` 前设置 |
| `dynamic_cast` 编译失败 | SDK 关闭 RTTI | 不要在 LLVM 类上使用 RTTI |
| `--link-shared` 报错 | SDK 只有静态库 | 去掉该参数 |
| 装了 add-on 但仍只有本机后端 | 显式设了 `native` 或宏 `MLC_LLVM_STATIC_NATIVE_ONLY` | 检查环境变量与编译宏 |
| `llvm-config: executable is not executable` | wheel 内权限丢失（被解压工具破坏） | 用 `pip install` 而不是手工解压 |

## 自己的项目该怎么验证

借仓库里的探针思路做三条断言：

```bash
# 1) 不依赖动态 LLVM
ldd ./my_consumer | grep -Ei 'llvm|zstd|libz\.' && echo "FAIL: 动态依赖" || echo "OK"

# 2) 只导出自己的符号（若产物是共享库）
nm -D --defined-only ./libmy.so | grep -i llvm && echo "FAIL: 泄漏" || echo "OK"

# 3) ABI 不超 manylinux 上限（若目标平台是 Linux）
readelf --version-info ./my_consumer | grep -Eo 'GLIBC_[0-9.]+' | sort -V | tail -1
```

第 3 条对分发的 wheel 尤其重要：超过 `GLIBC_2.28` 就不能标 `manylinux_2_28`。

## 版本升级注意

```bash
python -m pip install -U 'mlc-llvm-static[all]==23.1.2'
```

两个包会一起升级（`==` 钉扎）。升级后务必重跑上面的三条断言——LLVM 大版本变更时，`--system-libs` 的集合可能变化。

## 延伸阅读

- 前端所有可用查询：[llvm-config 兼容前端](../concepts/08-llvm-config-frontend.md)
- profile 语义：[profile 选择与派发](../concepts/07-profile-selection.md)
- 验证体系全貌：[验证体系](../concepts/14-verification-strategy.md)

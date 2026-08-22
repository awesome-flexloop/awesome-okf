---
type: concept
title: "策略系统 (Policy System)"
description: "CMake 的策略版本控制机制：如何通过 CMPxxxx 策略号管理行为变更的向后兼容性，cmake_policy 的 PUSH/POP 堆栈"
sources:
  references: [../references/cmmakefile.md, ../references/cmstate.md]
  facts: [F-090, F-030]
---

# 策略系统 (Policy System)

## 核心理解

CMake 随着版本迭代会改变某些行为，但为了**不破坏现有构建脚本**，引入了**策略（Policy）**机制。每个行为变更被赋予一个策略号 `CMPxxxx`，项目可以显式声明使用新行为（NEW）或旧行为（OLD）。

策略系统的设计哲学：
- **默认告警**：当使用旧行为时输出警告（Developer Warning），提示维护者更新
- **显式选择**：`cmake_policy()` 显式设置策略，消除警告
- **最小版本设置基线**：`cmake_minimum_required(VERSION 3.20)` 隐式将该版本引入的所有策略设为 NEW
- **作用域控制**：策略设置可以 PUSH/POP，不影响外层

## 策略号命名

每个策略格式为 `CMP<4位数字>`，按引入顺序编号：

| 策略 | 引入版本 | 行为变更 |
|------|---------|---------|
| CMP0000 | CMake 2.6 | 必须指定 cmake_minimum_required |
| CMP0048 | CMake 3.0 | `project()` 命令管理 VERSION 变量 |
| CMP0076 | CMake 3.13 | `target_sources()` 转换相对路径为绝对路径 |
| CMP0116 | CMake 3.20 | Ninja 依赖文件使用 `dyndep` |
| ... | ... | ... |
| CMP0170+ | 最新版本 | ... |

数字越小引入越早，截至 CMake 3.30+ 已有超过 170 个策略。

## 设置策略

### 方式 1：cmake_minimum_required（最常用）

```cmake
cmake_minimum_required(VERSION 3.20)
project(MyProject)
```

这会将 CMake 3.20 及之前引入的所有策略隐式设为 NEW，3.20 之后引入的策略默认告警。

### 方式 2：cmake_policy(SET ...)

```cmake
# 使用新行为
cmake_policy(SET CMP0076 NEW)

# 使用旧行为（不推荐，但有时需要兼容）
cmake_policy(SET CMP0076 OLD)
```

### 方式 3：cmake_policy(VERSION ...)

```cmake
# 等价于 cmake_minimum_required 设置版本的效果
cmake_policy(VERSION 3.20)
```

### 方式 4：-Wno-dev 关闭策略警告

```bash
cmake -S . -B build -Wno-dev
```

用于第三方项目，不想看到策略警告。

## 策略作用域与堆栈

策略设置通过**堆栈**管理，支持 `PUSH`/`POP`：

```cmake
cmake_policy(PUSH)                      # 保存当前策略状态
cmake_policy(SET CMP0116 OLD)           # 设置为旧行为
# ... 执行需要旧行为的代码 ...
add_subdirectory(third_party/old_lib)
cmake_policy(POP)                       # 恢复之前的策略状态
```

典型场景：包含第三方子目录，该子目录还没有更新以适配新策略。

```cmake
# 包含旧的第三方代码，避免其策略警告影响主项目
function(include_thirdparty dir)
  cmake_policy(PUSH)
  cmake_policy(SET CMP0076 OLD)  # 这个第三方库需要旧行为
  add_subdirectory(${dir})
  cmake_policy(POP)
endfunction()
include_thirdparty(third_party/libfoo)
```

## 策略与快照机制

策略作用域在 cmState 中通过 `SnapshotType::PolicyScope` 快照实现：

```
Base snapshot
└── PolicyScope PUSH (CMP0076=OLD)
    └── FunctionCall snapshot
        └── PolicyScope POP (恢复)
```

`cmake_policy(PUSH)` 创建新 PolicyScope 快照，`cmake_policy(POP)` 回退到上一个快照位置。

## if(POLICY)：检查策略是否存在

```cmake
if(POLICY CMP0116)
  cmake_policy(SET CMP0116 NEW)
endif()
```

用于兼容多个 CMake 版本——旧版本 CMake 没有 CMP0116 策略，需要先检查再设置。

## 常见策略场景

### CMP0048：project() 版本管理

```cmake
# OLD 行为（CMake 2.6）：
# project() 不设置 PROJECT_VERSION，需手动 set(PROJECT_VERSION ...)
# 变量 VERSION 会被设为项目版本号（污染全局）

# NEW 行为（CMake 3.0+）：
project(MyProject VERSION 1.2.3)
# 自动设置：
#   PROJECT_VERSION = 1.2.3
#   PROJECT_VERSION_MAJOR = 1
#   PROJECT_VERSION_MINOR = 2
#   PROJECT_VERSION_PATCH = 3
```

### CMP0077：option() 覆盖缓存变量

```cmake
# OLD 行为：set(CACHE) 不覆盖普通 option
# NEW 行为：option() 尊重已存在的缓存变量（允许通过 -D 覆盖默认值）
option(BUILD_TESTS "Build tests" ON)
# 如果 -DBUILD_TESTS=OFF，NEW 行为会使用 OFF
```

### CMP0116：Ninja dyndep

```cmake
# OLD 行为：Ninja 使用 DEPFILE 处理 Fortran/CMake 依赖
# NEW 行为：Ninja 使用 dyndep 动态依赖，更可靠
```

## 策略最佳实践

1. **始终设置 cmake_minimum_required**：这是最基本的要求，未设置会触发 CMP0000 错误
2. **使用合理的最低版本**：不要设置过低导致大量策略告警，也不要过高排除旧环境
3. **使用 PUSH/POP 隔离第三方代码**：不要为了消除警告而全局设置 OLD
4. **优先使用 NEW 行为**：OLD 行为可能在未来版本被移除
5. **定期更新 cmake_minimum_required**：提升最低版本后，策略自动设为 NEW
6. **不要对未知策略号 cmake_policy(SET)**：先用 `if(POLICY CMPxxxx)` 检查

## 关联概念

- [状态快照机制](state-snapshot.md) — PolicyScope 是快照类型之一
- [变量作用域链](variable-scope.md) — 策略作用域与变量作用域共享快照机制
- [配置-生成两阶段](configure-generate.md) — 策略在 Configure 阶段检查和应用

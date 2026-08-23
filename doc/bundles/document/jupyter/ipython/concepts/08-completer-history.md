---
type: concept
title: "08 - 补全、历史与别名"
description: IPython Tab 补全（IPCompleter/Jedi/字典键）、历史管理（SQLite/HistorySavingThread）、别名系统（AliasManager/默认别名）
tags: [completer, history, alias, jedi, sqlite, tab-completion]
generated: { by: "agent:source-code-to-okf-wiki", at: "2026-08-22T00:00:00+08:00" }
verified: { by: "process:seven-concepts-v", at: "2026-08-22T00:00:00+08:00" }
status: stable
stale_after: "2027-08-22"
sources:
  - id: ipython-history
    title: IPython/core/history.py
  - id: ipython-completer
    title: IPython/core/completer.py
  - id: ipython-alias
    title: IPython/core/alias.py
---

## IPCompleter Tab 补全系统

`IPCompleter` 是 IPython 的 Tab 补全引擎，继承自 `Completer` 基类 [F-440][F-441]，提供多种补全能力。补全系统基于 MatcherAPIv2 协议 [F-447]，支持可插拔的匹配器架构。

### 类层次

```
Completer (Configurable) [F-441]
└── IPCompleter [F-440]
    ├── Jedi 补全（语义级智能补全）
    ├── 字典键补全（dict key completion）
    ├── 文件路径补全
    ├── 魔法命令补全
    ├── 模块属性补全
    └── MatcherAPIv2 匹配器扩展
```

### 核心数据类型

```python
@dataclass
class Completion:
    """单个补全项 [F-442]"""
    start: int          # 补全起始位置
    end: int            # 补全结束位置
    text: str           # 补全文本
    type: str | None = None  # 类型（'function'、'module'、'keyword' 等）
    signature: str | None = None  # 函数签名

class CompletionContext:
    """补全上下文 [F-444]"""
    # 包含当前行、光标位置、完整代码、光标行号等信息

class SimpleCompletion:
    """简单补全结果 [F-443]"""
    text: str
    type: str = ""

class SimpleMatcherResult:
    """匹配器返回结果 [F-443]"""
    completions: list[SimpleCompletion]
```

### Jedi 智能补全

IPython 集成了 Jedi 库提供语义级补全 [F-446]：
- 分析 Python AST 推断变量类型
- 跨模块属性和方法补全
- 函数签名提示
- 类型推断（在类型注解可用时）

### 字典键补全

IPython 支持字典键的 Tab 补全 [F-446]：

```python
data = {"name": "IPython", "version": "9.0"}

# 输入 data["n<Tab> 会补全为 data["name"]
data["n  # <Tab> → data["name"]
```

字典键补全通过 `_DictKeyState` Flag 跟踪状态，支持字符串键和数字键。

### CompletionSplitter

`CompletionSplitter` 负责分割补全文本 [F-445]，确定哪些字符构成补全边界（如 `.`、`(`、`[`、`"`、`'` 等），以便正确提取需要补全的标识符。

### MatcherAPIv2 协议

MatcherAPIv2 是 IPython 8.0+ 引入的补全匹配器协议 [F-447]，允许第三方扩展注册自定义补全匹配器：

```python
def my_matcher(context: CompletionContext) -> SimpleMatcherResult:
    """自定义补全匹配器"""
    # 分析 context，返回匹配的补全列表
    return SimpleMatcherResult(
        completions=[SimpleCompletion(text="my_completion", type="keyword")]
    )

ip = get_ipython()
ip.Completer.custom_matchers.append(my_matcher)
```

### 补全触发场景

Tab 键在以下场景触发补全：

1. **标识符补全**：变量名、函数名、模块属性
2. **点号后补全**：`obj.` 后补全属性和方法
3. **导入补全**：`import x` 或 `from x import y` 时的模块名
4. **文件路径补全**：字符串中作为路径时补全文件名
5. **魔法命令补全**：`%` 后补全魔法名
6. **字典键补全**：`dict["k` 后补全键名
7. **%run 补全**：`%run` 后补全脚本文件名
8. **cd 补全**：`%cd` 后补全目录名

## HistoryManager 历史记录管理

`HistoryManager` 提供跨会话持久化的命令历史 [F-422]，使用 SQLite 数据库存储。

### 类层次

```
HistoryAccessorBase (LoggingConfigurable) [F-420]
├── 提供历史读取接口
└── HistoryAccessor [F-421]
    ├── 历史搜索和检索
    └── HistoryManager [F-422]
        ├── 完整历史写入和管理
        └── 包含 HistorySavingThread [F-424]
```

### SQLite 存储

历史数据存储在 IPython profile 目录下的 `history.sqlite` 文件中 [F-423]，包含以下表：
- **sessions**：会话记录（开始时间、结束时间、命令数等）
- **history**：输入历史（session、line、source）
- **output_history**：输出历史（session、line、output）

数据库结构设计为高效追加写入，支持跨会话查询。

### HistorySavingThread 异步保存

`HistorySavingThread` 是后台线程，负责将历史异步写入 SQLite [F-424]：

- 主线程将历史条目放入队列
- 后台线程批量写入数据库
- 避免阻塞 REPL 主循环
- atexit 时确保最终刷新

> **注意**：突然终止进程（如 `kill -9`）可能导致最后几条历史丢失，因为异步线程来不及刷新。

### 历史访问 API

```python
ip = get_ipython()
hist = ip.history_manager

# 获取输入历史
hist.get_tail(n=10)           # 最近 n 条输入
hist.search("import*")        # 搜索匹配模式的历史
hist.search("*plot*", n=20)   # 搜索最近 20 条匹配

# 获取带输出的历史
for session, line, inp, out in hist.get_tail(n=10, include_output=True):
    print(f"[{line}] {inp}")
    if out:
        print(f"     → {out}")

# In/Out 变量（内置）
In[1]     # 第 1 条输入
Out[1]    # 第 1 条输出
_         # 上一个输出
__        # 倒数第二个输出
___       # 倒数第三个输出
_ih[i]    # 输入历史列表
_oh[i]    # 输出历史字典
```

### 历史魔法命令

通过 HistoryMagics 提供历史相关魔法：

| 魔法 | 说明 |
|------|------|
| `%history`/`%hist` | 查看历史记录，支持 `-n`（行号）、`-o`（输出）、`-p`（提示符）、`-g`（跨会话）、`-f`（写入文件）等选项 |
| `%recall`/`%rep` | 将历史条目加载到输入行以便编辑 |
| `%rerun` | 重新执行历史条目 |

```python
# 查看最近 20 条历史
%history -n 20

# 搜索含 "import" 的历史
%history -g import*

# 将历史保存到文件
%history -f session_log.py 1-100

# 重新执行第 5 条
%rerun 5

# 将第 10 条调到当前输入行
%recall 10
```

### DummyDB

`DummyDB` 是空实现，在历史功能禁用时使用 [F-426]，避免 None 检查。

## AliasManager 别名系统

`AliasManager` 管理系统命令别名，允许为常用 shell 命令定义简写 [F-471]。

### 核心类

```python
class Alias:
    """单个系统命令别名 [F-470]"""
    name: str           # 别名名称
    cmd: str            # 展开后的命令
    
class AliasManager(Configurable):
    """别名管理器 [F-471]"""
    aliases: dict       # 别名字典
    
    def define_alias(self, name, cmd):
        """定义新别名"""
    def call_alias(self, alias_name, rest):
        """执行别名命令"""
    def expand_alias(self, line):
        """展开行首别名"""
```

### 默认别名

IPython 在 POSIX 系统上预定义了类 Unix 命令别名 [F-473]：

| 别名 | 命令 | 说明 |
|------|------|------|
| `cat` | `cat` | 查看文件内容 |
| `cp` | `cp` | 复制文件 |
| `mv` | `mv` | 移动/重命名文件 |
| `rm` | `rm` | 删除文件 |
| `mkdir` | `mkdir` | 创建目录 |
| `rmdir` | `rmdir` | 删除目录 |
| `less` | `less` / `more` | 分页查看 |
| `clear` | `clear` | 清屏 |

在 Windows 系统上，默认别名会适配为 Windows 命令（如 `dir`、`copy` 等）。

### 定义和使用别名

```python
# 通过魔法定义
%alias ll ls -la
%alias gs git status

# 或使用 AliasManager API
ip = get_ipython()
ip.alias_manager.define_alias("ll", "ls -la")

# 使用别名（! 前缀或 automagic）
ll /home
!ll /home

# 删除别名
%unalias ll

# 查看所有别名
%alias
```

### 别名展开机制

别名在 PrefilterManager 阶段展开 [F-461]：当行首单词匹配已定义的别名时，替换为完整命令。别名参数（行首命令后的内容）被追加到展开后的命令。

```python
# 输入:
ll -la /tmp

# 别名展开后:
!ls -la /tmp
```

### 别名异常

| 异常类 | 用途 | 事实 |
|--------|------|------|
| `AliasError` | 别名相关错误基类 | [F-472] |
| `InvalidAliasError` | 无效别名定义 | [F-472] |

## 三者协作关系

补全、历史和别名虽然是独立子系统，但在用户体验层面紧密协作：

```
用户输入
  │
  ├── Tab 键 → IPCompleter
  │     ├── 补全魔法名（从 MagicsManager 查询）
  │     ├── 补全文件名（从文件系统）
  │     ├── 补全历史（从 HistoryManager 查询）
  │     └── 补全别名（从 AliasManager 查询）
  │
  ├── Enter 键 → 执行管线
  │     ├── PrefilterManager 展开别名（AliasManager）
  │     ├── 执行代码
  │     └── 保存历史（HistoryManager，异步线程）
  │
  └── 上/下箭头 → 历史导航
        └── 从 HistoryManager 获取前/后一条输入
```

## 相关概念

- [输入转换与特殊语法](/concepts/07-input-transform.md)
- [魔法命令系统](/concepts/04-magic-system.md)
- [代码执行管线](/concepts/05-execution-pipeline.md)
- [信源参考 - 历史/补全/别名](/references/history-completer-source.md)

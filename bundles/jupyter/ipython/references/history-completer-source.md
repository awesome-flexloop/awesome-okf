---
type: Reference
title: History, Completer & Alias API 参考
description: IPython 历史管理、Tab 补全和系统别名完整 API 参考，包括 HistoryManager 会话与 SQLite 存储、HistorySavingThread 后台线程、Completer/IPCompleter 补全引擎、Completion/CompletionContext 数据结构，以及 AliasManager 别名管理
tags: [api, history, completer, alias, completion, sqlite, reference, core]
generated: { by: "agent:source-code-to-okf-wiki", at: "2026-08-22T00:00:00+08:00" }
verified: { by: "process:seven-concepts-v", at: "2026-08-22T00:00:00+08:00" }
status: stable
stale_after: 2027-08-22
sources:
  - id: ipython-history
    resource: /references/history-completer-source.md
    title: IPython/core/history.py HistoryManager & HistorySavingThread
  - id: ipython-completer
    resource: /references/history-completer-source.md
    title: IPython/core/completer.py Completer & IPCompleter
  - id: ipython-alias
    resource: /references/history-completer-source.md
    title: IPython/core/alias.py AliasManager & Alias
---

# History, Completer & Alias API 参考

IPython 提供三大用户体验核心组件：HistoryManager（SQLite 历史存储）、Completer/IPCompleter（Tab 补全引擎）和 AliasManager（系统命令别名）。

---

## HistoryManager

### 类定义

```python
class HistoryManager(HistoryAccessor):
    """组织所有历史相关功能的类

    继承自 HistoryAccessor（只读访问），增加写入和会话管理能力。
    使用 SQLite 数据库持久化存储，支持后台线程异步写入。
    """
```

定义在 `IPython/core/history.py`。

### 继承关系

```
LoggingConfigurable
    └── HistoryAccessorBase (抽象接口)
            └── HistoryAccessor (只读 SQLite 访问)
                    └── HistoryManager (读写 + 会话管理)
```

### 核心属性

| 属性 | 类型 | 说明 |
|------|------|------|
| `shell` | InteractiveShell | 关联的 Shell 实例 |
| `hist_file` | Path/Unicode | SQLite 历史文件路径（`:memory:` 使用内存数据库） |
| `enabled` | Bool | 是否启用 SQLite 历史（默认依赖 sqlite3 可用性） |
| `db` | sqlite3.Connection / DummyDB | 数据库连接 |
| `session_number` | int | 当前会话编号 |
| `input_hist_parsed` | list[str] | 解析后的输入历史（从索引 1 开始，索引 0 为空） |
| `input_hist_raw` | list[str] | 原始输入历史（未转换） |
| `output_hist` | dict | 输出历史（按执行计数索引） |
| `output_hist_reprs` | dict[int, str] | 输出的 text/plain 表示 |
| `outputs` | dict[int, list[HistoryOutput]] | MIME bundle 输出历史 |
| `exceptions` | dict[int, dict] | 异常 traceback 历史 |
| `dir_hist` | list[Path] | 工作目录访问历史 |
| `db_log_output` | Bool | 是否将输出写入数据库（默认 False） |
| `db_cache_size` | Integer | 每 N 条命令写一次数据库（默认 0，即禁用缓存） |
| `save_thread` | HistorySavingThread | 后台保存线程 |

### 数据库表结构

```sql
-- 会话表
CREATE TABLE sessions (
    session INTEGER PRIMARY KEY AUTOINCREMENT,
    start TIMESTAMP,
    end TIMESTAMP,
    num_cmds INTEGER,
    remark TEXT
);

-- 输入历史表
CREATE TABLE history (
    session INTEGER,
    line INTEGER,
    source TEXT,         -- 转换后的 Python 代码
    source_raw TEXT,     -- 原始用户输入
    PRIMARY KEY (session, line)
);

-- 输出历史表
CREATE TABLE output_history (
    session INTEGER,
    line INTEGER,
    output TEXT,
    PRIMARY KEY (session, line)
);
```

### 构造函数

```python
def __init__(self, shell, config=None, **traits):
    """创建关联到 Shell 实例的历史管理器

    1. 初始化输入/输出缓存列表
    2. 创建新数据库会话 (new_session)
    3. 启动后台保存线程 HistorySavingThread
    """
```

### 核心方法

#### 会话管理

```python
def new_session(self, conn=None) -> None:
    """创建新会话，插入 sessions 表并设置 session_number"""

def end_session(self) -> None:
    """结束当前会话，写入结束时间和命令数，更新 sessions 表"""

def reset(self, new_session=True) -> None:
    """清除当前会话历史（输出、异常、目录历史），可选开启新会话"""

def get_session_info(self, session=0):
    """获取会话信息

    Parameters
    ----------
    session : int — 会话号（0=当前，-1=上一个）

    Returns
    -------
    (session_id, start, end, num_cmds, remark)
    """
```

#### 输入/输出存储

```python
def store_inputs(self, line_num, source, source_raw=None) -> None:
    """存储输入到历史缓存

    Parameters
    ----------
    line_num : int — 提示符编号
    source : str — 转换后的 Python 代码
    source_raw : str — 原始输入（默认与 source 相同）

    行为:
    - 自动跳过 exit/quit 命令（不存储）
    - 更新 _i, _ii, _iii 变量和 In 列表
    - 追加到 db_input_cache
    """

def store_output(self, line_num) -> None:
    """将输出追加到数据库缓存（需 db_log_output=True）"""
```

#### 历史查询

```python
def get_tail(self, n=10, raw=True, output=False, include_latest=False):
    """获取最近 n 条历史记录

    Returns
    -------
    Iterable[(session, line, source)] 或 [(session, line, (source, output))]
    当前会话优先，按时间倒序排列
    """

def search(self, pattern="*", raw=True, search_raw=True,
           output=False, n=None, unique=False):
    """搜索历史记录

    Parameters
    ----------
    pattern : str — glob 模式（支持 * ?）
    search_raw : bool — 搜索原始输入还是转换后代码
    n : int — 限制返回条数
    unique : bool — 去重
    """

def get_range(self, session, start=1, stop=None, raw=True, output=False):
    """获取指定范围的历史记录

    Parameters
    ----------
    session : int — 会话号
    start/stop : int — 行号范围
    """

def get_range_by_str(self, rangestr, raw=True, output=False):
    """通过字符串格式获取历史范围

    格式示例: ~1/1-10, ~5/3-, ~8/
    ~n/ 表示第 n 个最近会话
    """
```

#### 缓存与关闭

```python
def writeout_cache(self) -> None:
    """强制将缓存写入数据库（与 save_thread 协调）"""

def close(self) -> None:
    """停止保存线程并关闭数据库连接（可安全重复调用）"""
```

### HistoryOutput

```python
@dataclass
class HistoryOutput:
    """单条输出记录"""
    output_type: Literal["out_stream", "err_stream", "display_data", "execute_result"]
    bundle: dict[str, str | list[str]]
```

---

## HistorySavingThread

```python
class HistorySavingThread(threading.Thread):
    """后台线程：异步写入历史到 SQLite，避免阻塞 UI

    daemon=True（随主进程退出）
    通过 save_flag (threading.Event) 触发写入
    """
```

### 核心属性

| 属性 | 说明 |
|------|------|
| `save_flag` | threading.Event，主线程设置此标志触发写入 |
| `_stop_now` | 停止标志 |
| `db` | 线程独立的 SQLite 连接（SQLite 不支持跨线程共享连接） |

### 核心方法

```python
def run(self) -> None:
    """线程主循环：等待 save_flag → 写入缓存 → 清空 flag → 重复"""

def stop(self) -> None:
    """停止线程：设置 _stop_now、设置 save_flag、写入剩余缓存、关闭连接"""
```

> 该线程在 `atexit` 注册 stop，确保退出时数据不丢失。

---

## DummyDB

```python
class DummyDB:
    """SQLite 不可用时的黑洞数据库

    所有 execute/commit/__enter__/__exit__/close 方法均为空操作，
    确保 HistoryManager 在无 sqlite3 环境下不崩溃。
    """
```

---

## Completer

### 类定义

```python
class Completer(Configurable):
    """基础补全器，提供 Python 名称和属性补全

    IPython 使用子类 IPCompleter 扩展此功能。
    """
```

定义在 `IPython/core/completer.py`。

### 核心配置 Traits

| Trait | 类型 | 默认值 | 说明 |
|-------|------|--------|------|
| `evaluation` | Enum | `"limited"` | 代码执行策略: forbidden/minimal/limited/unsafe/dangerous |
| `use_jedi` | Bool | 自动检测 | 是否使用 Jedi 补全 |
| `jedi_compute_type_timeout` | Int | 400 | Jedi 类型计算超时（毫秒） |
| `debug` | Bool | False | 调试模式 |
| `backslash_combining_completions` | Bool | True | 启用 LaTeX/Unicode 反斜杠补全 |
| `auto_close_dict_keys` | Bool | False | 自动闭合字典键引号 |
| `greedy` | Bool | False | 贪婪补全（已废弃，8.8+ 映射到 evaluation+auto_close） |
| `omit__names` | Enum (0/1/2) | 2 | 省略下划线名称（2=所有_，1=仅__dunder__，0=不省略） |
| `merge_completions` | Bool | True | 是否合并多个匹配器结果 |
| `dict_keys_only` | Bool | False | 仅显示字典键补全 |
| `policy_overrides` | Dict | {} | 覆盖 evaluation 策略的特定项 |
| `auto_import_method` | DottedObjectName | `"importlib.import_module"` | 自动导入方法（实验性） |
| `disable_matchers` | List[str] | [] | 禁用的匹配器 ID 列表 |
| `suppress_competing_matchers` | Bool/Dict/None | None | 是否抑制竞争匹配器 |

### evaluation 安全级别

| 级别 | 说明 |
|------|------|
| `forbidden` | 不执行任何代码评估 |
| `minimal` | 仅字面量和内置命名空间，不评估属性/操作 |
| `limited` | 访问所有命名空间，仅对白名单对象（dict/list/tuple/pandas.Series）评估方法 |
| `unsafe` | 评估所有方法和函数调用，但不执行 del 等副作用语法 |
| `dangerous` | 完全任意代码评估 |

### 核心方法

```python
def complete(self, text, state):
    """readline 兼容的补全接口（state=0,1,2... 依次调用直到返回 None）

    有 "." → attr_matches(text)
    无 "." → global_matches(text)
    """

def global_matches(self, text, context=None):
    """简单名称补全：关键字 + 内置函数 + 命名空间中定义的名称"""

def attr_matches(self, text):
    """属性补全：obj.attr 形式的补全"""
```

### CompletionSplitter

```python
class CompletionSplitter:
    """分割补全文本，确定要补全的词

    DELIMS: 默认分隔符（Python 标识符分隔符）
    GREEDY_DELIMS: 贪婪模式分隔符（仅保留空白）
    """
    def split_line(self, line, cursor_pos=None):
        """分割行，返回 (text, split_pos) 用于补全"""
```

---

## IPCompleter

### 类定义

```python
class IPCompleter(Completer):
    """扩展 Completer，增加 IPython 特有功能:
    - 魔法命令补全 (%magic, %%cell_magic)
    - 文件路径补全
    - 字典键补全
    - Unicode/LaTeX 符号补全（\\alpha → α）
    - 匹配器架构（可扩展 matcher 插件）
    """
```

### 构造函数

```python
def __init__(self, shell=None, namespace=None, global_namespace=None,
             config=None, **kwargs):
    """
    Parameters
    ----------
    shell : InteractiveShell — Shell 实例（访问魔法命令）
    namespace : dict — 补全使用的局部命名空间
    global_namespace : dict — 全局命名空间
    """
```

### 核心方法

```python
def complete(self, text=None, line_buffer=None, cursor_pos=None):
    """查找补全（Jupyter 前端使用的主要接口）

    Parameters
    ----------
    text : str — 要补全的文本
    line_buffer : str — 完整行缓冲
    cursor_pos : int — 光标位置

    Returns
    -------
    (text, matches) : (str, Sequence[str])
        text: 实际被补全的文本
        matches: 补全候选项列表
    """
```

### 匹配器系统

IPCompleter 使用可插拔的 matcher 架构：

```python
@completion_matcher(identifier="IPCompleter.*", priority=...)
def matcher(context: CompletionContext) -> SimpleMatcherResult:
    """自定义补全匹配器

    通过 @completion_matcher 装饰器注册
    priority 数字越小优先级越高
    """
```

内置匹配器包括：
- **魔法命令匹配器** — `%magic`、`%%cell_magic` 补全
- **字典键匹配器** — `d['` 后的键补全
- **文件路径匹配器** — 字符串中的路径补全
- **Unicode/LaTeX 匹配器** — `\alpha` → α
- **back_unicode_name_matcher** — Unicode 名称反查
- **Jedi 匹配器** — 基于 Jedi 的语义补全

---

## 补全数据结构

### Completion

```python
class Completion:
    """单个补全项"""
    def __init__(self, start: int, end: int, text: str, *,
                 type: str | None = None, signature: str | None = None,
                 _origin: str = ""):
        """
        start/end : 光标位置中被替换文本的起止
        text : 补全文本
        type : 类型提示（'function', 'module', 'keyword' 等）
        signature : 函数签名（如可用）
        """
```

### SimpleCompletion

```python
class SimpleCompletion:
    """简单补全项（仅文本、类型和签名）"""
```

### CompletionContext

```python
class CompletionContext:
    """补全上下文信息"""
    @property
    def token(self) -> str: ...        # 当前光标下的 token
    @property
    def full_text(self) -> str: ...   # 完整文本
    @property
    def cursor_position(self) -> int: ...  # 光标位置
    @property
    def line(self) -> str: ...        # 当前行
    @property
    def column(self) -> int: ...      # 列号
```

### MatcherResult

```python
class SimpleMatcherResult(TypedDict):
    """匹配器返回结果"""
    completions: list[SimpleCompletion]
    suppress_if_matches: bool  # 匹配到时是否抑制其他匹配器
```

---

## 辅助函数

```python
def has_open_quotes(s: str) -> str | bool:
    """检查字符串是否有未闭合的引号，返回未闭合的引号字符或 False"""

def protect_filename(s: str, protectables=PROTECTABLES) -> str:
    """转义文件名中的特殊字符"""

def expand_user(path: str) -> tuple[str, bool, str]:
    """展开 ~ 为用户主目录，返回 (expanded_path, has_tilde, tilde_value)"""

def compress_user(path, tilde_expand, tilde_val) -> str:
    """压缩路径中的用户主目录为 ~"""

def completions_sorting_key(word):
    """补全排序键函数：先按前缀匹配，再按字母序，_ 开头排后"""

def cursor_to_position(text, line, column) -> int:
    """将 (line, column) 转换为文本偏移量"""

def position_to_cursor(text, offset) -> tuple[int, int]:
    """将文本偏移量转换为 (line, column)"""

def match_dict_keys(keys, prefix, delims, extra_prefix=None):
    """匹配字典键（支持嵌套和部分键）"""

def back_unicode_name_matcher(context) -> SimpleMatcherResult:
    """反斜杠 Unicode 名称补全：\\GREEK SMALL LETTER ALPHA → α"""

def back_latex_name_matcher(context) -> SimpleMatcherResult:
    """LaTeX 命令补全：\\alpha → α"""
```

### provisionalcompleter

```python
@contextmanager
def provisionalcompleter(action='ignore'):
    """上下文管理器：临时启用实验性补全功能

    with provisionalcompleter():
        completer.complete(...)
    """
```

---

## Alias 类

### 类定义

```python
class Alias:
    """单个系统命令别名的可调用对象

    Alias 实例作为 line magic 注册，允许通过别名执行系统命令。
    """
```

定义在 `IPython/core/alias.py`。

### 黑名单

```python
blacklist = {'cd', 'popd', 'pushd', 'dhist', 'alias', 'unalias'}
"""禁止别名化的内置命令名"""
```

### 参数替换

| 占位符 | 说明 |
|--------|------|
| `%s` | 位置参数（每个替换一个参数） |
| `%l` | 替换整个输入行（与 %s 互斥） |
| `%%s` | 转义的 %s（字面量） |

### 构造函数

```python
def __init__(self, shell, name, cmd):
    """
    Parameters
    ----------
    shell : InteractiveShell
    name : str — 别名名称
    cmd : str — 系统命令模板

    验证规则:
    - name 不在 blacklist 中
    - name 不与现有非 Alias 魔法冲突
    - cmd 必须是字符串
    - %s 和 %l 不能同时使用
    """
```

### 核心方法

```python
def validate(self):
    """验证别名，返回参数个数（%s 出现次数 - %%s 次数）"""

def __call__(self, rest=''):
    """执行别名

    1. 替换 %l 为整个 rest
    2. 无参数：直接拼接 rest 到 cmd 后
    3. 有参数：按 %s 位置替换，剩余参数追加
    4. 调用 shell.system(cmd)
    """
```

---

## AliasManager

### 类定义

```python
class AliasManager(Configurable):
    """管理系统命令别名的类

    别名本质上是注册为 line magic 的 Alias 实例。
    """
```

### 核心属性

| 属性 | 类型 | 默认值 | 说明 |
|------|------|--------|------|
| `default_aliases` | List | 平台相关 | 默认别名列表 [(name, cmd), ...] |
| `user_aliases` | List | [] | 用户自定义别名（配置文件中设置） |
| `shell` | InteractiveShell | None | Shell 实例 |

### 默认别名

**POSIX 系统**（含 Linux/macOS/BSD）：

| 类别 | 别名 |
|------|------|
| 文件操作 | `mkdir`, `rmdir`, `mv`, `rm`, `cp`, `cat` |
| ls (Linux) | `ls='ls -F --color'`, `ll='ls -F -o --color'`, `lf`, `lk`, `ldir`, `lx` |
| ls (BSD/macOS) | `ls='ls -F -G'`, `ll='ls -F -l -G'`, 等 |
| ls (OpenBSD/NetBSD) | `ls='ls -F'`, `ll='ls -F -l'`, 等（无颜色） |

**Windows**：`ls='dir /on'`, `ddir`, `ldir`, `mkdir`, `rmdir`, `echo`, `ren`, `copy`

### 核心方法

```python
def init_aliases(self):
    """初始化：加载 default_aliases + user_aliases（通过 soft_define_alias）"""

def define_alias(self, name, cmd):
    """定义新别名（验证后注册为 line magic）

    Raises
    ------
    InvalidAliasError — 名称在黑名单/与魔法冲突/格式错误
    """

def soft_define_alias(self, name, cmd):
    """定义别名但不抛出异常（错误时仅日志记录）"""

def undefine_alias(self, name):
    """删除别名

    Raises
    ------
    ValueError — 名称不是别名
    """

def get_alias(self, name) -> Alias | None:
    """返回 Alias 对象，或 None"""

def is_alias(self, name) -> bool:
    """名称是否已定义为别名"""

def retrieve_alias(self, name) -> str:
    """返回别名展开后的命令字符串"""

def clear_aliases(self):
    """清除所有别名"""
```

### aliases 属性

```python
@property
def aliases(self) -> list[tuple[str, str]]:
    """返回所有当前别名 [(name, cmd), ...]"""
```

### 别名使用示例

```python
ip = get_ipython()

# 定义别名
ip.alias_manager.define_alias('ll', 'ls -la')
# 或通过魔法
# %alias ll ls -la

# 使用（作为魔法命令）
# ll /home  →  !ls -la /home

# 参数化别名
ip.alias_manager.define_alias('ap', 'ping -c 1 %s')
# ap localhost  →  !ping -c 1 localhost

# 整行替换
ip.alias_manager.define_alias('echoall', 'echo %l')
# echoall hello world  →  !echo hello world
```

---

## 异常类

```python
class AliasError(Exception):
    """别名相关错误基类"""

class InvalidAliasError(AliasError):
    """无效别名（黑名单、冲突、格式错误）"""
```

---

## 在 InteractiveShell 中的初始化

| 组件 | 初始化方法 | 属性名 |
|------|-----------|--------|
| HistoryManager | `init_history()` | `history_manager` |
| IPCompleter | `init_completer()` | `completer` |
| AliasManager | `init_alias()` | `alias_manager` |

### 用户命名空间中的历史变量

| 变量 | 说明 |
|------|------|
| `In` / `_ih` | 输入历史列表（`In[1]` 是第一个输入） |
| `Out` / `_oh` | 输出历史字典（`Out[1]` 是第一个输出） |
| `_` | 最近一个输出 |
| `__` | 倒数第二个输出 |
| `___` | 倒数第三个输出 |
| `_N` | 第 N 个输出（`_1`, `_2`, ...） |
| `_iN` | 第 N 个输入（`_i1`, `_i2`, ...） |

---

## 相关概念

- **[InteractiveShell](./interactiveshell-source.md)**：Shell 中 history_manager/completer/alias_manager 的初始化
- **[魔法命令系统](./magic-source.md)**：%hist/%history、%alias/%unalias、%rep 等历史相关魔法
- **[显示系统](./display-source.md)**：DisplayHook 中输出缓存和 _oh 更新逻辑
- **[输入转换](./inputtransformer-source.md)**：输入历史中 raw vs parsed 的区别

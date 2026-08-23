---
type: Concept
title: expect 模式匹配
description: expect/expect_exact/expect_list 详解、模式列表返回索引、EOF/TIMEOUT 处理、before/after/match 三元组、searchwindowsize/maxread
tags: [pexpect, expect, regex, pattern-matching]
generated: { by: "reference_agent/trae-glm", at: "2026-08-23T10:00:00Z" }
verified: { by: "process:seven-concepts-v", at: "2026-08-23T12:00:00Z" }
status: stable
stale_after: 2027-12-31
sources:
  - id: pexpect-source
    resource: /references/pexpect-source.md
---

# expect 模式匹配

## expect 核心方法

`expect()` 是 pexpect 的核心方法，在子进程输出流中搜索匹配的模式。

### 方法签名

```python
SpawnBase.expect(self, pattern, timeout=-1, searchwindowsize=-1,
                 async_=False, **kw)
```

| 参数 | 默认值 | 说明 |
|------|--------|------|
| `pattern` | （必填） | 字符串、编译正则、EOF、TIMEOUT，或它们的列表 |
| `timeout` | `-1` | 超时秒数；-1 使用 self.timeout；None 无限等待 |
| `searchwindowsize` | `-1` | 搜索窗口大小；-1 使用 self.searchwindowsize |
| `async_` | `False` | True 时返回 asyncio coroutine（需 asyncio 支持） |

### 返回值

返回匹配模式在列表中的**索引**（整数）。如果 pattern 不是列表，成功匹配时返回 0。

### 基本用法

```python
import pexpect

child = pexpect.spawn('ftp ftp.example.com', encoding='utf-8')

# 单模式匹配
child.expect('Name .*: ')
child.sendline('anonymous')

# 多模式匹配——返回索引
i = child.expect(['Password:', 'password required', pexpect.EOF])
if i == 0:
    child.sendline('user@example.com')
elif i == 1:
    print("Password required but not provided")
else:
    print("Connection closed")
```

## 三种 expect 变体

| 方法 | 匹配方式 | 性能 | 适用场景 |
|------|---------|------|---------|
| `expect(pattern)` | 正则表达式 | 中等 | 需要正则匹配（通配符、分组、大小写不敏感） |
| `expect_exact(pattern_list)` | 纯字符串 | 快 | 精确字符串匹配，无需正则，避免转义特殊字符 |
| `expect_list(pattern_list)` | 预编译正则列表 | 最快 | 循环中重复使用同一模式集，避免重复编译 |

### expect_exact

```python
# 不需要转义正则特殊字符
child.expect_exact('Password:')

# 也支持列表和 EOF/TIMEOUT
i = child.expect_exact(['Password:', 'Permission denied', pexpect.EOF])
```

### expect_list（性能优化）

在循环中使用时，先编译模式列表再调用 `expect_list`，避免每次重复编译：

```python
# 不推荐——循环内每次都编译
for _ in range(100):
    i = child.expect(['success', 'error', 'warning'])

# 推荐——编译一次，多次使用
cpl = child.compile_pattern_list(['success', 'error', 'warning'])
for _ in range(100):
    i = child.expect_list(cpl)
```

`compile_pattern_list(patterns)` 接受字符串、编译正则、EOF、TIMEOUT 或它们的列表，返回统一的编译后列表。字符串使用 `re.DOTALL`（dot 匹配换行符）编译，`ignorecase=True` 时追加 `re.IGNORECASE`。

## 匹配结果三元组

每次 expect 调用后，以下属性反映匹配结果：

| 属性 | 类型 | 说明 |
|------|------|------|
| `before` | str/bytes | 匹配位置之前的所有输出数据 |
| `after` | str/bytes/异常类型 | 匹配到的字符串；EOF/TIMEOUT 时为异常类型本身 |
| `match` | re.Match/None/异常 | 正则匹配对象（可提取分组）；EOF/TIMEOUT 时为异常类型 |
| `match_index` | int/None | 匹配模式在列表中的索引 |

```python
child.expect(r'(\w+)@(\w+):')
print(child.before)        # 匹配位置之前的内容
print(child.after)         # 完整匹配的字符串
print(child.match.group(1))  # 第一个捕获组
print(child.match.group(2))  # 第二个捕获组
print(child.match_index)   # 匹配的模式索引
```

## EOF 和 TIMEOUT 作为模式

将 `pexpect.EOF` 或 `pexpect.TIMEOUT` 加入模式列表，可以优雅处理这两种情况而无需 try/except：

```python
i = child.expect([
    'password:',        # 0
    'Permission denied', # 1
    pexpect.EOF,        # 2
    pexpect.TIMEOUT     # 3
], timeout=30)

if i == 0:
    child.sendline('secret')
elif i == 1:
    print("Access denied")
elif i == 2:
    print("Connection closed. Output so far:", child.before)
elif i == 3:
    print("Timed out. Output so far:", child.before)
```

未在模式列表中包含 EOF/TIMEOUT 时，会抛出对应异常：

```python
try:
    child.expect('something', timeout=10)
except pexpect.EOF:
    print("Child exited before pattern appeared")
    print(child.before)  # EOF 前所有输出
except pexpect.TIMEOUT:
    print("Pattern not found within timeout")
    print(child.before)  # 超时前所有输出
```

## 匹配规则详解

### 多模式匹配优先级

当多个模式同时匹配时：

1. **最先出现在流中的匹配优先**。
2. **同一位置多个模式匹配时，选择列表中最靠左的**（不是"最佳匹配"）。

```python
# 输入为 'foobar'
i = child.expect(['bar', 'foo', 'foobar'])
# 返回 1（foo），即使 'foobar' 是更完整的匹配

# 输入为 'foobar'，但分块到达
i = child.expect(['foobar', 'foo'])
# 如果 'foobar' 一次性到达，返回 0
# 如果 'foo' 先到达而 'bar' 延迟，可能返回 1
```

> **注意**：数据通过 PTY 分块到达的时序不可预测。在设计模式列表时，将更具体的模式放在更前面，避免被短模式抢先匹配。

### 正则标志

- 默认使用 `re.DOTALL`：`.` 匹配换行符 `\n`。
- 设置 `child.ignorecase = True` 后，所有后续 expect 调用追加 `re.IGNORECASE`。
- 也可传入预编译正则自定义标志：

```python
import re
child.expect(re.compile(r'password:', re.IGNORECASE))
```

## 搜索窗口与缓冲区

### maxread

`maxread`（默认 2000）控制每次 `read_nonblocking` 从 PTY 读取的最大字节数。增大可提高大量输出场景的性能，设为 1 禁用缓冲。

### searchwindowsize

`searchwindowsize` 限制每次搜索的缓冲区尾部窗口大小：

- `None`（默认）：搜索整个缓冲区，最准确但大数据量时慢。
- 正整数 N：只搜索最后 N 字节，减少搜索开销。匹配后缓冲区仍保留 maxread 大小。

```python
child = pexpect.spawn('some_command', searchwindowsize=1024)

# 或每次 expect 单独指定
child.expect('pattern', searchwindowsize=512)
```

### 缓冲区机制

Expecter 引擎维护两个缓冲区：

- `_buffer`：当前搜索窗口（可能被裁剪以优化性能）
- `_before`：完整历史数据，用于设置 `before` 属性

每次新数据到达时，引擎在搜索窗口中查找模式；找到匹配后，`before` 从 `_before` 提取，`after` 为匹配片段，匹配后的数据保留在新缓冲区中。

## read/readline 文件接口

SpawnBase 提供类文件对象的读取方法，内部基于 expect 实现：

### read(size=-1)

```python
data = child.read()       # 读取直到 EOF，返回所有输出
chunk = child.read(100)   # 读取最多 100 字节
```

- `size < 0`：读取直到 EOF 或 delimiter（默认 EOF），返回 `before`。
- `size > 0`：通过正则 `.{size}` 匹配精确字节数，返回 `after`。
- `size == 0`：返回空字符串。

### readline(size=-1)

```python
line = child.readline()   # 读取一行（以 \r\n 结尾）
```

PTY 模式下行终止符为 `\r\n`（CR/LF 对），即使在 Unix 上也是如此。size 参数除 0 外被忽略。

### 迭代器

```python
for line in child:
    print(line.rstrip())
    if 'Done' in line:
        break
```

### readlines()

```python
lines = child.readlines()  # 读取所有行直到 EOF
```

> **警告**：readlines() 会阻塞直到子进程关闭 stdout。如果子进程仍在运行，将阻塞至超时。

## 异步 expect

在 asyncio 环境中，`async_=True` 使 expect 返回协程：

```python
import asyncio
import pexpect

async def main():
    child = pexpect.spawn('some_command', encoding='utf-8')
    index = await child.expect('pattern', async_=True)
    print(index)

asyncio.run(main())
```

## 相关概念

- [spawn 类详解](/concepts/02-spawn-class.md)
- [发送与交互](/concepts/04-send-interact.md)
- [跨平台 spawn 变体](/concepts/06-cross-platform-spawn.md)
- [高级模式](/concepts/08-advanced-patterns.md)

[^pexpect-source]: pexpect 源码信源，见 [pexpect-source.md](/references/pexpect-source.md)。

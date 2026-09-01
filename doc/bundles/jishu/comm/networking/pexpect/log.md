# pexpect 知识包生成日志

## R 阶段（事实采集）

- 读取任务简报：`.trae/specs/ssh-python-okf-wiki/pexpect-task-brief.md`
- 参考格式范例：`projects/awesome-okf-xs/bundles/networking/paramiko/`（index.md、concepts/、examples/、references/）
- 逐模块阅读 pexpect v4.9.0 源码（`external/libs/pexpect/pexpect/`，commit fc8f062518b4）：
  - `__init__.py`（包导出、条件导入）
  - `spawnbase.py`（SpawnBase 基类、expect 引擎、read/readline）
  - `pty_spawn.py`（spawn 类、PTY 实现、interact）
  - `pxssh.py`（pxssh 类、login/logout/prompt、唯一提示符）
  - `popen_spawn.py`（PopenSpawn 跨平台实现）
  - `fdpexpect.py`（fdspawn 文件描述符）
  - `socket_pexpect.py`（SocketSpawn socket 实现）
  - `replwrap.py`（REPLWrapper、python/bash/zsh 工厂函数）
  - `run.py`（run() 函数、runu 弃用别名）
  - `expect.py`（Expecter、searcher_string、searcher_re）
  - `exceptions.py`（ExceptionPexpect、EOF、TIMEOUT）
  - `FSM.py`（FSM 有限状态机、ExceptionFSM）
  - `utils.py`（which、split_command_line、select_ignore_interrupts 等）
- 提取 **77 条**编号事实，输出至 `.trae/specs/ssh-python-okf-wiki/pexpect-facts.md`

## I 阶段（架构洞察）

- 提炼 **4 个核心架构洞察**，输出至 `.trae/specs/ssh-python-okf-wiki/pexpect-insights.md`：
  1. PTY 子进程控制模型与增量缓冲区匹配
  2. expect 正则匹配引擎——模式列表返回索引、before/after/match 三元组
  3. pxssh 对 SSH 登录的状态机封装（unique prompt 技巧）
  4. 跨平台 spawn 变体策略（pty_spawn/popen_spawn/fdspawn/SocketSpawn 继承层次）
- 设计知识地图：入门(2篇) → 核心(4篇) → 高级(3篇)，共 9 篇概念文档

## E 阶段（批量生成）

### Step 1: 创建目录结构
- `bundles/networking/pexpect/concepts/`
- `bundles/networking/pexpect/examples/`
- `bundles/networking/pexpect/references/`

### Step 2: 信源先行
- `references/pexpect-source.md`

### Step 3: concepts/（9篇）
1. `concepts/00-introduction.md`
2. `concepts/01-getting-started.md`
3. `concepts/02-spawn-class.md`
4. `concepts/03-expect-patterns.md`
5. `concepts/04-send-interact.md`
6. `concepts/05-pxssh.md`
7. `concepts/06-cross-platform-spawn.md`
8. `concepts/07-replwrap.md`
9. `concepts/08-advanced-patterns.md`

### Step 4: examples/（4篇）
1. `examples/ssh-login-automation.md`
2. `examples/ftp-interaction.md`
3. `examples/password-prompts.md`
4. `examples/repl-control.md`

### Step 5: index 与日志
- `concepts/index.md`
- `examples/index.md`
- `references/index.md`
- `index.md`（根，带 okf_version frontmatter）
- `log.md`（本文件）

## V 阶段（独立验证）

### Grep API 验证结果

**类名验证（全部通过）**：

| 类名 | 源码位置 | 状态 |
|------|---------|------|
| spawn | pty_spawn.py:29 | ✅ |
| pxssh | pxssh.py:52 | ✅ |
| PopenSpawn | popen_spawn.py:20 | ✅ |
| fdspawn | fdpexpect.py:35 | ✅ |
| SocketSpawn | socket_pexpect.py:32 | ✅ |
| SpawnBase | spawnbase.py:23 | ✅ |
| REPLWrapper | replwrap.py:17 | ✅ |
| ExceptionPexpect | exceptions.py:6 | ✅ |
| EOF | exceptions.py:29 | ✅ |
| TIMEOUT | exceptions.py:34 | ✅ |
| ExceptionPxssh | pxssh.py:32 | ✅ |
| ExceptionFSM | FSM.py:87 | ✅ |
| FSM | FSM.py:97 | ✅ |
| Expecter | expect.py:5 | ✅ |
| searcher_string | expect.py:187 | ✅ |
| searcher_re | expect.py:285 | ✅ |

**函数名验证（全部通过）**：

| 函数名 | 源码位置 | 状态 |
|--------|---------|------|
| run | run.py:7 | ✅ |
| runu | run.py:150 | ✅（弃用） |
| spawnu | pty_spawn.py:857 | ✅（弃用） |
| which | utils.py:48 | ✅ |
| split_command_line | utils.py:69 | ✅ |
| is_executable_file | utils.py:20 | ✅ |
| python | replwrap.py:111 | ✅ |
| bash | replwrap.py:129 | ✅ |
| zsh | replwrap.py:134 | ✅ |

**方法名验证（全部通过）**：

| 方法名 | 所属类 | 源码位置 | 状态 |
|--------|--------|---------|------|
| expect | SpawnBase | spawnbase.py:254 | ✅ |
| expect_list | SpawnBase | spawnbase.py:357 | ✅ |
| expect_exact | SpawnBase | spawnbase.py:385 | ✅ |
| expect_loop | SpawnBase | spawnbase.py:434 | ✅ |
| compile_pattern_list | SpawnBase | spawnbase.py:205 | ✅ |
| read | SpawnBase | spawnbase.py:444 | ✅ |
| readline | SpawnBase | spawnbase.py:473 | ✅ |
| read_nonblocking | spawn/PopenSpawn/fdspawn/SocketSpawn | 各文件 | ✅ |
| send | spawn/PopenSpawn/fdspawn/SocketSpawn | 各文件 | ✅ |
| sendline | spawn/PopenSpawn/fdspawn/SocketSpawn | 各文件 | ✅ |
| sendcontrol | spawn | pty_spawn.py:586 | ✅ |
| sendeof | spawn/PopenSpawn | pty_spawn.py:599 / popen_spawn.py:186 | ✅ |
| sendintr | spawn | pty_spawn.py:612 | ✅ |
| write | spawn/PopenSpawn/fdspawn/SocketSpawn | 各文件 | ✅ |
| writelines | spawn/PopenSpawn/fdspawn/SocketSpawn | 各文件 | ✅ |
| interact | spawn | pty_spawn.py:739 | ✅ |
| close | spawn/PopenSpawn/fdspawn/SocketSpawn | 各文件 | ✅ |
| kill | spawn/PopenSpawn | pty_spawn.py:715 / popen_spawn.py:171 | ✅ |
| terminate | spawn/fdspawn | pty_spawn.py:632 / fdpexpect.py:93 | ✅ |
| isalive | spawn/PopenSpawn/fdspawn/SocketSpawn | 各文件 | ✅ |
| wait | spawn/PopenSpawn | pty_spawn.py:672 / popen_spawn.py:156 | ✅ |
| waitnoecho | spawn | pty_spawn.py:344 | ✅ |
| getecho | spawn | pty_spawn.py:374 | ✅ |
| setecho | spawn | pty_spawn.py:382 | ✅ |
| getwinsize | spawn | pty_spawn.py:725 | ✅ |
| setwinsize | spawn | pty_spawn.py:730 | ✅ |
| login | pxssh | pxssh.py:256 | ✅ |
| logout | pxssh | pxssh.py:475 | ✅ |
| prompt | pxssh | pxssh.py:487 | ✅ |
| set_unique_prompt | pxssh | pxssh.py:511 | ✅ |
| sync_original_prompt | pxssh | pxssh.py:215 | ✅ |
| run_command | REPLWrapper | replwrap.py:68 | ✅ |
| set_prompt | REPLWrapper | replwrap.py:60 | ✅ |
| process | FSM | FSM.py:228 | ✅ |
| add_transition | FSM | FSM.py:131 | ✅ |
| add_transition_list | FSM | FSM.py:148 | ✅ |
| add_transition_any | FSM | FSM.py:164 | ✅ |
| set_default_transition | FSM | FSM.py:182 | ✅ |
| reset | FSM | FSM.py:122 | ✅ |

**pxssh 属性验证（全部通过）**：

| 属性名 | 源码位置 | 状态 |
|--------|---------|------|
| UNIQUE_PROMPT | pxssh.py:140 | ✅ |
| PROMPT_SET_SH | pxssh.py:144 | ✅ |
| PROMPT_SET_CSH | pxssh.py:145 | ✅ |
| PROMPT_SET_ZSH | pxssh.py:146 | ✅ |
| SSH_OPTS | pxssh.py:147 | ✅ |
| force_password | pxssh.py:156 | ✅ |
| options | pxssh.py:162 | ✅ |
| debug_command_string | pxssh.py:158 | ✅ |

### 平台差异确认

- `spawn`、`run`、`spawnu`、`runu` 在 `__init__.py:79-82` 被 `if sys.platform != 'win32'` 条件守卫，Windows 上不可从 `pexpect` 顶层导入。
- `PopenSpawn` 是 Windows 上唯一可用的 spawn 变体（基于 subprocess.Popen，无 PTY）。
- `SocketSpawn` 跨平台可用，是 Windows 上 socket 交互的推荐方式。
- `fdspawn` 在 Windows 上对 socket 无效（socket.fileno() 不可用于 select），源码 docstring 明确提示使用 socket_pexpect。

### 虚构 API 修复

1. **无虚构 API**：所有文档中引用的类、方法、属性均经 Grep 在源码中验证存在。
2. **spawnu/runu 弃用标注**：源码确认两者为弃用函数（pty_spawn.py:857-859、run.py:150-156），文档中明确标注"已弃用"。
3. **PopenSpawn 能力边界**：源码确认 PopenSpawn 不支持 interact/setwinsize/waitnoecho/terminate 等 PTY 专属方法，文档中能力矩阵如实反映。
4. **fdspawn.terminate 行为**：源码确认该方法直接抛出 ExceptionPexpect（fdpexpect.py:93-95），非静默无操作。
5. **pxssh.login 完整签名**：任务简报列出了主要参数，经源码核实完整签名包含 `ssh_tunnels`、`spawn_local_ssh`、`sync_original_prompt`、`ssh_config`、`cmd` 等额外参数，文档中完整记录。

### Frontmatter 检查

14 个内容文件（9 概念 + 4 示例 + 1 信源）全部包含 type/title/description/tags/generated/verified/status/stale_after/sources 九个字段。

### 链接检查

所有 `/concepts/`、`/examples/`、`/references/` 开头的交叉链接目标文件均存在，无断裂链接。

### 验证结论

- 零虚构 API（所有文档引用的类/方法/属性均经 Grep 验证存在）
- Frontmatter 完整率 100%
- 交叉链接无断裂
- 事实清单 77 条，均溯源至具体源码行
- 平台差异（Unix PTY vs Windows PopenSpawn）在多处文档中明确标注

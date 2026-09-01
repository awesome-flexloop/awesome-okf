---
okf_version: "0.2"
type: "concept"
title: "网关层I/O抽象"
sources:
  - "conda/gateways/connection/session.py"
  - "conda/gateways/disk/__init__.py"
  - "conda/gateways/connection/download.py"
  - "conda/gateways/subprocess.py"
---

# 网关层I/O抽象

`conda/gateways/` 是 conda 架构中的I/O边界层，负责封装所有外部交互——网络请求、磁盘操作、子进程调用和 repodata 缓存。它将上层业务逻辑（core/）与具体I/O实现解耦，使得核心求解和事务逻辑无需关心数据来自HTTP、FTP、S3、本地文件系统还是磁盘缓存。

## CondaSession：多协议HTTP会话

`CondaSession` 继承自 `requests.Session`，是 conda 所有网络请求的统一入口 [F-074]。它通过元类 `CondaSessionType` 实现**线程局部单例**——每个线程拥有独立的 Session 实例（避免 requests Session 的线程安全问题），按 auth 类型缓存。

### 五种协议适配器

`CondaSession` 挂载了五种协议适配器，覆盖 conda 支持的所有 URL scheme [F-074]：

```python
# session.py 构造函数中挂载
self.mount("http://", HTTPAdapter())
self.mount("https://", HTTPAdapter())
self.mount("ftp://", FTPAdapter())
self.mount("s3://", S3Adapter())
self.mount("file://", LocalFSAdapter())
```

| 适配器 | 协议 | 说明 |
|---|---|---|
| `HTTPAdapter` | http/https | 基于 requests 的HTTP适配器，配置重试策略（RETRIES=3）、SSL验证、代理、truststore |
| `FTPAdapter` | ftp | FTP文件下载支持 |
| `S3Adapter` | s3 | AWS S3存储访问，使用boto3（线程安全的独立session） |
| `LocalFSAdapter` | file | 本地文件系统URL（`file:///`），用于本地通道 |
| `EnforceUnusedAdapter` | 其他 | 离线模式下挂载，任何请求抛出 OfflineError |

离线模式（`context.offline`）时，非 file:// 的适配器被替换为 `EnforceUnusedAdapter`，所有远程请求直接抛出 `OfflineError`。

### 线程局部缓存

`CondaSessionType` 元类通过 `threading.local()` 实现每个线程独立的 Session 缓存 `gateways/connection/session.py#L221-L244`：

```python
class CondaSessionType(type):
    def __new__(mcs, name, bases, dct):
        dct["_thread_local"] = local()
        return super().__new__(mcs, name, bases, dct)

    def __call__(cls, **kwargs):
        storage_key = get_session_storage_key(kwargs.get("auth"))
        try:
            return cls._thread_local.sessions[storage_key]
        except (AttributeError, KeyError):
            session = super().__call__(**kwargs)
            cls._thread_local.sessions = {storage_key: session}
            return session
```

`get_session(url)` 函数根据 URL 匹配通道配置的 auth handler，返回对应的 Session 实例。未匹配到自定义auth时返回默认 Session。

### FORBIDDEN_HEADERS 安全机制

插件可通过 `conda_session_headers` 和 `conda_request_headers` 钩子添加自定义HTTP头，但20个被禁止的头（host/cookie/content-length/connection等）以及 `proxy-*`/`sec-*` 前缀的头会被 `_validate_plugin_headers()` 拦截，抛出 `PluginError` [F-075]。

## gateways/disk/：磁盘操作抽象

`gateways/disk/` 目录包含8个模块，按CRUD+操作类型组织 [F-076]：

| 模块 | 职责 |
|---|---|
| `create.py` | 创建目录、文件、硬链接/软链接 |
| `delete.py` | 删除文件/目录（`rm_rf`、`try_rmdir_all_empty`） |
| `read.py` | 读取文件内容、计算hash |
| `update.py` | 文件更新（替换、移动） |
| `link.py` | 硬链接/软链接/复制操作，`determine_link_type()` 决定链接策略 |
| `lock.py` | 文件锁（DirectoryLock/FileLock），防止并发conda进程冲突 |
| `permissions.py` | 文件权限操作（chmod、chown） |
| `test.py` | 磁盘操作测试工具（如 `hardlink_supported`、`softlink_supported`） |
| `__init__.py` | 通用工具：`mkdir_p`、`exp_backoff_fn`（指数退避重试） |

### 指数退避重试

`exp_backoff_fn(fn, *args, **kwargs)` 是 Windows 平台特有的重试机制 `gateways/disk/__init__.py#L19-L64`。Windows 上杀毒软件可能短暂锁定文件，导致 EPERM/EACCES 错误。该函数在非Windows平台直接调用函数；在Windows上遇到权限错误时，使用指数退避策略（sleep时间 = `(2^n + random) * 0.1`秒，最多7次，总计约6.5秒）重试。

```python
def exp_backoff_fn(fn, *args, max_tries=MAX_TRIES, **kwargs):
    if not on_win:
        return fn(*args, **kwargs)
    for n in range(max_tries):
        try:
            return fn(*args, **kwargs)
        except OSError as e:
            if e.errno in (EPERM, EACCES):
                sleep((2**n + random.random()) * 0.1)
            else:
                raise
```

### 文件锁

`gateways/disk/lock.py` 提供跨进程文件锁，确保多个 conda 进程不会同时修改同一个包缓存或环境前缀。锁在事务（UnlinkLinkTransaction）执行期间持有，防止并发install/remove操作损坏环境。

## 并行下载与包获取

并行下载逻辑分布在多个模块中：

- **`gateways/connection/download.py`**：单文件下载函数 `download(url, target_full_path, md5, sha256, size)`，支持进度回调、校验和验证、断点续传（`.part` 部分文件）、CHUNK_SIZE=16KB的流式下载
- **`core/package_cache_data.py`**：使用 `ThreadPoolExecutor` 实现多包并行下载（`context.fetch_threads` 控制并发数），并行提取包（`EXTRACT_THREADS` 控制），通过 `as_completed` 处理完成事件
- **`core/subdir_data.py`**：使用 `ThreadLimitedThreadPoolExecutor` 并行加载多个 subdir 的 repodata（`context.repodata_threads` 控制并发数）
- **`notices/fetch.py`**：通知消息并行获取
- **`_private/shards/`**：分片repodata并行下载

下载流程中的关键设计：
1. 先下载到 `.part` 临时文件，校验和验证通过后再原子重命名为目标文件
2. 下载失败时部分文件会重试（`ChecksumMismatchError` 的 `partial_download` 标志控制）
3. 使用 `time_recorder("download")` 装饰器记录下载耗时

## repodata缓存管理

`gateways/repodata/` 模块管理 repodata.json 的缓存：

- **`__init__.py`**：`RepodataFetch`、`RepodataState`、`cache_fn_url()` 等核心缓存逻辑 [F-077]
- **`lock.py`**：repodata 缓存文件的并发访问锁
- **`zstd.py`**：Zstandard 压缩支持，用于缓存的 repodata 序列化

缓存机制要点：
- 缓存文件路径由 `cache_fn_url(url)` 基于URL哈希生成
- `RepodataState` 跟踪缓存的状态（mod时间、etag、cache_control等），与 `.state.json` 后缀的状态文件配对
- `CACHE_STATE_SUFFIX` 常量定义状态文件后缀
- 缓存使用 pickle 序列化（`REPODATA_PICKLE_VERSION = 30`），版本不匹配时自动失效
- file:// URL的本地通道通过mtime检测缓存是否过期
- `RepodataFetch` 封装了"先查缓存→未命中则下载→验证→缓存→返回"的完整流程

## gateways/subprocess.py：子进程封装

`gateways/subprocess.py` 提供子进程调用的统一封装 [F-078]：

```python
Response = namedtuple("Response", ("stdout", "stderr", "rc"))
```

核心功能：
- **`any_subprocess(args, prefix, env=None, cwd=None)`**：在指定conda环境中执行任意命令，自动处理PATH和环境变量激活
- **`_format_output()`**：格式化子进程输出（命令、cwd、退出码、stdout、stderr）
- 子进程自动注册到 `ACTIVE_SUBPROCESSES` 集合，信号处理时可被转发信号
- `wrap_subprocess_call()` 封装跨平台的子进程调用（Unix使用 `os.execvpe`，Windows使用 `Popen`）
- 支持编码环境变量（`encode_environment`），处理Windows上的环境变量编码问题

## 架构位置

gateways 层位于 conda 七层架构的I/O边界位置：上层 core/（solve/index/link/package_cache_data）通过 gateways 访问外部资源，下层依赖 base/（context/constants）和 common/（compat/io/path）。这一分层确保核心业务逻辑可测试——在测试中可替换 gateways 层为 mock 实现，无需真实网络或磁盘操作。

---
okf_version: "0.2"
type: "concept"
title: "Channel 与 Subdir 模型"
sources:
  - conda/models/channel.py
  - conda/base/context.py
  - conda/base/constants.py
---

# Channel 与 Subdir 模型

Channel（通道）是 conda 定位包源的核心抽象，Subdir（子目录）则是通道内按平台划分的索引层级。两者共同决定了 conda 去哪里查找包元数据（repodata.json）和包文件。

## Channel 的 URL 分解模型

`Channel` 类将一个通道 URL 分解为 8 个结构化组件，类文档明确标注了分解顺序 [F-030]：

```
scheme <> auth <> location <> token <> channel <> subchannel <> platform <> package_filename
```

以 `https://conda.anaconda.org/conda-forge/linux-64/python-3.12-py312_0.conda` 为例：

| 组件 | 值 | 说明 |
|------|----|------|
| `scheme` | `https` | URL 协议（http/https/ftp/s3/file） |
| `auth` | `None` | 认证信息（用户名/密码） |
| `location` | `conda.anaconda.org` | 主机名+端口 |
| `token` | `None` | 私有通道令牌 |
| `name` | `conda-forge` | 通道名称 |
| `platform`(subdir) | `linux-64` | 平台子目录 |
| `package_filename` | `python-3.12-py312_0.conda` | 包文件名 |

Channel 的构造参数 `__init__` 接收这些字段，并提供 `subdir` 属性作为 `platform` 的别名 [F-032]：

```python
class Channel:
    def __init__(
        self,
        scheme: str | None = None,
        auth: str | None = None,
        location: str | None = None,
        token: str | None = None,
        name: str | None = None,
        platform: str | None = None,
        package_filename: str | None = None,
    ):
        ...
        self.scheme = scheme
        self.auth = auth
        self.location = location
        self.token = token
        self.name = name or ""
        self.platform = platform
        self.package_filename = package_filename

    @property
    def subdir(self) -> str | None:
        return self.platform
```

## from_value() 缓存机制

Channel 的实例化不走普通构造器路径，而是通过 `__new__()` 拦截 [F-031]：

1. **单参数且为 Channel 实例**：直接返回该实例（身份短路）
2. **单 str 参数**：调用 `from_value()` 走缓存路径
3. **含 `channels` kwarg**：返回 `MultiChannel`（多通道聚合）
4. **其他情况**：走 `super().__new__()` 正常构造

`from_value()` 是静态方法，使用 `@cache` 装饰器实现字符串到 Channel 实例的全局缓存 [F-033]。这意味着相同字符串始终返回同一个 Channel 对象，避免重复解析 URL。该方法能处理多种输入形式：

- `None` / `"<unknown>"` → 返回未知通道（UNKNOWN_CHANNEL）
- 带 scheme 的 URL（`https://...`、`file://...`）→ 调用 `from_url()` 解析
- 本地路径（`./local-channel`）→ 转换为 `file://` URL 再解析
- 已知通道名（`defaults`、`conda-forge`）→ 调用 `from_channel_name()` 查配置

缓存可通过 `Channel._reset_state()` 清除（清空 `from_value` 缓存），主要用于测试场景。

`__init__` 方法通过 `if self.__dict__: return` 实现幂等保护——若对象已初始化（来自 `__new__` 缓存返回），则跳过重复初始化，这是缓存模式与标准 Python 构造流程协作的关键。

### MultiChannel：多通道聚合

当传入 `channels` 关键字参数时，`__new__()` 返回 `MultiChannel` 实例而非普通 Channel。MultiChannel 是一个命名的通道组，代表多个底层 Channel 的聚合。`defaults` 就是最典型的 MultiChannel——它在不同平台上展开为 2~3 个实际 URL。用户在 `.condarc` 中通过 `custom_multichannels` 配置的自定义多通道（如 `mygroup`）也通过此机制处理。`from_value()` 在解析时会检查 `context.custom_multichannels`，若命中则构造 MultiChannel。

## Subdir：平台子目录

Subdir（即 `platform` 属性）标识通道中的平台子目录。conda 预定义了所有已知平台列表 `KNOWN_SUBDIRS` [F-029]，包含：

- **跨平台**：`noarch`（架构无关包）
- **Linux**：`linux-32`, `linux-64`, `linux-aarch64`, `linux-armv6l`, `linux-armv7l`, `linux-ppc64`, `linux-ppc64le`, `linux-riscv64`, `linux-s390x`
- **macOS**：`osx-64`, `osx-arm64`
- **Windows**：`win-32`, `win-64`, `win-arm64`
- **其他**：`freebsd-64`, `zos-z`, `emscripten-wasm32`, `wasi-wasm32`

平台名通过 `_platform_map` 从 Python 系统平台名映射而来 [F-025]：`linux`→`linux`、`darwin`→`osx`、`win32`→`win`、`freebsd13`→`freebsd`。这就是为什么 `sys.platform == "darwin"` 对应 subdir 是 `osx-64`/`osx-arm64`。

每个 subdir 下都有自己的 `repodata.json`，包含该平台所有包的索引信息。conda 求解时会同时加载用户配置的 channels × subdirs 矩阵中的所有 repodata。

## defaults 与 conda-forge 通道

- **defaults** 通道（`DEFAULTS_CHANNEL_NAME = "defaults"`）是 conda 的默认通道 [F-028]。它实际是一个 MultiChannel，在 Unix 下展开为 `https://repo.anaconda.com/pkgs/main` + `https://repo.anaconda.com/pkgs/r`，在 Windows 下额外增加 `https://repo.anaconda.com/pkgs/msys2`（由 `DEFAULT_CHANNELS_UNIX` / `DEFAULT_CHANNELS_WIN` 常量控制）。
- **conda-forge** 是社区驱动的通道，URL 为 `https://conda.anaconda.org/conda-forge`，通过 `DEFAULT_CHANNEL_ALIAS = "https://conda.anaconda.org"` 作为短名称解析的基础 URL。

## 与其他模型的关系

Channel 是 [MatchSpec 查询语言](04-matchspec.md) 中 `channel` 字段的类型，也是 [PackageRecord](06-package-records.md) 中 `channel` 字段的类型（通过 `ChannelField` 自动从 URL 构造）。SubdirData 以 `(channel.url(), repodata_fn)` 为缓存键管理每个 subdir 的 repodata 加载。

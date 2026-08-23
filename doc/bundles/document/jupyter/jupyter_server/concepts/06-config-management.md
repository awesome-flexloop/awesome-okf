---
type: Concept
title: "配置管理"
description: "Jupyter Server 双轨配置体系：traitlets 服务端配置与 BaseJSONConfigManager 前端/扩展 JSON 配置、配置文件位置、优先级与递归合并机制"
tags: [configuration, traitlets, json-config, config-files, setup]
generated: { by: "reference_agent/trae-cn", at: "2026-08-22T14:45:00Z" }
status: stable
stale_after: 2027-02-22
sources:
  - id: config
    resource: /references/config-source.md
    title: 配置管理源码信源
---

# 配置管理

Jupyter Server 采用**双轨配置体系**：服务端行为使用 traitlets 配置系统（Python 文件），前端 UI 和扩展配置使用 JSON 配置文件。两套系统独立运作，服务于不同层次。

## 双轨配置对比

| 维度 | traitlets 配置 | JSON 配置 |
|------|---------------|----------|
| 管理对象 | 服务端行为（端口、根目录、认证等） | 前端 UI 设置、扩展配置 |
| 文件格式 | Python (.py) | JSON (.json + .d/*.json) |
| 配置类 | `traitlets.config.Config` | `BaseJSONConfigManager` |
| 读取时机 | 启动时一次性加载 | API 实时读写 |
| 修改方式 | 编辑文件 + 重启 | REST API 动态修改 |
| 典型路径 | `~/.jupyter/jupyter_server_config.py` | `~/.jupyter/serverconfig/` |

## traitlets 配置系统

### 配置文件位置

Jupyter Server 按以下优先级搜索配置文件（后者覆盖前者）：

| 位置 | 路径（Linux/macOS） | 说明 |
|------|---------------------|------|
| 系统级 | `/usr/etc/jupyter/` | 系统管理员配置 |
| 环境级 | `$CONDA_PREFIX/etc/jupyter/` | Conda/venv 环境配置 |
| 用户级 | `~/.jupyter/` | 用户个人配置（最常用） |
| 当前目录 | `./` | 项目级配置 |

配置文件名为 `jupyter_server_config.py`。

### 生成默认配置

```bash
jupyter server --generate-config
```

在用户目录生成 `~/.jupyter/jupyter_server_config.py`，包含所有可配置项的注释说明。

### 配置语法

配置文件是纯 Python 文件，通过 `c = get_config()` 获取配置对象：

```python
# 获取配置对象（每个配置文件必须以此开头）
c = get_config()  # noqa

# ServerApp 配置
c.ServerApp.ip = '0.0.0.0'
c.ServerApp.port = 9999
c.ServerApp.root_dir = '/home/user/notebooks'
c.ServerApp.open_browser = False
c.ServerApp.allow_origin = 'https://example.com'

# IdentityProvider 配置
c.PasswordIdentityProvider.hashed_password = 'argon2:...'

# ContentsManager 配置
c.ContentsManager.allow_hidden = True
c.ContentsManager.preferred_dir = '/home/user/notebooks/start'

# KernelManager 配置
c.MappingKernelManager.cull_idle_timeout = 3600  # 1小时自动关闭空闲内核
c.MappingKernelManager.cull_interval = 300
```

### 命令行配置

所有 traitlets 配置项都可通过命令行参数覆盖：

```bash
# --<ClassName>.<trait_name>=<value>
jupyter server --ServerApp.port=9999 --ServerApp.root_dir=/tmp

# 布尔类型
jupyter server --no-browser  # 等价于 --ServerApp.open_browser=False
jupyter server --allow-root  # 等价于 --ServerApp.allow_root=True
```

### 配置优先级

```
命令行参数（最高优先级）
  ↑
命令行 --config 指定的配置文件
  ↑
当前目录的 jupyter_server_config.py
  ↑
用户目录 ~/.jupyter/jupyter_server_config.py
  ↑
环境目录 $CONDA_PREFIX/etc/jupyter/
  ↑
系统目录 /usr/etc/jupyter/
  ↑
代码中的 default 值（最低优先级）
```

## JSON 配置系统

### BaseJSONConfigManager

`BaseJSONConfigManager` 管理 JSON 格式的配置文件，支持**片段合并**机制：

```
{config_dir}/
├── {section_name}.json           # 主配置文件（用户配置，最高优先级）
└── {section_name}.d/             # 片段配置目录
    ├── 10-extension-a.json      # 扩展 A 的默认配置
    └── 20-extension-b.json      # 扩展 B 的默认配置
```

### 递归合并算法

`recursive_update(target, new)` 实现深度合并：

1. dict 值递归合并
2. None 值删除对应 key
3. 空字典自动清理
4. 基本类型值直接覆盖
5. `.d/` 目录中的文件按字母序先加载
6. 主 `.json` 文件最后加载（优先级最高）

这意味着扩展可以通过在 `.d/` 目录放置 JSON 文件提供默认配置，用户可以在主 `.json` 文件中覆盖。

### ConfigManager（前端配置）

`ConfigManager`（在 `services/config/` 中）管理前端编辑器和扩展配置，通过 REST API 暴露：

| 端点 | 方法 | 说明 |
|------|------|------|
| `/api/config/<section>` | GET | 获取配置 |
| `/api/config/<section>` | PUT | 替换整个配置 |
| `/api/config/<section>` | PATCH | 递归更新配置 |

示例：
```bash
# 获取 notebook 前端配置
curl http://localhost:8888/api/config/notebook?token=xxx

# 更新配置
curl -X PATCH http://localhost:8888/api/config/notebook?token=xxx \
  -H "Content-Type: application/json" \
  -d '{"CodeCell": {"cm_config": {"lineNumbers": true}}}'
```

### remove_defaults 写入优化

写入配置时，`set()` 方法会调用 `remove_defaults()` 将与默认值相同的配置项移除，避免配置文件膨胀。这意味着配置文件只包含与默认值不同的项。

## ServerApp 核心配置项速查

### 网络配置

| 配置项 | 默认值 | 说明 |
|--------|--------|------|
| `ip` | 'localhost' | 监听地址，'0.0.0.0' 允许所有 |
| `port` | 8888 | 监听端口 |
| `port_retries` | 50 | 端口冲突重试次数 |
| `base_url` | '/' | URL 前缀（反向代理时使用） |
| `allow_origin` | '' | CORS 允许来源 |
| `allow_credentials` | False | CORS 允许凭证 |

### 目录与文件

| 配置项 | 默认值 | 说明 |
|--------|--------|------|
| `root_dir` | cwd | Notebook 根目录 |
| `preferred_dir` | '' | 起始目录 |
| `static_url_prefix` | '/static/' | 静态文件 URL 前缀 |
| `extra_static_paths` | [] | 额外静态文件路径 |
| `extra_template_paths` | [] | 额外模板路径 |

### 安全配置

| 配置项 | 默认值 | 说明 |
|--------|--------|------|
| `token` | 随机值 | 认证 Token |
| `disable_check_xsrf` | False | 禁用 XSRF 保护 |
| `allow_remote_access` | False | 允许远程访问 |
| `max_body_size` | 536870912 | 请求体大小上限（512MB） |
| `cookie_secret` | 随机值 | Cookie 加密密钥 |

### Manager 配置

| 配置项 | 默认值 | 说明 |
|--------|--------|------|
| `contents_manager_class` | AsyncFileContentsManager | 内容管理器类 |
| `kernel_manager_class` | AsyncMappingKernelManager | 内核管理器类 |
| `session_manager_class` | SessionManager | 会话管理器类 |
| `kernel_spec_manager_class` | KernelSpecManager | Kernelspec 管理器类 |
| `config_manager_class` | ConfigManager | 配置管理器类 |
| `identity_provider_class` | PasswordIdentityProvider | 身份提供者类 |
| `authorizer_class` | AllowAllAuthorizer | 授权器类 |

### 功能开关

| 配置项 | 默认值 | 说明 |
|--------|--------|------|
| `terminals_enabled` | True | 启用终端功能 |
| `nbconvert_enabled` | True | 启用 nbconvert 转换 |
| `open_browser` | True | 启动时打开浏览器 |
| `autoreload` | False | 文件修改自动重载（开发用） |
| `quit_button` | True | 显示退出按钮 |

## 环境变量

| 环境变量 | 说明 |
|---------|------|
| `JUPYTER_SERVER_PORT` | 默认端口 |
| `JUPYTER_SERVER_ROOT_DIR` | 根目录 |
| `JUPYTER_TOKEN` | 认证 Token |
| `JUPYTER_CONFIG_DIR` | 配置目录（默认 `~/.jupyter`） |
| `JUPYTER_DATA_DIR` | 数据目录 |
| `JUPYTER_RUNTIME_DIR` | 运行时文件目录 |
| `JUPYTER_PATH` | 额外搜索路径（冒号分隔） |

## 自定义 Manager 类

所有核心 Manager 都可以通过配置替换为自定义实现：

```python
from jupyter_server.services.contents.manager import ContentsManager

class MyContentsManager(ContentsManager):
    """自定义内容管理器（如 S3、数据库存储）"""
    def get(self, path, content=True, type=None, format=None):
        # 自定义实现
        ...

c.ServerApp.contents_manager_class = MyContentsManager
```

可替换的 Manager：
- `contents_manager_class`: 自定义文件存储（S3、数据库等）
- `kernel_manager_class`: 自定义内核管理（Kubernetes、远端等）
- `session_manager_class`: 自定义会话存储（数据库等）
- `identity_provider_class`: 自定义认证（OAuth、LDAP 等）
- `authorizer_class`: 自定义授权（RBAC、ACL 等）

## 相关概念

- [快速上手](01-getting-started.md) — 基本启动和配置命令
- [认证授权系统](05-auth-system.md) — 安全相关配置详解
- [内容管理服务](07-contents-service.md) — ContentsManager 配置选项

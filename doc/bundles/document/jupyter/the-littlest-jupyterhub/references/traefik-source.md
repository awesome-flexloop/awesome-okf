---
type: Reference
title: traefik.py 源码信源
description: tljh/traefik.py 模块公共 API 信源文档
tags: [reference, source, traefik, proxy, binary, configuration, api]
sources:
  - id: tljh-traefik
    title: tljh/traefik.py
---

# traefik.py 源码信源

> Traefik 反向代理管理模块。负责 Traefik 二进制文件下载/校验、静态和动态配置渲染、额外配置合并。

## 模块常量

```python
traefik_version = "3.6.5"
checksums = {
    "linux_amd64": "a9d891026496e0e16cbe4e0599339487411c9876246238c06bbe1a532350a096",
    "linux_arm64": "801449a26d1389aa60bbb96e79a8ecc8c385b2e76b1dcaf487fd712c427b2831",
}
```

架构映射在模块顶层通过 if-elif 实现：`os.uname().machine` 为 `aarch64` 时 `plat = "linux_arm64"`，`x86_64` 时 `plat = "linux_amd64"`，其他架构 `plat = None`。

## 公共函数

### `checksum_file(path_or_file) → str`

计算文件 SHA256 哈希。参数可以是文件路径字符串或文件对象。

### `check_traefik_version(traefik_bin) → bool`

执行 `<traefik_bin> version` 并解析输出，检查版本号是否匹配 traefik_version。

### `ensure_traefik_binary(prefix)`

**带重试**：`@backoff.on_exception(backoff.expo, max_tries=2)`
确保正确版本的 Traefik 二进制存在：
1. 检查目标路径已有二进制的版本，匹配则直接返回
2. 版本不匹配则删除旧二进制
3. 从 `https://github.com/traefik/traefik/releases/download/v{version}/traefik_v{version}_{os}_{arch}.tar.gz` 下载
4. SHA256 校验验证
5. 解压 traefik 二进制到 `{prefix}/bin/traefik`
6. chmod 0o755

### `load_extra_config(extra_config_dir) → dict`

glob 加载 `extra_config_dir` 下所有 `*.toml` 文件，使用 toml.load 解析并合并为一个 dict 返回。

### `ensure_traefik_config(state_dir)`

渲染 Traefik 静态和动态配置：
1. 加载配置（从 config.yaml）和 secrets（traefik-api.secret）
2. Jinja2 渲染 traefik.toml（静态配置模板）到 `{state_dir}/traefik.toml`
3. Jinja2 渲染动态 TLS 配置模板到 `{state_dir}/rules/dynamic.toml`
4. 调用 `load_extra_config` 合并额外配置目录中的 TOML 文件
5. 确保 `{state_dir}/rules/rules.toml` 存在（空文件，供 JupyterHub 写入路由）
6. 确保 `{state_dir}/acme.json` 存在，权限 0o600
7. HTTPS 启用时校验配置：
   - 使用手动证书：必须同时提供 tls.key 和 tls.cert
   - 使用 Let's Encrypt：必须提供 email 和至少一个 domain

## 模板文件

### traefik.toml.tpl

Traefik 静态配置 Jinja2 模板，渲染变量：
- `traefik_api`：ip, port, username, password
- `http`：address, port
- `https`：enabled, address, port
- `letsencrypt`：email, domains[], staging
- `traefik_dynamic_config_dir`：动态配置目录路径
- `acme_file`：acme.json 路径

关键配置：
- API 启用（dashboard 在 auth_api 入口点）
- 日志级别 INFO
- 访问日志 JSON 格式，过滤 5xx 状态码
- 敏感头（Authorization/Cookie/Set-Cookie/X-Xsrftoken）redact
- 入口点：http、https（条件）、auth_api
- HTTP 入口点 idleTimeout=10m
- HTTPS 启用时 http 自动重定向到 https
- Let's Encrypt 使用 TLS-ALPN-01 挑战
- 文件提供者 watch=true

### traefik-dynamic.toml.tpl

Traefik 动态配置 Jinja2 模板，渲染 TLS 配置：
- minVersion=TLS12
- 密码套件列表
- 手动证书或 Let's Encrypt 自动证书配置

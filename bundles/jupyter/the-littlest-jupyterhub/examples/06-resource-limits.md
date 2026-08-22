---
title: 设置用户资源限制
description: 为 TLJH 用户配置内存和 CPU 限制，防止单个用户占用过多资源
type: Example
tags: [example, limits, memory, cpu, cgroups, systemd, resource-management, jupyterhub, tljh, devops]
sources:
  - id: tljh-configurer
    title: tljh/configurer.py
  - id: tljh-config-schema
    title: tljh/config_schema.py
---

# 设置用户资源限制

本文档演示如何通过 TLJH 配置限制每个用户 Notebook 服务器的内存和 CPU 使用量，防止单个用户占用过多资源影响其他用户。

## 前置条件

- TLJH 已安装并运行
- 服务器启用了 cgroup v2（大多数现代 Linux 发行版默认启用）

## 内存限制

### 设置内存上限

```bash
# 限制每个用户服务器最多使用 4GB 内存
sudo tljh-config set limits.memory 4G
sudo tljh-config reload hub
```

支持的单位：
- `K` / `KB`：千字节
- `M` / `MB`：兆字节
- `G` / `GB`：吉字节
- `T` / `TB`：太字节

示例：

```bash
# 小团队服务器，每人 2GB
sudo tljh-config set limits.memory 2G

# 教学环境，每人 1GB
sudo tljh-config set limits.memory 1G

# 数据科学服务器，每人 8GB
sudo tljh-config set limits.memory 8G
```

### 内存限制的效果

- 当用户 Notebook 进程尝试使用超过限制的内存时，cgroup 会触发 OOM（Out of Memory），内核会杀死进程
- JupyterHub 会检测到进程被杀死，并在界面显示错误
- 用户需要重启内核或重新启动服务器
- 这不会影响其他用户的服务器

### 移除内存限制

```bash
sudo tljh-config unset limits.memory
sudo tljh-config reload hub
```

## CPU 限制

### 设置 CPU 上限

```bash
# 限制每个用户服务器最多使用 2 个 CPU 核心
sudo tljh-config set limits.cpu 2.0
sudo tljh-config reload hub
```

CPU 限制值是一个浮点数：
- `1.0`：最多使用 1 个核心的 CPU 时间
- `2.0`：最多使用 2 个核心
- `0.5`：最多使用半个核心

示例：

```bash
# 轻量使用，半核
sudo tljh-config set limits.cpu 0.5

# 中等使用，1核
sudo tljh-config set limits.cpu 1.0

# 较重计算，2核
sudo tljh-config set limits.cpu 2.0
```

### CPU 限制的效果

- CPU 限制通过 cgroup CPUQuota 实现
- 当用户尝试使用超过限制的 CPU 时，进程会被节流（throttled），但不会被杀死
- 这意味着计算会变慢，但不会中断

### 移除 CPU 限制

```bash
sudo tljh-config unset limits.cpu
sudo tljh-config reload hub
```

## 同时设置内存和 CPU

```bash
sudo tljh-config set limits.memory 4G
sudo tljh-config set limits.cpu 2.0
sudo tljh-config reload hub
```

## 查看当前限制

```bash
sudo tljh-config show | grep -A 3 limits
```

或者查看 systemd 运行时配置（以用户 jupyter-alice 为例）：

```bash
systemctl show jupyter-alice --property=MemoryMax
systemctl show jupyter-alice --property=CPUQuota
```

## 资源限制建议

根据服务器总资源和用户数量合理分配：

| 用户数 | 服务器内存 | 建议每人内存 | 服务器 CPU | 建议每人 CPU |
|--------|-----------|-------------|-----------|-------------|
| 5-10 | 16GB | 2-4G | 4核 | 1-2 |
| 10-20 | 32GB | 2-3G | 8核 | 1 |
| 20-50 | 64GB | 1-2G | 16核 | 0.5-1 |
| 50-100 | 128GB | 1G | 32核 | 0.5 |

> ⚠️ 这些是建议值，实际应根据使用场景调整。建议预留 20-30% 系统资源给 Hub、Traefik 和操作系统。

## 监控资源使用

安装 jupyter-resource-usage 扩展，让用户在 Notebook 界面看到自己的内存使用：

```bash
sudo -E pip install jupyter-resource-usage
```

用户在 JupyterLab 右上角会看到内存使用指示器。

## 结合空闲清理使用

资源限制配合 idle culler 使用效果更好——不活跃的服务器被自动停止，释放资源：

```bash
# 空闲30分钟后停止
sudo tljh-config set services.cull.enabled true
sudo tljh-config set services.cull.timeout 1800
sudo tljh-config set services.cull.every 300
sudo tljh-config reload hub
```

## 验证限制生效

用户登录并启动服务器后，检查 cgroup 限制：

```bash
# 查看某用户进程的内存限制
cat /sys/fs/cgroup/system.slice/jupyter-alice.service/memory.max

# 查看当前内存使用
cat /sys/fs/cgroup/system.slice/jupyter-alice.service/memory.current

# 查看 CPU 配额
cat /sys/fs/cgroup/system.slice/jupyter-alice.service/cpu.max
```

## 注意事项

1. **cgroup 要求**：资源限制依赖 Linux cgroups，必须在支持 cgroup 的系统上使用（TLJH 仅支持 systemd 系统，天然支持 cgroup v2）
2. **内核内存**：限制的是用户进程的总内存，包括 Notebook 内核和终端进程
3. **超限行为**：内存超限会杀死进程（OOM kill），CPU 超限只是节流
4. **共享环境**：User 环境共享意味着包只安装一份，但每个用户的数据和计算是独立的
5. **管理员不受限**：管理员用户启动的服务器同样受资源限制（限制是对 Spawner 的全局设置）

## 故障排查

### 限制不生效

1. 确认已 reload hub：`sudo tljh-config reload hub`
2. 确认配置正确：`sudo tljh-config show`
3. 用户需要**停止并重新启动**已有服务器（不只是刷新页面）
4. 检查 cgroup 是否可用：`mount | grep cgroup`

### 用户频繁遇到 OOM

- 适当提高内存限制
- 教育用户及时关闭不用的 Notebook 内核
- 启用 idle culler 自动停止空闲服务器

### 系统卡顿

- 检查总资源使用：`htop` 或 `free -h`
- 如果所有用户同时使用高资源，可能需要降低每用户限制或增加服务器资源

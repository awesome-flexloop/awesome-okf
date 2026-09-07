# 实战示例

本目录收录 Podman 在真实生产/开发环境下的端到端实战示例，每个示例均包含前置检查、命令流水线、验收矩阵与常见问题，可直接复制后按环境微调即可落地。

* [01 - CentOS/RHEL 系 Rootless Podman 生产部署](01-rootless-production.md) — EL9 平台 9 步零 sudo 生产部署：cgroup v2 前置检查 → subordinate ID → delegation → fuse-overlayfs 验证 → Nginx 容器 → systemd --user 自启 → firewalld 放行 → CPU/内存/PIDs 资源限制 → 验收矩阵 8 项 Checklist。
* [02 - Quadlet 部署三服务生产级容器栈](02-quadlet-stack.md) — 4 类 Quadlet 单元（.network 隔离子网 / .volume Postgres 持久化 / .container×3 三层服务）：Postgres 16 + Redis 7 + Node.js Web，含 systemd 启动顺序、Secret 注入、健康检查 SQL/PING/HTTP、资源上限、auto-update 滚动、ReadOnly + Tmpfs 加固、验收矩阵 7 项。

```{toctree}
:hidden:
:maxdepth: 7

01-rootless-production
02-quadlet-stack
```

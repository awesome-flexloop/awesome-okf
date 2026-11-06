# 概念文档（Concepts）

10 篇概念文档按交付顺序编号：全景与载荷（00-01）→ 安装期契约（02-05）→ 安装与分发（06-08）→ 门禁与排障（09）。

| 编号 | 文档 | 主题 |
|---|---|---|
| 00 | [全景：从 rootfs 到可安装发行版](00-overview.md) | 四层交付物、适用边界、术语表、五步最短路径 |
| 01 | [准备与打包 rootfs tar](01-rootfs-tar.md) | tar 内容、官方命令、gzip、去宿主化与验证 |
| 02 | [编写 /etc/wsl-distribution.conf](02-wsl-distribution-conf.md) | oobe、shortcut、windowsterminal 三节七键 |
| 03 | [编写 OOBE 首次启动脚本](03-oobe.md) | 运行语义、幂等、创建/加组/回滚、测试矩阵 |
| 04 | [编写 /etc/wsl.conf 并处理 systemd](04-wsl-conf-systemd.md) | `[boot] systemd`、9 个问题单元与屏蔽命令 |
| 05 | [生成 Windows Terminal 配置文件](05-terminal-profile.md) | profileTemplate JSON、配色方案、自动补全字段 |
| 06 | [创建 .wsl 文件并安装](06-wsl-file-install.md) | 扩展名、双击、`--from-file`、在线列表与验收 |
| 07 | [分发清单结构与本地测试](07-manifest-local-test.md) | ModernDistributions、flavor、注册表覆盖、file:// |
| 08 | [三档分发与企业/公开上架](08-enterprise-and-publishing.md) | 成员资格、PR 流程、企业治理与官方缺口 |
| 09 | [官方建议、发布门禁与故障排查](09-recommendations-checklist.md) | 20 项检查、四段门禁、失败模式速查 |

```{toctree}
:hidden:
:maxdepth: 2

00-overview
01-rootfs-tar
02-wsl-distribution-conf
03-oobe
04-wsl-conf-systemd
05-terminal-profile
06-wsl-file-install
07-manifest-local-test
08-enterprise-and-publishing
09-recommendations-checklist
```

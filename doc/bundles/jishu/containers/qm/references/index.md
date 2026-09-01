# QM 信源索引

本目录包含 QM 项目所有文档内容的可验证信源登记。

| 信源文件 | 内容说明 | 对应源码 |
|----------|---------|---------|
| [readme-source.md](readme-source.md) | 项目官方 README 和 man 手册：定位、安装、SELinux、BlueChi、OOM 策略 | README.md, qm.8.md |
| [qmctl-source.md](qmctl-source.md) | qmctl 管理工具：命令、Python 实现、辅助 Shell 脚本 | tools/qmctl/, tools/*.sh |
| [subsystem-source.md](subsystem-source.md) | 子系统扩展：kvm/wayland/ros2/sound/video、OCI hooks | subsystems/, oci-hooks/, rpm/ |

## 事实清单

所有事实的编号来源见 facts-qm.md。

```{toctree}
:hidden:
:maxdepth: 2

qmctl-source
readme-source
subsystem-source
```

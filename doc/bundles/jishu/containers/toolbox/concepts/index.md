# 概念文档

按学习路径排列的 4 篇核心概念文档，建议按顺序阅读。

## 入门篇

* [00-introduction.md](00-introduction.md) — Toolbx 项目定位与背景：Toolbx 规范名称（Toolb**x**）、二进制名 `toolbox`、Go 1.22.0、Apache-2.0 许可证；OSTree 不可变系统问题背景（Fedora Silverblue/CoreOS，/usr 只读，无传统包管理器工作流）；Toolbx 解决方案（完全可变特权容器，可自由 dnf install 不影响主机）；非 OSTree 系统同样适用；Podman + OCI 技术栈选型；透传优于隔离的设计哲学；与 Docker/Distrobox 区别对比。
* [01-pass-through.md](01-pass-through.md) — 主机资源透传机制：10 类透传资源详解（主目录、cwd、Wayland/X11 图形套接字、网络栈、SSH agent、D-Bus 会话/系统总线、systemd journal、ulimits、/dev 设备与 udev、可移动设备）；环境变量透传清单；`/run/host` 万能逃生口挂载机制；容器内标识（⬢ 提示符、/run/.containerenv + /run/.toolboxenv 判断文件）；rootless 模式安全模型说明。

## 核心篇

* [02-workflow.md](02-workflow.md) — 日常开发工作流：三大核心命令详解——`toolbox create`（创建容器，--distro/--release/--image/--container 选项，默认命名规则 `<distro>-toolbox-<release>`）、`toolbox enter`（交互式进入，提示符变化，exit 离开容器不删除）、`toolbox run`（非交互式单命令执行，适合脚本调用）；生命周期管理——`list -c/-i`、`rm [-f/-a]`、`rmi [-f/-a]`；最佳实践（单容器 vs 多容器策略、Shell 别名、进入即工作模式、脚本中使用、全局选项 -v/-vv 排障）；完整命令速查表。
* [03-custom-images.md](03-custom-images.md) — 自定义镜像与高级用法：自定义镜像适用场景（团队统一环境、预装工具链、企业 CA、特殊发行版）；Toolbx 镜像必备特征（POSIX shell、sudo、useradd、/run/host 挂载点、com.github.containers.toolbox 标签）；三种构建方式（基于官方镜像扩展推荐、从基础镜像从头构建、社区工具）；Containerfile 编写示例；/run/host 逃生口 5 个高级场景（访问主机目录、chroot 故障排查、调用主机二进制、共享包缓存、跨容器共享）；自定义镜像版本标签、profile.d 环境配置、预装 vs dotfiles vs 手动安装决策矩阵；NVIDIA GPU 支持说明。

```{toctree}
:hidden:
:maxdepth: 2

00-introduction
01-pass-through
02-workflow
03-custom-images
```

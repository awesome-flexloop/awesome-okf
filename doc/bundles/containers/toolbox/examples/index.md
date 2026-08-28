# 示例文档

包含 2 个循序渐进的实战示例。

## 示例清单

* [01-first-toolbox.md](01-first-toolbox.md) — 创建第一个开发容器：Fedora/Arch/Ubuntu 多发行版安装方法；`toolbox create` 默认创建流程（首次镜像拉取提示、默认命名规则）；`toolbox enter` 交互式进入（⬢ 提示符变化识别）；容器内 `sudo dnf install` 安装 gcc/gdb/Go/Python/Node.js 开发工具链；主目录透传验证（编译产物在主机直接可见）；图形应用运行（Firefox）；`toolbox run` 非交互式单命令执行与 Shell 脚本集成；exit 离开容器（容器持久化保留）；`toolbox list/rm/rmi` 生命周期管理；subuid/subgid 配置等常见问题排查；10 项验证检查清单。
* [02-custom-image.md](02-custom-image.md) — 构建自定义 Toolbx 镜像：基于官方 `fedora-toolbox:39` 扩展编写 Containerfile；com.github.containers.toolbox 必需标签；dnf 包安装与 clean all 同层缓存清理；/etc/profile.d/go-dev.sh 环境变量配置；Vim 全局配置；`podman build -t localhost/go-dev-toolbox:v1.0.0` 构建；`toolbox create -i <image> -c go-dev` 基于自定义镜像创建容器；6 项镜像功能验证（Go 版本、环境变量、工具链、透传、网络、实际项目编译）；Go 工具 gopls/dlv/staticcheck 安装与 GOPATH 持久化；多阶段构建、分层缓存、.containerignore 等镜像优化技巧；推送到 Quay.io 远程 registry 团队共享；常见问题解答。

```{toctree}
:hidden:
:maxdepth: 2

01-first-toolbox
02-custom-image
```

# 示例文档

包含 5 个循序渐进的实战示例：01-02 为入门与自定义镜像，03-05 为实现层对应的多发行版、GPU 与测试体系实战。

## 示例清单

* [01-first-toolbox.md](01-first-toolbox.md) — 创建第一个开发容器：Fedora/Arch/Ubuntu 多发行版安装方法；`toolbox create` 默认创建流程（首次镜像拉取提示、默认命名规则）；`toolbox enter` 交互式进入（⬢ 提示符变化识别）；容器内 `sudo dnf install` 安装 gcc/gdb/Go/Python/Node.js 开发工具链；主目录透传验证（编译产物在主机直接可见）；图形应用运行（Firefox）；`toolbox run` 非交互式单命令执行与 Shell 脚本集成；exit 离开容器（容器持久化保留）；`toolbox list/rm/rmi` 生命周期管理；subuid/subgid 配置等常见问题排查；10 项验证检查清单。
* [02-custom-image.md](02-custom-image.md) — 构建自定义 Toolbx 镜像：基于官方 `fedora-toolbox:39` 扩展编写 Containerfile；com.github.containers.toolbox 必需标签；dnf 包安装与 clean all 同层缓存清理；/etc/profile.d/go-dev.sh 环境变量配置；Vim 全局配置；`podman build -t localhost/go-dev-toolbox:v1.0.0` 构建；`toolbox create -i <image> -c go-dev` 自定义镜像容器创建；6 项镜像功能验证（Go 版本、环境变量、工具链、透传、网络、实际项目编译）；Go 工具 gopls/dlv/staticcheck 安装与 GOPATH 持久化；多阶段构建、分层缓存、.containerignore 等镜像优化技巧；推送到 Quay.io 远程 registry 团队共享；常见问题解答。
* [03-multi-distro.md](03-multi-distro.md) — 多发行版容器实战：Ubuntu 24.04（quay.io/toolbx）、RHEL 9.3（registry.access.redhat.com/ubi9）、Arch（latest/rolling）创建进入全流程；distro-release-镜像-容器名对照表；release 校验拒绝规则；多容器并行与 -c 显式命名；toolbox.conf 持久化默认 distro/release/image；7 项跨发行版透传一致性验证与常见问题。
* [04-nvidia-gpu.md](04-nvidia-gpu.md) — NVIDIA GPU 容器实战：主机驱动/nvidia-container-toolkit 前提；零参数创建 GPU 容器与 -vv 日志观察；/dev/nvidia 设备、nvidia-smi、toolbx-nvidia.conf 验证；CUDA hello.cu 编译运行；cdi-nvidia.json spec 三段解读；驱动版本不匹配等 6 类故障排查表；与 230-cdi 冒烟测试对照。
* [05-system-tests.md](05-system-tests.md) — 运行与扩展 BATS 系统测试：bats ≥1.10 依赖与子模块初始化；TMPDIR=/var/tmp 与 TOOLBX 变量；localhost:50000 认证 registry（user/user，fedora-toolbox:34）；用例命名与 setup/teardown 约定；新增用例模板；CDI JSON 夹具驱动无 GPU 测试；11 个 Ansible playbook 复现 CI 环境。

```{toctree}
:hidden:
:maxdepth: 2

01-first-toolbox
02-custom-image
03-multi-distro
04-nvidia-gpu
05-system-tests
```

# 信源登记簿

本目录登记 Toolbx OKF Wiki 所有内容文档的事实来源，遵循「信源先行」原则——所有概念文档和示例文档的 frontmatter `sources` 字段均指向本目录下的信源文件。

## 信源文件清单

* [README.md 项目概览与定位](readme-source.md) — `README.md`、`doc/toolbox.1.md`：项目定位（Toolbx 名称迁移、Go 1.22.0、Apache-2.0）、OSTree 不可变系统背景、10 项主机资源透传清单、4 个支持发行版（Arch/Fedora/RHEL/Ubuntu）、fedora-toolbox 默认镜像、/run/host 主机逃生口、安全边界说明。
* [src/cmd/ 命令行接口与核心命令](cmd-source.md) — `src/cmd/root.go`、`src/cmd/create.go`、`src/cmd/enter.go`、`src/cmd/run.go`、`src/go.mod`：cobra CLI 框架、rootCmd 根命令定义、4 个全局选项（-y/--log-level/--log-podman/-v）、7 个核心子命令（create/enter/run/list/rm/rmi/completion）、8 个内部 pkg 包结构、10 个主要 Go 依赖、Meson 构建系统。

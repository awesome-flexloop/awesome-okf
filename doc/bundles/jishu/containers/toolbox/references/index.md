# 信源登记簿

本目录登记 Toolbx OKF Wiki 所有内容文档的事实来源，遵循「信源先行」原则——所有概念文档和示例文档的 frontmatter `sources` 字段均指向本目录下的信源文件。

## 信源文件清单

* [README.md 项目概览与定位](readme-source.md) — `README.md`、`doc/toolbox.1.md`：项目定位（Toolbx 名称迁移、Go 1.22.0、Apache-2.0）、OSTree 不可变系统背景、10 项主机资源透传清单、4 个支持发行版（Arch/Fedora/RHEL/Ubuntu）、fedora-toolbox 默认镜像、/run/host 主机逃生口、安全边界说明。
* [src/cmd/ 命令行接口与核心命令](cmd-source.md) — `src/cmd/root.go`、`src/cmd/create.go`、`src/cmd/enter.go`、`src/cmd/run.go`、`src/go.mod`：cobra CLI 框架、rootCmd 根命令定义、4 个全局选项（-y/--log-level/--log-podman/-v）、7 个核心子命令（create/enter/run/list/rm/rmi/completion）、8 个内部 pkg 包结构、10 个主要 Go 依赖、Meson 构建系统。
* [实现层源码地图](source-code-map.md) — 第二轮信源，锚定 commit 81401f64：src/cmd 13 个非测试文件的内部实现（create/initContainer/run 等）、src/pkg 7 个子包（podman/shell/skopeo/nvidia/term/utils/version）逐文件 URL、go-build-wrapper、profile.d、data、test/system、playbooks、images 构建资产。
* [官方手册、设计目标与版本演进信源](docs-man-source.md) — doc/ 10 个 man 页（9 个 section 1 + toolbox.conf.5）、GOALS.md（三条非目标）、NEWS 0.1.2-0.3（CVE 与特性演进）逐文件 URL 与官方意图/代码互证要点。

```{toctree}
:hidden:
:maxdepth: 2

cmd-source
docs-man-source
readme-source
source-code-map
```

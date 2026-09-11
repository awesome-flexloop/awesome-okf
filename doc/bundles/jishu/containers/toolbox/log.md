# Changelog

## v1.1.0 (2026-09-11)

### 新增

第二轮多轮增量扩展（实现层源码深读，信源锚定 commit 81401f64b3865129ea66f2a5e02a7eb40edd4fb8 / 0.3-85-g81401f6），新增 12 个文档：

- 7 篇概念文档（编号续接）：
  - 04-podman-argv-layer.md：外部 CLI 编排器架构、pkg/podman 命令映射、JSON 双形态、版本门控
  - 05-name-resolution.md：4 发行版 Distro 注册表、名称解析三级优先级、toolbox.conf、43 个环境变量白名单、libsubid 校验
  - 06-create-argv.md：podman create argv 解剖（14 个安全/namespace 参数、固定与条件挂载、socket 发现、拉取确认）
  - 07-init-container.md：容器内引导八步、15 条 rbind、Kerberos/PKCS#11/RPM 配置、初始化戳记协议
  - 08-cross-distro-binary.md：/run/host 动态链接策略、-z lazy、CoreOS 双构建标签
  - 09-nvidia-cdi.md：CNCF CDI 生成-传递-应用三段式、NVML 探测矩阵、无硬件静默降级
  - 10-build-and-tests.md：Meson 构建、22 个 BATS 系统测试、CI/playbook、四族官方镜像
- 3 篇示例文档：
  - 03-multi-distro.md：Ubuntu/RHEL/Arch 多发行版容器实战与 toolbox.conf
  - 04-nvidia-gpu.md：NVIDIA GPU 透传验证与排障
  - 05-system-tests.md：BATS 系统测试运行与扩展
- 2 篇信源登记：
  - source-code-map.md：src/pkg、cmd 内部、构建脚本、profile.d、data、test、images 逐文件 URL（锚定 81401f64）
  - docs-man-source.md：doc/ 10 个 man 页、GOALS.md、NEWS 信源
- 各级 index.md（表格 + toctree）追加新文档；束根索引更新学习路径与计数（8→20 个内容文档）。

### 事实来源

- 约 120 条编号事实（F-001~F-197）+ 10 条计数断言，存于工作区 `.trae/specs/okf-wiki-ecosystem/toolbox-source-okf-wiki/facts.md`；
- 计数断言经脚本独立复核并修正两处目测错误（环境变量 42→43、man 页 9→10）；
- 关键 API/函数/路径经 V 阶段 Grep 比对 vendor/toolbox 源码；
- 新增文档跨轮引用第一轮 readme/cmd 信源，未重写已验证的第一轮文档结论。

## v1.0.0 (2026-08-26)

### 新增

- 初始版本，基于 Toolbx（github.com/containers/toolbox）源码深度阅读生成
- 4 篇概念文档：
  - 00-introduction.md：项目定位与 OSTree 不可变系统背景
  - 01-pass-through.md：主机资源透传机制
  - 02-workflow.md：日常开发工作流（create/enter/run/list/rm/rmi）
  - 03-custom-images.md：自定义镜像与 /run/host 逃生口
- 2 篇示例文档：
  - 01-first-toolbox.md：创建第一个开发容器完整流程
  - 02-custom-image.md：构建自定义 Go 开发环境镜像
- 2 篇信源登记文件：
  - readme-source.md：README.md 项目概览
  - cmd-source.md：src/cmd/ 命令行接口与核心命令
- 3 个目录索引文件 + 根索引与本日志

# 概念文档索引

按学习路径顺序排列，建议从00开始依次阅读。

| 编号 | 文档 | 核心内容 |
|------|------|----------|
| [00](00-introduction.md) | 项目介绍 | 项目定位、核心特性、模板变量、适用场景 |
| [01](01-getting-started.md) | 快速上手 | 安装cookiecutter、生成项目、构建、测试、运行全流程 |
| [02](02-template-structure.md) | 模板结构解析 | 生成项目目录结构、各文件职责、协同关系 |
| [03](03-cookiecutter-variables.md) | 模板变量详解 | 4个模板变量、14个基础镜像选项、预设配置文件用法 |
| [04](04-dockerfile-template.md) | Dockerfile模板与编写指南 | Dockerfile结构、非root安全模型、包安装规范、常见错误 |
| [05](05-testing-framework.md) | 测试框架详解 | TrackedContainer类、pytest fixtures、自定义测试编写 |
| [06](06-cicd-workflow.md) | CI/CD工作流 | GitHub Actions流水线、触发条件、Docker Hub集成 |
| [07](07-devcontainer.md) | Dev Container开发环境 | VS Code开发容器、Docker-in-Docker、推荐扩展 |
| [08](08-config-presets.md) | 预设配置与基础镜像选择 | 14个预设配置、镜像继承关系、场景化选择指南 |
| [09](09-best-practices.md) | 最佳实践 | Dockerfile编写、安全、性能、版本管理、测试、CI/CD |

```{toctree}
:hidden:

00-introduction
01-getting-started
02-template-structure
03-cookiecutter-variables
04-dockerfile-template
05-testing-framework
06-cicd-workflow
07-devcontainer
08-config-presets
09-best-practices
```

---
type: Reference
title: Awesome OKF for Xuanspace
sources:
  - id: xuanspace-readme
    resource: https://github.com/xinetzone/xuanspace
    title: XuanSpace（玄境）README 结构模板
---

# Awesome OKF for Xuanspace

> 技术为器、思想为道，器以载道

![License: Apache-2.0](https://img.shields.io/badge/License-Apache--2.0-green)

## 关于本库

**awesome-okf-xs** 是 [XuanSpace（玄境）](https://github.com/xinetzone/xuanspace) 项目的**开源知识格式（Open Knowledge Format，OKF）文档库**。

它承载玄境项目"道"的一面——将文档、复盘、洞察、模式、最佳实践等知识资产，以 OKF 格式统一组织、存储与发布；与承载"器"（代码与工具）的 xuanspace 正反向协同，共同实践"器以载道"的理念。

## 特性亮点

- 📚 **OKF 格式**：以开源知识格式（OKF）组织结构化知识文档
- 🧩 **bundle 组织**：知识文档以 OKF bundle（知识束）为单位组织与索引
- 🧭 **以 xuanspace 为基底**：内容来源于玄境项目，规范模板继承自 xuanspace
- 🤖 **AI Agent 就绪**：内置 AGENTS.md 与 `.agents/` 规范目录，支持 AI 协作
- 🔗 **相对路径引用**：文档交叉引用统一使用相对路径，便于跨仓库迁移

## 目录结构

```
awesome-okf-xs/
├── bundles/          # OKF bundle 文档（结构化知识束）
├── docs/             # 通用文档与索引
├── references/       # 参考资料与原始来源
├── .agents/          # AI 智能体规范目录
├── AGENTS.md         # 智能体协作入口
└── README.md         # 本文件 - 项目说明
```

## 快速开始

### 前置条件

- Git
- 任意支持 Markdown 与 YAML frontmatter 的编辑器

### 本地使用

1. 克隆仓库：

   ```bash
   git clone git@github.com:awesome-flexloop/awesome-okf.git
   ```

2. 浏览文档：进入 `bundles/` 查看已组织的知识束，或从 `docs/index.md` 开始

3. AI 协作：阅读 [AGENTS.md](AGENTS.md) 了解智能体协作规范

## 已收录知识束（Bundles）

| Bundle | 路径 | 简介 |
|---|---|---|
| OKF 规范中文转译知识包 | [bundles/okf-spec/](bundles/okf-spec/) | OKF v0.2 规范中文转译知识包（15 概念 + 3 示例 + 1 信源），权威信源为 [GoogleCloudPlatform/knowledge-catalog](https://github.com/GoogleCloudPlatform/knowledge-catalog) 的 SPEC.md |

## 文档与资源

- 🤖 **AI 协作**：详见 [AGENTS.md](AGENTS.md)
- 🤝 **基底项目**：[xinetzone/xuanspace](https://github.com/xinetzone/xuanspace)
- 🐛 **问题反馈**：[GitHub Issues](https://github.com/awesome-flexloop/awesome-okf/issues)

## 许可证

Apache License 2.0 - 详见 [LICENSE](LICENSE) 文件。
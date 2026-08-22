# litegitpuller 架构洞察与知识地图（I阶段）

## 核心架构洞察

### 洞察1：纯前端URL驱动的Git克隆，无服务端依赖

- **陈述**：litegitpuller 是一个纯前端 JupyterLab 扩展，完全通过浏览器端 fetch API 调用 GitHub/GitLab 的 REST API 来"克隆"仓库，不依赖 Jupyter 服务端的 Git 操作。
- **证据**：F-025（getFileList 为抽象方法，由子类通过 fetch 实现）、F-043（GithubPuller 使用 GitHub API v3 的 `/git/trees` 和 `/contents` 端点）、F-047（GitlabPuller 使用 GitLab API v4 的 `/repository/tree` 和 `/repository/files` 端点）、F-007（Python 包无运行时依赖）
- **反常识**：它不是真正的 `git clone`——而是通过 API 递归遍历文件树、逐文件下载内容再通过 JupyterLab 的 Contents API 写入文件系统。初学者可能以为它在服务端执行 git 命令。
- **行动**：概念文档需明确区分"API拉取"与"git clone"的差异，在入门文档中就讲清工作原理。

### 洞察2：模板方法模式——抽象基类定义克隆流程，子类实现平台差异

- **陈述**：`GitPuller` 抽象基类通过模板方法模式（Template Method）定义了完整的克隆流程（创建目录树→获取文件列表→创建子目录→逐文件下载上传→错误报告），而将平台相关的 API 调用（`getFileList`、`getFile`）委托给具体子类 `GithubPuller` 和 `GitlabPuller` 实现。
- **证据**：F-019~F-024（clone 方法实现完整流程）、F-025~F-026（两个抽象方法）、F-042~F-048（两个子类仅实现这两个抽象方法）
- **反常识**：新增 Git 平台支持（如 Gitea、Bitbucket）只需继承 GitPuller 并实现两个方法即可，不需要修改 clone 主流程——但平台适配的 URL 转换逻辑写在 index.ts 的 activate 函数中而非工厂类中。
- **行动**：核心概念文档需详细讲解模板方法模式在此处的应用，examples 中可展示如何自定义 Puller。

### 洞察3：nbgitpuller 冲突检测机制

- **陈述**：扩展激活时首先通过 HTTP 请求检测服务端是否安装了 nbgitpuller（请求 `/git-pull/api` 端点），如果检测到则自身不激活，避免两者重复拉取同一仓库。
- **证据**：F-049~F-051（testNbGitPuller 函数及 activate 中的检测逻辑）
- **反常识**：litegitpuller 主要面向 JupyterLite（纯浏览器环境无服务端 Git），但代码中仍做了与服务端 nbgitpuller 的兼容检测，这说明它也可以在常规 JupyterLab 中使用。
- **行动**：概念文档需说明与 nbgitpuller 的关系和区别。

### 洞察4：文件上传的两阶段策略（根路径创建→重命名）

- **陈述**：`createFile` 方法不直接在目标路径创建文件，而是先在根路径创建一个唯一命名的临时文件，上传后再 rename 到目标路径。这是因为 JupyterLab 的 upload API 要求文件先上传到根目录。
- **证据**：F-031~F-033（createFile 中 while 循环确保根目录无同名冲突，upload 后 rename）
- **反常识**：文件名冲突处理只在根目录层面做了唯一化（加数字前缀），目标路径上已存在的文件会直接跳过并记录错误（F-022），不会覆盖也不会重命名。
- **行动**：在讲解文件操作流程时需强调这一行为，避免用户误以为文件会被更新。

### 洞察5：URL参数即配置——零UI的极简设计

- **陈述**：整个扩展没有任何 UI 组件（无菜单、无按钮、无对话框），完全通过 URL 查询参数（repo、branch、provider、urlpath、uploadpath）驱动工作，CSS 文件为空。
- **证据**：F-052~F-060（所有配置从 URLSearchParams 获取）、F-014~F-016（样式文件无实际CSS）、F-058（requires 仅 IDefaultFileBrowser，无额外UI token）
- **反常识**：这意味着用户无法在 JupyterLab 界面中手动触发克隆，必须通过构造URL的方式使用——链接生成器（nbgitpuller link generator）是实际使用时的关键工具。
- **行动**：入门文档必须重点讲解URL参数构造方式，examples 中给出各种URL构造示例。

## 知识地图

### 文档分组与学习路径

```
入门（零基础理解）
├── 00-introduction.md    → 什么是litegitpuller、与nbgitpuller区别、适用场景
├── 01-getting-started.md → 安装方法、URL参数详解、第一个使用示例
│
核心（理解工作原理）
├── 02-architecture.md    → 整体架构、模板方法模式、数据流
├── 03-gitpuller-base.md  → GitPuller抽象基类、clone流程、文件操作
├── 04-platform-pullers.md → GithubPuller/GitlabPuller实现、API差异
├── 05-extension-plugin.md → JupyterLab插件结构、激活逻辑、nbgitpuller检测
│
高级（扩展与限制）
├── 06-url-parameters.md  → URL参数完整参考、链接生成
├── 07-limitations.md     → API速率限制、大仓库限制、不支持的Git特性
└── 08-custom-provider.md → 自定义Puller、扩展新平台
```

### 示例文档清单

```
examples/
├── 01-basic-github.md     → GitHub仓库拉取基础示例
├── 02-gitlab-repo.md      → GitLab仓库拉取示例
├── 03-open-notebook.md    → 拉取后自动打开Notebook
├── 04-custom-uploadpath.md → 自定义上传路径
└── index.md
```

### 信源文档清单

```
references/
├── index-ts-source.md     → src/index.ts 信源（插件激活、URL解析、nbgitpuller检测）
├── gitpuller-ts-source.md → src/gitpuller.ts 信源（GitPuller/GithubPuller/GitlabPuller类）
├── python-package-source.md → litegitpuller/__init__.py 信源（Python包结构）
├── build-config-source.md  → pyproject.toml/package.json 信源（构建配置）
└── index.md
```

### 事实覆盖映射

| 文档 | 覆盖事实 |
|------|---------|
| 00-introduction.md | F-001~F-008, F-060~F-061 |
| 01-getting-started.md | F-052~F-060, F-006 |
| 02-architecture.md | F-009~F-010, F-017~F-024, F-042~F-048 |
| 03-gitpuller-base.md | F-017~F-041 |
| 04-platform-pullers.md | F-042~F-048, F-055~F-056 |
| 05-extension-plugin.md | F-005, F-036~F-037, F-049~F-059 |
| 06-url-parameters.md | F-052~F-060 |
| 07-limitations.md | F-061, F-022~F-023, F-040 |
| 08-custom-provider.md | F-025~F-026, F-042~F-048 |

## G2 质量门自检

- [x] 每个洞察包含四元组：陈述、证据（引用F-xxx）、反常识、行动
- [x] 知识地图包含文档分组（入门/核心/高级）、依赖关系、学习路径
- [x] 文档清单覆盖 concepts/examples/references
- [x] 每个概念文档明确了覆盖的事实编号

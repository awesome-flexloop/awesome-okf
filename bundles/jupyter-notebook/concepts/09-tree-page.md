---
title: 文件浏览器与Tree页面
type: concept
bundle: jupyter-notebook
okf-version: "0.2"
chapter: "09"
difficulty: beginner
tags: ["frontend", "tree", "file-browser", "routing"]
prerequisites: ["01-architecture-overview", "04-handlers"]
sources: ["F-022"]
next: ["10-frontend-packages"]
---

# 09 | 文件浏览器与Tree页面

Tree页面是Notebook的默认入口（`/tree`），提供文件浏览器功能，是用户管理Notebook文件、启动终端、创建新文档的主要界面。

## TreeHandler路由逻辑

TreeHandler是Tree页面的后端入口，路由 `/tree(.*)`，其 `get()` 方法实现了智能路由逻辑：

```python
class TreeHandler(NotebookBaseHandler):
    @web.authenticated
    async def get(self, path: str = "") -> None:
        path = path.strip("/")
        cm = self.contents_manager

        if await ensure_async(cm.dir_exists(path=path)):
            # 目录 → 显示tree页面
            if await ensure_async(cm.is_hidden(path)) and not cm.allow_hidden:
                raise web.HTTPError(404)
            page_config = self.get_page_config()
            page_config["treePath"] = path
            tpl = self.render_template("tree.html", page_config=page_config)
            return self.write(tpl)

        if await ensure_async(cm.file_exists(path)):
            # 文件 → 根据类型重定向
            model = await ensure_async(cm.get(path, content=False))
            if model["type"] == "notebook":
                url = ujoin(self.base_url, "notebooks", url_escape(path))
            else:
                url = ujoin(self.base_url, "files", url_escape(path))
            self.redirect(url)
            return None

        raise web.HTTPError(404)
```

> **信源**: [app.py:L133-170](file:///d:/spaces/SpecWeave/external/libs/jupyter/notebook/notebook/app.py#L133-L170)（F-022）

### 路由决策树

```
访问 /tree/<path>
       │
       ▼
  path是目录吗？
       ├── 是 ──→ 是隐藏目录且不允许隐藏？
       │           ├── 是 ──→ 404
       │           └── 否 ──→ 渲染tree.html，设置treePath
       │
       └── 否 ──→ path是文件吗？
                   ├── 是 ──→ 文件类型是notebook？
                   │           ├── 是 ──→ 重定向到 /notebooks/<path>
                   │           └── 否 ──→ 重定向到 /files/<path>
                   │
                   └── 否 ──→ 404
```

### 设计亮点

1. **统一入口**: `/tree` 既是文件浏览器URL，也是文件访问URL，后端智能判断
2. **自动跳转**: 直接访问 `.ipynb` 文件的 `/tree/` URL会自动跳转到Notebook编辑器
3. **隐藏文件保护**: 隐藏目录（`.`开头）默认404，可通过 `ContentsManager.allow_hidden = True` 开启
4. **异步兼容**: 使用 `ensure_async()` 兼容同步和异步ContentsManager

## page_config.treePath

当访问目录时，TreeHandler在page_config中设置 `treePath` 字段：

```python
page_config["treePath"] = path  # 如 "subfolder/data"
```

前端JavaScript读取此值来确定初始显示的目录。根目录访问时 `treePath` 为空字符串（即根目录）。

## 前端Tree组件

Tree页面的前端功能由以下包提供：

| npm包 | 职责 |
|-------|------|
| `@jupyter-notebook/tree` | NotebookTree主widget |
| `@jupyter-notebook/tree-extension` | 文件操作命令、widget工厂 |
| `@jupyterlab/filebrowser` (JupyterLab) | 核心文件浏览器组件 |

### NotebookTree

`NotebookTree` 是Tree页面的主widget，包含：
- 文件浏览器面板（FileBrowser）
- 启动器卡片（Launcher Card：新建Notebook/Console/Terminal）
- 上传按钮
- 新建文件/文件夹按钮

### 文件操作

tree-extension注册了以下核心命令：

```typescript
// 文件操作命令（示例）
"filebrowser:open"          // 打开选中文件
"filebrowser:rename"        // 重命名
"filebrowser:delete"        // 删除
"filebrowser:duplicate"     // 复制
"filebrowser:shutdown"      // 关闭kernel
"filebrowser:mkdir"         // 新建文件夹
"filebrowser:new-file"      // 新建文件
"filebrowser:upload"        // 上传文件
```

## 与NotebookHandler的协作

TreeHandler和NotebookHandler之间有双向重定向：

| 访问URL | 实际文件 | 处理 |
|---------|---------|------|
| `/tree/mydir/` | mydir是目录 | 显示tree页面，进入mydir |
| `/tree/nb.ipynb` | nb.ipynb是notebook文件 | 重定向 → `/notebooks/nb.ipynb` |
| `/tree/data.csv` | data.csv是普通文件 | 重定向 → `/files/data.csv` |
| `/notebooks/mydir/` | mydir是目录 | 重定向 → `/tree/mydir/` |
| `/notebooks/nb.ipynb` | nb.ipynb存在 | 显示Notebook编辑器 |

**注意**：NotebookHandler和TreeHandler形成了一个**URL规范化层**——无论用户使用哪个URL前缀访问，最终都会跳转到正确的页面类型。

## 默认URL

```python
default_url = Unicode("/tree", config=True)
```

> **信源**: [app.py:L251](file:///d:/spaces/SpecWeave/external/libs/jupyter/notebook/notebook/app.py#L251)

`default_url = "/tree"` 意味着访问 `http://localhost:8888/` 会自动跳转到 `http://localhost:8888/tree`，即文件浏览器页面。

可以通过配置修改默认URL：

```python
# 配置默认打开JupyterLab界面
c.LabServerApp.default_url = "/lab"

# 配置默认打开某个Notebook
c.JupyterNotebookApp.default_url = "/notebooks/welcome.ipynb"
```

## 前端URL路由

前端通过IRouter处理页面内导航：

```typescript
// application-extension中的路由处理
const TREE_PATTERN = new RegExp('/(notebooks|edit)/(.*)');
```

当用户在SPA内导航时：
1. Router捕获URL变化
2. 匹配TREE_PATTERN判断是Notebook还是编辑器
3. 调用对应命令打开文件
4. 更新浏览器URL（不刷新页面）

## 文件类型检测

后端通过 `ContentsManager.get()` 获取文件模型，根据 `model["type"]` 判断文件类型：

| type值 | 打开方式 |
|--------|---------|
| `"notebook"` | 重定向到 `/notebooks/` → Notebook编辑器 |
| `"directory"` | 显示tree页面 |
| `"file"` | 重定向到 `/files/` → 根据MIME类型渲染（下载/预览/编辑） |

Jupyter的ContentsManager使用文件扩展名和内容检测来确定文件类型，`.ipynb` 文件被识别为 `"notebook"` 类型。

## 隐藏文件处理

```python
if await ensure_async(cm.is_hidden(path)) and not cm.allow_hidden:
    self.log.info("Refusing to serve hidden directory, via 404 Error")
    raise web.HTTPError(404)
```

默认情况下，隐藏文件/目录（Unix下以 `.` 开头）返回404。开启方式：

```python
c.ContentsManager.allow_hidden = True
```

## 自定义Tree页面

### 自定义模板

Tree页面使用Jinja2模板 `tree.html`。通过修改模板可以添加自定义HTML。

但在v7中，推荐通过前端插件方式扩展Tree页面，而非修改模板。

### 前端扩展Tree页面

```typescript
import { INotebookTree } from '@jupyter-notebook/tree';

const treePlugin: JupyterFrontEndPlugin<void> = {
    id: 'my-extension:tree',
    autoStart: true,
    requires: [INotebookTree],
    activate: (app: JupyterFrontEnd, tree: INotebookTree) => {
        // 在Tree页面添加自定义widget
        const myWidget = new MyWidget();
        tree.addWidget(myWidget);
    }
};
```

## 下一步

- → [前端包结构](./10-frontend-packages.md) 了解各npm包的职责划分

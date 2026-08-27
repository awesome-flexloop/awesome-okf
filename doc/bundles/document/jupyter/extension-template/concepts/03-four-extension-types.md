---
type: Concept
title: 四种扩展类型对比与选型
description: 详细对比 frontend、mimerenderer、frontend-and-server、theme 四种扩展类型的架构差异、适用场景和生成代码的区别。
tags: [extension-types, frontend, mimerenderer, server, theme, comparison]
generated: { by: "source-code-to-okf-wiki", at: "2026-08-22T12:20:00Z" }
verified: { by: "process:seven-concepts-v", at: "2026-08-22T12:20:00Z" }
status: stable
stale_after: 2027-08-22
sources:
  - id: copier-config
    resource: /references/copier-config.md
    title: Copier 配置参数全参考
  - id: frontend-entry
    resource: /references/frontend-entry-source.md
    title: 前端入口模板解析
  - id: server-routes
    resource: /references/server-routes-source.md
    title: Python 服务端模板解析
---

## 四种扩展类型对比

extension-template 支持四种 JupyterLab 扩展类型，它们在架构复杂度、技术栈和适用场景上有显著差异。选择正确的类型是开发扩展的第一步。

## 类型对比总览

| 维度 | frontend | mimerenderer | frontend-and-server | theme |
|------|----------|-------------|---------------------|-------|
| **技术栈** | TypeScript | TypeScript | TS + Python | CSS + TS |
| **后端代码** | ❌ | ❌ | ✅（tornado APIHandler） | ❌ |
| **核心 API** | JupyterFrontEndPlugin | IRenderMime.IExtension | 前后端双插件 | IThemeManager |
| **生成 Python 包** | ✅（仅分发） | ✅（仅分发） | ✅（含路由逻辑） | ✅（仅分发） |
| **设置系统** | 可选 | ❌ | 可选 | ❌ |
| **适用场景** | 添加 UI/命令/面板 | 自定义 MIME 类型渲染 | 需要后端计算/IO | 修改界面外观 |

## frontend（纯前端扩展）

**适用场景**：为 JupyterLab 添加新的 UI 组件、命令面板项、菜单栏、侧边栏面板、快捷键、文件编辑器等。这是最常用的扩展类型。

**核心代码结构**：

```typescript
// src/index.ts
import { JupyterFrontEnd, JupyterFrontEndPlugin } from '@jupyterlab/application';

const plugin: JupyterFrontEndPlugin<void> = {
  id: 'myextension:plugin',
  autoStart: true,
  activate: (app: JupyterFrontEnd) => {
    console.log('JupyterLab extension myextension is activated!');
    // 在这里添加命令、菜单项、widget 等
  }
};
export default plugin;
```

**关键依赖**：
- `@jupyterlab/application: ^4.0.0`
- 可选：`@jupyterlab/settingregistry`（设置）

**activate 生命周期**：JupyterLab 启动时自动调用 `activate` 函数，接收 `JupyterFrontEnd` 实例（即 JupyterLab 应用对象），通过它可以访问命令系统、文档注册表、服务管理器等。

## mimerenderer（MIME 渲染器）

**适用场景**：当 notebook 或文件输出特定 MIME 类型的数据时（如 `application/vnd.geo+json`、`application/x-custom-type`），提供自定义的渲染方式，替代默认的文本显示。

**核心代码结构**：

```typescript
// src/index.ts
import { IRenderMime } from '@jupyterlab/rendermime-interfaces';
import { Widget } from '@lumino/widgets';

export class OutputWidget extends Widget implements IRenderMime.IRenderer {
  constructor(options: IRenderMime.IRendererOptions) {
    super();
    this._mimeType = options.mimeType;
    this.addClass('mimerenderer-my_type');
  }

  renderModel(model: IRenderMime.IMimeModel): Promise<void> {
    const data = model.data[this._mimeType] as string;
    this.node.textContent = data.slice(0, 16384);
    return Promise.resolve();
  }
  private _mimeType: string;
}

const extension: IRenderMime.IExtension = {
  id: 'myextension:plugin',
  rendererFactory: { safe: true, mimeTypes: [MIME_TYPE], createRenderer: ... },
  rank: 100,
  dataType: 'string',
  fileTypes: [{ name: 'my_type', mimeTypes: [MIME_TYPE], extensions: ['.my_type'] }],
  documentWidgetFactoryOptions: { name: 'My Viewer', ... }
};
export default extension;
```

**专用参数**（生成时询问）：
- `mimetype`：MIME 类型标识符（如 `application/vnd.my-org.my-type`）
- `mimetype_name`：简短名称（用于文件类型注册）
- `file_extension`：关联文件扩展名（如 `.my_type`）
- `viewer_name`：查看器显示名称
- `data_format`：数据格式（`string` 或 `json`）

**安全模型**：`rendererFactory.safe` 属性标记渲染器是否能安全处理不受信任的 notebook 数据。`safe: true` 表示渲染经过清理的安全输出（如文本、图片）；`safe: false` 表示渲染活动内容（如 HTML/JS），在不受信任的 notebook 中会显示"Run cell to view output"提示。

## frontend-and-server（全栈扩展）

**适用场景**：需要后端计算能力的扩展，如访问文件系统、启动子进程、调用 Python 科学计算库、操作数据库、代理外部 API 等。前端通过 REST API 与后端通信。

**前端核心代码**：与 frontend 类似，但额外导入 `requestAPI` 函数：

```typescript
// src/index.ts
import { requestAPI } from './request';

const plugin: JupyterFrontEndPlugin<void> = {
  id: 'myextension:plugin',
  autoStart: true,
  activate: (app: JupyterFrontEnd) => {
    requestAPI<any>('hello', app.serviceManager.serverSettings)
      .then(data => console.log(data))
      .catch(reason => console.error('Server extension missing!', reason));
  }
};
```

**后端核心代码**：

```python
# myextension/routes.py
from jupyter_server.base.handlers import APIHandler
import tornado, json

class HelloRouteHandler(APIHandler):
    @tornado.web.authenticated
    def get(self):
        self.finish(json.dumps({"data": "Hello from server!"}))

def setup_route_handlers(web_app):
    base_url = web_app.settings["base_url"]
    route = url_path_join(base_url, "myextension", "hello")
    web_app.add_handlers(".*$", [(route, HelloRouteHandler)])
```

```python
# myextension/__init__.py
from .routes import setup_route_handlers

def _jupyter_server_extension_points():
    return [{"module": "myextension"}]

def _load_jupyter_server_extension(server_app):
    setup_route_handlers(server_app.web_app)
```

**关键设计要点**：
- URL 命名空间：`/{{ python_name | replace('_', '-') }}/endpoint`（下划线转连字符）
- 所有 HTTP 方法必须加 `@tornado.web.authenticated` 装饰器
- 前端使用 `requestAPI<T>()` 函数（封装了 `ServerConnection.makeRequest`）
- CI 中有 `check_auth.py` 脚本自动检查所有端点是否都有认证装饰器

**额外依赖**：
- Python: `jupyter_server>=2.13.0,<3`
- JS: `@jupyterlab/coreutils: ^6.0.0`、`@jupyterlab/services: ^7.0.0`

## theme（主题扩展）

**适用场景**：自定义 JupyterLab 的整体外观，包括颜色、字体、间距等。主题通过覆盖 JupyterLab 的 CSS 变量实现。

**核心代码结构**：

```typescript
// src/index.ts
import { JupyterFrontEnd, JupyterFrontEndPlugin } from '@jupyterlab/application';
import { IThemeManager } from '@jupyterlab/apputils';

const plugin: JupyterFrontEndPlugin<void> = {
  id: 'mytheme:plugin',
  autoStart: true,
  requires: [IThemeManager],
  activate: (app: JupyterFrontEnd, manager: IThemeManager) => {
    const style = 'mytheme/index.css';
    manager.register({
      name: 'mytheme',
      isLight: true,
      load: () => manager.loadCSS(style),
      unload: () => Promise.resolve(undefined)
    });
  }
};
export default plugin;
```

**样式文件结构**：
- `style/variables.css`：定义 CSS 自定义属性（覆盖 JupyterLab 默认变量）
- `style/index.css`：@import variables.css 并添加自定义样式

**关键 CSS 变量**：JupyterLab 定义了 100+ 个 CSS 变量（`--jp-*` 前缀），涵盖颜色、字体、边框、阴影、布局等。主题通过重新定义这些变量实现外观定制。

**isLight 属性**：标记主题是亮色（`true`）还是暗色（`false`），JupyterLab 据此切换默认图标颜色和某些组件的渲染方式。

## 条件渲染矩阵

模板通过 Jinja2 条件块在同一套文件中生成不同类型的代码。以下是关键文件的条件分支：

| 文件 | frontend | theme | frontend-and-server | mimerenderer |
|------|----------|-------|---------------------|--------------|
| `src/index.ts` | JupyterFrontEndPlugin | IThemeManager 注册 | +requestAPI 调用 | IRenderMime.IExtension |
| `src/request.ts` | ❌ 不生成 | ❌ 不生成 | ✅ 生成 | ❌ 不生成 |
| `{{python_name}}/__init__.py` | 仅 _jupyter_labextension_paths | 同 frontend | +server extension 点 | 同 frontend |
| `{{python_name}}/routes.py` | ❌ 不生成 | ❌ 不生成 | ✅ 生成 | ❌ 不生成 |
| `schema/plugin.json` | 可选(has_settings) | 可选(has_settings) | 可选(has_settings) | ❌ 不生成 |
| `style/variables.css` | ❌ 不生成 | ✅ 生成 | ❌ 不生成 | ❌ 不生成 |
| `pyproject.toml deps` | 空 | 空 | jupyter_server | 空 |

## 如何选择

1. **想加按钮/命令/面板** → frontend
2. **想渲染自定义数据格式** → mimerenderer
3. **需要调用 Python 库或访问系统资源** → frontend-and-server
4. **想改变界面颜色和样式** → theme

如果不确定，从 frontend 开始——它是最简单也是最灵活的类型，后续可以添加 server 组件或拆分为多插件。

## 相关概念

- [前端扩展开发](06-frontend-extension.md)
- [服务端扩展开发](07-server-extension.md)
- [MIME 渲染器开发](08-mime-renderer.md)
- [主题扩展开发](09-theme-extension.md)
- [生成项目结构详解](04-project-structure.md)

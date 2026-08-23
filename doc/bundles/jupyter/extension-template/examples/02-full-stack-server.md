---
type: Example
title: 全栈扩展：前后端通信
description: 创建一个 frontend-and-server 类型的扩展，实现后端 API 端点、前端调用和数据展示。
tags: [full-stack, server, api, frontend-and-server, backend, communication]
generated: { by: "source-code-to-okf-wiki", at: "2026-08-22T12:20:00Z" }
verified: { by: "process:seven-concepts-v", at: "2026-08-22T12:20:00Z" }
status: stable
stale_after: 2027-08-22
prerequisites:
  - 理解服务端扩展开发：/concepts/07-server-extension.md
  - 理解前端扩展开发：/concepts/06-frontend-extension.md
---

## 全栈扩展：前后端通信

本示例创建一个全栈扩展，后端提供 `/hello` 和 `/greet` 两个 API 端点，前端通过按钮点击调用后端 API 并展示返回数据。

## 步骤 1：生成项目

```bash
mkdir greet-extension && cd greet-extension
copier copy --trust https://github.com/jupyterlab/extension-template .
```

选择：
- extension kind: **frontend-and-server**
- JS package name: **greet-extension**
- Python package name: **greet_extension**
- user settings: **No**
- tests: **No**

## 步骤 2：安装开发环境

```bash
pip install -e ".[dev]"
jupyter-builder develop . --overwrite
jlpm install
jlpm build
```

验证后端扩展注册：
```bash
jupyter server extension list
# 应显示 greet_extension OK
```

## 步骤 3：自定义后端端点

修改 `greet_extension/routes.py`：

```python
import json
from jupyter_server.base.handlers import APIHandler
from jupyter_server.utils import url_path_join
import tornado

class HelloHandler(APIHandler):
    @tornado.web.authenticated
    def get(self):
        self.finish(json.dumps({
            "message": "Hello from Jupyter Server!"
        }))

class GreetHandler(APIHandler):
    @tornado.web.authenticated
    def get(self):
        name = self.get_argument("name", "World")
        self.finish(json.dumps({
            "message": f"Hello, {name}!"
        }))

    @tornado.web.authenticated
    def post(self):
        body = json.loads(self.request.body)
        name = body.get("name", "World")
        self.finish(json.dumps({
            "message": f"POST: Greetings, {name}!"
        }))

def setup_route_handlers(web_app):
    host_pattern = ".*$"
    base_url = web_app.settings["base_url"]

    handlers = [
        (url_path_join(base_url, "greet-extension", "hello"), HelloHandler),
        (url_path_join(base_url, "greet-extension", "greet"), GreetHandler),
    ]

    web_app.add_handlers(host_pattern, handlers)
```

> 注意：URL 命名空间使用连字符（`greet-extension`），而不是下划线。Python 包名 `greet_extension` 中的 `_` 在 URL 中转为 `-`。

## 步骤 4：编写前端代码

修改 `src/index.ts`：

```typescript
import {
  JupyterFrontEnd,
  JupyterFrontEndPlugin
} from '@jupyterlab/application';

import { requestAPI } from './request';
import { Widget } from '@lumino/widgets';

class GreetWidget extends Widget {
  private _output: HTMLPreElement;
  private _input: HTMLInputElement;

  constructor(serverSettings: any) {
    super();
    this.addClass('greet-extension-widget');
    this.id = 'greet-extension-panel';
    this.title.label = 'Greet';
    this.title.closable = true;

    // 创建 UI 元素
    const header = document.createElement('h2');
    header.textContent = 'Server Communication Demo';

    this._input = document.createElement('input');
    this._input.type = 'text';
    this._input.placeholder = 'Enter your name';
    this._input.value = 'World';

    const btnHello = document.createElement('button');
    btnHello.textContent = 'Say Hello (GET)';
    btnHello.onclick = async () => {
      try {
        const data = await requestAPI<any>('hello', serverSettings);
        this._output.textContent = JSON.stringify(data, null, 2);
      } catch (e) {
        this._output.textContent = `Error: ${e}`;
      }
    };

    const btnGreet = document.createElement('button');
    btnGreet.textContent = 'Greet Me (GET with param)';
    btnGreet.onclick = async () => {
      try {
        const name = encodeURIComponent(this._input.value);
        const data = await requestAPI<any>(`greet?name=${name}`, serverSettings);
        this._output.textContent = JSON.stringify(data, null, 2);
      } catch (e) {
        this._output.textContent = `Error: ${e}`;
      }
    };

    const btnPostGreet = document.createElement('button');
    btnPostGreet.textContent = 'Post Greeting (POST)';
    btnPostGreet.onclick = async () => {
      try {
        const data = await requestAPI<any>('greet', serverSettings, {
          method: 'POST',
          body: JSON.stringify({ name: this._input.value })
        });
        this._output.textContent = JSON.stringify(data, null, 2);
      } catch (e) {
        this._output.textContent = `Error: ${e}`;
      }
    };

    this._output = document.createElement('pre');
    this._output.className = 'greet-output';

    const controls = document.createElement('div');
    controls.className = 'greet-controls';
    controls.appendChild(this._input);
    controls.appendChild(btnHello);
    controls.appendChild(btnGreet);
    controls.appendChild(btnPostGreet);

    this.node.appendChild(header);
    this.node.appendChild(controls);
    this.node.appendChild(this._output);
  }
}

const plugin: JupyterFrontEndPlugin<void> = {
  id: 'greet-extension:plugin',
  autoStart: true,
  activate: (app: JupyterFrontEnd) => {
    console.log('greet-extension activated!');

    const { commands, shell } = app;

    commands.addCommand('greet-extension:open', {
      label: 'Open Greet Panel',
      execute: () => {
        const widget = new GreetWidget(app.serviceManager.serverSettings);
        shell.add(widget, 'main');
        shell.activateById(widget.id);
      }
    });
  }
};

export default plugin;
```

## 步骤 5：添加样式

修改 `style/base.css`：

```css
.greet-extension-widget {
  padding: 16px;
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.greet-controls {
  display: flex;
  gap: 8px;
  flex-wrap: wrap;
}

.greet-controls input {
  padding: 6px 10px;
  border: 1px solid var(--jp-border-color1);
  border-radius: var(--jp-border-radius);
}

.greet-controls button {
  padding: 6px 12px;
  background: var(--jp-brand-color1);
  color: white;
  border: none;
  border-radius: var(--jp-border-radius);
  cursor: pointer;
}

.greet-controls button:hover {
  background: var(--jp-brand-color0);
}

.greet-output {
  padding: 12px;
  background: var(--jp-layout-color2);
  border-radius: var(--jp-border-radius);
  font-family: var(--jp-code-font-family);
  font-size: var(--jp-code-font-size);
  white-space: pre-wrap;
  min-height: 100px;
}
```

## 步骤 6：运行测试

```bash
# 终端 1
jlpm run watch

# 终端 2 - 重启 jupyter lab（改了 Python 代码必须重启）
jupyter lab
```

打开命令面板（Ctrl+Shift+C），搜索 "Open Greet Panel"，点击三个按钮测试：
- **Say Hello** → GET `/greet-extension/hello` → 返回 "Hello from Jupyter Server!"
- **Greet Me** → GET `/greet-extension/greet?name=YourName` → 返回个性化问候
- **Post Greeting** → POST `/greet-extension/greet` with JSON body → 返回 POST 问候

## 关键点总结

1. **URL 命名空间**：Python 包名 `greet_extension` → URL `/greet-extension/`（`_` 转 `-`）
2. **认证装饰器**：所有 HTTP 方法必须加 `@tornado.web.authenticated`
3. **requestAPI**：封装了 `ServerConnection.makeRequest`，自动处理认证 token 和 base URL
4. **POST 请求**：通过 `init` 参数传入 `{ method: 'POST', body: JSON.stringify(...) }`
5. **Python 代码变更**：修改 `.py` 文件后必须**重启 JupyterLab 服务器**

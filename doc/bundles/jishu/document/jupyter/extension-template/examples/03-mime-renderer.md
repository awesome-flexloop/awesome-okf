---
type: Example
title: 自定义 MIME 渲染器
description: 创建一个 mimerenderer 类型的扩展，为自定义 JSON 数据格式提供可视化渲染。
tags: [mimerenderer, visualization, custom-mime, renderer, json]
generated: { by: "source-code-to-okf-wiki", at: "2026-08-22T12:20:00Z" }
verified: { by: "process:seven-concepts-v", at: "2026-08-22T12:20:00Z" }
status: stable
stale_after: 2027-08-22
prerequisites:
  - 理解 MIME 渲染器开发：/concepts/08-mime-renderer.md
---

## 自定义 MIME 渲染器

本示例创建一个 MIME 渲染器扩展，为 `application/x-person` 类型的 JSON 数据提供美观的卡片式渲染。

## 步骤 1：生成项目

```bash
mkdir person-renderer && cd person-renderer
copier copy --trust https://github.com/jupyterlab/extension-template .
```

选择：
- extension kind: **mimerenderer**
- MIME type: **application/x-person**
- MIME type name: **person**
- File extension: **.person**
- Viewer name: **Person Viewer**
- Data format: **json**
- JS package name: **person-renderer**
- Python package name: **person_renderer**
- tests: **No**

## 步骤 2：安装

```bash
pip install -e ".[dev]"
jupyter-builder develop . --overwrite
jlpm install
jlpm build
```

## 步骤 3：自定义渲染逻辑

修改 `src/index.ts`：

```typescript
import { IRenderMime } from '@jupyterlab/rendermime-interfaces';
import { JSONObject } from '@lumino/coreutils';
import { Widget } from '@lumino/widgets';

const MIME_TYPE = 'application/x-person';
const CLASS_NAME = 'mimerenderer-person';

interface PersonData {
  name: string;
  age?: number;
  role?: string;
  avatar?: string;
  bio?: string;
}

export class OutputWidget extends Widget implements IRenderMime.IRenderer {
  constructor(options: IRenderMime.IRendererOptions) {
    super();
    this._mimeType = options.mimeType;
    this.addClass(CLASS_NAME);
  }

  renderModel(model: IRenderMime.IMimeModel): Promise<void> {
    const data = model.data[this._mimeType] as PersonData;

    // 创建卡片
    const card = document.createElement('div');
    card.className = 'person-card';

    // 头像
    if (data.avatar) {
      const img = document.createElement('img');
      img.src = data.avatar;
      img.className = 'person-avatar';
      card.appendChild(img);
    } else {
      const placeholder = document.createElement('div');
      placeholder.className = 'person-avatar-placeholder';
      placeholder.textContent = data.name?.charAt(0).toUpperCase() || '?';
      card.appendChild(placeholder);
    }

    // 信息区
    const info = document.createElement('div');
    info.className = 'person-info';

    const name = document.createElement('h3');
    name.textContent = data.name || 'Unknown';
    info.appendChild(name);

    if (data.role) {
      const role = document.createElement('span');
      role.className = 'person-role';
      role.textContent = data.role;
      info.appendChild(role);
    }

    if (data.age !== undefined) {
      const age = document.createElement('span');
      age.className = 'person-age';
      age.textContent = `${data.age} years old`;
      info.appendChild(age);
    }

    if (data.bio) {
      const bio = document.createElement('p');
      bio.className = 'person-bio';
      bio.textContent = data.bio;
      info.appendChild(bio);
    }

    card.appendChild(info);
    this.node.appendChild(card);

    return Promise.resolve();
  }

  private _mimeType: string;
}

export const rendererFactory: IRenderMime.IRendererFactory = {
  safe: true,
  mimeTypes: [MIME_TYPE],
  createRenderer: options => new OutputWidget(options)
};

const extension: IRenderMime.IExtension = {
  id: 'person-renderer:plugin',
  rendererFactory,
  rank: 100,
  dataType: 'json',
  fileTypes: [{
    name: 'person',
    mimeTypes: [MIME_TYPE],
    extensions: ['.person']
  }],
  documentWidgetFactoryOptions: {
    name: 'Person Viewer',
    primaryFileType: 'person',
    fileTypes: ['person'],
    defaultFor: ['person']
  }
};

export default extension;
```

## 步骤 4：添加样式

创建/修改 `style/base.css`：

```css
.mimerenderer-person {
  padding: 12px;
}

.person-card {
  display: flex;
  gap: 16px;
  padding: 16px;
  background: var(--jp-layout-color1);
  border: 1px solid var(--jp-border-color2);
  border-radius: 8px;
  box-shadow: var(--jp-elevation-z2);
  max-width: 400px;
}

.person-avatar {
  width: 64px;
  height: 64px;
  border-radius: 50%;
  object-fit: cover;
  flex-shrink: 0;
}

.person-avatar-placeholder {
  width: 64px;
  height: 64px;
  border-radius: 50%;
  background: var(--jp-brand-color1);
  color: white;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 28px;
  font-weight: bold;
  flex-shrink: 0;
}

.person-info {
  display: flex;
  flex-direction: column;
  gap: 4px;
}

.person-info h3 {
  margin: 0;
  color: var(--jp-ui-font-color0);
  font-size: var(--jp-ui-font-size3);
}

.person-role {
  color: var(--jp-brand-color1);
  font-weight: 500;
}

.person-age {
  color: var(--jp-ui-font-color2);
  font-size: var(--jp-ui-font-size0);
}

.person-bio {
  margin: 4px 0 0 0;
  color: var(--jp-ui-font-color1);
  font-size: var(--jp-ui-font-size1);
  line-height: 1.4;
}
```

## 步骤 5：测试渲染器

构建并启动 JupyterLab：

```bash
jlpm run watch  # 终端 1
jupyter lab     # 终端 2
```

在 JupyterLab 中测试：

### 方法 1：创建 .person 文件

1. 新建一个文本文件，命名为 `test.person`
2. 写入 JSON 内容：
```json
{
  "name": "Alice Zhang",
  "age": 28,
  "role": "Data Scientist",
  "bio": "Passionate about machine learning and open source."
}
```
3. 保存文件，双击打开 → 应该看到渲染的卡片

### 方法 2：在 Notebook 中输出 MIME 数据

```python
from IPython.display import display
import json

data = {
    "name": "Bob Li",
    "age": 35,
    "role": "Software Engineer",
    "bio": "Building tools for data scientists.",
    "avatar": "https://example.com/bob.jpg"
}

display({
    "application/x-person": data
}, raw=True)
```

## 关键点总结

1. **`safe: true`**：此渲染器只做 DOM 渲染，不执行脚本或网络请求，所以标记为安全
2. **`dataType: 'json'`**：JupyterLab 会自动将 JSON 数据解析为 JavaScript 对象
3. **renderModel 每次调用都会重建 DOM**：如果需要更新数据而不重建，可以使用 model.setData() 触发重新渲染
4. **文件扩展名注册**：`.person` 文件会自动用此渲染器打开
5. **使用 CSS 变量**：样式使用 `var(--jp-*)` 以自动适配主题

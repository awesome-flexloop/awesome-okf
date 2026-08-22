---
type: Example
title: 创建自定义暗色主题
description: 创建一个暗色主题扩展，修改 CSS 变量实现深色界面外观。
tags: [theme, dark-mode, css-variables, appearance, styling]
generated: { by: "source-code-to-okf-wiki", at: "2026-08-22T12:20:00Z" }
verified: { by: "process:seven-concepts-v", at: "2026-08-22T12:20:00Z" }
status: stable
stale_after: 2027-08-22
prerequisites:
  - 理解主题扩展开发：/concepts/09-theme-extension.md
---

## 创建自定义暗色主题

本示例创建一个基于蓝色调的暗色主题。

## 步骤 1：生成项目

```bash
mkdir midnight-theme && cd midnight-theme
copier copy --trust https://github.com/jupyterlab/extension-template .
```

选择：
- extension kind: **theme**
- JS package name: **midnight-theme**
- Python package name: **midnight_theme**
- tests: **No**

## 步骤 2：安装

```bash
pip install -e ".[dev]"
jupyter-builder develop . --overwrite
jlpm install
jlpm build
```

## 步骤 3：修改主题注册代码

修改 `src/index.ts`，设置 `isLight: false`：

```typescript
import {
  JupyterFrontEnd,
  JupyterFrontEndPlugin
} from '@jupyterlab/application';
import { IThemeManager } from '@jupyterlab/apputils';

const plugin: JupyterFrontEndPlugin<void> = {
  id: 'midnight-theme:plugin',
  autoStart: true,
  requires: [IThemeManager],
  activate: (app: JupyterFrontEnd, manager: IThemeManager) => {
    const style = 'midnight-theme/index.css';

    manager.register({
      name: 'Midnight Theme',
      isLight: false,              // 暗色主题
      load: () => manager.loadCSS(style),
      unload: () => Promise.resolve(undefined),
      themeScrollbars: true         // 自定义滚动条
    });
  }
};

export default plugin;
```

## 步骤 4：自定义 CSS 变量

修改 `style/variables.css`。以下是一个完整的暗色主题配置：

```css
:root {
  /* 阴影：暗色主题需要更高的 base-lightness */
  --jp-shadow-base-lightness: 200;
  --jp-shadow-umbra-color: rgba(200, 200, 200, 0.2);
  --jp-shadow-penumbra-color: rgba(200, 200, 200, 0.14);
  --jp-shadow-ambient-color: rgba(200, 200, 200, 0.12);

  /* Elevation（复用默认值，因为 base-lightness 已调整） */
  --jp-elevation-z0: none;
  --jp-elevation-z1: 0 2px 1px -1px var(--jp-shadow-umbra-color),
                     0 1px 1px 0 var(--jp-shadow-penumbra-color),
                     0 1px 3px 0 var(--jp-shadow-ambient-color);
  --jp-elevation-z2: 0 3px 1px -2px var(--jp-shadow-umbra-color),
                     0 2px 2px 0 var(--jp-shadow-penumbra-color),
                     0 1px 5px 0 var(--jp-shadow-ambient-color);
  --jp-elevation-z4: 0 2px 4px -1px var(--jp-shadow-umbra-color),
                     0 4px 5px 0 var(--jp-shadow-penumbra-color),
                     0 1px 10px 0 var(--jp-shadow-ambient-color);
  --jp-elevation-z8: 0 5px 5px -3px var(--jp-shadow-umbra-color),
                     0 8px 10px 1px var(--jp-shadow-penumbra-color),
                     0 3px 14px 2px var(--jp-shadow-ambient-color);
  --jp-elevation-z16: 0 8px 10px -5px var(--jp-shadow-umbra-color),
                      0 16px 24px 2px var(--jp-shadow-penumbra-color),
                      0 6px 30px 5px var(--jp-shadow-ambient-color);
  --jp-elevation-z24: 0 11px 15px -7px var(--jp-shadow-umbra-color),
                      0 24px 38px 3px var(--jp-shadow-penumbra-color),
                      0 9px 46px 8px var(--jp-shadow-ambient-color);

  /* 边框 */
  --jp-border-width: 1px;
  --jp-border-color0: #1e3a5f;
  --jp-border-color1: #1e3a5f;
  --jp-border-color2: #152d4a;
  --jp-border-color3: #0f2238;
  --jp-border-radius: 2px;

  /* UI 字体 */
  --jp-ui-font-scale-factor: 1.2;
  --jp-ui-font-size0: 0.8333em;
  --jp-ui-font-size1: 13px;
  --jp-ui-font-size2: 1.2em;
  --jp-ui-font-size3: 1.44em;
  --jp-ui-font-family: -apple-system, blinkmacsystemfont, 'Segoe UI', helvetica, arial, sans-serif;

  /* UI 字体颜色（暗色背景上的浅色文字） */
  --jp-ui-font-color0: rgba(255, 255, 255, 1);
  --jp-ui-font-color1: rgba(255, 255, 255, 0.87);
  --jp-ui-font-color2: rgba(255, 255, 255, 0.54);
  --jp-ui-font-color3: rgba(255, 255, 255, 0.38);

  --jp-ui-inverse-font-color0: rgba(0, 0, 0, 1);
  --jp-ui-inverse-font-color1: rgba(0, 0, 0, 0.87);
  --jp-ui-inverse-font-color2: rgba(0, 0, 0, 0.54);
  --jp-ui-inverse-font-color3: rgba(0, 0, 0, 0.38);

  /* 内容字体 */
  --jp-content-line-height: 1.6;
  --jp-content-font-size1: 14px;
  --jp-content-font-color0: rgba(255, 255, 255, 1);
  --jp-content-font-color1: rgba(255, 255, 255, 0.87);
  --jp-content-font-color2: rgba(255, 255, 255, 0.54);
  --jp-content-font-color3: rgba(255, 255, 255, 0.38);
  --jp-content-link-color: #64b5f6;
  --jp-content-font-family: -apple-system, blinkmacsystemfont, 'Segoe UI', helvetica, arial, sans-serif;

  /* 代码字体 */
  --jp-code-font-size: 13px;
  --jp-code-line-height: 1.3077;
  --jp-code-font-family: 'Fira Code', menlo, consolas, 'DejaVu Sans Mono', monospace;

  /* 布局颜色（深蓝暗色） */
  --jp-layout-color0: #0a1929;      /* 最深背景（编辑器区域） */
  --jp-layout-color1: #0f2744;      /* 主背景（面板、工具栏） */
  --jp-layout-color2: #163556;      /* 次要背景（侧边栏） */
  --jp-layout-color3: #1e4a72;      /* 高亮/悬停背景 */
  --jp-layout-color4: #2a5d8f;      /* 最深前景色 */

  /* 反布局颜色 */
  --jp-inverse-layout-color0: #e3f2fd;
  --jp-inverse-layout-color1: #bbdefb;
  --jp-inverse-layout-color2: #90caf9;
  --jp-inverse-layout-color3: #64b5f6;
  --jp-inverse-layout-color4: #42a5f5;

  /* 品牌色（蓝色调） */
  --jp-brand-color0: #1976d2;
  --jp-brand-color1: #2196f3;
  --jp-brand-color2: #42a5f5;
  --jp-brand-color3: #64b5f6;

  /* 强调色 */
  --jp-accent-color0: #2e7d32;
  --jp-accent-color1: #4caf50;
  --jp-accent-color2: #81c784;
  --jp-accent-color3: #a5d6a7;

  /* 状态颜色 */
  --jp-warn-color0: #e65100;
  --jp-warn-color1: #ff9800;
  --jp-error-color0: #c62828;
  --jp-error-color1: #f44336;
  --jp-success-color0: #2e7d32;
  --jp-success-color1: #4caf50;
  --jp-info-color0: #01579b;
  --jp-info-color1: #03a9f4;

  /* 单元格编辑器 */
  --jp-cell-editor-background: #0d1f33;
  --jp-cell-editor-border-color: #1a3a5c;
  --jp-cell-editor-active-background: var(--jp-layout-color0);
  --jp-cell-editor-active-border-color: var(--jp-brand-color1);

  /* 输入框 */
  --jp-input-background: #0d1f33;
  --jp-input-border-color: #1a3a5c;
  --jp-input-active-background: #0a1929;
  --jp-input-active-border-color: var(--jp-brand-color1);

  /* 编辑器选中 */
  --jp-editor-selected-background: #1a3a5c;
  --jp-editor-selected-focused-background: #1a4a7c;

  /* CodeMirror 语法高亮（暗色适配） */
  --jp-mirror-editor-keyword-color: #c792ea;     /* 紫色 */
  --jp-mirror-editor-atom-color: #f78c6c;        /* 橙色 */
  --jp-mirror-editor-number-color: #f78c6c;      /* 橙色 */
  --jp-mirror-editor-def-color: #82aaff;         /* 蓝色 */
  --jp-mirror-editor-variable-color: #e0e0e0;
  --jp-mirror-editor-variable-2-color: #89ddff;
  --jp-mirror-editor-property-color: #c792ea;
  --jp-mirror-editor-operator-color: #89ddff;
  --jp-mirror-editor-comment-color: #546e7a;
  --jp-mirror-editor-string-color: #c3e88d;      /* 绿色 */
  --jp-mirror-editor-string-2-color: #89ddff;
  --jp-mirror-editor-meta-color: #ffcb6b;
  --jp-mirror-editor-builtin-color: #82aaff;
  --jp-mirror-editor-tag-color: #f07178;
  --jp-mirror-editor-attribute-color: #c792ea;
  --jp-mirror-editor-quote-color: #c3e88d;
  --jp-mirror-editor-link-color: #82aaff;
  --jp-mirror-editor-error-color: #ff5370;

  /* 工具栏 */
  --jp-toolbar-background: var(--jp-layout-color1);
  --jp-toolbar-border-color: var(--jp-border-color1);
  --jp-toolbar-active-background: var(--jp-layout-color3);

  /* Rendermime */
  --jp-rendermime-error-background: #2a1a1a;
  --jp-rendermime-table-row-background: var(--jp-layout-color2);
  --jp-rendermime-table-row-hover-background: var(--jp-layout-color3);

  /* 对话框 */
  --jp-dialog-background: rgba(0, 0, 0, 0.6);

  /* 状态栏 */
  --jp-statusbar-height: 24px;

  /* In/Out 提示符 */
  --jp-cell-inprompt-font-color: #82aaff;
  --jp-cell-outprompt-font-color: #f78c6c;

  /* Jupyter 图标 */
  --jp-jupyter-icon-color: #f37726;
  --jp-notebook-icon-color: #f37726;

  /* 滚动条暗色样式 */
  --jp-scrollbar-background-color: var(--jp-layout-color2);
  --jp-scrollbar-thumb-color: var(--jp-layout-color4);
  --jp-scrollbar-endpad: 3px;
}
```

## 步骤 5：添加自定义滚动条样式

修改 `style/index.css`，在 import 之后添加滚动条样式：

```css
@import url('./variables.css');

/* 暗色滚动条样式 */
::-webkit-scrollbar {
  width: 10px;
  height: 10px;
}

::-webkit-scrollbar-track {
  background: var(--jp-layout-color1);
}

::-webkit-scrollbar-thumb {
  background: var(--jp-layout-color3);
  border-radius: 5px;
}

::-webkit-scrollbar-thumb:hover {
  background: var(--jp-brand-color1);
}

/* 代码字体默认设置 */
tt, code, kbd, samp, pre {
  font-family: var(--jp-code-font-family);
  font-size: var(--jp-code-font-size);
  line-height: var(--jp-code-line-height);
}
```

## 步骤 6：测试主题

```bash
jlpm run watch
jupyter lab
```

在 JupyterLab 中切换主题：
1. 菜单栏 → Settings → Theme → **Midnight Theme**
2. 界面应该变成深蓝色的暗色主题
3. 检查 notebook、文件浏览器、终端、设置面板等区域的显示

## 调优建议

1. **不要一次改所有变量**：先改布局颜色和字体颜色，再调整品牌色和语法高亮
2. **使用浏览器 DevTools**：在 DevTools 中实时修改 CSS 变量预览效果
3. **检查对比度**：使用 Chrome DevTools 的对比度检查工具确保文字可读
4. **参考官方暗色主题**：对比 `@jupyterlab/theme-dark-extension` 的变量值
5. **测试所有面板**：Notebook、文件编辑器、终端、命令面板、设置编辑器都要检查

## 关键点总结

1. **`isLight: false`** 必须设置，否则 JupyterLab 会按亮色主题渲染图标
2. **`--jp-shadow-base-lightness`** 必须调大（如 200），否则暗色上阴影不可见
3. **布局颜色反转**：暗色背景用深色值，字体颜色用浅色值（与亮色主题相反）
4. **`themeScrollbars: true`** 让 JupyterLab 隐藏默认滚动条，允许自定义
5. **语法高亮颜色**：CodeMirror 颜色需要适配暗色背景，亮色主题的颜色在暗色上可能不醒目

---
type: Concept
title: 主题扩展开发
description: 理解 JupyterLab 主题系统、CSS 变量覆盖机制、IThemeManager 注册 API，以及如何创建亮色/暗色主题。
tags: [theme, css-variables, ithememanager, dark-mode, styling, appearance]
generated: { by: "source-code-to-okf-wiki", at: "2026-08-22T12:20:00Z" }
verified: { by: "process:seven-concepts-v", at: "2026-08-22T12:20:00Z" }
status: stable
stale_after: 2027-08-22
sources:
  - id: index-ts
    location: template/src/index.ts.jinja
    lines: "22-30"
  - id: variables-css
    location: template/style/{% if kind == 'theme' %}variables.css{% endif %}
    lines: "1-398"
  - id: index-css
    location: template/style/index.css.jinja
    lines: "1-12"
---

## 主题扩展开发

主题扩展通过覆盖 JupyterLab 的 CSS 自定义属性（CSS Variables）来改变界面外观。JupyterLab 定义了一套完整的 CSS 变量体系（`--jp-*` 前缀），主题只需重新定义这些变量即可实现全局外观定制，无需修改任何组件代码。

## 主题架构

JupyterLab 的主题系统基于以下机制：

1. **CSS 变量层**：所有 JupyterLab 组件使用 `var(--jp-*)` 引用颜色、字体、间距等值
2. **主题注册**：插件通过 `IThemeManager.register()` 注册主题，提供名称和 CSS 加载函数
3. **动态加载**：用户切换主题时，JupyterLab 加载/卸载主题 CSS 文件
4. **明暗模式**：`isLight` 属性标记主题为亮色或暗色，影响默认图标和组件渲染

## 生成代码结构

theme 类型生成的前端入口代码非常简洁：

```typescript
import { JupyterFrontEnd, JupyterFrontEndPlugin } from '@jupyterlab/application';
import { IThemeManager } from '@jupyterlab/apputils';

const plugin: JupyterFrontEndPlugin<void> = {
  id: 'mytheme:plugin',
  autoStart: true,
  requires: [IThemeManager],           // 必须注入 IThemeManager
  activate: (app: JupyterFrontEnd, manager: IThemeManager) => {
    const style = 'mytheme/index.css'; // 主题 CSS 的 labextension 路径

    manager.register({
      name: 'mytheme',                // 主题显示名称
      isLight: true,                  // true=亮色主题，false=暗色主题
      load: () => manager.loadCSS(style),   // 加载 CSS
      unload: () => Promise.resolve(undefined),
      themeScrollbars: false          // 可选：是否自定义滚动条样式
    });
  }
};

export default plugin;
```

关键点：
- `requires: [IThemeManager]`——主题插件必须依赖 IThemeManager
- `style` 路径格式为 `<labextension-name>/index.css`，对应 `myextension/labextension/index.css`
- `loadCSS()` 会动态将 CSS 注入页面
- `isLight` 决定图标颜色和某些组件的渲染行为

## CSS 文件结构

主题的样式文件组织如下：

```
style/
├── index.css         # 入口：@import variables.css + 额外样式
└── variables.css     # 定义所有 CSS 变量（核心文件）
```

### index.css

```css
@import url('./variables.css');

/* 可选：对特定元素的额外覆盖 */
tt, code, kbd, samp, pre {
  font-family: var(--jp-code-font-family);
  font-size: var(--jp-code-font-size);
  line-height: var(--jp-code-line-height);
}
```

`@import url('./variables.css')` 是必须的，它引入变量定义。在 import 之后可以添加额外的 CSS 规则来覆盖特定组件样式。

### variables.css

这是主题的核心文件，`:root` 选择器下定义所有 CSS 变量。模板生成了完整的默认变量集（亮色主题），包含 100+ 个变量，分为以下几大类。

## CSS 变量分类

### 1. 阴影与高程（Elevation）

基于 Material Design 的 elevation 系统，控制不同层级元素的阴影：

```css
:root {
  --jp-shadow-base-lightness: 0;     /* 暗色主题设为更大的值如 100+ */
  --jp-elevation-z0: none;           /* 无阴影（平面） */
  --jp-elevation-z1: 0 2px 1px -1px ...; /* 轻微抬升 */
  --jp-elevation-z4: 0 2px 4px -1px ...; /* 卡片、对话框 */
  --jp-elevation-z8: 0 5px 5px -3px ...; /* 下拉菜单 */
  --jp-elevation-z16: 0 8px 10px -5px ...; /* 弹出层 */
  --jp-elevation-z24: 0 11px 15px -7px ...; /* 模态对话框 */
}
```

### 2. 边框

```css
--jp-border-width: 1px;
--jp-border-color0: var(--md-grey-400);  /* 最重要的边框 */
--jp-border-color1: var(--md-grey-400);
--jp-border-color2: var(--md-grey-300);
--jp-border-color3: var(--md-grey-200);  /* 最不重要的边框 */
--jp-border-radius: 2px;
```

数字含义（0-3 序列的统一规则）：
- **0**: 最高对比度/最重要/特殊强调
- **1**: 主要/常规场景（最常用）
- **2**: 次要/背景
- **3**: 三级/最弱

### 3. UI 字体

用于界面元素（菜单、按钮、标签等）：

```css
--jp-ui-font-size0: 0.8333em;   /* 小号 */
--jp-ui-font-size1: 13px;       /* 基础大小 */
--jp-ui-font-size2: 1.2em;      /* 中号 */
--jp-ui-font-size3: 1.44em;     /* 大号 */
--jp-ui-font-family: -apple-system, blinkmacsystemfont, 'Segoe UI', ...;
--jp-ui-font-color0: rgba(0, 0, 0, 1);      /* 最强 */
--jp-ui-font-color1: rgba(0, 0, 0, 0.87);   /* 主要文本 */
--jp-ui-font-color2: rgba(0, 0, 0, 0.54);   /* 次要文本 */
--jp-ui-font-color3: rgba(0, 0, 0, 0.38);   /* 禁用/提示文本 */
```

### 4. 内容字体

用于用户创建的内容（notebook 单元格、Markdown 渲染等）：

```css
--jp-content-font-size1: 14px;     /* 基础内容字体 */
--jp-content-font-color1: rgba(0, 0, 0, 0.87);
--jp-content-link-color: var(--md-blue-700);
--jp-content-line-height: 1.6;
```

### 5. 代码字体

用于代码编辑器和代码单元格：

```css
--jp-code-font-size: 13px;
--jp-code-font-family: menlo, consolas, 'DejaVu Sans Mono', monospace;
--jp-code-line-height: 1.3077;
```

### 6. 布局颜色

```css
--jp-layout-color0: white;           /* 最底层背景 */
--jp-layout-color1: white;           /* 主要区域背景 */
--jp-layout-color2: var(--md-grey-200); /* 次级区域（侧边栏、工具栏） */
--jp-layout-color3: var(--md-grey-400); /* 高亮/选中背景 */
--jp-layout-color4: var(--md-grey-600); /* 最深的背景色 */
```

### 7. 品牌与强调色

```css
--jp-brand-color0: #ec0c4b;       /* 最强品牌色（Jupyter 粉红） */
--jp-brand-color1: #ed225d;       /* 主要品牌色（按钮、链接、活动状态） */
--jp-brand-color2: #ee376b;
--jp-brand-color3: #ee3b6e;       /* 最弱品牌色 */
--jp-accent-color0/1/2/3: ...    /* 强调色（成功、确认等） */
```

### 8. 状态颜色

```css
--jp-warn-color1: var(--md-orange-500);    /* 警告 */
--jp-error-color1: var(--md-red-500);      /* 错误 */
--jp-success-color1: var(--md-green-500);  /* 成功 */
--jp-info-color1: var(--md-cyan-500);      /* 信息 */
```

### 9. 单元格与编辑器

```css
--jp-cell-editor-background: var(--md-grey-100);
--jp-cell-editor-active-background: var(--jp-layout-color0);
--jp-cell-editor-active-border-color: var(--jp-brand-color1);
--jp-cell-inprompt-font-color: #307fc1;   /* In [] 提示符颜色 */
--jp-cell-outprompt-font-color: #bf5b3d;  /* Out[] 提示符颜色 */
--jp-mirror-editor-keyword-color: #008000; /* 语法高亮：关键字 */
--jp-mirror-editor-string-color: #ba2121;  /* 语法高亮：字符串 */
--jp-mirror-editor-comment-color: #408080; /* 语法高亮：注释 */
```

## 创建暗色主题

创建暗色主题的关键修改：

1. **设置 `isLight: false`**
2. **调整 `--jp-shadow-base-lightness`**（从 0 改为 200+，使阴影在暗色背景上可见）
3. **反转布局颜色**（深色背景 + 浅色文字）
4. **调整品牌/强调色**确保在暗色背景上对比度足够
5. **反转字体颜色**（从黑色透明度改为白色透明度）

示例暗色主题关键变量：

```css
:root {
  --jp-shadow-base-lightness: 200;

  --jp-layout-color0: #111111;
  --jp-layout-color1: #212121;
  --jp-layout-color2: #333333;
  --jp-layout-color3: #424242;
  --jp-layout-color4: #616161;

  --jp-ui-font-color0: rgba(255, 255, 255, 1);
  --jp-ui-font-color1: rgba(255, 255, 255, 0.87);
  --jp-ui-font-color2: rgba(255, 255, 255, 0.54);
  --jp-ui-font-color3: rgba(255, 255, 255, 0.38);

  --jp-border-color0: var(--md-grey-700);
  --jp-border-color1: var(--md-grey-700);
  --jp-border-color2: var(--md-grey-800);
  --jp-border-color3: var(--md-grey-900);
}
```

## Material Design 颜色参考

模板变量中引用了 Material Design 颜色（`--md-grey-*`、`--md-blue-*` 等），这些由 JupyterLab 内置提供：

| Material 色号 | 亮色主题常用 | 暗色主题常用 |
|--------------|-------------|-------------|
| grey-100 | #f5f5f5 (很亮的灰) | - |
| grey-200 | #eeeeee | - |
| grey-300 | #e0e0e0 | - |
| grey-400 | #bdbdbd | - |
| grey-600 | - | #757575 |
| grey-700 | - | #616161 |
| grey-800 | - | #424242 |
| grey-900 | - | #212121 |

## 主题开发最佳实践

1. **优先修改变量而非组件样式**：通过修改 `--jp-*` 变量实现全局一致的外观，避免直接覆盖组件 CSS
2. **保持 0-3 序列的一致性**：同一组变量中，数字越小对比度越高/越重要
3. **测试对比度**：确保文本颜色与背景色的对比度满足 WCAG AA 标准（4.5:1 对正文）
4. **检查两种模式**：如果主题只提供暗色或亮色，确保 `isLight` 设置正确
5. **使用 `themeScrollbars: true`**：如果主题自定义滚动条样式，启用此选项让 JupyterLab 隐藏默认滚动条
6. **参考官方主题**：JupyterLab 内置的 `@jupyterlab/theme-light-extension` 和 `@jupyterlab/theme-dark-extension` 是最佳参考

## package.json 主题配置

theme 类型的 package.json 在 `jupyterlab` 字段中有特殊配置：

```json
{
  "jupyterlab": {
    "extension": "lib/index.js",
    "themePath": "style/index.css",
    "outputDir": "mytheme/labextension",
    "discovery": {
      "server": {
        "managers": ["pip"],
        "base": { "name": "mytheme" }
      }
    }
  }
}
```

`themePath` 指向主题 CSS 入口文件，JupyterLab 通过这个路径识别扩展为主题。

## 相关概念

- [四种扩展类型对比](/concepts/03-four-extension-types.md)
- [前端扩展开发](/concepts/06-frontend-extension.md)
- [生成项目结构详解](/concepts/04-project-structure.md)

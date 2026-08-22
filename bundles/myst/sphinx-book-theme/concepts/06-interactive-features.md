---
type: concept
title: 06 - 交互功能详解
description: 全屏模式、TOC智能隐藏、Thebe在线代码执行、打印优化、侧边栏切换修复等JavaScript交互功能
tags:
- sphinx-book-theme
- javascript
- fullscreen
- thebe
- intersection-observer
- print
generated: 2026-08-23
status: stable
stale_after: 2027-08-23
sources:
- src/sphinx_book_theme/assets/scripts/index.js
---

# 交互功能详解

sphinx-book-theme 通过 `index.js` 实现了多种客户端交互功能：全屏切换、TOC智能隐藏、Thebe集成、打印优化、按钮tooltip管理、侧边栏行为修复。

## DOM就绪机制

所有JS功能通过 `sbRunWhenDOMLoaded(cb)` 注册，在DOM完全加载后执行（F-168-F-020）：

```javascript
var sbRunWhenDOMLoaded = (cb) => {
  if (document.readyState != "loading") {
    cb();
  } else if (document.addEventListener) {
    document.addEventListener("DOMContentLoaded", cb);
  } else {
    document.attachEvent("onreadystatechange", function () {
      if (document.readyState == "complete") cb();
    });
  }
};
```

该函数兼容现代浏览器（addEventListener）和旧版IE（attachEvent）。

## 全屏模式

`toggleFullScreen()` 函数实现全屏切换（F-029-F-050）：

- 检测当前是否全屏：检查 `document.fullscreenElement` 或 `document.webkitFullscreenElement`
- 进入全屏：`docElm.requestFullscreen()` 或 `docElm.webkitRequestFullscreen()`（Safari兼容）
- 退出全屏：`document.exitFullscreen()` 或 `document.webkitExitFullscreen()`

全屏按钮默认启用（`use_fullscreen_button: True`），点击后文章区域占据整个屏幕。

## TOC智能隐藏

`initTocHide()` 使用 IntersectionObserver API 实现两个功能（F-066-F-138）：

### 功能1：边注进入视口时隐藏TOC

当右侧边距中的边注/旁注/margin内容滚动到屏幕上时，自动隐藏右侧TOC（次级侧边栏），避免内容重叠。

```javascript
let hideTocCallback = (entries, observer) => {
  entries.forEach((entry) => {
    if (entry.isIntersecting) {
      onScreenItems.push(entry.target);  // 进入视口
    } else {
      // 从列表移除
    }
  });
  // 任何边注内容可见时隐藏TOC
  if (onScreenItems.length > 0) {
    document.querySelector("div.bd-sidebar-secondary").classList.add("hide");
  } else {
    document.querySelector("div.bd-sidebar-secondary").classList.remove("hide");
  }
};
```

触发条件（rootMargin: `"0px 0px -33% 0px"`）：当边注元素顶部进入屏幕上2/3区域时触发（F-173）。

### 功能2：滚动检测添加scrolled类

通过监听 `.sbt-scroll-pixel-helper` 像素元素（在layout.html中添加，F-147），检测页面是否滚动：

```javascript
let manageScrolledClassOnBody = (entries, observer) => {
  if (entries[0].boundingClientRect.y < 0) {
    document.body.classList.add("scrolled");
  } else {
    document.body.classList.remove("scrolled");
  }
};
```

CSS可以通过 `body.scrolled` 选择器实现滚动后的样式变化（如缩小header、添加阴影等）。

### 监听的选择器

JS监听以下CSS类的元素（F-171-F-172）：

```
marginnote, sidenote, margin, margin-caption,
full-width, sidebar, popout
```

每个类名支持四种写法以兼容历史版本：
- `.{cls}`：标准短横线命名（如 `.marginnote`）
- `.tag_{cls}`：Sphinx旧版生成的前缀
- `.{cls_with_underscores}`：下划线变体（如 `.margin_note`）
- `.tag_{cls_with_underscores}`：前缀+下划线变体

## Thebe 在线代码执行

`initThebeSBT()` 函数实现Thebe一键启动（F-143-F-156）：

1. 在页面第一个 `<h1>` 后查找是否已有 `.thebe-launch-button`
2. 若没有，动态插入一个 `<button class='thebe-launch-button'>`
3. 调用 sphinx-thebe 提供的全局 `initThebe()` 函数

Thebe配置由Python端的 `update_mode_thebe_config` 自动填充（F-135-F-166）：
- 若用户未配置 `thebe_config["repository_url"]`，自动从主题的 `repository_url` 填充
- 若用户未配置 `repository_branch`，默认使用 "master"（注意：非 "main"）
- 若启用Thebe但未添加 sphinx_thebe 扩展，发出警告

Thebe按钮的点击通过 `javascript: "initThebeSBT()"` 类型按钮触发（F-214-F-224）。

## 打印优化

`addNoPrint()` 函数为导航元素添加 `noprint` 类（F-162-F-176）：

```javascript
var noPrintSelector = [
  ".bd-header-announcement",
  ".bd-header",
  ".bd-header-article",
  ".bd-sidebar-primary",
  ".bd-sidebar-secondary",
  ".bd-footer-article",
  ".bd-footer-content",
  ".bd-footer",
].join(",");
```

打印时这些元素被CSS `@media print` 隐藏。同时 layout.html 中添加了专用打印目录区域（F-148）：

```html
<div id="jb-print-docs-body" class="onlyprint">
    <h1>{{ pagetitle }}</h1>
    <div id="jb-print-toc">
        <h2>{{ translate(theme_toc_title) }}</h2>
        <nav aria-label="Page">{{ page_toc }}</nav>
    </div>
</div>
```

`.onlyprint` 类在屏幕显示时隐藏，打印时显示。PDF下载按钮通过 `window.print()` 触发浏览器打印（F-119）。

## 按钮Blur处理

`addBlurToButtons()` 为按钮添加点击后 blur 行为（F-188-F-210），防止tooltip在点击后持续显示：

```javascript
const buttonSelectors = [
  ".theme-switch-button",
  ".search-button",
  ".primary-toggle",
  ".secondary-toggle",
];
```

点击这些按钮后调用 `button.blur()` 移除焦点，从而隐藏Bootstrap tooltip。

## 宽屏侧边栏切换修复

`fixSidebarToggle()` 修复了PST侧边栏切换在宽屏上的行为问题（F-217-F-242）：

**问题**：PST的侧边栏切换按钮在宽屏（>=992px）上也会打开模态对话框（modal），而用户期望的是折叠/展开侧边栏。

**修复**：
1. 使用capture phase（`addEventListener`第三个参数`true`）在PST处理之前拦截点击事件
2. 检测 `window.matchMedia("(min-width: 992px)")` 判断是否宽屏
3. 宽屏时：`event.preventDefault()` + `event.stopImmediatePropagation()` 阻止PST的modal逻辑，改为切换 `pst-sidebar-hidden` 类
4. 窄屏时：不干预，使用PST默认的modal行为

## 全局函数暴露

以下函数被暴露到 `window` 作用域，供HTML onclick属性调用（F-181-F-182）：

- `window.initThebeSBT`：Thebe启动函数
- `window.toggleFullScreen`：全屏切换函数

## DOM就绪初始化

所有功能在DOM就绪后按以下顺序初始化（F-247-F-250）：

```javascript
sbRunWhenDOMLoaded(initTocHide);       // TOC智能隐藏
sbRunWhenDOMLoaded(addNoPrint);        // 打印类标记
sbRunWhenDOMLoaded(addBlurToButtons);  // 按钮blur
sbRunWhenDOMLoaded(fixSidebarToggle);  // 宽屏侧边栏修复
```

## 相关概念

- [头部按钮系统](/concepts/04-header-buttons.md)
- [Margin指令与边注旁注](/concepts/05-margin-sidenotes.md)
- [样式定制与第三方扩展适配](/concepts/08-customization.md)
- [交互式计算书籍配置示例](/examples/interactive-book.md)

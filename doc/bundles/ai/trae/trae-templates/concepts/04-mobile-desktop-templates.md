---
type: Concept
title: 移动端和桌面端模板
description: mobile-desktop 分类包含 3 个跨平台应用模板：Flutter（Dart 跨端）、Electron（网页技术桌面端），以及 React Native/Expo（React 移动端），覆盖主流的移动和桌面应用开发场景。
tags: [trae-templates, mobile, desktop, flutter, electron, react-native, expo]
generated: { by: "reference_agent/trae-cn", at: 2026-04-22T00:00:00+08:00 }
verified: { by: "process:seven-concepts-v", at: 2026-04-22T00:00:00+08:00 }
status: stable
stale_after: 2026-10-22
sources:
  - id: src
    resource: /references/templates-source.md
    title: Trae Templates 源码信源
---

## 移动端和桌面端模板总览

mobile-desktop 分类包含 3 个跨平台应用开发模板，覆盖三种主流方案：

| 模板 | 技术栈 | 目标平台 | 开发语言 | 调试方式 |
|------|--------|----------|----------|----------|
| react-native | React Native + Expo | iOS/Android/Web | JavaScript | Expo Go 扫码 |
| flutter-starter | Flutter | iOS/Android/Web/Desktop | Dart | Flutter SDK |
| electron-starter | Electron | Windows/macOS/Linux | HTML/JS/Node.js | npm start |

三个模板代表了三种不同的跨平台开发哲学：
- **React Native**：用 React 写原生 UI（Learn once, write anywhere）
- **Flutter**：自绘引擎，一切皆 Widget（一次编写，多端运行）
- **Electron**：用网页技术开发桌面应用（Chromium + Node.js）

## flutter-starter：Flutter 跨端应用

**路径**：`templates/mobile-desktop/flutter-starter/`

Flutter 新项目模板，支持 iOS、Android、Web 和桌面端。

**文件结构**（5 个文件）：
```
flutter-starter/
├── pubspec.yaml      # Flutter/Dart 依赖配置
├── lib/
│   └── main.dart     # Flutter 应用入口
├── .gitignore
├── README.md
└── README.zh-CN.md
```

**技术栈**：Flutter、Dart

**说明**：README 为 Flutter 默认生成内容，包含官方文档和 Codelab 链接。与其他模板不同，Flutter 项目通常需要通过 `flutter create` 命令生成完整的平台特定代码（ios/、android/、web/ 等目录），此模板提供最精简的 Dart 入口。

**Flutter 特点**：
- Skia/Impeller 自绘引擎，UI 一致性高
- Hot Reload 开发体验
- 单代码库支持 6 个平台（iOS/Android/Web/Windows/macOS/Linux）
- Widget 组合式 UI 范式

## electron-starter：Electron 桌面应用

**路径**：`templates/mobile-desktop/electron-starter/`

Electron 极简桌面应用模板，使用网页技术栈开发跨平台桌面应用。

**文件结构**（6 个文件）：
```
electron-starter/
├── package.json    # Electron 依赖和启动脚本
├── main.js         # Electron 主进程
├── index.html      # 渲染进程页面
├── .gitignore
├── README.md
└── README.zh-CN.md
```

**技术栈**：Electron、Node.js、HTML/JavaScript

**启动方式**：
```bash
npm install
npm start
```

**Electron 架构要点**：
- **主进程**（main.js）：Node.js 环境，管理窗口生命周期、系统交互
- **渲染进程**（index.html）：Chromium 环境，运行网页 UI
- 通过 IPC（进程间通信）在主进程和渲染进程之间传递消息

**适用场景**：
- VS Code、Discord、Slack 类桌面应用
- 需要网页 UI + 系统 API 访问的工具
- 已有 Web 应用需要打包为桌面应用

## react-native：React Native + Expo 移动应用

**路径**：`templates/mobile-desktop/react-native/`

React Native（Expo）极简应用模板，使用 React 范式开发原生移动应用。

**文件结构**（5 个文件）：
```
react-native/
├── package.json    # Expo/RN 依赖
├── App.js          # 应用根组件
├── .gitignore
├── README.md
└── README.zh-CN.md
```

**技术栈**：React Native、Expo、JavaScript

**启动方式**：
```bash
npm install
npm start
# 用 Expo Go 应用扫描二维码（Android/iOS）
# 或按 w 在浏览器打开 Web 版本
```

**Expo 优势**：
- 无需配置 Xcode/Android Studio 即可开始开发
- Expo Go App 扫码实时预览
- 大量内置 API（相机、位置、通知等）
- OTA 更新支持

**React Native 特点**：
- 使用原生 UI 组件（非 WebView）
- React 开发范式（组件化、Hooks）
- 热更新支持
- 接近原生的性能体验

## 跨平台方案对比

| 维度 | React Native (Expo) | Flutter | Electron |
|------|---------------------|---------|----------|
| **目标平台** | iOS/Android/Web | iOS/Android/Web/Desktop | Windows/macOS/Linux |
| **编程语言** | JavaScript/TypeScript | Dart | HTML/JS/Node.js |
| **UI 渲染** | 原生组件 | Skia 自绘 | Chromium (Web) |
| **性能** | 接近原生 | 接近原生 | 较高内存占用 |
| **包体积** | 中 | 中 | 大（含 Chromium） |
| **开发体验** | Expo Go 扫码调试 | Hot Reload | 浏览器 DevTools |
| **学习曲线** | 低（React 开发者） | 中（新语言 Dart） | 低（Web 开发者） |
| **生态成熟度** | 成熟 | 成熟 | 成熟 |
| **典型应用** | Instagram、Discord、Airbnb | 闲鱼、BMW、Google Pay | VS Code、Slack、Discord |

## 选择建议

| 需求/场景 | 推荐模板 |
|-----------|----------|
| 已有 React 经验，开发 iOS/Android App | react-native |
| 追求多端一致性和高性能 UI | flutter-starter |
| 用网页技术开发桌面工具 | electron-starter |
| 需要同时支持移动和 Web | react-native 或 flutter-starter |
| 团队最熟悉的技术栈 | 选对应技术栈的模板 |

## 最小可用设计在移动端模板中的体现

- **react-native**：仅 App.js + package.json，不含导航、状态管理
- **flutter-starter**：仅 main.dart + pubspec.yaml，使用 Flutter 默认结构
- **electron-starter**：main.js + index.html 最小双进程模型

所有模板都不预设 UI 框架（如 React Navigation、Provider、Bloc 等），不包含原生平台配置目录（ios/、android/ 由工具链按需生成）。

## 相关概念

- [五维分面分类体系](/concepts/01-template-classification.md)
- [Web 前端模板](/concepts/02-web-frontend-templates.md)
- [后端服务模板](/concepts/03-backend-templates.md)
- [数据与 AI 模板](/concepts/05-data-ai-templates.md)
- [工具与 DevOps 模板](/concepts/06-tools-devops-templates.md)

## 相关内容

- [源码信源索引](/references/templates-source.md)

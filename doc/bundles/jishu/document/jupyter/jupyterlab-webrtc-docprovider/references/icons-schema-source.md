---
type: Reference
title: 图标与Schema源码（icons.ts + schema/plugin.json）
description: LabIcon图标定义和JSON Schema配置规范
tags: [icons, labicon, schema, settings, configuration]
generated: { by: "agent:source-code-to-okf-wiki", at: "2026-08-22T07:06:00Z" }
verified: { by: "process:grep-verify", at: "2026-08-22T07:10:00Z" }
status: stable
stale_after: 2027-08-22
sources:
  - id: icons-ts
    resource: https://github.com/jupyterlite/jupyterlab-webrtc-docprovider/blob/main/src/icons.ts
    title: src/icons.ts - Icon definitions
  - id: plugin-json
    resource: https://github.com/jupyterlite/jupyterlab-webrtc-docprovider/blob/main/schema/plugin.json
    title: schema/plugin.json - Settings schema
---

## icons.ts 源码分析

定义3个 `LabIcon` 实例，使用内联 SVG 字符串：

```typescript
export const webrtcIcon = new LabIcon({
  name: 'webrtc-docprovider:webrtc',
  svgstr: WEBRTC_SVG,
});
export const shareIcon = new LabIcon({
  name: 'webrtc-docprovider:share',
  svgstr: SHARE_SVG,
});
export const shareOffIcon = new LabIcon({
  name: 'webrtc-docprovider:share-off',
  svgstr: SHARE_OFF_SVG,
});
```

SVG 文件从 `style/img/` 目录导入：
- `webrtc.svg`：WebRTC 图标（用于设置面板和命令）
- `share.svg`：分享启用图标（状态栏）
- `share-off.svg`：分享禁用图标（状态栏）

## schema/plugin.json 源码分析

JSON Schema Draft-07，定义用户可配置的设置项：

### Schema 元数据

- `title`: "WebRTC Sharing"
- `description`: "Settings for WebRTC-based collaborative editing"
- `additionalProperties`: false
- `jupyter.lab.setting-icon`: "webrtc-docprovider:webrtc"
- `jupyter.lab.setting-icon-label`: "WebRTC Sharing"

### 配置属性

| 属性 | 类型 | 默认值 | 说明 |
|------|------|--------|------|
| `disabled` | boolean | false | 是否禁用 WebRTC 分享 |
| `room` | null \| string | null | 房间名（null=随机，string=自定义） |
| `roomPrefix` | null \| string | null | 房间前缀（自定义需≥10字符，null=用host/origin） |
| `signalingUrls` | null \| string[] | null | 信令服务器URL数组（必须 ws:// 或 wss:// 开头） |
| `usercolor` | null \| string | null | 用户光标颜色（3位或6位hex） |
| `username` | null \| string | null | 显示用户名 |

每个属性使用 `oneOf` 定义两种选择：null（随机/默认）或具体值（自定义）。

### signalingUrls 验证

```json
{
  "items": {
    "pattern": "wss?://.*",
    "type": "string"
  }
}
```

使用正则 `wss?://.*` 验证 URL 格式。

### usercolor 验证

```json
{
  "pattern": "[0-9a-f]{3}|[0-9a-f]{6}",
  "type": "string"
}
```

接受3位或6位十六进制 RGB 值（小写）。

### roomPrefix 约束

自定义前缀最小长度为10字符（`minLength: 10`）。

## 相关概念

- [配置三级优先级系统](../concepts/09-configuration.md)
- [构建与打包系统](../concepts/10-build-and-packaging.md)

---
type: Concept
title: 配置三级优先级系统
description: jupyterlab-webrtc-docprovider配置遵循URL参数→插件设置→PageConfig/默认值的三级优先级链，支持服务器部署配置、用户偏好和临时分享三种场景
tags: [configuration, priority, settings, url-params, pageconfig, overrides, deployment]
generated: { by: "agent:source-code-to-okf-wiki", at: "2026-08-22T07:06:00Z" }
verified: { by: "process:grep-verify", at: "2026-08-22T07:10:00Z" }
status: stable
stale_after: 2027-08-22
sources:
  - id: manager-src
    resource: /references/manager-source.md
    title: src/manager.ts - Configuration priority chain
  - id: schema-src
    resource: /references/icons-schema-source.md
    title: schema/plugin.json - Settings schema
---

## 三级配置模型

jupyterlab-webrtc-docprovider 的所有用户可配置项遵循统一的三级优先级模型：

```
┌─────────────────────────────────────────────────┐
│  Level 3: URL 参数（最高优先级）                   │
│  ?room=demo&username=Alice&usercolor=e65100     │
│  适用：临时分享、快速演示、URL 直接分享链接         │
├─────────────────────────────────────────────────┤
│  Level 2: 用户设置（Settings Editor）             │
│  Settings → WebRTC Sharing 面板                  │
│  或 overrides.json 预配置                        │
│  适用：个人偏好持久化                             │
├─────────────────────────────────────────────────┤
│  Level 1: PageConfig / 系统默认（最低优先级）      │
│  jupyter_server_config.json / jupyter-lite.json │
│  DEFAULT_SIGNALING_SERVERS / 随机值              │
│  适用：服务器部署配置、安全默认值                   │
└─────────────────────────────────────────────────┘
```

每个配置项的 Getter 实现相同的短路求值模式：`URL值 || 设置值 || 默认值`。

## 配置项详解

### disabled（禁用开关）

| 优先级 | 来源 | 键名 | 说明 |
|--------|------|------|------|
| **前置检查** | PageConfig | `collaborative` | 服务器未启用协作模式时，强制禁用 |
| L2 | 用户设置 | `disabled` | 用户手动禁用 |

```typescript
get disabled(): boolean {
  // 前置：服务器配置检查
  const collaborative = PageConfig.getOption('collaborative') === 'true';
  if (!collaborative) return true;
  // L2: 用户设置
  return !!this._composite.disabled;
}
```

**注意**：`disabled` 不支持 URL 参数覆盖。它由服务器配置和用户设置控制。

### room（房间名）

| 优先级 | 来源 | 获取方式 | 示例 |
|--------|------|---------|------|
| L3 | URL 参数 | `?room=demo` | 临时加入 demo 房间 |
| L2 | 用户设置 | `settings.composite.room` | 预设常用房间 |
| L1 | 随机默认 | `UUID.uuid4()` | 私密房间，不与他人共享 |

### username（用户名）

| 优先级 | 来源 | 获取方式 | 说明 |
|--------|------|---------|------|
| L3 | URL 参数 | `?username=Alice` | 临时指定显示名 |
| L2 | 用户设置 | `settings.composite.username` | 持久化用户名 |
| L1 | 随机默认 | `getAnonymousUserName()` | JupyterLab 提供的匿名名称（如 "Anonymous Kangaroo"） |

`getAnonymousUserName()` 来自 `@jupyterlab/docprovider` 包，生成随机动物名。

### usercolor（光标颜色）

| 优先级 | 来源 | 获取方式 | 格式 |
|--------|------|---------|------|
| L3 | URL 参数 | `?usercolor=e65100` | 6位hex，不含# |
| L2 | 用户设置 | `settings.composite.usercolor` | 3位或6位hex |
| L1 | 随机默认 | `getRandomColor().slice(1)` | JupyterLab 主题色中随机选择 |

注意：`getRandomColor()` 返回带 `#` 前缀的颜色字符串，`.slice(1)` 去掉前缀以保持内部一致性。

### roomPrefix（房间前缀）

| 优先级 | 来源 | 获取方式 | 说明 |
|--------|------|---------|------|
| L1a | PageConfig | `webRtcRoomPrefix` | 服务器部署配置 |
| L2 | 用户设置 | `settings.composite.roomPrefix` | 自定义前缀（≥10字符） |
| L1b | 自动检测 | `window.location.origin` | 非localhost用origin |
| L1b特殊 | 随机 | `UUID.uuid4()` | localhost 时随机生成 |

```typescript
if (roomPrefix == null) {
  const { hostname, origin } = window.location;
  roomPrefix = LOCAL_HOSTS.includes(hostname.toLowerCase())
    ? UUID.uuid4()
    : origin;
}
```

### signalingUrls（信令服务器）

| 优先级 | 来源 | 获取方式 | 说明 |
|--------|------|---------|------|
| L1a | PageConfig | `fullWebRtcSignalingUrls`（JSON） | 服务器端注入 |
| L2 | 用户设置 | `settings.composite.signalingUrls` | 自定义服务器列表 |
| L1b | 默认值 | `DEFAULT_SIGNALING_SERVERS` | 3个公共服务器 |

PageConfig 值需要 JSON.parse，解析失败时回退到下一优先级。使用默认公共服务器时控制台输出警告。

## 配置方式

### 方式1：URL 参数（最灵活）

```
http://localhost:8888/lab?room=project-standup&username=Bob&usercolor=4caf50
```

适合快速分享链接、即时协作。URL 参数会被消费（"these parameters will probably be consumed, but that's okay"），不会残留在地址栏中造成混淆。

### 方式2：用户设置面板

在 JupyterLab 中：Settings → Settings Editor → WebRTC Sharing

可配置所有6个选项，更改立即生效（通过 `settings.changed` 信号）。

### 方式3：overrides.json（系统级预配置）

在 `{sys.prefix}/share/jupyter/lab/settings/overrides.json` 中预配置默认值：

```json
{
  "@jupyterlite/webrtc-docprovider:plugin": {
    "disabled": false,
    "room": "default-room",
    "roomPrefix": "my-org-unique-prefix-2024",
    "signalingUrls": ["wss://signaling.my-org.com"],
    "username": "Team Member",
    "usercolor": "1976d2"
  }
}
```

这会覆盖系统默认值，但用户仍可通过 Settings Editor 或 URL 参数更改。

### 方式4：Jupyter Server 配置

```json
// jupyter_server_config.json
{
  "LabServerApp": {
    "collaborative": true
  }
}
```

或通过 Jupyter 页面配置注入 `fullWebRtcSignalingUrls` 和 `webRtcRoomPrefix`。

### 方式5：JupyterLite 配置

```json
// jupyter-lite.json
{
  "jupyter-config-data": {
    "collaborative": true,
    "fullWebRtcSignalingUrls": ["wss://signaling.example.com"]
  }
}
```

JupyterLite 还支持通过 `overrides.json` 配置插件设置。

## JSON Schema 验证

所有用户设置通过 JSON Schema（schema/plugin.json）验证：

| 属性 | 类型约束 | 验证规则 |
|------|---------|---------|
| `disabled` | boolean | - |
| `room` | null \| string | null=随机, string=自定义 |
| `roomPrefix` | null \| string | string最小长度10 |
| `signalingUrls` | null \| string[] | 每项匹配 `wss?://.*` |
| `usercolor` | null \| string | 匹配 `[0-9a-f]{3}\|[0-9a-f]{6}` |
| `username` | null \| string | - |

Schema 设置了 `additionalProperties: false`，拒绝未知属性。

## initUrlParams 与 initRandomParams

```typescript
protected initUrlParams(): WebRtcManager.IURLParams {
  const params = new URLSearchParams(window.location.search);
  return {
    room: (params.get('room') || '').trim() || null,
    username: (params.get('username') || '').trim() || null,
    usercolor: (params.get('usercolor') || '').trim() || null,
  };
}

protected initRandomParams(): WebRtcManager.IRandomParams {
  return {
    room: UUID.uuid4(),
    usercolor: getRandomColor().slice(1),
    username: getAnonymousUserName(),
  };
}
```

- `initUrlParams()`：解析 URL 查询参数，空字符串转换为 null（确保短路逻辑正确）
- `initRandomParams()`：生成随机默认值，所有字段都是非空字符串

## 设计模式总结

三级优先级链是 JupyterLab 扩展的常见配置模式，其优点：
1. **灵活**：支持从服务器部署到个人偏好再到临时分享的全部场景
2. **安全**：服务器可强制禁用协作，localhost 自动使用随机前缀防止意外连接
3. **零配置可用**：安装即可用，随机用户名/颜色/房间保证开箱即用体验
4. **生产就绪**：支持自定义信令服务器和前缀，满足生产部署需求

## 相关概念

- [WebRtcManager配置管理](/concepts/03-webrtc-manager.md)
- [安装与快速开始](/concepts/01-getting-started.md)
- [房间ID哈希与信令机制](/concepts/05-room-and-signaling.md)

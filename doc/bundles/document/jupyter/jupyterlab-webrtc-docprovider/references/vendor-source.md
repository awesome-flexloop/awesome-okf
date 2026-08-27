---
type: Reference
title: Vendor补丁源码（vendor/SimplePeerExtended.js）
description: SimplePeerExtended扩展simple-peer实现大消息分块传输，解决y-webrtc大数据传输问题
tags: [vendor, simple-peer, webrtc, chunking, patch, data-channel]
generated: { by: "agent:source-code-to-okf-wiki", at: "2026-08-22T07:06:00Z" }
verified: { by: "process:grep-verify", at: "2026-08-22T07:10:00Z" }
status: stable
stale_after: 2027-08-22
sources:
  - id: simple-peer-ext
    resource: https://github.com/jupyterlite/jupyterlab-webrtc-docprovider/blob/main/vendor/SimplePeerExtended.js
    title: vendor/SimplePeerExtended.js - Patched simple-peer with chunking
---

## SimplePeerExtended.js 源码分析

这是一个对 `simple-peer` 库的扩展补丁，解决了原始 simple-peer 在 WebRTC DataChannel 上传输大消息时的缓冲问题。补丁源自 @datakurre 的贡献。

### 问题背景

原始 `simple-peer` 使用简单的 `send()` 方法发送数据，当消息较大时：
1. DataChannel 缓冲可能溢出
2. 消息可能因 WebRTC 帧大小限制被截断或丢失
3. y-webrtc 同步大文档时容易断开连接

### 常量定义

```javascript
export const CHUNK_SIZE = 1024 * 16 - 512;  // 15872 字节（16KB - 512B头部）
export const TX_SEND_TTL = 1000 * 30;        // 30秒发送超时
export const MAX_BUFFERED_AMOUNT = 64 * 1024; // 64KB（simple-peer默认值）
```

### SimplePeerExtended 类

继承自 `Peer`（simple-peer），扩展了分块编码/解码和流量控制功能。

```javascript
class SimplePeerExtended extends Peer {
  constructor(opts) {
    super(opts);
    this._txOrdinal = 0;        // 发送序号
    this._rxPackets = [];        // 接收包缓存
    this._txPause = false;       // 发送暂停标志
    this.webRTCMessageQueue = []; // 发送消息队列
    this.webRTCPaused = false;   // WebRTC暂停标志
  }
```

### 分块编码格式（encodePacket）

每个分块包含40字节头部 + 数据载荷：

| 偏移 | 长度 | 字段 | 类型 | 说明 |
|------|------|------|------|------|
| 0 | 8字节 | txOrd | Int64BE | 发送序号（事务ID） |
| 8 | 8字节 | index | Int64BE | 分块索引 |
| 16 | 8字节 | length | Int64BE | 本分块数据长度 |
| 24 | 8字节 | totalSize | Int64BE | 消息总大小 |
| 32 | 8字节 | chunkSize | Int64BE | 分块大小 |
| 40 | 可变 | chunk | Uint8Array | 实际数据 |

使用 `Int64BE`（8字节大端64位整数）编码头部字段，由 vendored 的 `int64-buffer.min.js` 提供。

### Webpack 集成补丁

`webpack.config.js` 通过 `string-replace-loader` 在构建时替换 y-webrtc 对 simple-peer 的引用：

```javascript
{
  test: /y-webrtc\.js$/,
  loader: 'string-replace-loader',
  options: {
    search: 'simple-peer/simplepeer.min.js',
    replace: ['./', '..', '..', '..', 'vendor', 'SimplePeerExtended.js']
      .join(path.sep)
      .replace(/\\/g, '\\\\'),
  },
}
```

使用 `path.join` 风格的段数组拼接路径（跨平台兼容），并对 Windows 路径分隔符进行双重转义以适配 webpack 的字符串替换。注释引用了 y-webrtc PR #25。

这样 y-webrtc 在运行时使用的是打了补丁的 SimplePeerExtended 而非原版 simple-peer。

### crypto 模块 polyfill

webpack 配置中设置 `fallback: { crypto: false }`，因为浏览器环境不需要 Node.js 的 crypto 模块。

## 相关概念

- [Vendor补丁与大消息传输](../concepts/08-vendor-patches.md)
- [WebRtcProvider文档提供者](../concepts/04-document-provider.md)
- [构建与打包系统](../concepts/10-build-and-packaging.md)

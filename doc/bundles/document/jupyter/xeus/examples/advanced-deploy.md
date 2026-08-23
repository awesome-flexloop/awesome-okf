---
type: Example
title: 生产环境部署示例
description: 配置COOP/COEP头、Service Worker、CDN加速和离线支持的生产级JupyterLite+xeus部署方案
tags: [production, deploy, cdn, coop-coep, service-worker, performance]
generated: { by: "agent:source-code-to-okf-wiki", at: "2026-08-22T20:10:00+08:00" }
verified: { by: "process:seven-concepts-v", at: "2026-08-22T20:10:00+08:00" }
status: stable
stale_after: 2027-08-22
sources:
  - id: worker-modes
    resource: /concepts/03-dual-worker-modes.md
    title: 双Worker通信模式
  - id: build-system
    resource: /concepts/05-build-system.md
    title: 构建系统
---

## 目标

配置一个生产级JupyterLite+xeus部署，满足：
1. 启用crossOriginIsolated（coincident模式，最优性能）
2. 正确配置Service Worker
3. CDN加速静态资源
4. 离线可用（PWA）
5. 缓存策略优化

## 方案一：Nginx 部署（推荐）

### 完整Nginx配置

```nginx
server {
    listen 443 ssl http2;
    server_name jupyterlite.example.com;

    # SSL配置
    ssl_certificate /etc/letsencrypt/live/jupyterlite.example.com/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/jupyterlite.example.com/privkey.pem;

    # 网站根目录
    root /var/www/jupyterlite/_output;
    index index.html;

    # ─── 核心：Cross-Origin隔离头（启用coincident模式）───
    # 这些头是SharedArrayBuffer工作的前提
    add_header Cross-Origin-Opener-Policy "same-origin" always;
    add_header Cross-Origin-Embedder-Policy "require-corp" always;
    add_header Cross-Origin-Resource-Policy "cross-origin" always;

    # 安全头
    add_header X-Content-Type-Options "nosniff" always;
    add_header X-Frame-Options "DENY" always;
    add_header Referrer-Policy "strict-origin-when-cross-origin" always;

    # ─── 缓存策略 ───

    # 带hash的文件（JupyterLab打包产物）：长期缓存
    location ~* \.[a-f0-9]{8,}\.(js|css|woff2?|ttf|eot|png|jpg|svg|wasm)$ {
        expires 1y;
        add_header Cache-Control "public, immutable";
        add_header Cross-Origin-Opener-Policy "same-origin" always;
        add_header Cross-Origin-Embedder-Policy "require-corp" always;
        add_header Cross-Origin-Resource-Policy "cross-origin" always;
    }

    # WASM文件：特殊MIME类型 + 长期缓存
    location ~* \.wasm$ {
        application/wasm;
        expires 1y;
        add_header Cache-Control "public, immutable";
    }

    # tar.gz包（conda包）：中期缓存
    location ~* /kernel_packages/.*\.tar\.gz$ {
        expires 7d;
        add_header Cache-Control "public";
    }

    # HTML和JSON：不缓存（保证更新及时）
    location ~* \.(html|json)$ {
        add_header Cache-Control "no-cache, must-revalidate";
    }

    # Service Worker：不缓存（或极短缓存）
    location ~* (service-worker|sw)\.js$ {
        add_header Cache-Control "no-cache, no-store, must-revalidate";
    }

    # SPA路由回退
    location / {
        try_files $uri $uri/ /index.html;
    }

    # 启用gzip/brotli压缩
    gzip on;
    gzip_types text/plain text/css application/json application/javascript
               text/xml application/xml application/xml+rss text/javascript
               application/wasm;
    gzip_min_length 1000;
}

# HTTP→HTTPS重定向
server {
    listen 80;
    server_name jupyterlite.example.com;
    return 301 https://$server_name$request_uri;
}
```

### COOP/COEP注意事项

启用COOP/COEP后，所有跨域资源必须满足以下条件之一：

1. 资源发送 `Cross-Origin-Resource-Policy: cross-origin` 头
2. 资源通过CORS加载（`<script crossorigin="anonymous">`、`<img crossorigin>`等）
3. 资源是同源的

**常见问题**：
- 第三方CDN的字体/图片可能缺少CORP头 → 将资源下载到本地或使用支持CORP的CDN
- 内联脚本/样式可能被CSP阻止（如果配置了CSP）

### 验证Cross-Origin Isolation

部署后在浏览器DevTools控制台验证：

```javascript
console.log('crossOriginIsolated:', crossOriginIsolated);
// 期望输出: crossOriginIsolated: true

console.log('SharedArrayBuffer available:', typeof SharedArrayBuffer !== 'undefined');
// 期望输出: SharedArrayBuffer available: true
```

如果为false，检查：
1. 响应头是否正确发送（DevTools→Network→Headers）
2. 是否有第三方资源缺少CORP头
3. 页面是否通过HTTPS加载（localhost例外）

## 方案二：CDN加速部署

### 使用CDN加速kernel_packages

kernel_packages中的tar.gz文件通常较大（几MB到几十MB），适合CDN缓存。

1. 将 `_output/xeus/` 目录上传到CDN
2. 修改构建配置使用CDN URL

修改 `jupyter_lite_config.md`（通过empack_config配置）：

```json
{
  "XeusAddon": {
    "empack_config": {
      "package_url_template": "https://cdn.example.com/xeus/{env_name}/kernel_packages/{filename}"
    }
  }
}
```

或者在构建后手动修改 `empack_env_meta.json` 中的 `package_url_template`。

### CDN缓存配置建议

| 资源类型 | 缓存时间 | 说明 |
|---------|---------|------|
| JS/CSS（带hash） | 1年 | 内容hash变化URL自动变 |
| WASM文件 | 1年 | 带版本路径 |
| tar.gz包 | 7天-30天 | 包版本固定 |
| kernels.json | 不缓存 | 内核清单 |
| index.html | 不缓存 | 入口文件 |
| Service Worker | 不缓存 | 确保及时更新 |

## 方案三：GitHub Pages + COOP/COEP

GitHub Pages默认不发送COOP/COEP头。有两个解决方案：

### 方案A：使用 coi-serviceworker

[coi-serviceworker](https://github.com/gzuidhof/coi-serviceworker) 是一个通过Service Worker注入COOP/COEP头的解决方案。

1. 下载 `coi-serviceworker.min.js` 到项目目录
2. 在 `jupyter_lite_config.json` 中配置extra内容：

```json
{
  "LiteBuildConfig": {
    "contents": ["static"]
  }
}
```

3. 创建 `static/` 目录，放入coi-serviceworker
4. 需要自定义index.html加载coi-serviceworker（通过JupyterLite模板覆盖）

### 方案B：使用Netlify/Vercel（支持自定义头）

**Netlify**（`netlify.toml`）：

```toml
[[headers]]
  for = "/*"
  [headers.values]
    Cross-Origin-Opener-Policy = "same-origin"
    Cross-Origin-Embedder-Policy = "require-corp"
    Cross-Origin-Resource-Policy = "cross-origin"

[[headers]]
  for = "/xeus/*/kernel_packages/*.tar.gz"
  [headers.values]
    Cache-Control = "public, max-age=604800"
```

**Vercel**（`vercel.json`）：

```json
{
  "headers": [
    {
      "source": "/(.*)",
      "headers": [
        { "key": "Cross-Origin-Opener-Policy", "value": "same-origin" },
        { "key": "Cross-Origin-Embedder-Policy", "value": "require-corp" },
        { "key": "Cross-Origin-Resource-Policy", "value": "cross-origin" }
      ]
    }
  ]
}
```

## 离线支持（PWA）

JupyterLite 默认注册了 Service Worker，但要完全离线使用xeus内核，需要确保所有资源被缓存：

### 关键缓存资源

| 资源 | 必要性 | 缓存策略 |
|------|--------|---------|
| JupyterLab JS/CSS | 必须 | 预缓存 |
| xeus内核JS/WASM/DATA | 必须 | 预缓存或运行时缓存 |
| kernel_packages/*.tar.gz | 推荐 | 运行时缓存（按需） |
| fonts/images | 推荐 | 缓存优先 |

### 验证离线功能

1. 首次访问站点，等待所有核心资源加载
2. 在DevTools→Application→Service Workers中勾选"Offline"
3. 刷新页面，验证内核能启动
4. 创建Notebook执行简单代码

注意：运行时%conda install需要网络下载包，离线时不可用。预装包在离线时可用。

## 性能优化建议

### 1. 启用coincident模式

性能收益最大的优化——正确配置COOP/COEP头启用SharedArrayBuffer：
- 文件系统操作更快（同步SAB vs 异步postMessage轮询）
- stdin不需要Service Worker同步XHR
- 整体交互响应更快

### 2. 预装常用包

构建时预装常用包，避免首次使用时运行时下载：
- numpy/pandas/matplotlib等基础包放入environment.yml
- 运行时安装仅用于临时探索

### 3. 压缩WASM和tar.gz

确保Web服务器启用：
- gzip/brotli压缩WASM文件（虽然WASM已有二进制压缩，但gzip可额外减少15-20%）
- tar.gz已压缩，不需要再压缩

### 4. 使用HTTP/2或HTTP/3

HTTP/2多路复用显著改善并行下载WASM和tar.gz包的性能。

### 5. 预加载关键资源

在index.html中添加preload：

```html
<link rel="preload" href="xeus/kernels/xpython/xpython.wasm" as="fetch" type="application/wasm" crossorigin>
```

## 监控和诊断

### 健康检查端点

部署后验证关键端点：

```bash
# 检查kernels.json
curl -I https://jupyterlite.example.com/xeus/kernels.json

# 检查WASM文件可达
curl -I https://jupyterlite.example.com/xeus/kernels/xpython/xpython.wasm

# 检查COOP/COEP头
curl -I https://jupyterlite.example.com/ | grep -i cross-origin
```

### 浏览器端诊断

在DevTools Console检查：

```javascript
// 1. 确认crossOriginIsolated
console.log('COOP/COEP:', crossOriginIsolated);

// 2. 确认Service Worker注册
navigator.serviceWorker.getRegistrations().then(regs => {
  console.log('Service Workers:', regs.length);
});

// 3. 检查内核规格fetch
fetch('/xeus/kernels.json').then(r => r.json()).then(console.log);
```

## 相关概念

- [双Worker通信模式](../concepts/03-dual-worker-modes.md)
- [快速开始](../concepts/01-getting-started.md)
- [构建系统详解](../concepts/05-build-system.md)
- [基础部署示例](basic-deploy.md)

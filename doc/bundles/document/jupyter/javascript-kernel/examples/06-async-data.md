---
type: Tutorial
title: 异步编程与数据获取
description: 使用 fetch、async/await、Promise 和实时数据流
tags: [async, await, fetch, promise, api, data, stream, websocket]
generated: { by: "agent:source-code-to-okf-wiki", at: "2026-08-22T00:00:00+08:00" }
status: stable
stale_after: 2027-08-22
prerequisites: ["01-first-notebook"]
sources:
  - id: jk-executor
    title: executor.ts
---

# 异步编程与数据获取

JavaScript Kernel 原生支持 `async/await`，可以直接在单元格中使用顶层 await 获取数据、调用 API。

## Fetch API

### 获取 JSON 数据

```javascript
// 获取 GitHub 仓库信息
const repo = await fetch('https://api.github.com/repos/jupyterlite/jupyterlite')
  .then(r => r.json());

console.log(`仓库: ${repo.full_name}`);
console.log(`Stars: ${repo.stargazers_count}`);
console.log(`描述: ${repo.description}`);
repo
```

### 获取文本数据

```javascript
const text = await fetch('https://jsonplaceholder.typicode.com/posts/1')
  .then(r => r.text());
console.log(text.substring(0, 200));
```

### POST 请求

```javascript
const response = await fetch('https://jsonplaceholder.typicode.com/posts', {
  method: 'POST',
  headers: { 'Content-Type': 'application/json' },
  body: JSON.stringify({
    title: '来自 JS Kernel',
    body: '这是通过 fetch POST 发送的数据',
    userId: 1
  })
});
const result = await response.json();
console.log("创建的帖子 ID:", result.id);
result
```

### 错误处理

```javascript
try {
  const data = await fetch('https://api.github.com/repos/nonexistent/repo')
    .then(r => {
      if (!r.ok) throw new Error(`HTTP ${r.status}: ${r.statusText}`);
      return r.json();
    });
} catch(e) {
  console.error("请求失败:", e.message);
}
```

## 并行请求

```javascript
// 并行获取多个 API
const [users, posts, comments] = await Promise.all([
  fetch('https://jsonplaceholder.typicode.com/users').then(r => r.json()),
  fetch('https://jsonplaceholder.typicode.com/posts').then(r => r.json()),
  fetch('https://jsonplaceholder.typicode.com/comments').then(r => r.json())
]);

console.log(`Users: ${users.length}, Posts: ${posts.length}, Comments: ${comments.length}`);
```

### Promise.allSettled

```javascript
const results = await Promise.allSettled([
  fetch('https://api.github.com/repos/jupyterlite/jupyterlite').then(r => r.json()),
  fetch('https://api.github.com/repos/jupyterlite/javascript-kernel').then(r => r.json()),
  fetch('https://invalid-url-that-will-fail.xyz').then(r => r.json())  // 会失败
]);

results.forEach((r, i) => {
  if (r.status === 'fulfilled') {
    console.log(`请求 ${i + 1} 成功:`, r.value.full_name || r.value.name);
  } else {
    console.log(`请求 ${i + 1} 失败:`, r.reason.message);
  }
});
```

## 数据处理

### 获取并可视化数据

```javascript
// 获取数据并生成 HTML 表格
const posts = await fetch('https://jsonplaceholder.typicode.com/posts')
  .then(r => r.json());

let html = '<table style="border-collapse:collapse;width:100%;font-size:0.85em">';
html += '<tr style="background:#4A90D9;color:white"><th style="padding:6px;border:1px solid #ddd">ID</th><th style="padding:6px;border:1px solid #ddd">Title</th><th style="padding:6px;border:1px solid #ddd">User ID</th></tr>';
for (const post of posts.slice(0, 10)) {
  const bg = post.id % 2 === 0 ? '#f0f4ff' : 'white';
  html += `<tr style="background:${bg}"><td style="padding:6px;border:1px solid #ddd;text-align:center">${post.id}</td><td style="padding:6px;border:1px solid #ddd">${post.title}</td><td style="padding:6px;border:1px solid #ddd;text-align:center">${post.userId}</td></tr>`;
}
html += '</table>';
display(html);
```

### 数据聚合

```javascript
const posts = await fetch('https://jsonplaceholder.typicode.com/posts')
  .then(r => r.json());

// 按 userId 分组统计帖子数
const userPostCounts = {};
for (const post of posts) {
  userPostCounts[post.userId] = (userPostCounts[post.userId] || 0) + 1;
}

console.log("用户帖子数统计:");
for (const [userId, count] of Object.entries(userPostCounts)) {
  const bar = '█'.repeat(count);
  console.log(`User ${userId}: ${bar} ${count}`);
}
```

## 定时器与延迟

### 基本延迟

```javascript
console.log("开始...");
await new Promise(r => setTimeout(r, 1000));
console.log("1秒后");
await new Promise(r => setTimeout(r, 1000));
console.log("2秒后");
```

### 轮询

```javascript
const { Output } = Jupyter.widgets;
const out = new Output();
display(out);

for (let i = 5; i >= 0; i--) {
  out.clearOutput();
  out.appendStdout(`倒计时: ${i} 秒\n`);
  if (i === 0) {
    out.appendStdout("🚀 发射！\n");
  }
  await new Promise(r => setTimeout(r, 1000));
}
```

### 轮询 API

```javascript
// 定期检查某个状态
const { Output } = Jupyter.widgets;
const out = new Output();
const stopBtn = Jupyter.widgets.Button({ description: '停止轮询', button_style: 'danger' });
display(stopBtn);
display(out);

let stopped = false;
stopBtn.onClick(() => { stopped = true; });

let pollCount = 0;
while (!stopped && pollCount < 10) {
  pollCount++;
  const time = new Date().toLocaleTimeString();
  out.appendStdout(`[${time}] 轮询 #${pollCount}\n`);
  await new Promise(r => setTimeout(r, 2000));
}
out.appendStdout("轮询结束\n");
```

## WebSocket（IFrame 模式）

IFrame 模式支持 WebSocket 实时通信：

```javascript
const { Output, Button } = Jupyter.widgets;
const out = new Output();
const connectBtn = new Button({ description: '连接', button_style: 'success' });
const disconnectBtn = new Button({ description: '断开', button_style: 'danger' });
disconnectBtn.disabled = true;

display(Jupyter.widgets.HBox({ children: [connectBtn, disconnectBtn] }));
display(out);

let ws = null;

connectBtn.onClick(() => {
  if (ws) return;
  // 使用公共 echo WebSocket 服务（演示用）
  ws = new WebSocket('wss://echo.websocket.events');
  
  ws.onopen = () => {
    out.appendStdout("WebSocket 已连接\n");
    connectBtn.disabled = true;
    disconnectBtn.disabled = false;
    ws.send("Hello from JavaScript Kernel!");
  };
  
  ws.onmessage = (event) => {
    out.appendStdout(`收到: ${event.data}\n`);
  };
  
  ws.onerror = (err) => {
    out.appendStderr(`错误: ${err.message || '连接错误'}\n`);
  };
  
  ws.onclose = () => {
    out.appendStdout("WebSocket 已断开\n");
    connectBtn.disabled = false;
    disconnectBtn.disabled = true;
    ws = null;
  };
});

disconnectBtn.onClick(() => {
  if (ws) ws.close();
});
```

> ⚠️ WebSocket 连接在 IFrame 和 Worker 模式中都可用，但需注意 CORS 和目标服务器的 WebSocket 支持。

## 实时时钟示例

```javascript
const { Output } = Jupyter.widgets;
const out = new Output();
const stopBtn = Jupyter.widgets.Button({ description: '停止时钟', button_style: 'warning' });
display(stopBtn);
display(out);

let running = true;
stopBtn.onClick(() => { running = false; });

function updateClock() {
  if (!running) return;
  const now = new Date();
  const time = now.toLocaleTimeString('zh-CN', { hour12: false });
  const date = now.toLocaleDateString('zh-CN', { weekday: 'long', year: 'numeric', month: 'long', day: 'numeric' });
  
  out.clearOutput();
  out.appendDisplayData({
    'text/html': `<div style="text-align:center;padding:20px">
      <div style="font-size:3em;font-family:monospace;color:#4A90D9;font-weight:bold">${time}</div>
      <div style="color:#666;margin-top:8px">${date}</div>
    </div>`,
    'text/plain': `${date} ${time}`
  });
  
  setTimeout(updateClock, 1000);
}
updateClock();
```

## 注意事项

1. **所有单元格代码都在 async function 中执行**，所以顶层 `await` 直接可用
2. **fetch 受 CORS 限制**，目标 API 需要支持跨域请求
3. **setTimeout/setInterval** 在单元格执行完毕后仍然运行，记得清理
4. **Promise 未捕获的 rejection** 会显示为错误输出
5. **长时间运行的异步操作**不会阻塞 UI（Worker 模式完全不阻塞，IFrame 模式在 await 期间让出主线程）

## 相关文档

- [03-执行模型](../concepts/03-execution-model.md) — 顶层 await 的实现原理
- [03-使用 Widgets](03-using-widgets.md) — Output widget 配合异步操作
- [09-常见问题](../concepts/09-faq-limitations.md) — Worker 模式下的限制

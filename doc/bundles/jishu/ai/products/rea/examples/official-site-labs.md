---
type: Example
title: "REA 官网实验 速度 百分比与验证码"
description: "用公开纯函数检验恐龙更新顺序、计算器百分比分支及 Aegis 公共测试 key，区分教学模块和原应用"
sources:
  - id: site
    resource: ../references/official-site-source.md
  - id: facts
    resource: ../references/facts.md
generated: {by: "process:seven-concepts-e", at: "2026-10-12"}
status: draft
---

# REA 官网实验 速度 百分比与验证码

官网把逆向结果缩成可检查的规则，再用新界面演示。恐龙恢复速度更新、计算器解释百分比分支、Aegis 重建默认 TOTP 计算。下面的独立 Node 教学脚本无需 REA、游戏、Windows Calculator 或 APK；本轮只验证算法，不运行原目标。

## 恐龙先比较再增加

上游目标是 wayou 的 HTTP 浏览器版本，不是 `chrome://dino/`。规则起始 6、阈值 13、每次 collision-free update 增加 0.001；先比较再增加，不能替换为强制 clamp（F-149~F-151）。

```javascript
const assert = require("node:assert/strict");
function advanceSpeed(speed) {
  return speed < 13 ? speed + 0.001 : speed;
}
function simulateSpeed(updates) {
  let speed = 6;
  for (let i = 0; i < updates; i++) speed = advanceSpeed(speed);
  return speed;
}
for (const [updates, expected] of [
  [0, 6],
  [1000, 7.000000000000334],
  [4000, 9.99999999999956],
  [7000, 12.999999999997897],
  [10000, 13.000999999997896],
]) assert.equal(simulateSpeed(updates), expected);
assert.equal(advanceSpeed(13), 13);
assert.equal(advanceSpeed(12.9995), 13.000499999999999);
assert.ok(advanceSpeed(12.9995) > 13);
console.log("speed rule passed");
```

10000 次后显示三位小数为 13.001。上游原 Runner 的控制实验由独立 Playwright controller 完成；本轮复测官网 speed module，与五个已登记值一致，但未重跑 Runner。官网新小游戏的绘图、跳跃、碰撞和固定 60 updates/sec 是教学代码，不属恢复源码。

## 百分比的两个分支

Windows Calculator 11.2508.4.0 x64 的 launcher 只负责启动应用，逻辑位于 CalcViewModel.dll。函数选择经人工扫描辅助，Microsoft 固定源码作交叉解释，并未确认为安装包 build commit（F-146~F-148）。

```javascript
const assert = require("node:assert/strict");
function percentageOperand(previous, current, operator) {
  return ["multiply", "divide"].includes(operator)
    ? current / 100
    : current * (previous / 100);
}
assert.equal(200 + percentageOperand(200, 10, "add"), 220);
assert.equal(200 * percentageOperand(200, 10, "multiply"), 20);
console.log("percentage summary passed");
```

这是用 JS Number 写的两例教学摘要，不模拟完整 Calculator 的有理数系统、所有模式或状态机。Microsoft 单元测试只读未执行，上游 Windows GUI 输入核验未完成，本轮也不宣称原应用验证。

## Aegis 公共测试 key

默认 TOTP 将秒数除以 30 后向下取整，counter 编为八字节 big-endian，再算 HMAC-SHA1、动态截断、十进制取模与补零（F-160~F-164）。SHA1、六位、30 秒是默认值，不是所有导入账户的固定参数。

```javascript
const assert = require("node:assert/strict");
const { createHmac } = require("node:crypto");
function exampleCode(seconds, digits = 6) {
  const counter = Buffer.alloc(8);
  counter.writeBigUInt64BE(BigInt(Math.floor(seconds / 30)));
  const hash = createHmac("sha1", "12345678901234567890")
    .update(counter).digest();
  const offset = hash[hash.length - 1] & 15;
  const number = hash.readUInt32BE(offset) & 0x7fffffff;
  return String(number % 10 ** digits).padStart(digits, "0");
}
for (const [seconds, expected] of [
  [59, "94287082"],
  [1111111109, "07081804"],
  [1111111111, "14050471"],
  [1234567890, "89005924"],
  [2000000000, "69279037"],
  [20000000000, "65353130"],
]) {
  assert.equal(exampleCode(seconds, 8), expected);
  assert.equal(exampleCode(seconds, 6), expected.slice(-6));
}
assert.equal(exampleCode(30), "287082");
assert.equal(exampleCode(59), "287082");
assert.equal(exampleCode(60), "359152");
console.log("public OTP vectors passed");
```

key 是 RFC 公共测试串，不要输入真实账户 secret。相邻时间块重新计算，但验证码不保证总不相同。上游 133 输入由提取 Java harness、独立 Python 与 WebCrypto 对照；本轮重新对照 WebCrypto 与独立计算和公开输入，不运行 APK，也不验证 Android UI、vault 或签名。

以上脚本彼此独立，应分别运行。轻量测试输出与上游成绩的归属见 [验证记录](../references/official-site-verification.md)。

## 相关概念

- [重建验证](../concepts/13-reconstruction-verification.md)
- [五项官网案例](showcase-cases-example.md)
- [官网覆盖与固定证据](../references/official-site-source.md)

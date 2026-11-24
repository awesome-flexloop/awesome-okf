---
type: Example
title: "演练 02：维护者发布 Runbook（含仅更新安装器与预发布晋升）"
description: "按 RELEASING.md 复现一次发布：准备 CI 束、暂存、PR 合并、预发布/正式发布、发布后核验、清理旧版；附仅换安装器与容器测试路径"
tags: [发布流程, Runbook, 预发布, 安装器更新, 核验, 维护者]
generated: { by: "seven-concepts-cmd", at: "2026-11-21T12:00:00+08:00" }
status: stable
stale_after: 2027-05-31
---

# 演练 02：维护者发布 Runbook

> **性质**：按 `tools/RELEASING.md` 的步骤重排（F-031 ~ F-043），命令与判定条件均来自该文档与脚本。**本包未执行发布**，也未访问 GitHub Release。

## 前置检查（一次性）

```bash
git clone git@github.com:skyline-projext/skylinevpn-cli.git
cd skylinevpn-cli
tools/install-hooks.sh          # 锁定身份 + 装 commit-msg / pre-push
test -s ~/.config/skylinevpn-release/forbidden-terms && echo "禁止词清单就绪"
```

缺任何一项都不要开始：没有钩子等于没有早期反馈，没有禁止词清单则 `build_release.py` 直接拒绝运行（F-057、F-070）。

## 六步主流程

### 步骤 1：放入三个 CI 束

把上游构建产物放到仓库根（不要提交）：

```text
Linux-CLI-*.zip
macOS-CLI*.zip
Windows-CLI*.zip        # 含 ARM64 包时一并放入
```

这些文件名在 `.gitignore` 中（F-011、F-031），`git status` 不应出现它们。

### 步骤 2：暂存发布目录

```bash
python3 tools/build_release.py v3.0.1
```

成功标志：`dist/v3.0.1/` 存在，内含各平台安装包、三份安装器、`SHA256SUMS.txt`、`RELEASE_NOTES.md`（F-033）。失败时目录会被删除（F-059）。

自查三项：

```bash
ls dist/v3.0.1/
(cd dist/v3.0.1 && sha256sum -c SHA256SUMS.txt)
grep -c "releases/download/v3.0.1/" dist/v3.0.1/skyline-linux-install.sh
```

第一项看资产齐全，第二项看清单自洽，第三项看安装器已指向本 tag（F-034）。

### 步骤 3：走 PR（squash only）

`main` 只接受 PR，且只允许 squash 合并；PR 标题即提交标题，正文留空（F-036）。合并后本地同步：

```bash
git checkout main && git pull --ff-only
```

### 步骤 4：发布（先预发布，再晋升）

```bash
# 可选：先给测试者
tools/publish-release.sh v3.0.1 --prerelease

# 测试通过后晋升
gh release edit v3.0.1 --prerelease=false --latest
```

或直接正式发布：

```bash
tools/publish-release.sh v3.0.1
```

发布门会依次检查 token 属主、身份、校验和、HEAD 与 `origin/main` 一致，并要求终端回打确认（F-071、F-072）。任何一项不满足都会中止，不要试图跳过。

### 步骤 5：发布后核验

在**匿名**环境（未登录 gh、无缓存的网络）执行：

```bash
# 下载全部资产与 SHA256SUMS.txt 到空目录
sha256sum -c SHA256SUMS.txt
```

再在网页上确认：Release 与**每个资产**的上传者都是 `skyline-projext`（F-039）。上传者不对，即使哈希通过也不要放行。

### 步骤 6：清理旧版本

确认新版可用后，删除上一个 Release 但保留其 tag（F-040）：

```bash
gh release delete v3.0.0        # 不要加 --cleanup-tag
```

代价要清楚：旧资产删除后无法再安装旧版（D-6）。若本次发布有风险，宁可先停在预发布。

## 特例 A：只更新安装器（包不变）

适用场景：安装器措辞/进度条/下载地址需要修，但二进制未变。

```bash
python3 tools/build_release.py v3.0.1 --accept-upstream-terms
git diff --stat dist/v3.0.1      # 只应看到三份安装器 + Linux 束 + SHA256SUMS 变化
sha256sum dist/v3.0.1/*.deb dist/v3.0.1/*.pkg dist/v3.0.1/*.zip
gh release upload v3.0.1 dist/v3.0.1/* --clobber
```

判据：`.deb` / `.pkg` / `.zip` 的哈希必须与上一版**逐字节相同**；若不同，说明动了包，必须重走完整流程（F-041、F-035）。

`--accept-upstream-terms` 的含义：上游资产中已知的禁用字符串降级为警告（F-059）。它不改变生成物的致命规则。

## 特例 B：安装器测试（无真机也可）

```bash
# debian:12 容器：无 systemd、无 TUN，要求"完整安装退出 0"
podman run --rm -v "$PWD/dist/v3.0.1:/pkg:ro" debian:12 \
  bash -c "bash /pkg/skyline-linux-install.sh --lang en; echo exit=\$?"

# 免 root 校验
bash dist/v3.0.1/skyline-linux-install.sh --check dist/v3.0.1/skyline-linux-cli_3.0.1_amd64.deb

# Windows 安装器：用 pwsh 解析器做语法校验
pwsh -NoProfile -Command "\$null = [System.Management.Automation.Language.Parser]::ParseFile('dist/v3.0.1/skyline-windows-install.ps1',[ref]\$null,[ref]\$errs); if(\$errs){\$errs;exit 1}"
```

这三条对应仓库文档的测试口径（F-042），不能替代真实平台安装，但能在发布前抓住语法与步骤标记类错误。

## 发布前最后核对

- [ ] `dist/<tag>/` 存在且 `sha256sum -c` 通过
- [ ] 安装器内无其他 tag 的下载地址（F-056）
- [ ] 三平台版本一致（F-054）
- [ ] `RELEASE_NOTES.md` 含防诈骗声明与官网（F-061）
- [ ] 本地 HEAD == `origin/main`
- [ ] 新克隆装了钩子（若本次有新成员参与）

## 主题关联

- [02 发行拓扑](../concepts/02-distribution-topology.md)
- [04 暂存管线](../concepts/04-release-staging-pipeline.md)
- [05 身份与泄漏门](../concepts/05-identity-and-leak-gates.md)

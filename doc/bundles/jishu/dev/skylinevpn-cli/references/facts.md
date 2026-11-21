---
type: Reference
title: "skylinevpn-cli 仓库事实登记（F-001 ~ F-072）"
description: "对 skylinevpn-cli 发行仓库 HEAD 415d0bb（v3.0.1）的一手只读核验，逐条登记 72 项可追溯事实，供本束全部概念与示例文档引用"
source_repo: "\\\\10.16.11.3\\ai\\notebook\\libs\\skylinevpn\\skylinevpn-cli"
source_commit: "415d0bb"
source_version: "3.0.1"
measured_at: "2026-11-21"
generated: { by: "seven-concepts-cmd", at: "2026-11-21T12:00:00+08:00" }
status: stable
stale_after: 2027-05-31
---

# 仓库事实登记

> **信源等级**：L1（被解读对象自身的仓库内容与 git 元数据），非二手转述。
> **性质标注**：`[事实]` 可由仓库文件逐字核验；`[文档口径]` 仓库文档的自我描述，未经运行时复现；`[清点]` 本次现场目录/文件清点所得。
> **核验方式**：只读 `git log` / `git tag` / `git remote`、六份 README、`CHANGELOG.md`、`LICENSE`、`.gitignore`、`.gitattributes`、`tools/` 下四个脚本与 `RELEASING.md`；**未执行** `skyline` 二进制、**未运行** 安装器、**未访问** GitHub Release 页面与 SkylineVPN 服务端。
> 核验结论、口径冲突与对抗审查见 [verification.md](verification.md)。

## A. 仓库与版本（F-001 ~ F-012）

| 编号 | 事实 | 依据 | 级别 | 性质 |
|------|------|------|------|------|
| F-001 | 远端为 `git@github.com:skyline-projext/skylinevpn-cli.git`，默认分支 `main` | `git remote -v`、`git branch -a` | P0 | [事实] |
| F-002 | HEAD 为 `415d0bb`，提交日期 2026-10-28，标题 `Add Windows ARM64 package and pre-release option (#5)` | `git log -1` | P0 | [事实] |
| F-003 | 仓库共 6 条提交：`7bed184`（2026-10-17，`SkylineVPN CLI v3.0.0`）为初始提交，其余 5 条为 2026-10-18 与 2026-10-28 的 PR 合并 | `git log --format="%h\|%ad\|%s"` | P0 | [事实] |
| F-004 | 仅有两个标签：`v3.0.0`、`v3.0.1` | `git tag` | P0 | [事实] |
| F-005 | 初始提交之后的 5 条提交标题均带 `(#1)` ~ `(#5)` 形式 | `git log` | P0 | [事实] |
| F-006 | 非初始提交的作者为 `skyline-projext <176280006+skyline-projext@users.noreply.github.com>`，提交者为 `GitHub <noreply@github.com>` | `git log -1 --format` | P0 | [事实] |
| F-007 | 仓库不含产品源码：根目录为 6 份 README、`CHANGELOG.md`、`LICENSE`、`.gitattributes`、`.gitignore`，另加 `tools/` 下 4 个脚本与 `RELEASING.md`；根目录文件合计 42,028 字节 | 目录清点 | P0 | [清点] |
| F-008 | README 共 6 种语言：英语、简体中文、繁体中文、日语、俄语、波斯语 | 目录清点 | P0 | [事实] |
| F-009 | `LICENSE` 为专有许可：仅允许持官网有效订阅者下载、安装、使用；禁止修改、逆向工程、转售、再许可、再分发 | `LICENSE` | P0 | [事实] |
| F-010 | `.gitattributes` 规定 `*.sh` / `*.py` / `*.md` 为 LF，`*.ps1` / `*.cmd` 为 CRLF | `.gitattributes` | P1 | [事实] |
| F-011 | `.gitignore` 忽略 `dist/`、`upstream/`、`*.zip`、`*.tar.gz`、`*.deb`、`*.pkg`、`*.dmg`、`*.msi`、`*.version` 等构建输入与产物 | `.gitignore` | P0 | [事实] |
| F-012 | `.gitignore` 同时忽略 `.env*`、`*.pem`、`*.key`、`*token*`、`*secret*`，以及 `CLAUDE.md`、`AGENTS.md`、`MEMORY.md`、`.claude/`、`*.jsonl` 等智能体文件 | `.gitignore` | P0 | [事实] |

## B. 产品与命令面（F-013 ~ F-030）

| 编号 | 事实 | 依据 | 级别 | 性质 |
|------|------|------|------|------|
| F-013 | 平台矩阵：Linux（Ubuntu 22.04+ / Debian 12+，amd64、arm64）、macOS 12+（Intel 与 Apple 芯片）、Windows 10+（x64）、Windows 11（ARM64） | `README.zh-CN.md` 系统要求表 | P0 | [文档口径] |
| F-014 | 主干命令 5 条：`skyline login`、`skyline nodes`、`skyline connect <编号或 --best>`、`skyline status`、`skyline disconnect` | `README.zh-CN.md` 使用节 | P0 | [文档口径] |
| F-015 | 辅助命令：`mode smart` / `mode global`、`nodes --refresh`、`me`、`lang english` / `lang chinese`、`logout`（`--purge`）、`version`、`--help` | `README.zh-CN.md` 命令表 | P0 | [文档口径] |
| F-016 | CLI 内无法购买订阅，须先在官网购买后用同一账号登录 | `README.zh-CN.md` 提示块 | P0 | [文档口径] |
| F-017 | 唯一官网为 `www.skylinevpn.com`；`getskyline.org` 被声明为钓鱼网站并与该公司无关联 | `README.zh-CN.md` 防诈骗提示 | P0 | [文档口径] |
| F-018 | 官方 Telegram 频道仅 `@skyline_vpn`（公告）与 `@skyline_vpn_1`（通知） | `README.zh-CN.md` Telegram 节 | P0 | [文档口径] |
| F-019 | 安装器行为：检测系统架构、校验 SHA-256、安装后台服务、询问显示语言 | `README.zh-CN.md` 安装节 | P0 | [文档口径] |
| F-020 | 可预指定语言：macOS/Linux `\| sudo bash -s -- --lang en`，Windows `-Lang en`；中文用 `zh` | `README.zh-CN.md` 安装节 | P0 | [文档口径] |
| F-021 | 三平台一键安装命令均指向 `releases/latest/download/<安装器>` | `README.zh-CN.md` 安装节 | P0 | [文档口径] |
| F-022 | 离线安装形态：Linux 为 `skyline-linux-cli-universal-*.tar.gz`（内含 `install.sh`）；macOS 为 `.pkg` 与安装脚本同目录；Windows 为含 `install.cmd` 的 zip | `README.zh-CN.md` 离线安装节 | P0 | [文档口径] |
| F-023 | `bash skyline-{linux,macos}-install.sh --check <file>` 可在不安装的情况下校验安装包 | `README.zh-CN.md` 离线安装节 | P0 | [文档口径] |
| F-024 | 更新方式为再次运行安装命令，始终获取最新版本 | `README.zh-CN.md` 更新节 | P0 | [文档口径] |
| F-025 | 卸载：Linux `sudo apt-get remove skyline-cli`（`purge` 连数据与日志）；macOS `/usr/local/lib/skyline/uninstall.sh`（`--purge`）；Windows `uninstall.ps1`（`-Purge`） | `README.zh-CN.md` 卸载表 | P0 | [文档口径] |
| F-026 | 日志路径：`/var/log/skyline/`、`/Library/Logs/Skyline/`、`%ProgramData%\Skyline CLI\logs` | `README.zh-CN.md` 故障排除节 | P0 | [文档口径] |
| F-027 | Linux VPS/容器需要 `/dev/net/tun`；容器须 `--device /dev/net/tun --cap-add NET_ADMIN` | `README.zh-CN.md` 故障排除节 | P0 | [文档口径] |
| F-028 | Windows 安装后须开新终端；Linux 须注销重登一次才能免 `sudo` 使用 `skyline` | `README.zh-CN.md` 使用节注记 | P0 | [文档口径] |
| F-029 | `CHANGELOG.md` 记录 v3.0.0（2026-10-17）为首个公开版本，v3.0.1（2026-10-27）新增 Windows 11 ARM64 支持 | `CHANGELOG.md` | P0 | [事实] |
| F-030 | v3.0.0 功能清单：一键安装器（架构检测 + SHA-256）、分步进度条、中英界面、智能分流与全局模式 | `CHANGELOG.md` | P0 | [事实] |

## C. 发行架构（F-031 ~ F-044）

| 编号 | 事实 | 依据 | 级别 | 性质 |
|------|------|------|------|------|
| F-031 | 发行输入为三个 CI 束，置于仓库根且被 git 忽略：`Linux-CLI-*.zip`、`macOS-CLI*.zip`、`Windows-CLI*.zip`（另有 ARM64 包时随 Windows 束） | `tools/RELEASING.md` 步骤 1 | P0 | [文档口径] |
| F-032 | 暂存命令为 `python3 tools/build_release.py <tag>`；`--src` 默认仓库根，`--out` 默认 `dist/<tag>` | `tools/build_release.py` 文档串与参数解析 | P0 | [事实] |
| F-033 | 产物为各平台安装包、三份安装器、`SHA256SUMS.txt` 与 `RELEASE_NOTES.md` | `build_release.py` 输出清单 | P0 | [事实] |
| F-034 | 安装器内所有 `/releases/download/<tag>/` 被重写为本次 tag，使安装器与其自身安装包匹配 | `build_release.py` 的 `retag()` | P0 | [事实] |
| F-035 | 若上游安装器已指向该 tag，则资产按上游构建结果逐字节发布（Linux 离线束直接复制） | `build_release.py` 的 `build_linux()` 分支 | P0 | [事实] |
| F-036 | `main` 只接受 PR；仅允许 squash 合并，以 PR 标题为提交标题、正文留空 | `tools/RELEASING.md` 步骤 3 | P0 | [文档口径] |
| F-037 | 发布命令为 `tools/publish-release.sh <tag>`，内部调用 `gh release create --latest`；`--prerelease` 改为预发布 | `publish-release.sh` | P0 | [事实] |
| F-038 | 预发布晋升命令为 `gh release edit <tag> --prerelease=false --latest` | `RELEASING.md` 步骤 4 | P0 | [文档口径] |
| F-039 | 发布后核验：匿名下载全部资产、`sha256sum -c SHA256SUMS.txt`、核对 release 与每个资产的上传者均为 `skyline-projext` | `RELEASING.md` 步骤 5 | P0 | [文档口径] |
| F-040 | 仅保留最新 release：旧 release 删除但保留 tag（明确不带 `--cleanup-tag`） | `RELEASING.md` 步骤 6 | P0 | [文档口径] |
| F-041 | 仅更新安装器时：以 `--accept-upstream-terms` 重新暂存，只允许三份安装器、Linux 束与 `SHA256SUMS.txt` 变化，`.deb`/`.pkg`/`.zip` 必须逐字节一致，再 `gh release upload --clobber` | `RELEASING.md` 安装器更新节 | P0 | [文档口径] |
| F-042 | 安装器测试路径：debian:12 容器完整安装须退出 0（该环境无 systemd 与 TUN）；`--check` 免 root；Windows 用 pwsh 解析器做语法校验 | `RELEASING.md` 测试节 | P0 | [文档口径] |
| F-043 | `RELEASING.md` 禁止提交二进制、`*.version`、内部测试脚本、token、智能体指令与记忆文件 | `RELEASING.md` 末段 | P0 | [文档口径] |
| F-044 | `tools/` 下共 4 个脚本：`build_release.py`、`check-identity.sh`、`install-hooks.sh`、`publish-release.sh` | 目录清点 | P1 | [清点] |

## D. build_release.py 机制（F-045 ~ F-064）

| 编号 | 事实 | 依据 | 级别 | 性质 |
|------|------|------|------|------|
| F-045 | tag 必须匹配 `^v\d+\.\d+\.\d+([-.][0-9A-Za-z.-]+)?$`，否则中止 | `main()` 校验 | P0 | [事实] |
| F-046 | `sub()` 封装 `re.subn` 并强制命中次数落在 `[count_min, count_max]`，上游格式漂移即失败 | `sub()` | P0 | [事实] |
| F-047 | `var()` 按变量名与引号风格提取安装器变量，未找到即失败 | `var()` | P0 | [事实] |
| F-048 | `one()` 要求 glob 恰好命中 1 个文件，0 个或多个都中止 | `one()` | P0 | [事实] |
| F-049 | Linux：按安装器内嵌的 `DEB_SHA256_AMD64/ARM64` 校验两个 `.deb`；解包 universal 束，并要求束内 `install.sh` 与外层安装器逐字一致 | `build_linux()` | P0 | [事实] |
| F-050 | Linux 需重打包时，以 `uid=gid=0`、`uname=gname=root`、同目录布局重写 tar.gz | `build_linux()` 的 `reset()` | P0 | [事实] |
| F-051 | macOS：按 `PKG_SHA256` 校验 `.pkg`，且 `SELF_URL` 须以安装器文件名结尾；只发布 `.pkg` 与安装器 | `build_macos()` | P0 | [事实] |
| F-052 | Windows：校验 `ZipSha256`；`ZipNameArm64`、`ZipSha256Arm64`、`ZipUrlArm64` 必须同时存在或同时为空 | `build_windows()` | P0 | [事实] |
| F-053 | Windows 依据包内 `core/skyline-cli-core.version` 的 `arch=` 字段判定架构，缺省视为 amd64 | `build_windows()` | P0 | [事实] |
| F-054 | 三平台 app version 不一致即中止；tag 与 app version 不一致仅打印提示、不中止 | `main()` | P0 | [事实] |
| F-055 | `LEAK_PATTERNS` 共 15 条：云存储/CDN 痕迹、Telegram、「开发群」、`.github/workflows`、非本仓 `github.com`、`PLAN`、`D-编号`、`用户：`、`App 会话`、裸 `CI`、`Artifact`、agent 身份关键字、session 串、邮箱 | `LEAK_PATTERNS` | P0 | [事实] |
| F-056 | `check_leaks()` 同时断言安装器内每个 `/releases/download/<tag>/` 都等于本次 tag | `check_leaks()` | P0 | [事实] |
| F-057 | 禁止词清单位于仓库外 `~/.config/skylinevpn-release/forbidden-terms`（可被 `SKYLINE_FORBIDDEN_TERMS` 覆盖），缺失或为空即拒绝运行 | `forbidden_terms()` | P0 | [事实] |
| F-058 | 扫描器解压 gzip / xz / zstd / Apple pbzx，并按 zip / tar / ar(.deb) / xar(.pkg) 递归到最后一层文件；匹配同时覆盖 UTF-8 与 UTF-16LE 字节序列 | `unwrap()`、`members()`、`scan_terms()` | P0 | [事实] |
| F-059 | 生成物（`RELEASE_NOTES.md`、`SHA256SUMS.txt`）命中禁止词恒为致命；上游资产命中在 `--accept-upstream-terms` 下降级为警告；失败时删除 `dist/<tag>` | `main()` 收尾 | P0 | [事实] |
| F-060 | `SHA256SUMS.txt` 覆盖暂存目录内全部资产，且在 `RELEASE_NOTES.md` 之前生成，故 notes 自身不在校验清单 | `main()` 顺序 | P0 | [事实] |
| F-061 | `RELEASE_NOTES.md` 含防诈骗声明、官网、三平台一键安装命令、资产表与三平台 build 号 | `notes()` | P0 | [事实] |
| F-062 | `brand_bash()` 注入 6 步进度条并要求 `stage` 标记命中，缺失即失败；`--check` 模式下总步数改为 3 | `brand_bash()` | P0 | [事实] |
| F-063 | `brand_ps1()` 注入 4 步进度，实际安装交由包内 `install.ps1` | `brand_ps1()` | P0 | [事实] |
| F-064 | `scrub_common()` 改写面向客户措辞：Telegram 取件地址改为 Releases、开发群改为官网客服、CI 占位提示去 CI 化 | `scrub_common()` | P0 | [事实] |

## E. 身份与泄漏门（F-065 ~ F-072）

| 编号 | 事实 | 依据 | 级别 | 性质 |
|------|------|------|------|------|
| F-065 | 发布身份锁定为 `skyline-projext <176280006+skyline-projext@users.noreply.github.com>`；提交者额外允许 `GitHub <noreply@github.com>` | `check-identity.sh` | P0 | [事实] |
| F-066 | `--commit-msg` 模式检查四项：提交信息泄漏模式、信息内禁止词、暂存区智能体文件、暂存区禁止词 | `check-identity.sh` | P0 | [事实] |
| F-067 | 全量模式检查：HEAD 全部提交的作者/提交者、提交信息、历史上出现过的文件名、每个已提交版本的内容与索引 | `check-identity.sh` | P0 | [事实] |
| F-068 | `MSG_LEAKS` 禁止 `co-authored-by`/`signed-off-by`/`reviewed-by`/`claude-session`/`generated-by` 踪迹，以及 `claude.ai`、`anthropic`、`claude code`、`session_*` | `check-identity.sh` | P0 | [事实] |
| F-069 | `AGENT_FILES` 覆盖 `CLAUDE.md`/`AGENTS.md`/`GEMINI.md`/`MEMORY.md`/`.mcp.json`/`.cursorrules`/`copilot-instructions.md`/`.claude`/`.cursor`/`.codex`/`.aider*`/`.continue`/`memory/` 与 `*.jsonl` | `check-identity.sh` | P0 | [事实] |
| F-070 | `install-hooks.sh` 锁定本克隆的 `user.name`/`user.email`，写入 `commit-msg` 与 `pre-push` 两个钩子；钩子仅在本地 `.git/hooks`，不随仓库推送 | `install-hooks.sh` | P0 | [事实] |
| F-071 | `publish-release.sh` 要求 `GH_TOKEN`（缺省时从 `~/.zshrc` 的 `export_ghp_skylinevpn_token` 读取），并校验 token 属主为 `skyline-projext` | `publish-release.sh` | P0 | [事实] |
| F-072 | `publish-release.sh` 依次要求：`dist/<tag>` 已暂存、`SHA256SUMS.txt` 校验通过、身份检查通过、本地 HEAD 等于 `origin/main`、终端回打发布账号确认；任一不满足即中止 | `publish-release.sh` | P0 | [事实] |

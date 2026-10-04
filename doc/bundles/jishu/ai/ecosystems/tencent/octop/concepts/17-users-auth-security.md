---
type: Concept
title: "用户、RBAC、SSO 与登录验证码"
description: "UserManager 与 users 表、admin/user 两角色、26 条权限的三组分类与 resource_policy、邀请码与 Argon2id 口令策略、四类 SSO provider 的 OIDC/OAuth 架构、七类登录验证码。"
tags: [octop, users, rbac, permissions, sso, oidc, captcha, argon2, invites]
generated: { by: "reference_agent/trae-cn", at: 2026-10-04T10:00:00+08:00 }
verified: { by: "process:grep-v", at: 2026-10-04T10:00:00+08:00 }
status: stable
stale_after: 2027-10-04
sources:
  - id: facts
    resource: /spec/facts.md
    title: Octop 源码事实清单 F-407/F-409、F-441~F-454、F-480~F-496（v1.0.2b5，commit e473dd3c）
---

# 用户、RBAC、SSO 与登录验证码

Octop 是多用户平台：每个登录身份持有角色、细粒度权限键、资源配额与个性化偏好；登录既支持本地口令，也支持 OIDC 与三家国产 OAuth 单点登录，并可在登录链路前挂一层验证码。这些能力全部位于 `src/octop/infra/users/` 与 `src/octop/infra/auth/` 两个领域子包中。

## 用户模型与 users 表

用户领域的内存模型是 `UserManager` 持有的 `User` dataclass（F-441）：

```python
class Role(StrEnum):
    ADMIN = "admin"
    USER = "user"

@dataclass
class User:
    id: int
    username: str
    role: str          # 角色模板公开 id：admin | user | 自定义 ULID
    display_name: str | None
    locale: str = "zh"
    permissions: list[str] = field(default_factory=list)

    @property
    def is_admin(self) -> bool:
        return self.role == Role.ADMIN
```

注意 1.0.2b3 起 `role` 字段存储的是**角色模板 id**（内置为 `admin`/`user`，自定义角色为 ULID），而不再是权限位的拷贝（F-441、F-149）。

`users` 表在备份快照中被逐列清点为 **11 列**（F-409）：

| # | 列 | 用途 |
|---|---|---|
| 1 | `id` | 主键 |
| 2 | `username` | 登录名 |
| 3 | `password_hash` | Argon2id 散列 |
| 4 | `role` | 角色模板 id |
| 5 | `display_name` | 显示名 |
| 6 | `disabled` | 是否停用 |
| 7 | `created_at` | 创建时间 |
| 8 | `locale` | 语言偏好 |
| 9 | `preferences_json` | 个性化偏好 JSON |
| 10 | `login_failed_count` | 连续失败计数 |
| 11 | `login_locked_until` | 锁定截止时间戳 |

用户拥有的数据在备份/恢复时按 **8 张归属表**重写属主：`agents`、`channels`、`cron_jobs`、`sessions`、`threads`、`connectors`、`connector_oauth_states`、`usage_log`（F-407）。登录失败次数下限为 `max(1, ...)`、锁定秒数下限为 `max(60, ...)`，避免配置出非法的 0 或负值（F-446）。

## 26 条权限与三组分类

权限不是层级树，而是一个**模块键目录**：持有键即可进入该模块管理页并执行写操作；聊天、读取等日常行为永远不被权限拦截，`admin` 角色绕过全部校验（F-442、F-444）。`PERMISSIONS` 注册表实测 **26 条**，分三组：

| 组 | 条数 | 键逐字 |
|---|---:|---|---|
| settings | 4 | `channels`、`connectors`、`skill_packages`、`knowledge_bases` |
| control | 4 | `terminal`、`browser`、`desktop`、`mobile` |
| admin | 18 | `users`、`sso`、`providers`、`ollama_models`、`onnx_models`、`storage_backends`、`plugins`、`security`、`admin_console`、`envs`、`search`、`knowledge_settings`、`voice`、`observability`、`backup`、`tls`、`update`、`captcha` |

来源：F-442、F-443。

```python
BASELINE_PERMISSIONS = {key for key, p in PERMISSIONS.items() if p.category == "settings"}

def user_has_permission(user, key: str) -> bool:
    if key not in PERMISSIONS:
        return False            # 未知键一律拒绝
    if user.is_admin:
        return True             # admin 绕过
    return key in (user.permissions or [])
```

settings 组是新用户的**基线勾选集**：它会在新建用户时默认选中，但仍显式写入存储，并非隐式授予（F-444）。未知权限键在保存时会被 `validate_permission_keys` 拒绝，防止脏权限流入（F-444）。

## resource_policy：从权限键到资源配额

权限键管「能不能进模块」，资源策略管「能用多少」。`resource_policy.py` 定义三条每用户命名策略（F-454）：

| 策略键 | 语义 |
|---|---|
| `workspace_root_dir` | 允许的工作区根目录；容器内忽略该策略 |
| `token_quota` | 令牌配额；周期内 `used >= quota` 即拒绝 |
| `max_agents` | Agent 数量上限；计数时过滤 `kind="expert"` |

权限与策略的变更全程写审计日志。用户域实测 **11 个审计动作**：`user.create`、`user.sso_create`、`sso_bind`、`sso_unbind`、`auth.login`、`user.set_permissions`、`set_workspace_root_dir`、`set_token_quota`、`set_max_agents`、`set_role`、`set_email`（F-447）。

同一套键还驱动前端侧边栏：偏好中的 `SIDEBAR_NAV_KEYS` 实测 **19 个**键（`chat`、`experts`、`tasks`、`token-usage`、`personalization`、`channels`、`connectors`、`skill-packages`、`knowledge-bases`、`bridge`、`workbench`、`remote-desktop`、`acp`、`admin-users`、`models`、`admin-storage`、`admin-plugins`、`admin-security`、`admin-advanced`），自定义分组上限 24、名称 ≤40 字符、标题 ≤80 字符（F-448）。偏好另含 5 个数据键：`remote_browser_bookmarks`（上限 12 条）、`preferred_model`、`model_reasoning`（`auto`/`enabled`/`disabled`）、`timezone`、`sidebar_nav`（F-448）。

## 邀请码：一次性入站开户

管理员可以不直接建用户，而是发一次性邀请链接（F-451、F-452）：

- 码长 **11 字符**，字母表为 `ascii_letters + digits`，通过 `secrets.choice` 生成
- 有效期 **1~90 天**，默认 **7 天**（`DEFAULT_EXPIRES_DAYS=7`）
- 公共兑换端点限流：**60 秒窗口内最多 20 次**（`RATE_LIMIT_BURST=20`）
- 链接形态 `/invite?code={code}`；落库碰撞最多重试 8 次
- 四态流转：`pending` → `used`/`expired`/`revoked`，兑换时重复判定后三态（F-453）
- 审计动作：`invite.create`、`invite.revoke`、`invite.redeem`（F-453）

1.0.2b3 起邀请携带**角色模板与头像快照**，兑换出的用户即使之后模板变更也保留开户时的角色与头像（F-149）。

## 口令策略与账户附属能力

口令散列使用 Argon2id（`argon2-cffi` 的 `PasswordHasher()` 默认参数），最短 **8 位**，必须同时包含字母与数字，且不得与旧密码相同（F-449、F-450）。另有 **14 个**大小写不敏感的弱口令黑名单：

```
password, password1, password12, password123, 12345678, 123456789,
qwerty123, admin123, welcome1, letmein1, changeme1, octop123,
abc12345, iloveyou1
```

用户名只允许字母数字与 `_.-`，最大长度 **64**；OIDC claims 无法给出合法名时兜底为 `"sso_" + sha256(subject)[:12]`（F-445）。其余账户附属能力（F-454）：

- **acting 代理身份**：CLI/通道代用户操作时解析优先级为 `as_username` → `pinned_username` → Agent owner
- **email**：正则 `^[^@\s]+@[^@\s]+\.[^@\s]+$`，比较前 `strip().lower()`
- **profile_avatar**：支持 png/jpeg/webp/gif 四类媒体，响应 `Cache-Control: private, max-age=60`，落盘经 `.tmp` 文件原子替换

## 单点登录：一个 service，四类 provider

SSO 子包位于 `src/octop/infra/auth/sso/`，由 `SsoService` 编排 discovery、PKCE、ID Token 校验、密钥加解密与回跳净化，provider 适配层放在 `providers/`（F-480~F-486）：

```
浏览器 ──/oidc/start 或 /oauth/start──▶ SsoService
                                          │
        ┌─────────────────────────────────┼──────────────────────────────┐
        ▼                ▼                ▼                ▼             ▼
  discovery.py     pkce.py         id_token.py       crypto.py   redirect_after.py
  /.well-known/    S256 挑战        RS256/ES256       sso_fernet  仅允许站内路径
  openid-          verifier 64B     leeway=60、kid    Fernet 加密  默认 /chat
  configuration    nonce 32B        exp/iat/nonce     凭据落库
        │                │                │                │             │
        └──────────── providers/base.py：SSO_KINDS = ("oidc","feishu","dingtalk","wecom") ┘
```

登录态有两个短 TTL（F-480、F-481）：

| 常量 | 值 | 含义 |
|---|---:|---|---|
| `_LOGIN_STATE_TTL_SECONDS` | 600 | state/nonce 10 分钟有效 |
| `_LOGIN_CODE_TTL_SECONDS` | 60 | 回调换取的登录 code 1 分钟有效 |

- state cookie 由 API 层下发：`octop_sso_state`、path `/api/auth`、httponly、samesite=lax、secure 随 https，TTL 同为 600 秒（F-518）
- provider 凭据经 `SecretRepo.get_or_create("sso_fernet")` 取密钥后以 Fernet 对称加密落库（F-481）
- OIDC discovery 走标准 `/.well-known/openid-configuration`，缓存 3600 秒，issuer 比较前去尾斜杠（F-483）
- 默认 scopes 为 `openid profile email`，强制 PKCE S256（F-487）
- 回跳地址默认 `/chat`，拒绝控制字符以及 `//`、反斜杠、`://`、`http:` 等开放重定向载体；strict origin 只接受 http/https 且不得带 path/query/fragment/username（F-484、F-485）

**ID Token 仅接受 `RS256` 与 `ES256`**（F-482）的安全含义：强制非对称签名——验签公钥来自 IdP 的 JWKS 端点且要求令牌头带 `kid`，客户端密钥无法被用来伪造令牌；同时配合 `exp`/`iat` 必含、60 秒时钟容差与 nonce 严格匹配，抑制重放与混 token 攻击。对称算法（如 HS256）被明确排除。

三家国产 OAuth 各有取舍（F-488、F-489）：飞书区分国际/国内双区域主机，且其 authorize 不使用 OIDC nonce；钉钉网页登录不使用 nonce/PKCE、scope 为 `openid`、prompt 为 `consent`；企业微信走 `login.work.weixin.qq.com` 的 `CorpApp` 登录，请求体不含 nonce/code_challenge，配置额外需要 `agent_id`。

## 登录验证码：7 个内置 provider

`infra/auth/captcha/` 在启动时由 `boot_from_services` 装配，登录入口统一经 `ensure_captcha`：token 为空直接抛 `CAPTCHA_REQUIRED`（F-496）。内置注册实测 **7 个 provider**（F-494）：

| slug | 远端校验 | 要点 |
|---|---|---|
| `slider` | 否 | 内置滑块；远程分支断言 `"slider never verifies remotely"`（F-490） |
| `tencent` | 是 | 腾讯云验证码，`CaptchaType=9`、版本 `2019-07-22`，通过条件 `CaptchaCode==1 且 EvilLevel!=100`，需 CAM 密钥对（F-493） |
| `turnstile` | 是 | Cloudflare `challenges.cloudflare.com/turnstile/v0/siteverify`（F-491） |
| `hcaptcha` | 是 | `api.hcaptcha.com/siteverify`（F-491） |
| `recaptcha` | 是 | Google siteverify，`listed=False`（F-491） |
| `recaptcha-v3` | 是 | `requires_score=True`，别名 `recaptcha_v3`，要求 action 必须等于 `"login"`（F-491） |
| `geetest-v4` | 是 | 别名 `geetest`/`geetest4`/`gt4`；`sign_token = HMAC-SHA256(captcha_key, lot_number)`，仅 `result=="success"` 放行（F-492） |

启动环境快照 `CaptchaEnv` 为 frozen dataclass，实测 **6 字段**：`provider`、`site_key`、`secret`、`v3_min_score`（默认 **0.5**）、`cam_secret_id`、`cam_secret_key`（F-495）。对应环境变量为 `OCTOP_CAPTCHA_PROVIDER`（缺省 `slider`）、`OCTOP_CAPTCHA_SITE_KEY`、`OCTOP_CAPTCHA_SECRET`、`OCTOP_CAPTCHA_V3_MIN_SCORE`、`OCTOP_CAPTCHA_CAM_SECRET_ID/KEY`（F-495）。运行时配置存于 settings 键 `captcha.settings`；无 token 的 provider 对外只序列化为 `{"provider": "slider"}`（F-496）。

管理员把自己锁在门外时，唯一的离线逃生通道是 CLI（详见 [/concepts/20-api-cli-surface.md](20-api-cli-surface.md)）：

```bash
octop captcha reset
```

它直接打开本地 SQLite 删除 `captcha.settings`，不影响 `OCTOP_CAPTCHA_*` 启动环境变量（F-559）。

## 相关概念

- [/concepts/04-db-di.md](04-db-di.md)
- [/concepts/20-api-cli-surface.md](20-api-cli-surface.md)
- [/concepts/01-server-lifecycle.md](01-server-lifecycle.md)

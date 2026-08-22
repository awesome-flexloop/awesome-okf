---
title: 配置 HTTPS 与 Let's Encrypt
description: 使用 Let's Encrypt 免费证书为 TLJH 启用 HTTPS
type: Example
tags: [example, https, lets-encrypt, tls, ssl, certificates, security, jupyterhub, tljh, devops]
sources:
  - id: tljh-traefik
    title: tljh/traefik.py
  - id: tljh-config
    title: tljh/config.py
---

# 配置 HTTPS 与 Let's Encrypt

本文档演示如何使用 Let's Encrypt 免费 SSL 证书为 TLJH 启用 HTTPS。

## 前置条件

- TLJH 已安装并运行在 80 端口
- 服务器有公网 IP
- 拥有一个已解析到服务器 IP 的域名
- 80 和 443 端口对外开放（防火墙/安全组）

## 步骤1：确认域名解析

在本地机器上验证域名指向服务器 IP：

```bash
nslookup yourdomain.example.com
```

确保返回的 IP 地址是你的服务器 IP。

在服务器上确认可以访问自己：

```bash
curl -I http://yourdomain.example.com
```

应返回 HTTP 200。

## 步骤2：配置 Let's Encrypt

```bash
sudo tljh-config set https.enabled true
sudo tljh-config set https.letsencrypt.email your-email@example.com
sudo tljh-config add-item https.letsencrypt.domains yourdomain.example.com
```

- `email`：Let's Encrypt 用于发送证书到期通知的邮箱
- `domains`：你的域名列表（可以添加多个）

如果有多个域名：

```bash
sudo tljh-config add-item https.letsencrypt.domains app.yourdomain.example.com
```

## 步骤3：重载代理配置

```bash
sudo tljh-config reload proxy
```

## 步骤4：验证 HTTPS

等待几秒钟让证书申请完成，然后在浏览器中访问：

```
https://yourdomain.example.com
```

应该能看到安全的 HTTPS 连接（地址栏显示锁图标）。

也可以用 curl 验证：

```bash
curl -I https://yourdomain.example.com
```

HTTP 访问（80端口）会自动重定向到 HTTPS（443端口）。

## 测试环境（Staging）

在正式申请证书前，建议先用 Let's Encrypt 的 staging 环境测试，避免触发速率限制：

```bash
sudo tljh-config set https.letsencrypt.staging true
sudo tljh-config reload proxy
```

测试完成后切回正式环境：

```bash
sudo tljh-config unset https.letsencrypt.staging
sudo tljh-config reload proxy
```

## 使用手动证书

如果你有自己的 TLS 证书（如内部 CA 签发或购买的商业证书）：

```bash
sudo tljh-config set https.enabled true
sudo tljh-config set https.tls.key /path/to/private.key
sudo tljh-config set https.tls.cert /path/to/certificate.crt
sudo tljh-config reload proxy
```

- `key`：私钥文件路径（PEM 格式）
- `cert`：证书文件路径（PEM 格式，可包含完整证书链）

确保证书文件和私钥对 Traefik 进程可读（traefik 以 root 运行，通常无问题）。

## 证书存储和续期

- Let's Encrypt 证书存储在 `/opt/tljh/state/acme.json`，权限 0o600
- Traefik 自动处理证书续期（在证书到期前自动续期）
- 无需手动设置 cron 任务

## 修改 HTTPS 端口

默认 HTTPS 端口为 443，如需修改：

```bash
sudo tljh-config set https.port 8443
sudo tljh-config reload proxy
```

## 禁用 HTTPS

如需回到纯 HTTP：

```bash
sudo tljh-config set https.enabled false
sudo tljh-config reload proxy
```

## 故障排查

### 证书申请失败

查看 Traefik 日志：

```bash
sudo journalctl -u traefik -n 100
```

常见原因：
1. **域名未正确解析**：DNS 尚未生效或指向错误 IP
2. **端口被封**：80 或 443 端口被防火墙/云安全组阻止
3. **速率限制**：短时间内申请次数过多，使用 staging 环境测试
4. **邮箱格式无效**：确保 email 格式正确（JSON Schema 会验证 email 格式）

### 证书续期失败

- 检查 80 端口是否对外开放（tunnel 验证需要 80 端口）
- 检查磁盘空间（acme.json 所在分区）
- 查看 Traefik 日志中的 ACME 错误

### 浏览器显示不安全

- 检查系统时间是否正确
- 如果使用 staging 环境，浏览器会不信任证书（这是正常的，staging 证书不受信任）
- 确认证书的域名与访问的域名匹配

### HTTPS 配置后无法访问

1. 确认 traefik 服务在运行：`sudo systemctl status traefik`
2. 检查配置是否正确：`sudo cat /opt/tljh/state/traefik.toml`
3. 检查 443 端口是否在监听：`sudo ss -tlnp | grep 443`

## HTTPS 配置参考

最终 config.yaml 中的 HTTPS 配置类似：

```yaml
https:
  enabled: true
  address: ""
  port: 443
  letsencrypt:
    email: your-email@example.com
    domains:
      - yourdomain.example.com
    staging: false
  tls:
    key: ""
    cert: ""
```

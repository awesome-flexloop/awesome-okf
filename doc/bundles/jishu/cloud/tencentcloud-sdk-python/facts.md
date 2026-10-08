# R 阶段事实清单：tencentcloud-sdk-python 3.1.185

> 本文件是「腾讯云 Python SDK 源码学习」知识包的 R（Retrospective）阶段产物，所有事实均自源码逐字采集，每条标注信源位置，供 I/E/V 阶段引用。事实编号 F-001 起。

## 信源表

| 信源 ID | 内容 | 版本/时点 | 位置 |
|---|---|---|---|
| SRC-REPO | tencentcloud-sdk-python 源码仓库（GitHub: TencentCloud/tencentcloud-sdk-python） | tag `3.1.185`，commit `be50b26d4d997c5d8d9c07fc84c03ee5e05ece68`，提交时间 2026-10-02 03:57:10 +0800，提交信息 "release 3.1.185"，工作树 clean | 本地只读副本 `external/dao/runtime/tencent/tencentcloud-sdk-python`（主仓 gitignore 的外部信源区；本束文档不产生 file:/// 引用） |
| SRC-README | 仓库 README.md（中文） | 3.1.185 时点，共 375 行 | SRC-REPO: README.md |
| SRC-SETUP | setup.py / setup.cfg / MANIFEST.in / tox.ini / package.py / products.md | 3.1.185 时点 | SRC-REPO 根目录 |

## A 面：包元数据与分发

- F-001：`tencentcloud/__init__.py` 仅含一行赋值 `__version__ = '3.1.185'`（文件头版权声明外）。〔SRC-REPO: tencentcloud/__init__.py:17〕
- F-002：setup.py 中 `name='tencentcloud-sdk-python'`，`install_requires=["requests>=2.16.0"]`，`extras_require={"async": ["httpx>=0.22.0"]}`，`version=tencentcloud.__version__`。〔SRC-SETUP: setup.py:14-18〕
- F-003：setup.py classifiers 列出 Programming Language :: Python :: 2.7、3、3.7、3.8、3.9、3.10、3.11、3.12；packages 使用 `find_packages(exclude=["tests*"])`，license 为 Apache License 2.0。〔SRC-SETUP: setup.py:25-41〕
- F-004：README「依赖环境」写明依赖 Python 2.7、3.6 ~ 3.12；endpoint 一般形式为 `*.tencentcloudapi.com`。〔SRC-README:4-8〕
- F-005：README 记载两种安装形态：安装指定产品包（先装 `tencentcloud-sdk-python-common`，再装 `tencentcloud-sdk-python-指定产品包名缩写`）与安装全产品包 `tencentcloud-sdk-python`；异步功能通过 `[async]` extra 安装。〔SRC-README:25-42〕
- F-006：README 注意事项：「安装全产品 SDK 和安装指定产品的 SDK 两种方式只能选择其中一种」；多产品包建议与 common 包保持同一版本。〔SRC-README:44-46〕
- F-007：package.py 是仓库自带的分包打包工具，argparse 参数为 `--services`（nargs='+'）与 `--upload`；对 `tencentcloud/` 下每个选中的目录在 temp-directory 中复制 `tencentcloud/__init__.py` 与该产品目录，调用 `python3.8 -m build` 构建、`twine upload` 上传。〔SRC-SETUP: package.py:165-193〕
- F-008：package.py 中 common 包的依赖声明为 `install_requires=["requests>=2.16.0"]` + async extras；非 common 产品包依赖声明为 `tencentcloud-sdk-python-common>=%s,<%s`，上界由 `get_highest_version()` 计算为主版本号 +1 的 `X.0.0`。〔SRC-SETUP: package.py:117-127〕
- F-009：setup.cfg 内容为 `[bdist_wheel]` 下 `universal=1`；MANIFEST.in 为 `include README.rst`、`include LICENSE`、`recursive-include QcloudApi *`。〔SRC-SETUP: setup.cfg, MANIFEST.in〕
- F-010：tox.ini envlist 为 `py{27,36,37,38,39,310,311,312}`，deps 含 pytest、pytest-cov、pytest-asyncio、`.[async]`；py27 环境以 `--ignore-glob='*_async.py'` 忽略异步文件；passenv 包含 TENCENTCLOUD_SECRET_ID、TENCENTCLOUD_SECRET_KEY、TENCENTCLOUD_ROLE_ARN、HTTPS_PROXY。〔SRC-SETUP: tox.ini〕
- F-011：products.md 是产品包名缩写登记表，表头为「包名 | 产品中文名 | 更新历史 | 更新时间」，共 262 个数据行（脚本计数，匹配 cloud.tencent.com 链接）。〔SRC-SETUP: products.md〕

## B 面：仓库结构与规模（计数均由脚本独立复核）

- F-012：`tencentcloud/` 下共有 263 个子目录，其中 `common/`（公共运行时）与 `config/`（配置服务产品，含 v20220802 版本包）各一个，其余 261 个为产品目录。〔SRC-REPO: tencentcloud/，脚本 os.listdir 计数〕
- F-013：products.md 登记 262 个包名，其中 `as` 包名对应目录实际名为 `autoscaling`（md 行与目录集合差集仅此一对）；261 个产品目录全部含至少一个 `v*` 版本子目录，无空壳产品目录。〔脚本三方对账：products.md 行集合 vs tencentcloud/ 目录集合〕
- F-014：全仓 `tencentcloud/` 下存在 300 个 `*_client.py`（同步产品客户端）、300 个 `*_client_async.py`、300 个 `models.py`、300 个 `errorcodes.py`（glob 计数 `tencentcloud/*/v*/...`）。〔脚本 glob 计数〕
- F-015：300 个版本包分布在 262 个产品目录上（含 config）；34 个产品拥有多个 API 版本，其中 iotvideo、rce、thpc、vm 四个产品各有 3 个版本，其余 30 个多版本产品各有 2 个版本。〔脚本 Counter 计数〕
- F-016：`tencentcloud/` 下 Python 文件总数 1783（glob `tencentcloud/**/*.py` 递归计数）。〔脚本计数〕
- F-017：`QcloudApi/` 为遗留 SDK 目录，含 52 个 Python 文件；其中 `QcloudApi/modules/` 含 46 个 .py（含 `__init__.py` 与 `base.py`，即 44 个具体产品模块文件）。〔脚本 glob 计数〕
- F-018：`examples/` 下有 49 个 .py 文件，覆盖 cvm、cls、hunyuan、common_client、ess、ecc、hcm、apigateway_proxy 等目录。〔脚本 glob 计数〕
- F-019：CVM 产品 v20170312 版本包四件套规模：cvm_client.py 2713 行、含 106 个大写作动作方法（正则 `^    def [A-Z]`）；models.py 23652 行、含 286 个 class；errorcodes.py 含 417 个错误码常量赋值（正则 `^[A-Z_]+ = `）。〔脚本计数〕
- F-020：公共运行时 `tencentcloud/common/` 共 20 个 Python 文件：common 目录 11 个（abstract_client.py、abstract_client_async.py、abstract_model.py、circuit_breaker.py、common_client.py、common_client_async.py、credential.py、retry.py、retry_async.py、sign.py、__init__.py）、profile/ 3 个、http/ 4 个、exception/ 2 个。〔Glob 列举〕
- F-021：产品目录下的 `__init__.py`（如 tencentcloud/cvm/__init__.py）为空文件；`tencentcloud/common/__init__.py` 同样为空。〔Read：两文件均 0 字节〕

## C 面：同步运行时内核 AbstractClient

- F-022：`AbstractClient` 类属性：`_requestPath = '/'`、`_apiVersion = ''`、`_endpoint = ''`、`_service = ''`、`_sdkVersion = 'SDK_PYTHON_%s' % tencentcloud.__version__`、`_default_content_type = 'application/x-www-form-urlencoded'`。〔abstract_client.py:64-72〕
- F-023：`AbstractClient.__init__(credential, region, profile=None)` 保存 credential/region，profile 缺省时 new `ClientProfile()`；据此创建 `ApiRequest`（参数取 httpProfile 的 reqTimeout/proxy/scheme/certification/pre_conn_pool_size）；keepAlive 时调用 `self.request.set_keep_alive()`；request_client 字串为 SDK 版本号，profile.request_client 非空时前缀拼接。〔abstract_client.py:74-95〕
- F-024：模块加载时设置 logger 名为 `tencentcloud_sdk_common`，并挂载 `EmptyHandler`（emit 空实现）；同时 `warnings.filterwarnings("ignore", module="tencentcloud", category=UserWarning)`。〔abstract_client.py:46,54-61〕
- F-025：`_build_req_inter(action, params, req_inter, options)` 按 options 与 signMethod 三路分流：options['SkipSign'] 为真走 `_build_req_without_signature`；signMethod == "TC3-HMAC-SHA256" 或 options["IsMultipart"] 为真走 `_build_req_with_tc3_signature`；signMethod 为 HmacSHA1/HmacSHA256 走 `_build_req_with_old_signature`；其他值抛 TencentCloudSDKException("ClientError", "Invalid signature method.")。〔abstract_client.py:131-140〕
- F-026：`_fix_params`/`_format_params` 将嵌套 dict/list/tuple 展平为点号/下标键：list 项键为 `prefix.idx`，dict 项键为 `prefix.k`；标量直接落键；非容器非字典类型抛 TencentCloudSDKException("ClientParamsError", ...)。〔abstract_client.py:97-129〕
- F-027：旧签名请求公共参数包含 Action（首字母大写化）、RequestClient、Nonce（`random.randint(1, sys.maxsize)`）、Timestamp、Version；region 存在时加 Region；token 存在时加 Token；secret_id 存在时加 SecretId；另加 SignatureMethod、Language；最终 `urlencode(params)` 写 body，Content-Type 为 application/x-www-form-urlencoded。〔abstract_client.py:142-173〕
- F-028：TC3 请求的 header 键包括 Host、X-TC-Action、X-TC-RequestClient、X-TC-Timestamp、X-TC-Version、X-TC-Region、X-TC-Token（临时凭证时）、X-TC-Language；unsignedPayload 为真时加 `X-TC-Content-SHA256: UNSIGNED-PAYLOAD`。〔abstract_client.py:192-207〕
- F-029：TC3 请求 GET 时 body 为 urlencode 结果；POST 默认 Content-Type 为 application/json、body 为 `json.dumps(params)`；IsMultipart 时生成 `uuid.uuid4().hex` boundary 并调 `_get_multipart_body`；GET 与 multipart 组合直接抛错。〔abstract_client.py:176-217〕
- F-030：TC3 Authorization 头格式为 `TC3-HMAC-SHA256 Credential=<secret_id>/<date>/<service>/tc3_request, SignedHeaders=content-type;host, Signature=<hex>`。〔abstract_client.py:223-225〕
- F-031：`_get_tc3_signature` 构造规范请求六段（HTTPRequestMethod、CanonicalURI、CanonicalQueryString、CanonicalHeaders、SignedHeaders、HashedRequestPayload），以两个换行连接，payload 经 sha256；再对规范请求取 sha256 摘要组成 string2sign（算法名、X-TC-Timestamp、CredentialScope、摘要），交由 `Sign.sign_tc3`。〔abstract_client.py:227-264〕
- F-032：`_get_multipart_body` 手工拼装 multipart 字节流：每个参数一个 `--boundary` 段，options['BinaryParams'] 中的键加 `filename=`，list/dict 值 json.dumps 并标 Content-Type: application/json，结尾 `--boundary--`。〔abstract_client.py:310-333〕
- F-033：`_get_endpoint` 优先级：httpProfile.endpoint → options["Endpoint"] 经 urlparse 取 hostname → `_service + "." + httpProfile.rootDomain`（rootDomain 默认 tencentcloudapi.com）。〔abstract_client.py:349-359；http_profile.py:49〕
- F-034：`_check_status` 在 HTTP 状态码 != 200 时抛 `TencentCloudSDKException("ServerNetworkError", resp_inter.content)`。〔abstract_client.py:335-338〕
- F-035：`_check_error` 仅在响应 Content-Type 为 text/plain 或 application/json 时解析；JSON 中 `Response.Error` 存在时取 Code/Message/RequestId 抛 TencentCloudSDKException；`Response.DeprecatedWarning` 存在时发 DeprecationWarning（先 `warnings.filterwarnings("default")`）。〔abstract_client.py:361-377〕
- F-036：`_call` 校验 headers 必须为 dict；headers 中无 x-tc-traceid（小写比较）时自动填入 `X-TC-TraceId = uuid4()`；disable_region_breaker 为假时改走 `_call_with_region_breaker`，否则构造 RequestInternal、`_build_req_inter`、必要时改写为 apigw_endpoint、调 `self.request.send_request(req)`。〔abstract_client.py:421-439〕
- F-037：`call` 内部定义 `_call_once`（_call→_check_status→_check_error→debug 日志），用 `self.profile.retryer or NoopRetryer()` 的 `send_request` 包裹，返回 `.content`。〔abstract_client.py:441-451〕
- F-038：对外还提供 `call_json`（返回 json.loads 后的对象）、`call_sse`（返回 `_process_response_sse` 生成器）、`call_octet_stream`（要求 TC3-HMAC-SHA256 + POST，body 为字节，options 置 IsOctetStream）、`call_with_region_breaker` 四个调用入口，重试包裹方式与 call 相同。〔abstract_client.py:474-558〕
- F-039：`_process_response` 按响应 Content-Type 分流：`text/event-stream` 走 SSE 解析，否则走 `_process_response_json`（取 JSON 的 "Response" 键，实例化 resp_type 并 `_deserialize`）。〔abstract_client.py:414-419,570-576〕
- F-040：`_process_response_sse` 按 SSE 协议逐行解析：空行产出当前事件 dict 并重置；冒号开头为注释；只收集 data（多 data 行以 `\n` 连接）、event、id、retry（retry 转 int）键，其他键忽略。〔abstract_client.py:379-412〕
- F-041：日志配置方法 `set_stream_logger`（StreamHandler）、`set_file_logger`（RotatingFileHandler，maxBytes=512MB，backupCount=10）、`set_default_logger`（清空 handlers 并挂回 EmptyHandler）；默认 FMT 为 `'%(asctime)s %(process)d %(filename)s L%(lineno)s %(levelname)s %(message)s'`。〔abstract_client.py:72,578-623〕

## D 面：模型层 AbstractModel 与代码生成模式

- F-042：`AbstractModel` 定义类属性 `_headers = None` 与 headers property；`_serialize(allow_none=False)` 遍历 `vars(self)`、跳过 `_headers`，嵌套 AbstractModel/list 递归序列化，跳过 None（allow_none 为真时保留），输出键名由属性名转换：`k[1].upper() + k[2:]`（即去掉下划线前缀后首字母大写）。〔abstract_model.py:19-51〕
- F-043：`to_json_string` 默认 `ensure_ascii=False` 并以 `_serialize(allow_none=True)` 序列化；`from_json_string` 反序列化到自身；`__repr__` 直接返回 JSON 字符串。〔abstract_model.py:57-73〕
- F-044：产品模型（以 CVM AccountQuota 为例）每个字段以 `_FieldName = None` 存储，配 @property 同名 getter/setter；`_deserialize` 对每个非 None 入参键按标量/对象/列表逐类还原，嵌套对象通过无参构造 + `obj._deserialize(item)` 递归。〔cvm/v20170312/models.py:21-130〕
- F-045：请求模型（以 DescribeInstancesRequest 为例）同样继承 AbstractModel，docstring 内同时承载中文参数说明、类型标注（如 `list of Filter`）与 HTML 格式的官网文档片段；字段如 _InstanceIds、_Filters、_Offset、_Limit。〔cvm/v20170312/models.py:7038-7056〕
- F-046：产品客户端继承 AbstractClient 并覆盖三个类属性，CVM 为 `_apiVersion = '2017-03-12'`、`_endpoint = 'cvm.tencentcloudapi.com'`、`_service = 'cvm'`。〔cvm/v20170312/cvm_client.py:23-26〕
- F-047：同步动作方法模板（以 AllocateHosts 为例）：`params = request._serialize()`、`headers = request.headers`、`body = self.call(Action名, params, headers=headers)`、`json.loads(body)`、实例化对应 Response 模型并 `_deserialize(response["Response"])`；异常处理为 TencentCloudSDKException 直接 raise，其余异常包装为 TencentCloudSDKException(type(e).__name__, str(e))。〔cvm_client.py:29-50〕
- F-048：errorcodes.py 每个错误码是一个大写常量赋值，格式 `NAME = 'Dotted.Code'`，上方注释为中文说明，例如 `ACCOUNTQUALIFICATIONRESTRICTIONS = 'AccountQualificationRestrictions'`。〔cvm/v20170312/errorcodes.py:17-21〕

## E 面：签名算法 Sign

- F-049：`Sign.sign(secret_key, sign_str, sign_method)`（静态方法）仅支持 HmacSHA256/HmacSHA1，其他方法抛 TencentCloudSDKException；以 hmac + binascii.b2a_base64 输出 base64 签名（去掉末尾换行）。〔common/sign.py:13-33〕
- F-050：`Sign.sign_tc3(secret_key, date, service, str2sign)` 的三级派生密钥为：kDate = HMAC("TC3"+key, date)、kService = HMAC(kDate.digest, service)、kSigning = HMAC(kService.digest, "tc3_request")，最终签名 = HMAC(kSigning.digest, str2sign) 的 hexdigest。〔common/sign.py:36-48〕
- F-051：旧版签名串 `_format_sign_string` 将参数键中 `_` 替换为 `.`，按键排序后 `k=v` 以 `&` 连接，前缀为 `reqMethod + endpoint + '/' + '?' + 参数串`。〔abstract_client.py:340-347〕

## F 面：HTTP 传输层

- F-052：同步传输基于第三方库 requests 与 certifi；`ProxyConnection` 内部持有 `requests.Session()`，certification 缺省时取 `certifi.where()`；代理未显式传入时从 HTTPS_PROXY/HTTP_PROXY 环境变量读取并检查 NO_PROXY；请求统一 `stream=True`。〔common/http/request.py:7-59〕
- F-053：pre_conn_pool_size > 0 时挂载自定义 `PreConnAdapter`；HTTPSPreConnPool/HTTPPreConnPool 在初始化时清空连接池并启动 daemon 线程循环预建 TCP 连接放入 urllib3 池。〔http/request.py:45-48；http/pre_conn.py:12-49〕
- F-054：`ApiRequest._request` 用 `_handle_host` 补全 scheme（无 hostname 时按 is_http 补 http:// 或 https://）；GET 把 data 拼到 URL 后且 body=None，POST 将 data 作 body；其他方法抛 ClientParamsError；keep_alive 时加 `Connection: Keep-Alive`；send_request 捕获任意异常并包装成 `TencentCloudSDKException("ClientNetworkError", str(e))`。〔http/request.py:75-118〕
- F-055：`RequestInternal` 是内部请求载体（host/method/uri/header/data，data 默认空串），`__str__` 输出可读的请求快照。〔http/request.py:121-134〕
- F-056：`ResponsePrettyFormatter` 格式化状态行（10→HTTP/1.0、11→HTTP/1.1、20→HTTP/2.0）、响应头与正文，供 debug 日志使用。〔http/request.py:137-161〕
- F-057：HttpProfile 默认值：endpoint=None、reqTimeout=60（None 归一为 60）、reqMethod="POST"、protocol/scheme="https"、keepAlive=False、proxy=None、rootDomain="tencentcloudapi.com"、certification=None、apigw_endpoint=None、pre_conn_pool_size=0。〔profile/http_profile.py:37-52〕
- F-058：ClientProfile 默认 signMethod="TC3-HMAC-SHA256"、language="zh-CN"（仅允许 zh-CN/en-US，否则抛异常）、disable_region_breaker=True；request_client 需匹配正则 `^[0-9a-zA-Z-_,;.]+$` 且截断至 128 字符；retryer 字段可注入自定义重试器。〔profile/client_profile.py:38-60〕

## G 面：凭证体系

- F-059：`Credential(secret_id, secret_key, token=None)` 对 secret_id/secret_key 做非空与首尾空格校验，违例抛 InvalidCredential；提供 secretId/secretKey property 与 `get_credential_info()` 返回三元组 (id, key, token)。〔common/credential.py:38-76〕
- F-060：`CVMRoleCredential(role_name=None)` 从 `http://metadata.tencentyun.com/latest/meta-data/cam/security-credentials/` 取角色名与临时凭证；`_expired_timeout = 300` 秒；threading.Lock 保护；元数据 Code != "Success" 时抛异常（update_credential 内 except 捕获后 pass）。〔credential.py:79-173〕
- F-061：`STSAssumeRoleCredential` 固定 _region="ap-guangzhou"、_version='2018-08-13'、_service="sts"、_endpoint="sts.tencentcloudapi.com"；用 CommonClient 调 AssumeRole，取 Response.Credentials 的 Token/TmpSecretId/TmpSecretKey；过期时间取 `ExpiredTime - duration_seconds * 0.9`；duration_seconds 默认 7200（docstring 载最大值 43200）。〔credential.py:176-276〕
- F-062：`EnvironmentVariableCredential` 读 `TENCENTCLOUD_SECRET_ID`/`TENCENTCLOUD_SECRET_KEY`，缺失或空串返回 None。〔credential.py:279-295〕
- F-063：`ProfileCredential` 依次查找 `~/.tencentcloud/credentials` 与 `/etc/tencentcloud/credentials`，用 configparser 读 ini 的 [default] 段 secret_id/secret_key/role_arn，值做 strip；无文件或字段缺失返回 None。〔credential.py:298-340〕
- F-064：`DefaultCredentialProvider.get_credentials` 顺序尝试：环境变量 → 配置文件 → CVM 实例角色 → `DefaultTkeOIDCRoleArnProvider`（TKE OIDC），首个非 None 返回，全部失败抛 TencentCloudSDKException("ClientSideError", "no valid credentail.")；结果缓存于 self.cred。〔credential.py:343-388〕
- F-065：`OIDCRoleArnCredential` 用 CommonClient（credential=None）以 options={'SkipSign': True} 调 sts 的 AssumeRoleWithWebIdentity；过期时间取 `ExpiredTime - duration_seconds * 0.1`；`_init_from_tke` 从 TKE_REGION、TKE_PROVIDER_ID、TKE_WEB_IDENTITY_TOKEN_FILE、TKE_ROLE_ARN 四个环境变量装配。〔credential.py:391-528〕
- F-066：README「凭证管理」章登记 5 种方式：环境变量、配置文件（ini）、角色扮演（STSAssumeRoleCredential）、实例角色（CVMRoleCredential）、凭证提供链（顺序写明为「环境变量->配置文件->实例角色->TKE OIDC凭证」）。〔SRC-README:32-105〕

## H 面：重试与地域熔断

- F-067：`NoopRetryer.send_request(fn)` 直接 `return fn()`。〔common/retry.py:7-15〕
- F-068：`StandardRetryer(max_attempts=3, backoff_fn=None, logger=None)`，send_request 循环最多 max_attempts 次，不满足重试条件时成功返回 resp 或抛 err；重试前 sleep(backoff(n))。〔retry.py:18-55〕
- F-069：`should_retry` 仅对 TencentCloudSDKException 且错误码属于 {ClientNetworkError, ServerNetworkError, RequestLimitExceeded, RequestLimitExceeded.UinLimitExceeded, RequestLimitExceeded.GlobalRegionUinLimitExceeded} 重试；默认退避 `backoff(n) = 2 ** n` 秒。〔retry.py:57-76〕
- F-070：CHANGELOG 首条记录为 `### [3.0.1317] - 2025-02-12`，内容「支持重试功能」。〔CHANGELOG.md:3-4〕
- F-071：熔断器三常量 STATE_CLOSED=0、STATE_HALF_OPEN=1、STATE_OPEN=2；Counter 记录 failures/total/consecutive_successes/consecutive_failures。〔common/circuit_breaker.py:20-53〕
- F-072：`ready_to_open` 条件为（failures >= max_fail_num 且失败率 >= max_fail_percent）或连续失败数 >= 5。〔circuit_breaker.py:66-69〕
- F-073：CircuitBreaker 带 threading.Lock 与 generation（0-9 循环）；CLOSED 窗口到期换代清零；OPEN 到期转 HALF_OPEN；HALF_OPEN 中成功数达到 max_requests 转回 CLOSED、任何失败转回 OPEN；after_requests 发现 generation 已变则丢弃本次结果。〔circuit_breaker.py:56-134〕
- F-074：RegionBreakerProfile 默认 backup_endpoint="ap-guangzhou.tencentcloudapi.com"、max_fail_num=5、max_fail_percent=0.75、window_interval=300 秒、timeout=60 秒、max_requests=5；check_endpoint 校验备份域名必须为 tencentcloudapi.com 或 `${region}.tencentcloudapi.com` 形态，失败率必须在 0~1 之间。〔profile/client_profile.py:63-108〕
- F-075：`_call_with_region_breaker` 在 need_break 时把端点改写为 `_service + "." + backup_endpoint`；请求后按「resp 中含 RequestId 且错误码 != InternalError」判成功，其余判失败上报熔断器，异常继续外抛。〔abstract_client.py:453-472〕
- F-076：熔断器默认不启用——AbstractClient.__init__ 中 `if not self.profile.disable_region_breaker` 才创建 CircuitBreaker，而 ClientProfile 的 disable_regionbreaker 默认值为 True。〔abstract_client.py:87-91；client_profile.py:41〕

## I 面：CommonClient、异步栈与 SSE

- F-077：`CommonClient(AbstractClient)` 构造签名 `(service, version, credential, region, profile=None)`，region/version/service 任一为 None 即抛异常；将 version/service 写入 `_apiVersion`/`_service` 后调用父类构造，不覆盖 `_endpoint`（端点由服务名+根域名推导）。〔common/common_client.py:41-47〕
- F-078：CommonClient docstring 说明「只安装 tencentcloud-sdk-python-common 包即可访问所有产品 API」；README 记载该方式从 3.0.396 开始支持。〔common_client.py:23-39；SRC-README:169-174〕
- F-079：异步栈基于 httpx，`abstract_client_async.py` import httpx 并定义 `AbstractClient`（与同步类同名，不同模块）；构造时创建 `httpx.AsyncClient`（timeout、keepAlive 关闭时 max_keepalive_connections=0、proxy、verify/cert），实现 `__aenter__`/`__aexit__`/`close()`。〔abstract_client_async.py:29,81-128〕
- F-080：异步调用链由 `RequestChain` 拦截器组织：默认链顺序为 _inter_retry → _inter_deserialize_resp →（有熔断器时）_inter_breaker → _inter_build_request → _inter_send_request；`proceed()` 取下一个拦截器并对快照递增 idx。〔abstract_client_async.py:56-78,143-158〕
- F-081：异步产品客户端方法为 `async def`，签名带类型标注（request: models.XxxRequest, opts: Dict = None）-> XxxResponse，统一 `await self.call_and_deserialize(action=..., params=request._serialize(), resp_cls=..., headers=request.headers, opts=opts or {})`。〔cvm/v20170312/cvm_client_async.py:28-45〕
- F-082：README 记载异步调用从 3.1.0 版本开始支持，需安装 `tencentcloud-sdk-python-common[async]`，使用 `*_client_async` 模块，建议 async with，接口与同步一致仅需加 await。〔SRC-README:176-187〕
- F-083：异步反序列化拦截器支持三类返回：resp_cls == dict 返回 json.loads；AbstractModel 子类实例化并 _deserialize；其他抛 ClientParamsError；Content-Type 为 text/event-stream 时 async 生成器逐行解析 SSE。〔abstract_client_async.py:225-318〕
- F-084：异步 TC3 构建中存在对 httpx 0.22.0 的兼容注释：该版本会过滤空 value 的 query 参数，故不用 params 而手工把 query 拼到 URL；py36 最高只能装 httpx 0.22.0。〔abstract_client_async.py:457-459〕

## J 面：遗留 QcloudApi（云 API 旧版）

- F-085：`QcloudApi.qcloudapi.QcloudApi(module, config)` 持模块名与 config dict；`_factory` 以 1 个 if + 43 个 elif 共 44 个具名分支按模块名 import 对应类（cdb/account/cvm/image/lb/.../sts/dc，与 modules/ 下 44 个产品模块文件一一对应），未命中任何分支时设置 endpoint 为 `module + '.api.qcloud.com'` 并返回 base.Base。〔QcloudApi/qcloudapi.py:12-147；脚本计数〕
- F-086：QcloudApi 的 call(action, params, ...) 经工厂取服务实例，先在实例属性中找同名方法直接调用，找不到则回落 `service.call(action, params)`；另有 setSecretId/setSecretKey/setRequestMethod/setRegion/setSignatureMethod/generateUrl 方法。〔qcloudapi.py:151-196〕
- F-087：遗留 Base 类 `requestUri = '/v2/index.php'`，签名默认 HmacSHA1；公共参数 Action/RequestClient/Region/Version/Token/SecretId/Nonce/Timestamp/SignatureMethod 在 `_build_req_inter` 中填充，签名对象为 `QcloudApi.common.sign.Sign(self.secretId, self.secretKey)` 的 make 方法。〔QcloudApi/modules/base.py:39-140〕
- F-088：MANIFEST.in 以 `recursive-include QcloudApi *` 将整个遗留 SDK 打入全产品分发包。〔MANIFEST.in〕

## K 面：测试与示例

- F-089：tests/unit 含 5 个测试文件：test_ai_domain.py、test_import.py、test_retry.py、test_serialization.py、test_set_endpoint.py（另有 tests/integration 集成测试目录，含 cls/common/cvm/iai/ocr 子目录）。〔目录列举〕
- F-090：test_retry.py 对 5 个可重试错误码逐一断言：max_attempts=3 时实际尝试次数为 max_attempts+1=4 次，最终抛出原错误码。〔tests/unit/test_retry.py:19-50〕
- F-091：test_serialization.py 以 CVM DescribeInstances 的模拟 JSON（含 InstanceSet 嵌套对象、None 字段、DataDisks 列表等）验证模型序列化/反序列化往返。〔tests/unit/test_serialization.py:7-60〕
- F-092：examples/common_client/ 含 describe_instances.py、describe_instances_async.py、chat_completions_async.py、cls_upload_log.py 与一个 binary.data 文件。〔目录列举〕
- F-093：README 详细版示例展示 HttpProfile 可配置项（scheme/keepAlive/reqMethod/reqTimeout/endpoint）、ClientProfile 的 signMethod/language/retryer（StandardRetryer(max_attempts=3, logger=...)）、自定义 header（X-TC-TraceId，经 req.headers 传入）。〔SRC-README:111-160〕
- F-094：README「更多示例」链接覆盖常见 JSON 接口同步/异步、CommonClient 同步/异步、AI 流式接口（hunyuan/v20230901/chat_completions_async.py）、CLS 上传日志等场景。〔SRC-README:217-223〕
- F-095：异常类 `TencentCloudSDKException(Exception)` 字段为 code/message/requestId，`__str__` 输出 `[TencentCloudSDKException] code:%s message:%s requestId:%s`，提供 get_code/get_message/get_request_id 三个 getter。〔common/exception/tencent_cloud_sdk_exception.py:5-27〕

## L 面：运行时行为杂项

- F-096：`_call` 的 X-TC-TraceId 自动注入发生在每次实际请求前（headers 已有同名键时跳过，键名比较统一 lower()）。〔abstract_client.py:421-427〕
- F-097：httpProfile.apigw_endpoint 非空时，请求 host 与 Host 头被改写为该网关端点（签名仍按原 endpoint 计算）。〔abstract_client.py:436-438〕
- F-098：无签名模式 `_build_req_without_signature` 除不计算签名外，其余 X-TC-* 头照常填充，Authorization 头置为字符串 "SKIP"；该选项被 OIDCRoleArnCredential 刷新凭证时使用。〔abstract_client.py:266-307；credential.py:500-502〕
- F-099：产品包 setup 模板（package.py SETUP 字符串）的 classifiers 只列到 Python 3.7，与全产品 setup.py（列到 3.12）不同；分包 setup.cfg 同样 universal=1（py2/py3 通用 wheel）。〔package.py:60-75〕
- F-100：README 记载 requests 2.30+ 适配 urllib3 2.0 后在 OpenSSL 1.0.x 环境可能出现 `urllib3 v2.0 only supports OpenSSL 1.1.1+` ImportError，解法为降 urllib3 至 1.26.x 或重编 Python。〔SRC-README:10-13〕

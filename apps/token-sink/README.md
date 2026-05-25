# token-sink

结果落池模块。

默认对接兼容 `grok2api` 管理接口的 token sink。注册成功后，执行器会把新增 `sso` token 推送到 `api.endpoint`。

当前约定：

- `api.endpoint`：token 管理接口，例如 `http://127.0.0.1:8000/admin/api/tokens`
- `api.token`：管理口令
- `api.append=true`：先读取存量再去重合并，保护已有 token
- `api.append=false`：直接以本次结果覆盖远端数据

建议后续继续在这里收敛的功能：

- token 入池结果校验
- 可选回写运行统计
- 死信重试
- 多个 sink 目标并发推送

在当前一体化部署里，根目录 [docker-compose.register.yml](../../docker-compose.register.yml) 已经内置 `jiujiu532/grok2api` 防封版服务。控制台默认会把 `api.endpoint` 指向：

- `http://grok2api:8000/admin/api/tokens`

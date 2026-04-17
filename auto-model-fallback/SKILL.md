---
name: auto-model-fallback
description: 自动识别主模型故障并切换到备用模型的容错机制。支持 HTTP 5xx 错误、空响应、速率限制等情况下的自动降级。
trigger: 当 API 返回 500/502/503/504 错误、超时、空响应或速率限制时自动触发
category: hermes-core
---

# 自动模型降级切换（Auto Model Fallback）

## 功能概述

当主模型（MiniMax-M2.7）出现以下情况时，Hermes 会自动切换到备用模型（MiniMax-M2.5）：

- HTTP 5xx 服务器错误（500/502/503/504）
- API 超时或连接失败
- 空响应或畸形响应
- 速率限制（Rate Limit）
- 服务繁忙无法响应

## 配置方式

在 `~/.hermes/config.yaml` 中配置：

```yaml
model:
  default: MiniMax-M2.7
  provider: minimax-cn

fallback_model:
  provider: minimax-cn
  model: MiniMax-M2.5
```

## 触发场景

| 错误类型 | 状态码 | 触发条件 |
|---------|-------|---------|
| 服务器内部错误 | 500 | MiniMax 服务端异常 |
| Bad Gateway | 502 | 上游服务无响应 |
| Service Unavailable | 503 | 服务过载/维护中 |
| Gateway Timeout | 504 | 请求超时 |
| 空响应 | - | 返回内容为空 |
| 速率限制 | 429 | 超出调用配额 |

## 工作原理

1. **错误分类**：每次 API 错误经过 `classify_api_error()` 分类
2. **Fallback 判定**：如果 `should_fallback=True`，触发 `_try_activate_fallback()`
3. **模型切换**：自动更换 client、model、provider 配置
4. **重试恢复**：重置 retry_count，继续使用备用模型

## 注意事项

- 备用模型需确保有可用额度
- Fallback 切换是当次会话临时生效，下次会话恢复主模型
- 可配置多个备用模型形成 chain（列表格式）
- 如果所有备用模型都失败，会返回明确错误信息

## 查看日志

```bash
# 启动时会显示 fallback 配置
hermes

# 查看错误日志
tail -f ~/.hermes/logs/errors.log
```

## 手动切换

如果需要手动切换模型，使用 `/model` 命令：

```
/model MiniMax-M2.5 minimax-cn
```

这会持久化切换到备用模型，而不是临时 fallback。
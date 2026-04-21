---
name: auto-model-fallback
description: 自动识别主模型故障并切换到备用模型的容错机制。按优先级降级：MiniMax-M2.7 → MiniMax-M2.5highspeed → MiniMax-M2.5。支持 HTTP 5xx 错误、空响应、速率限制等情况。
trigger: 当 API 返回 500/502/503/504 错误、超时、空响应或速率限制时自动触发
category: hermes-core
---

# 自动模型降级切换（Auto Model Fallback）

## 功能概述

模型降级链（按优先级）：

1. **主模型**：MiniMax-M2.7（最快最强）
2. **第一降级**：MiniMax-M2.5highspeed（高速版）
3. **第二降级**：MiniMax-M2.5（标准版）

当主模型出现以下情况时，自动切换到下一级：

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
  model: MiniMax-M2.5-HighSpeed

extra_fallback_model:
  provider: minimax-cn
  model: MiniMax-M2.5
```

## 降级链

| 层级 | 模型 | 触发条件 |
|------|------|---------|
| 主 | MiniMax-M2.7 | 正常状态 |
| 第一降级 | MiniMax-M2.5highspeed | 主模型 5xx/超时/空响应/限速 |
| 第二降级 | MiniMax-M2.5 | 第一降级也失败 |

## 触发场景

| 错误类型 | 状态码 | 触发条件 |
|---------|-------|---------|
| 服务器内部错误 | 500 | MiniMax 服务端异常 |
| Bad Gateway | 502 | 上游服务无响应 |
| Service Unavailable | 503 | 服务过载/维护中 |
| Gateway Timeout | 504 | 请求超时 |
| **所有 5xx 错误** | **5xx** | **任何服务端错误** |
| 空响应 | - | 返回内容为空 |
| 速率限制 | 429 | 超出调用配额 |

## 工作原理

1. **错误分类**：每次 API 错误经过 `classify_api_error()` 分类
2. **5xx 检测**：状态码 500/501/502/503/504/505 等全部触发 should_fallback=True
3. **Fallback 判定**：如果 `should_fallback=True`，触发 `_try_activate_fallback()`
4. **模型切换**：自动更换 client、model、provider 配置（沿降级链向下）
5. **重试恢复**：重置 retry_count，继续使用备用模型
6. **多级降级**：如第一降级也失败，继续尝试第二降级

## 注意事项

- 所有降级模型需确保有可用额度
- Fallback 切换是当次会话临时生效，下次会话恢复主模型
- 如果所有模型都失败，会返回明确错误信息

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
/model MiniMax-M2.5highspeed minimax-cn
```

这会持久化切换到指定模型，而不是临时 fallback。

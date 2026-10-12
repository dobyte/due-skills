---
title: "节点服务器示例"
slug: "node-server"
keywords: ["due", "节点", "服务器", "完整", "消息处理"]
description: "完整的节点服务器示例，包含消息处理"
hide_title: true
---

# 节点服务器示例

本示例演示了完整的节点服务器设置，包含全面的消息处理，包括请求解析、响应生成和错误处理。

## 特性

- 完整的节点组件初始化
- Redis 定位器用于用户追踪
- Consul 注册中心用于服务发现
- 带错误处理的高级路由处理器
- JSON 消息编解码
- 基于时间的响应

## 项目结构

```
node-server/
├── main.go          # 主入口文件
└── etc/
    └── etc.toml     # 配置文件
```

## 核心组件

### 节点初始化

```go
container := due.NewContainer()
locator := redis.NewLocator()
registry := consul.NewRegistry()
component := node.NewNode(
    node.WithLocator(locator),
    node.WithRegistry(registry),
)
initApp(component.Proxy())
container.Add(component)
container.Serve()
```

### 带错误处理的路由处理器

```go
func greetHandler(ctx node.Context) {
    req := &greetReq{}
    res := &greetRes{}
    
    ctx.Defer(func() {
        if err := ctx.Response(res); err != nil {
            log.Errorf("响应失败: %v", err)
        }
    })
    
    if err := ctx.Parse(req); err != nil {
        log.Errorf("解析失败: %v", err)
        res.Code = codes.InternalError.Code()
        return
    }
    
    res.Code = codes.OK.Code()
    res.Message = fmt.Sprintf("服务器时间: %s", xtime.Now().Format(xtime.DateTime))
}
```

## 配置说明

编辑 `etc/etc.toml` 来配置：

- **节点设置**：实例 ID、名称、RPC 地址、编解码器
- **Redis 定位器**：用户位置追踪的连接设置
- **Consul 注册中心**：服务发现配置
- **数据包设置**：消息格式和大小限制
- **日志**：输出级别和目标

## 运行示例

1. 启动 Redis，地址为 `127.0.0.1:6379`
2. 启动 Consul，地址为 `127.0.0.1:8500`
3. 运行服务器：

```bash
go run main.go
```

## 测试

使用 client-tcp 或 client-ws 示例发送消息并接收带有服务器时间戳的响应。

## 错误处理

本示例演示了正确的错误处理：
- 请求解析错误
- 响应传递错误
- 错误码传播
- 用于调试的日志记录

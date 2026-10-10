---
title: "TCP 客户端示例"
slug: "client-tcp"
keywords: ["due", "客户端", "tcp", "网络", "连接"]
description: "TCP 客户端示例，连接到 Due 网关服务器"
hide_title: true
---

# TCP 客户端示例

本示例演示了如何创建一个 TCP 客户端，连接到 Due 网关服务器、发送消息并处理响应。

## 特性

- TCP 客户端初始化
- 启动时自动连接
- 消息发送和接收
- 响应解析和错误处理
- 周期性消息发送

## 项目结构

```
client-tcp/
├── main.go          # 主入口文件
└── etc/
    └── etc.toml     # 配置文件
```

## 核心组件

### 客户端设置

```go
component := client.NewClient(
    client.WithClient(tcp.NewClient()),
)
```

### 钩子监听器

```go
// 监听组件启动
proxy.AddHookListener(cluster.Start, startHandler)
// 监听连接建立
proxy.AddEventListener(cluster.Connect, connectHandler)
// 监听消息响应
proxy.AddRouteHandler(greet, greetHandler)
```

### 消息发送

```go
conn.Push(&cluster.Message{
    Route: 1,
    Data: &greetReq{
        Message: "Hello from client",
    },
})
```

## 配置说明

`etc/etc.toml` 中的关键设置：

- **客户端设置**：实例名称、编解码器（json）
- **TCP 客户端**：拨号地址 `127.0.0.1:3553`、拨号超时（`dialTimeout`）、心跳间隔
- **数据包**：消息格式设置

## 运行示例

1. 启动网关服务器（gate-tcp 示例），端口 3553
2. 启动节点服务器（quick-start 示例）
3. 运行客户端：

```bash
go run main.go
```

客户端将自动连接、发送消息、接收响应，并每秒重复一次。

---
title: "WebSocket 网关示例"
slug: "gate-ws"
keywords: ["due", "网关", "websocket", "ws", "网络"]
description: "WebSocket 网关服务器设置，适用于浏览器和移动客户端"
hide_title: true
---

# WebSocket 网关示例

本示例演示了如何在 Due 框架中设置 WebSocket 网关服务器，非常适合浏览器和移动客户端。

## 特性

- WebSocket 服务器初始化
- 带用户定位器的网关组件
- 通过 Consul 进行服务发现
- 连接管理
- 跨域支持
- 心跳机制配置

## 项目结构

```
gate-ws/
├── main.go          # 主入口文件
└── etc/
    └── etc.toml     # 配置文件
```

## 核心组件

### 网关设置

```go
// 创建 WebSocket 服务器
server := ws.NewServer()
// 创建用户定位器
locator := redis.NewLocator()
// 创建服务发现
registry := consul.NewRegistry()
// 创建网关组件
component := gate.NewGate(
    gate.WithServer(server),
    gate.WithLocator(locator),
    gate.WithRegistry(registry),
)
```

## 配置说明

`etc/etc.toml` 中的关键配置部分：

- **WebSocket 服务器**：
  - 监听地址 `:3553`
  - 连接路径 `/`
  - 最大连接数：5000
  - 允许源：`["*"]`（允许所有）
  - 心跳间隔：10s
  - 心跳机制：resp

## 运行示例

1. 启动 Redis，地址为 `127.0.0.1:6379`
2. 启动 Consul，地址为 `127.0.0.1:8500`
3. 启动节点服务器
4. 运行网关：

```bash
go run main.go
```

通过 WebSocket 连接到 `ws://127.0.0.1:3553/`

## 使用场景

- Web 浏览器客户端
- 移动应用程序
- 跨平台客户端
- 实时 Web 应用

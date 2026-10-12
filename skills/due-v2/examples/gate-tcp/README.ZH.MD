---
title: "TCP 网关示例"
slug: "gate-tcp"
keywords: ["due", "网关", "tcp", "网络", "服务器"]
description: "TCP 网关服务器设置，用于处理客户端连接"
hide_title: true
---

# TCP 网关示例

本示例演示了如何在 Due 框架中设置 TCP 网关服务器，以处理客户端连接并将消息路由到节点服务器。

## 特性

- TCP 服务器初始化
- 带用户定位器的网关组件
- 通过 Consul 进行服务发现
- 连接管理
- 消息路由到后端节点

## 项目结构

```
gate-tcp/
├── main.go          # 主入口文件
└── etc/
    └── etc.toml     # 配置文件
```

## 核心组件

### 网关设置

```go
// 创建 TCP 服务器
server := tcp.NewServer()
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

- **集群网关**：实例设置、分发策略
- **TCP 服务器**：监听地址 `:3553`、最大连接数、心跳
- **Redis 定位器**：用户位置追踪
- **Consul 注册中心**：服务发现

## 运行示例

1. 启动 Redis，地址为 `127.0.0.1:6379`
2. 启动 Consul，地址为 `127.0.0.1:8500`
3. 启动节点服务器（如 quick-start 示例）
4. 运行网关：

```bash
go run main.go
```

网关默认监听 TCP 端口 `3553`。

## 架构

```
客户端 → TCP 网关 → 节点服务器
       (端口 3553)   (RPC)
```

网关负责：
- 客户端连接管理
- 消息转发到相应节点
- 用户绑定/解绑
- 心跳监控

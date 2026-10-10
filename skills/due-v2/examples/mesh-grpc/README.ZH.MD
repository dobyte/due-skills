---
title: "gRPC 网格示例"
slug: "mesh-grpc"
keywords: ["due", "网格", "grpc", "rpc", "分布式", "微服务"]
description: "基于 gRPC 的网格网络，实现分布式服务间通信"
hide_title: true
---

# gRPC 网格示例

本示例演示了如何在 Due 中设置基于 gRPC 的网格网络，通过服务发现实现服务间通信。

## 特性

- gRPC 传输器实现高性能 RPC
- 基于 Consul 的服务发现
- 带服务提供者注册的服务器组件
- 带发现路由的客户端组件
- Protocol Buffer 定义

## 项目结构

```
mesh-grpc/
├── server/
│   ├── main.go          # 服务器入口
│   └── etc/etc.toml     # 服务器配置
├── client/
│   ├── main.go          # 客户端入口
│   └── etc/etc.toml     # 客户端配置
└── service/
    ├── pb/
    │   ├── greeter.proto        # Proto 定义
    │   ├── greeter.pb.go        # 生成的代码
    │   └── greeter_grpc.pb.go   # 生成的 gRPC 代码
    ├── server/
    │   └── server.go            # 服务实现
    └── client/
        └── client.go            # 客户端封装
```

## 核心组件

### 服务器设置

```go
registry := consul.NewRegistry()
transporter := grpc.NewTransporter()
component := mesh.NewMesh(
    mesh.WithRegistry(registry),
    mesh.WithTransporter(transporter),
)
// 网格必须注册至少一个服务提供者，否则启动时会直接退出。
initAPP(component.Proxy())

func initAPP(proxy *mesh.Proxy) {
    server.NewServer(proxy).Init()
}
```

### 服务实现

```go
type Server struct {
    pb.UnimplementedGreeterServer
    proxy *mesh.Proxy
}

func (s *Server) Init() {
    s.proxy.AddServiceProvider("greeter", &pb.Greeter_ServiceDesc, s)
}

func (s *Server) Hello(_ context.Context, args *pb.HelloArgs) (*pb.HelloReply, error) {
    return &pb.HelloReply{Message: "Hello " + args.Name}, nil
}
```

### 客户端使用

```go
cli, _ := client.NewClient(transporter.NewClient)
reply, _ := cli.Hello(context.Background(), &pb.HelloArgs{Name: "fuxiao"})
```

## 运行示例

1. 启动 Consul，地址为 `127.0.0.1:8500`
2. 启动服务器：

```bash
cd server && go run main.go
```

3. 运行客户端：

```bash
cd client && go run main.go
```

## 架构

```
客户端 → Consul 服务发现 → gRPC 服务器
                           (网格组件)
```

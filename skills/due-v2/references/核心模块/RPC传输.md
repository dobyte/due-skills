# RPC传输 (Transport)

## 概述

RPC传输模块是 Due 框架的核心组件,提供高性能的远程过程调用能力。支持 GRPC 和 RPCX 两种主流RPC框架,实现服务间的通信和调用。

## 包路径

```go
import (
    "github.com/dobyte/due/transport/grpc/v2"
    "github.com/dobyte/due/transport/rpcx/v2"
)
```

## GRPC 传输器

### 服务器配置

```toml
[transport.grpc.server]
    # 服务器监听地址。空或:0时系统将会随机端口号
    addr = ":0"
    # 是否将内部通信地址暴露到公网。默认为false
    expose = false
    # 私钥文件
    keyFile = ""
    # 证书文件
    certFile = ""
```

### 客户端配置

```toml
[transport.grpc.client]
    # CA证书文件
    caFile = ""
    # 证书域名
    serverName = ""
    # 分发策略。支持策略：随机（random）、轮询（rr）、加权轮询（wrr）、一致性哈希（ch）。默认为rr
    dispatch = "rr"
```

### 使用示例

```go
package main

import (
    "github.com/dobyte/due/transport/grpc/v2"
    "github.com/dobyte/due/v2/cluster/mesh"
)

func main() {
    // 创建RPC传输器
    transporter := grpc.NewTransporter()
    // 创建网格组件
    component := mesh.NewMesh(
        mesh.WithTransporter(transporter),
    )
    // ...
}
```

## RPCX 传输器

### 服务器配置

```toml
[transport.rpcx.server]
    # 服务器监听地址。空或:0时系统将会随机端口号
    addr = ":0"
    # 是否将内部通信地址暴露到公网。默认为false
    expose = false
    # 私钥文件
    keyFile = ""
    # 证书文件
    certFile = ""
```

### 客户端配置

```toml
[transport.rpcx.client]
    # CA证书文件
    caFile = ""
    # 证书域名
    serverName = ""
    # 连接池大小，默认为10
    poolSize = 10
```

### 使用示例

```go
package main

import (
    "github.com/dobyte/due/transport/rpcx/v2"
    "github.com/dobyte/due/v2/cluster/mesh"
)

func main() {
    // 创建RPC传输器
    transporter := rpcx.NewTransporter()
    // 创建网格组件
    component := mesh.NewMesh(
        mesh.WithTransporter(transporter),
    )
    // ...
}
```

## 核心 API

### 传输器接口

```go
type Transporter interface {
    // 获取传输器组件名称
    Name() string
    // 创建服务端
    NewServer() (Server, error)
    // 创建客户端连接。target 支持三种形式：
    //   direct://127.0.0.1:8011                通过地址直连
    //   direct://711baf8d-8a06-11ef-b7df-...   通过实例ID直连
    //   discovery://service_name               通过服务名进行服务发现
    NewClient(target string) (Client, error)
    // 设置默认的服务发现组件。仅在客户端尚未配置服务发现组件时生效
    SetDefaultDiscovery(discovery registry.Discovery)
    // 关闭传输器并释放所有客户端连接与资源
    Close() error
}
```

### 服务端接口

```go
type Server interface {
    // 启动服务端
    Start() error
    // 停止服务端
    Stop() error
    // 监听地址
    Addr() string
    // 协议方案（grpc/rpcx）
    Scheme() string
    // 服务端点
    Endpoint() *endpoint.Endpoint
    // 注册服务。desc 为服务描述：grpc 为 desc 对象，rpcx 为服务路径字符串
    RegisterService(desc, service any) error
}
```

### 客户端接口

```go
type Client interface {
    // 调用服务方法
    Call(ctx context.Context, service, method string, args any, reply any, opts ...any) error
    // 获取底层客户端连接
    Client() any
}
```

## GRPC 服务端示例

```go
package main

import (
    "context"
    "github.com/dobyte/due/transport/grpc/v2"
    "github.com/dobyte/due/v2/cluster/mesh"
)

type Server struct {
    proxy *mesh.Proxy
}

func (s *Server) Init() {
    // 注册服务提供者
    s.proxy.AddServiceProvider("greeter", &pb.Greeter_ServiceDesc, s)
}

func (s *Server) Hello(ctx context.Context, req *pb.HelloRequest) (*pb.HelloReply, error) {
    return &pb.HelloReply{Message: "Hello " + req.Name}, nil
}

func main() {
    // 创建传输器
    transporter := grpc.NewTransporter()
    
    // 创建网格组件
    component := mesh.NewMesh(
        mesh.WithTransporter(transporter),
    )
    
    // 初始化服务
    server := &Server{proxy: component.Proxy()}
    server.Init()
    
    // ...
}
```

## GRPC 客户端示例

```go
package main

import (
    "context"
    "github.com/dobyte/due/transport/grpc/v2"
    "google.golang.org/grpc"
)

func main() {
    // 创建传输器
    transporter := grpc.NewTransporter()
    
    // 创建客户端连接
    client, err := transporter.NewClient("discovery://greeter")
    if err != nil {
        panic(err)
    }
    
    // 获取GRPC客户端
    grpcClient := client.Client().(grpc.ClientConnInterface)
    
    // 创建服务客户端
    greeterClient := pb.NewGreeterClient(grpcClient)
    
    // 调用远程方法
    reply, err := greeterClient.Hello(context.Background(), &pb.HelloArgs{Name: "fuxiao"})
    if err != nil {
        panic(err)
    }
    
    println(reply.Message)
}
```

## 最佳实践

1. **服务发现**:
   - `discovery://service_name`：通过服务名进行服务发现，配合注册中心实现动态路由
   - `direct://127.0.0.1:8011`：通过地址直连
   - `direct://<实例ID>`：通过实例ID直连

2. **安全性**:
   - 生产环境启用TLS加密
   - 配置证书确保通信安全

3. **负载均衡**:
   - 利用注册中心的负载均衡能力
   - 合理设置权重参数

4. **错误处理**:
   - 实现重试机制提高可用性
   - 设置合理的超时时间

## 相关文件

- 传输层抽象接口：`github.com/dobyte/due/v2/transport`
- GRPC 传输器源码:`github.com/dobyte/due/transport/grpc/v2`
- RPCX 传输器源码:`github.com/dobyte/due/transport/rpcx/v2`
- 配置示例:`examples/*/etc/etc.toml`

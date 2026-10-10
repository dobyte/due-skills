---
title: "gRPC Mesh Example"
slug: "mesh-grpc"
keywords: ["due", "mesh", "grpc", "rpc", "distributed", "microservices"]
description: "gRPC-based mesh networking between distributed services"
hide_title: true
---

# gRPC Mesh Example

This example demonstrates how to set up a gRPC-based mesh network in Due, enabling inter-service communication with service discovery.

## Features

- gRPC transporter for high-performance RPC
- Consul-based service discovery
- Server component with service provider registration
- Client component with discovery-based routing
- Protocol Buffer definitions

## Project Structure

```
mesh-grpc/
├── server/
│   ├── main.go          # Server entry point
│   └── etc/etc.toml     # Server configuration
├── client/
│   ├── main.go          # Client entry point
│   └── etc/etc.toml     # Client configuration
└── service/
    ├── pb/
    │   ├── greeter.proto        # Proto definition
    │   ├── greeter.pb.go        # Generated code
    │   └── greeter_grpc.pb.go   # Generated gRPC code
    ├── server/
    │   └── server.go            # Service implementation
    └── client/
        └── client.go            # Client wrapper
```

## Key Components

### Server Setup

```go
registry := consul.NewRegistry()
transporter := grpc.NewTransporter()
component := mesh.NewMesh(
    mesh.WithRegistry(registry),
    mesh.WithTransporter(transporter),
)
// The mesh must register at least one service provider, otherwise it exits on startup.
initAPP(component.Proxy())

func initAPP(proxy *mesh.Proxy) {
    server.NewServer(proxy).Init()
}
```

### Service Implementation

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

### Client Usage

```go
cli, _ := client.NewClient(transporter.NewClient)
reply, _ := cli.Hello(context.Background(), &pb.HelloArgs{Name: "fuxiao"})
```

## Running the Example

1. Start Consul on `127.0.0.1:8500`
2. Start the server:

```bash
cd server && go run main.go
```

3. Run the client:

```bash
cd client && go run main.go
```

## Architecture

```
Client → Consul Discovery → gRPC Server
                            (mesh component)
```

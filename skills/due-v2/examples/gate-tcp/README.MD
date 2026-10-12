---
title: "TCP Gateway Example"
slug: "gate-tcp"
keywords: ["due", "gateway", "tcp", "network", "server"]
description: "TCP gateway server setup for handling client connections"
hide_title: true
---

# TCP Gateway Example

This example demonstrates how to set up a TCP gateway server in the Due framework to handle client connections and route messages to node servers.

## Features

- TCP server initialization
- Gateway component with user locator
- Service discovery via Consul
- Connection management
- Message routing to backend nodes

## Project Structure

```
gate-tcp/
├── main.go          # Main entry point
└── etc/
    └── etc.toml     # Configuration file
```

## Key Components

### Gateway Setup

```go
// Create TCP server
server := tcp.NewServer()
// Create user locator
locator := redis.NewLocator()
// Create service discovery
registry := consul.NewRegistry()
// Create gateway component
component := gate.NewGate(
    gate.WithServer(server),
    gate.WithLocator(locator),
    gate.WithRegistry(registry),
)
```

## Configuration

Key configuration sections in `etc/etc.toml`:

- **Cluster Gate**: Instance settings, dispatch strategy
- **TCP Server**: Listen address `:3553`, max connections, heartbeat
- **Redis Locator**: User location tracking
- **Consul Registry**: Service discovery

## Running the Example

1. Start Redis on `127.0.0.1:6379`
2. Start Consul on `127.0.0.1:8500`
3. Start a node server (e.g., quick-start example)
4. Run the gateway:

```bash
go run main.go
```

The gateway listens on TCP port `3553` by default.

## Architecture

```
Client → TCP Gateway → Node Server
         (Port 3553)    (RPC)
```

The gateway handles:
- Client connection management
- Message forwarding to appropriate nodes
- User binding/unbinding
- Heartbeat monitoring

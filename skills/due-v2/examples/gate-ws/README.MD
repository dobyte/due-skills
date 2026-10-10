---
title: "WebSocket Gateway Example"
slug: "gate-ws"
keywords: ["due", "gateway", "websocket", "ws", "network"]
description: "WebSocket gateway server setup for browser and mobile clients"
hide_title: true
---

# WebSocket Gateway Example

This example demonstrates how to set up a WebSocket gateway server in the Due framework, ideal for browser and mobile clients.

## Features

- WebSocket server initialization
- Gateway component with user locator
- Service discovery via Consul
- Connection management
- Cross-origin support
- Heartbeat mechanism configuration

## Project Structure

```
gate-ws/
├── main.go          # Main entry point
└── etc/
    └── etc.toml     # Configuration file
```

## Key Components

### Gateway Setup

```go
// Create WebSocket server
server := ws.NewServer()
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

- **WebSocket Server**: 
  - Listen address `:3553`
  - Connection path `/`
  - Max connections: 5000
  - Origins: `["*"]` (allow all)
  - Heartbeat interval: 10s
  - Heartbeat mechanism: resp

## Running the Example

1. Start Redis on `127.0.0.1:6379`
2. Start Consul on `127.0.0.1:8500`
3. Start a node server
4. Run the gateway:

```bash
go run main.go
```

Connect via WebSocket to `ws://127.0.0.1:3553/`

## Use Cases

- Web browser clients
- Mobile applications
- Cross-platform clients
- Real-time web applications

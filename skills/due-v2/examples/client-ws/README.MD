---
title: "WebSocket Client Example"
slug: "client-ws"
keywords: ["due", "client", "websocket", "ws", "connection"]
description: "Demonstrates WebSocket client implementation in Due framework"
hide_title: true
---

# WebSocket Client Example

This example demonstrates how to build a WebSocket client in Due framework to connect to a gate server and send/receive messages.

## Features

- WebSocket client initialization
- Automatic connection to gate server
- Message sending and receiving
- Connection event handling
- Hook listeners for lifecycle management

## Project Structure

```
client-ws/
├── main.go          # Main entry point
└── etc/
    └── etc.toml     # Configuration file
```

## Key Components

### Client Initialization

```go
// Create WebSocket client
component := client.NewClient(
    client.WithClient(ws.NewClient()),
)
```

### Connection Setup

```go
// Hook listener for startup
proxy.AddHookListener(cluster.Start, func(proxy *client.Proxy) {
    if _, err := proxy.Dial(); err != nil {
        log.Errorf("connect server failed: %v", err)
    }
})

// Event listener for connection
proxy.AddEventListener(cluster.Connect, func(conn *client.Conn) {
    log.Info("connected to server")
    doPushMessage(conn)
})
```

### Sending Messages

```go
// Send message to server
conn.Push(&cluster.Message{
    Route: greet,
    Data: &greetReq{
        Message: "Hello from client",
    },
})
```

### Receiving Messages

```go
// Route handler for response
proxy.AddRouteHandler(greet, func(ctx *client.Context) {
    res := &greetRes{}
    ctx.Parse(res)
    log.Info(res.Message)
})
```

## Configuration

Edit `etc/etc.toml` to configure:

- **Cluster Client**: Instance name, codec (`json`)
- **WebSocket Client**: Dial URL `ws://127.0.0.1:3553`, dial timeout (`dialTimeout`), heartbeat interval
- **Packet**: Byte order, route size, sequence size, buffer size

## Running the Example

1. Start a gate server (gate-tcp or gate-ws example)
2. Update server address in `etc/etc.toml`
3. Run the client:

```bash
go run main.go
```

## Message Flow

1. Client starts and dials server
2. Connection established, sends initial message
3. Server responds, client receives and logs
4. Client sends next message after 1 second
5. Cycle continues automatically

## Next Steps

- Try [client-tcp](../client-tcp/) for TCP protocol
- Try [gate-ws](../gate-ws/) to build the server side
- Try [bind-gate](../bind-gate/) to implement user authentication

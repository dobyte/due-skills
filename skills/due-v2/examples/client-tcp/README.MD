---
title: "TCP Client Example"
slug: "client-tcp"
keywords: ["due", "client", "tcp", "network", "connection"]
description: "TCP client example connecting to a Due gateway server"
hide_title: true
---

# TCP Client Example

This example demonstrates how to create a TCP client that connects to a Due gateway server, sends messages, and handles responses.

## Features

- TCP client initialization
- Automatic connection on startup
- Message sending and receiving
- Response parsing and error handling
- Periodic message sending

## Project Structure

```
client-tcp/
├── main.go          # Main entry point
└── etc/
    └── etc.toml     # Configuration file
```

## Key Components

### Client Setup

```go
component := client.NewClient(
    client.WithClient(tcp.NewClient()),
)
```

### Hook Listeners

```go
// Listen for component start
proxy.AddHookListener(cluster.Start, startHandler)
// Listen for connection established
proxy.AddEventListener(cluster.Connect, connectHandler)
// Listen for message responses
proxy.AddRouteHandler(greet, greetHandler)
```

### Message Sending

```go
conn.Push(&cluster.Message{
    Route: 1,
    Data: &greetReq{
        Message: "Hello from client",
    },
})
```

## Configuration

Key settings in `etc/etc.toml`:

- **Client Settings**: Instance name, codec (json)
- **TCP Client**: Dial address `127.0.0.1:3553`, dial timeout (`dialTimeout`), heartbeat interval
- **Packet**: Message format settings

## Running the Example

1. Start a gateway server (gate-tcp example) on port 3553
2. Start a node server (quick-start example)
3. Run the client:

```bash
go run main.go
```

The client will automatically connect, send a message, receive the response, and repeat every second.

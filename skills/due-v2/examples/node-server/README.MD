---
title: "Node Server Example"
slug: "node-server"
keywords: ["due", "node", "server", "complete", "message-handling"]
description: "Complete node server example with message handling"
hide_title: true
---

# Node Server Example

This example demonstrates a complete node server setup with comprehensive message handling, including request parsing, response generation, and error handling.

## Features

- Complete node component initialization
- Redis locator for user tracking
- Consul registry for service discovery
- Advanced route handler with error handling
- JSON message encoding/decoding
- Time-based responses

## Project Structure

```
node-server/
├── main.go          # Main entry point
└── etc/
    └── etc.toml     # Configuration file
```

## Key Components

### Node Initialization

```go
container := due.NewContainer()
locator := redis.NewLocator()
registry := consul.NewRegistry()
component := node.NewNode(
    node.WithLocator(locator),
    node.WithRegistry(registry),
)
initApp(component.Proxy())
container.Add(component)
container.Serve()
```

### Route Handler with Error Handling

```go
func greetHandler(ctx node.Context) {
    req := &greetReq{}
    res := &greetRes{}
    
    ctx.Defer(func() {
        if err := ctx.Response(res); err != nil {
            log.Errorf("response failed: %v", err)
        }
    })
    
    if err := ctx.Parse(req); err != nil {
        log.Errorf("parse failed: %v", err)
        res.Code = codes.InternalError.Code()
        return
    }
    
    res.Code = codes.OK.Code()
    res.Message = fmt.Sprintf("Server time: %s", xtime.Now().Format(xtime.DateTime))
}
```

## Configuration

Edit `etc/etc.toml` to configure:

- **Node Settings**: Instance ID, name, RPC address, codec
- **Redis Locator**: Connection settings for user location tracking
- **Consul Registry**: Service discovery configuration
- **Packet Settings**: Message format and size limits
- **Logging**: Output level and destinations

## Running the Example

1. Start Redis on `127.0.0.1:6379`
2. Start Consul on `127.0.0.1:8500`
3. Run the server:

```bash
go run main.go
```

## Testing

Use client-tcp or client-ws examples to send messages and receive responses with server timestamps.

## Error Handling

The example demonstrates proper error handling:
- Request parsing errors
- Response delivery errors
- Error code propagation
- Logging for debugging

---
title: "Actor Model Example"
slug: "actor-model"
keywords: ["due", "actor", "concurrency", "node", "game-server"]
description: "Demonstrates the Actor concurrency model in Due framework with room-based game logic"
hide_title: true
---

# Actor Model Example

This example demonstrates how to use the Actor concurrency model in Due framework to build a room-based game server with complex state management.

## Features

- Actor-based concurrency for game room management
- Middleware authentication based on UID
- Room creation, joining, and game actions
- Processor pattern for room lifecycle management
- Structured application layout (app/logic/middleware/route)

## Project Structure

```
actor-model/
├── main.go                    # Main entry point
├── etc/
│   └── etc.toml               # Configuration file
└── app/
    ├── app.go                 # Application initialization
    ├── base/
    │   └── base.go            # Base response struct
    ├── logic/
    │   ├── core.go            # Core game logic
    │   ├── protocol.go        # Request/response message definitions
    │   ├── room.go            # Room management
    │   └── room_processor.go  # Room Actor processor
    ├── middleware/
    │   └── auth.go            # Authentication middleware
    └── route/
        └── route.go           # Route registration
```

## Key Components

### Actor Processor

```go
type roomProcessor struct {
    node.BaseProcessor
    actor *node.Actor
    room  *room
}

func newRoomProcessor(actor *node.Actor, args ...any) node.Processor {
    return &roomProcessor{
        actor: actor,
        room:  args[0].(*room),
    }
}

func (p *roomProcessor) Init() {
    p.actor.AddRouteHandler(route.Join, p.join)
    p.actor.AddRouteHandler(route.Play, p.play)
}
```

### Actor Registration

```go
proxy.Router().Group(func(group *node.RouterGroup) {
    // Login
    group.AddRouteHandler(route.Login, c.login)
    // Set the auth middleware for the following routes
    group.Middleware(middleware.Auth)
    // Create room
    group.AddRouteHandler(route.Create, c.create, node.AuthorizedRoute)
    // Join room
    group.AddRouteHandler(route.Join, c.join, node.AuthorizedRoute)
    // Play
    group.AddRouteHandler(route.Play, c.play, node.StatefulRoute)
})
```

### Actor Spawning

```go
actor, err := c.proxy.Spawn(newRoomProcessor,
    node.WithActorID(xconv.String(r.id)),
    node.WithActorArgs(r),
    node.WithActorKind(roomActor),
)
if err != nil {
    log.Errorf("spawn actor failed: %v", err)
    return
}
```

## Configuration

Edit `etc/etc.toml` to configure:

- **Cluster Node**: Instance ID, name, RPC address
- **Redis Locator**: Connection address for user location tracking
- **Consul Registry**: Service discovery settings
- **Packet**: Message format settings
- **Logging**: Level, format, output

## Running the Example

1. Ensure Redis is running on `127.0.0.1:6379`
2. Ensure Consul is running on `127.0.0.1:8500`
3. Run the server:

```bash
go run main.go
```

## Use Cases

- Multiplayer game rooms (card games, board games)
- Chat rooms with state management
- Real-time collaborative applications
- Any scenario requiring isolated state per user group

## Next Steps

- Try [bind-node](../bind-node/) to understand stateful routing
- Try [eventbus-nats](../eventbus-nats/) for cross-server events

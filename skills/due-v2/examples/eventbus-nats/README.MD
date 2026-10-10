---
title: "EventBus NATS Example"
slug: "eventbus-nats"
keywords: ["due", "eventbus", "nats", "pubsub", "event-driven"]
description: "Demonstrates NATS-based event bus for distributed event-driven architecture"
hide_title: true
---

# EventBus NATS Example

This example demonstrates how to use the NATS-based event bus in Due framework for distributed event-driven communication.

## Features

- NATS event bus initialization
- Event publishing and subscribing
- Cross-server event propagation
- Topic-based event routing
- Automatic reconnection handling

## Project Structure

```
eventbus-nats/
├── main.go          # Main entry point
└── etc/
    └── etc.toml     # Configuration file
```

## Key Components

### Event Bus Initialization

```go
// Set global event bus to NATS
eventbus.SetEventbus(nats.NewEventbus())
```

### Publishing Events

```go
// Publish an event to a topic
if err := eventbus.Publish(context.Background(), "message", &Payload{
    Message: "hello world",
}); err != nil {
    log.Errorf("publish event failed: %v", err)
}
```

### Subscribing to Events

```go
// Subscribe to events; the handler receives an *eventbus.Event
sub, err := eventbus.Subscribe(context.Background(), "message", func(evt *eventbus.Event) {
    payload := &Payload{}
    if err := evt.Payload.Scan(payload); err != nil {
        log.Errorf("scan payload failed: %v", err)
        return
    }
    log.Infof("evt id: %s, topic: %s, payload message: %s", evt.ID, evt.Topic, payload.Message)
})
if err != nil {
    log.Errorf("subscribe event failed: %v", err)
    return
}
```

### Unsubscribing

```go
// Cancel the subscription through the returned Subscription
if err := sub.Unsubscribe(context.Background()); err != nil {
    log.Errorf("unsubscribe event failed: %v", err)
}
```

## Configuration

```toml
[eventbus.nats]
    # Connection address, defaults to nats://127.0.0.1:4222
    url = "nats://127.0.0.1:4222"
    # Connection timeout, defaults to 2s
    timeout = "2s"
    # Key prefix
    prefix = "due:eventbus"
```

## Running the Example

1. Ensure NATS server is running on `127.0.0.1:4222`
2. Run:

```bash
go run main.go
```

## API Reference

- `eventbus.SetEventbus(eb Eventbus)` - Set the global event bus
- `eventbus.Publish(ctx, topic, message)` - Publish an event
- `eventbus.Subscribe(ctx, topic, handler, balance...)` - Subscribe to events, returns a `Subscription`
- `Subscription.Unsubscribe(ctx)` - Cancel a subscription
- `eventbus.Close()` - Close the event bus

## Use Cases

- Cross-server communication
- Distributed event processing
- Real-time notifications
- Audit logging
- Microservice coordination

## Next Steps

- Try [cache-redis](../cache-redis/) for distributed caching
- Try [mesh-grpc](../mesh-grpc/) for RPC-based communication

---
title: "Third Redis Example"
slug: "third-redis"
keywords: ["due", "redis", "client", "cache", "nosql"]
description: "Demonstrates Redis client integration for high-performance data operations"
hide_title: true
---

# Third Redis Example

This example demonstrates how to integrate the Redis client in Due framework for high-performance key-value operations.

## Features

- Redis client initialization
- Single/Cluster/Sentinel mode support
- Connection pool configuration
- TLS support
- Custom command execution
- Pub/Sub support

## Project Structure

```
third-redis/
├── main.go          # Main entry point
├── etc/
│   └── etc.toml     # Configuration file
└── redis/
    └── redis.go     # Redis client wrapper
```

## Key Components

### Client Initialization

```go
// Get a Redis client by name (config section: [redis.default])
client := redis.Instance("default")

// A single-node, cluster or sentinel setup is selected automatically
// by the underlying UniversalClient based on the configuration.
```

### Basic Operations

```go
// Set
client.Set(ctx, "key", "value", 0)

// Get
val, err := client.Get(ctx, "key").Result()

// Hash
client.HSet(ctx, "user:1", "name", "john")
client.HGet(ctx, "user:1", "name")

// List
client.LPush(ctx, "queue", "item1", "item2")
client.RPop(ctx, "queue")
```

### Pub/Sub

```go
// Subscribe
pubsub := client.Subscribe(ctx, "channel")
msg, err := pubsub.ReceiveMessage(ctx)

// Publish
client.Publish(ctx, "channel", "message")
```

## Configuration

```toml
[redis.default]
    addrs = ["127.0.0.1:6379"]
    db = 0
    username = ""
    password = ""
    maxRetries = 3
    poolSize = 200
    minIdleConns = 10
    dialTimeout = "5s"
    readTimeout = "1s"
    writeTimeout = "1s"
```

## Running the Example

1. Ensure Redis is running on `127.0.0.1:6379`
2. Run:

```bash
go run main.go
```

## API Reference

- `redis.Instance(name...)` - Get a Redis client by name
- `redis.NewInstance(config)` - Create a Redis client from config
- `client.Ping(ctx)` - Ping the server
- `client.Set/Get/Del` - String operations
- `client.HSet/HGet/HDel` - Hash operations
- `client.LPush/LPop/RPush/RPop` - List operations
- `client.SAdd/SMembers/SRem` - Set operations
- `client.Subscribe/Publish` - Pub/Sub operations

## Use Cases

- Session storage
- Real-time leaderboards
- Rate limiting
- Message queues
- Caching layer
- Distributed counters

## Next Steps

- Try [cache-redis](../cache-redis/) for cache abstraction
- Try [lock-redis](../lock-redis/) for distributed locking

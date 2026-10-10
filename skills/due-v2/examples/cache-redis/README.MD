---
title: "Cache Redis Example"
slug: "cache-redis"
keywords: ["due", "cache", "redis", "getset"]
description: "Demonstrates Redis cache usage with GetSet pattern in Due framework"
hide_title: true
---

# Cache Redis Example

This example demonstrates how to use the Redis cache module in Due framework with the GetSet pattern for lazy initialization.

## Features

- Redis cache initialization
- GetSet pattern (get or create)
- Automatic cache expiration handling
- Type-safe result conversion

## Project Structure

```
cache-redis/
├── main.go          # Main entry point
└── etc/
    └── etc.toml     # Configuration file
```

## Key Components

### Cache Initialization

```go
// Set global cache to Redis
cache.SetCache(redis.NewCache())
```

### GetSet Pattern

```go
// Get from cache, or create if not exists
unix, err := cache.GetSet(context.Background(), "key", func() (any, error) {
    return xtime.Now().Unix(), nil
}).Int64()
```

### Configuration

```toml
[cache.redis]
    addrs = ["127.0.0.1:6379"]
    db = 0
    password = ""
    maxRetries = 3
    prefix = "due:cache"
```

## Running the Example

1. Ensure Redis is running on `127.0.0.1:6379`
2. Run:

```bash
go run main.go
```

## API Reference

- `cache.SetCache(cache Cache)` - Set global cache instance
- `cache.Get(ctx, key)` - Get value from cache
- `cache.Set(ctx, key, value, expiration)` - Set value with expiration
- `cache.GetSet(ctx, key, fn)` - Get or create value
- `cache.Delete(ctx, keys...)` - Delete keys
- `cache.IncrInt/DecrInt` - Increment/decrement integers
- `cache.IncrFloat/DecrFloat` - Increment/decrement floats

## Use Cases

- User session caching
- Game state persistence
- Rate limiting counters
- Configuration caching

## Next Steps

- Try [lock-redis](../lock-redis/) for distributed locking
- Try [eventbus-nats](../eventbus-nats/) for event-driven architecture

---
title: "Lock Redis Example"
slug: "lock-redis"
keywords: ["due", "lock", "redis", "distributed-lock", "concurrency"]
description: "Demonstrates Redis-based distributed locking for concurrent resource access"
hide_title: true
---

# Lock Redis Example

This example demonstrates how to use the Redis-based distributed lock in Due framework for managing concurrent access to shared resources.

## Features

- Redis lock maker initialization
- Create a named locker and acquire/release it
- Blocking acquire and try-acquire (with optional expiration)
- Automatic lock expiration and renewal
- Concurrent lock demonstration

## Project Structure

```
lock-redis/
├── main.go          # Main entry point
└── etc/
    └── etc.toml     # Configuration file
```

## Key Components

### Lock Initialization

```go
// Set the global lock maker to the Redis implementation
lock.SetMaker(redis.NewMaker())
```

### Acquiring and Releasing Locks

```go
// Create a locker by name, then acquire it (blocks until acquired)
locker := lock.Make("lock")
if err := locker.Acquire(ctx); err != nil {
    log.Errorf("acquire lock failed: %v", err)
    return
}
defer locker.Release(ctx)
```

### Try-Acquire with Expiration

```go
// Try to acquire the lock with an expiration; returns an error if it is held
if err := locker.TryAcquire(ctx, 5*time.Second); err != nil {
    log.Warnf("lock not available: %v", err)
    return
}
```

### Releasing Locks

```go
// Release the lock
if err := locker.Release(ctx); err != nil {
    log.Errorf("release lock failed: %v", err)
}
```

## Configuration

```toml
[lock.redis]
    addrs = ["127.0.0.1:6379"]
    db = 0
    password = ""
    maxRetries = 3
    prefix = "due:lock"
    # 锁默认过期时间，默认 3s
    expiration = "3s"
    # 获取锁的重试间隔，默认 20ms
    acquireInterval = "20ms"
    # 获取锁的最大重试次数，默认 0（无限重试）
    acquireMaxRetries = 0
```

## Running the Example

1. Ensure Redis is running on `127.0.0.1:6379`
2. Run:

```bash
go run main.go
```

## API Reference

- `lock.SetMaker(maker lock.Maker)` – Set the global lock maker (closes the previous one)
- `lock.GetMaker() lock.Maker` – Get the global lock maker
- `lock.Make(name string) lock.Locker` – Create a locker by name via the global maker
- `lock.Close() error` – Close the global maker
- `lock.Maker` – `Make(name string) Locker`, `Close() error`
- `lock.Locker` – `Acquire(ctx) error`, `TryAcquire(ctx, expiration ...time.Duration) error`, `Release(ctx) error`

## Use Cases

- Preventing duplicate operations
- Rate limiting
- Resource access control
- Leader election
- Distributed transaction coordination

## Next Steps

- Try [cache-redis](../cache-redis/) for distributed caching
- Try [eventbus-nats](../eventbus-nats/) for event coordination

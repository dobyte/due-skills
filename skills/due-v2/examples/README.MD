---
title: "Due Framework Examples"
slug: "examples"
keywords: ["due", "framework", "examples", "go", "game-server", "distributed"]
description: "Collection of examples demonstrating Due framework features and usage"
hide_title: true
---

# Due Framework Examples

This directory contains various examples demonstrating different features and usage patterns of the Due framework.

## Available Examples

### Quick Start
- **[quick-start](quick-start/)** - Basic node server setup with route handlers
- **[node-server](node-server/)** - Complete node server example with message handling

### Gateway Components
- **[gate-tcp](gate-tcp/)** - TCP gateway server setup
- **[gate-ws](gate-ws/)** - WebSocket gateway server setup

### Client Components
- **[client-tcp](client-tcp/)** - TCP client connecting to gateway
- **[client-ws](client-ws/)** - WebSocket client connecting to gateway

### Advanced Features
- **[actor-model](actor-model/)** - Actor model implementation with rooms and processors
- **[mesh-grpc](mesh-grpc/)** - gRPC-based mesh networking between services
- **[bind-gate](bind-gate/)** - Binding users to gateways during login
- **[bind-node](bind-node/)** - Binding users to specific nodes with stateful routing

### Infrastructure Components
- **[cache-redis](cache-redis/)** - Redis-based caching implementation
- **[config-file](config-file/)** - File-based configuration management
- **[eventbus-nats](eventbus-nats/)** - NATS-based event bus for pub/sub messaging
- **[lock-redis](lock-redis/)** - Redis-based distributed locking

### Third-Party Integrations
- **[third-gorm](third-gorm/)** - GORM database integration
- **[third-redis](third-redis/)** - Redis client integration
- **[third-jwt](third-jwt/)** - JWT authentication integration

## Getting Started

Each example includes:
- `README.MD` - English documentation
- `README.ZH.MD` - Chinese documentation
- Complete source code
- Configuration files in `etc/etc.toml`

To run an example:
1. Navigate to the example directory
2. Ensure required dependencies are installed (Redis, Consul, etc.)
3. Configure `etc/etc.toml` as needed
4. Run `go run main.go`

## Requirements

- Go 1.27 or higher
- Redis (for locator, cache, lock examples)
- Consul (for service discovery examples)
- NATS (for eventbus examples)
- MySQL (for GORM examples)

## Documentation

For complete documentation, visit [Due Framework Documentation](https://github.com/dobyte/due)

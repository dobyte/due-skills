---
title: "Third JWT Example"
slug: "third-jwt"
keywords: ["due", "jwt", "authentication", "token", "security"]
description: "Demonstrates JWT token-based authentication with Redis storage"
hide_title: true
---

# Third JWT Example

This example demonstrates how to implement JWT (JSON Web Token) authentication in Due framework with Redis-based token storage.

## Features

- JWT token generation and validation
- Redis-based token storage
- Token refresh mechanism
- HTTP request token extraction
- User context extraction

## Project Structure

```
third-jwt/
├── main.go          # Main entry point
├── etc/
│   └── etc.toml     # Configuration file
└── jwt/
    ├── jwt.go       # JWT implementation
    └── store.go     # Redis token store
```

## Key Components

### JWT Initialization

```go
// Get a JWT instance by name (config section: [jwt.default])
ins := jwt.Instance("default")
```

### Token Generation

```go
// Generate a token; the identity key carries the user ID
token, err := ins.GenerateToken(jwt.Payload{
    ins.IdentityKey(): 1,
    "nickname":        "fuxiao",
})
// token.Token is the signed JWT string
```

### Token Validation

```go
// Parse and verify the payload from a token string
payload, err := ins.ExtractPayload(token.Token)
```

### Middleware Integration

```go
// Extract the authenticated identity from an incoming HTTP request
identity, err := ins.Http().ExtractIdentity(r)
```

### Token Refresh

```go
// Refresh a token before it expires
newToken, err := ins.RefreshToken(token.Token)
```

## Configuration

```toml
[jwt.default]
    issuer = "due"
    validDuration = 7200
    secretKey = "xxxx"
    identityKey = "uid"
    locations = "query:token,header:Authorization"

    [jwt.default.store]
        addrs = ["127.0.0.1:6379"]
        db = 0
        password = ""
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

- `jwt.Instance(name...)` - Get a JWT instance by name
- `jwt.NewInstance(config)` - Create a JWT instance from config
- `ins.GenerateToken(payload)` - Generate a token
- `ins.ExtractPayload(token)` - Parse and verify a token's payload
- `ins.ExtractIdentity(token)` - Extract the identity from a token
- `ins.RefreshToken(token)` - Refresh a token
- `ins.DestroyToken(token)` - Destroy a token
- `ins.IdentityKey()` - Get the configured identity key
- `ins.Http()` - HTTP request helpers (`ExtractPayload`, `ExtractIdentity`, `Middleware`, ...)

## Use Cases

- User authentication
- API authorization
- Stateless session management
- Single sign-on (SSO)
- Microservice authentication

## Next Steps

- Try [bind-gate](../bind-gate/) to integrate JWT with gateway binding
- Try [third-redis](../third-redis/) for token storage optimization

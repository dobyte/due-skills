---
title: "Third GORM Example"
slug: "third-gorm"
keywords: ["due", "gorm", "mysql", "database", "orm"]
description: "Demonstrates GORM database integration with MySQL for data persistence"
hide_title: true
---

# Third GORM Example

This example demonstrates how to integrate GORM (Go Object Relational Mapping) with MySQL in Due framework for database operations.

## Features

- GORM MySQL initialization
- Connection pool configuration
- Custom logger integration
- JSON serializer support
- Multi-instance support
- Transaction execution via `db.Connection`

## Project Structure

```
third-gorm/
├── main.go              # Main entry point
├── etc/
│   └── etc.toml         # Configuration file
└── gorm/
    ├── mysql.go         # MySQL initialization
    ├── logger.go        # Custom logger
    └── serializer/
        └── json.go      # JSON serializer
```

## Key Components

### Database Initialization

```go
// Get a GORM instance by name (config section: [mysql.default])
db := gormcomp.Instance("default")

// Run statements within a dedicated connection/transaction
if err := db.Connection(func(tx *gorm.DB) error {
    return nil
}); err != nil {
    log.Errorf("db connection error: %v", err)
}
```

### Connection Pool

```go
// Access the underlying *sql.DB to configure the pool
database, err := db.DB()
database.SetMaxIdleConns(50)
database.SetMaxOpenConns(50)
database.SetConnMaxLifetime(time.Hour)
```

### Model Definition

```go
type User struct {
    ID        int64          `gorm:"primarykey"`
    Username  string         `gorm:"size:50;uniqueIndex"`
    Email     string         `gorm:"size:100"`
    Status    int            `gorm:"default:1"`
    Extra     any            `gorm:"serializer:json"` // handled by the registered "json" serializer
    CreatedAt time.Time
    UpdatedAt time.Time
}
```

### CRUD Operations

```go
// Create
db.Create(&User{Username: "john", Email: "john@example.com"})

// Read
var user User
db.First(&user, "username = ?", "john")

// Update
db.Model(&user).Update("status", 2)

// Delete
db.Delete(&user)
```

## Configuration

```toml
[mysql.default]
    dsn = "root:123456@tcp(127.0.0.1:3306)/due_default?charset=utf8mb4&parseTime=True&loc=Local"
    logLevel = "info"
    maxIdleConns = 50
    maxOpenConns = 50
    slowThreshold = "2s"
    connMaxLifetime = "1h"
```

## Running the Example

1. Ensure MySQL is running on `127.0.0.1:3306`
2. Create database: `CREATE DATABASE due_default;`
3. Run:

```bash
go run main.go
```

## API Reference

- `gorm.Instance(name...)` - Get a GORM instance by name
- `gorm.NewInstance(config)` - Create a GORM instance from config
- `db.Connection(fn)` - Run fn within a dedicated connection/transaction
- `db.Create(value)` - Insert record
- `db.First(dest, conditions...)` - Query first record
- `db.Find(dest, conditions...)` - Query multiple records
- `db.Save(value)` - Update or insert
- `db.Delete(value)` - Delete record
- `db.AutoMigrate(models...)` - Auto-migrate schema

## Use Cases

- User data persistence
- Game state storage
- Transaction records
- Configuration management
- Audit logs

## Next Steps

- Try [third-redis](../third-redis/) for caching database queries
- Try [cache-redis](../cache-redis/) for high-performance data access

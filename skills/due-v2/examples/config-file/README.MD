---
title: "Config File Example"
slug: "config-file"
keywords: ["due", "config", "file", "toml", "yaml"]
description: "Demonstrates file-based configuration management in Due framework"
hide_title: true
---

# Config File Example

This example demonstrates how to use the file-based configuration source in Due framework.

## Features

- File configuration source initialization
- TOML/YAML/JSON format support
- Configuration reading and watching
- Multiple configuration files

## Project Structure

```
config-file/
├── main.go                 # Main entry point
├── etc/
│   └── etc.toml            # Framework configuration
└── config/
    └── config.toml         # Application configuration
```

## Key Components

### Configuration Source

```go
// Set the file configurator as the global configurator
config.SetConfigurator(config.NewConfigurator(
    config.WithSources(file.NewSource()),
))
```

### Reading Configuration

```go
// Read a config value (returns a value.Value)
timezone := config.Get("config.timezone").String()
```

### Watching Configuration

```go
// Watch for configuration changes; the callback receives the names of the changed configs
config.Watch(func(names ...string) {
    log.Infof("config changed: %v", names)
}, "config")
```

## Configuration Format

```toml
# etc/etc.toml - framework configuration
[config.file]
    # Config file or directory path
    path = "./config"
    # Read-write mode. Options: read-only | write-only | read-write, defaults to read-only
    mode = "read-write"

# config/config.toml - application configuration
timezone = "UTC"
```

## Running the Example

```bash
go run main.go
```

## API Reference

- `config.SetConfigurator(configurator Configurator)` - Set the global configurator
- `config.NewConfigurator(opts...)` / `config.WithSources(sources...)` - Build a configurator from sources
- `config.Get(pattern, def...)` - Get a value (returns `value.Value`)
- `config.Has(pattern)` - Check whether a config exists
- `config.Watch(cb, names...)` - Watch for config changes
- `config.Load(ctx, source, file...)` - Load the config of a source
- `config.Store(ctx, source, file, content, override...)` - Save config to a source

## Use Cases

- Application configuration management
- Multi-environment configuration (dev/test/prod)
- Dynamic configuration reloading
- Configuration hot-updates

## Next Steps

- Try [config-file](../config-file/) with different formats (YAML/JSON)
- Try [eventbus-nats](../eventbus-nats/) for configuration change events

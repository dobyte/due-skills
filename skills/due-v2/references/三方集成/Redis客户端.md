# Redis 客户端集成

## 概述

Due 框架通过 go-redis 库集成 Redis，支持单机、哨兵和集群模式。封装层提供连接池管理、TLS 加密连接、超时配置等功能，并通过 Due 的 `pool.Factory` 实现多实例管理。

## 第三方依赖

| 库名 | 版本 | 说明 |
|------|------|------|
| [github.com/go-redis/redis/v8](https://github.com/go-redis/redis/v8) | v8.11.5 | Go Redis 客户端 |

## 配置参数

| 名称 | 类型 | 描述 |
|------|------|------|
| `addrs` | []string | 连接地址列表（支持多地址用于集群/哨兵模式） |
| `db` | int | 数据库号，默认为 0 |
| `username` | string | 用户名，默认空 |
| `password` | string | 密码，默认空 |
| `keyFile` | string | TLS 私钥文件路径，默认空 |
| `certFile` | string | TLS 证书文件路径，默认空 |
| `caFile` | string | TLS CA 证书文件路径，默认空 |
| `maxRetries` | int | 网络相关的错误最大重试次数，默认 3 次 |
| `poolSize` | int | 最大连接池限制，默认为 200 个连接 |
| `minIdleConns` | int | 最小空闲连接数，默认 20 个连接 |
| `dialTimeout` | string | 拨号超时时间，支持单位：ns、us/µs、ms、s、m、h、d。默认 `3s` |
| `idleTimeout` | string | 连接最大空闲时间，支持单位同上。默认 `0s`（不限制） |
| `readTimeout` | string | 读超时时间，支持单位同上。默认 `1s` |
| `writeTimeout` | string | 写超时时间，支持单位同上。默认 `1s` |

## 配置文件示例

```toml
[redis.default]
    # 连接地址
    addrs = ["127.0.0.1:6379"]
    # 数据库号，默认为0
    db = 0
    # 用户名，默认空
    username = ""
    # 密码，默认空
    password = ""
    # 私钥文件
    keyFile = ""
    # 证书文件
    certFile = ""
    # CA证书文件
    caFile = ""
    # 网络相关的错误最大重试次数，默认3次
    maxRetries = 3
    # 最大连接池限制，默认为200个连接
    poolSize = 200
    # 最小空闲连接数
    minIdleConns = 10
    # 拨号超时时间
    dialTimeout = "5s"
    # 连接最大空闲时间，默认0s
    idleTimeout = "0s"
    # 读超时，默认1s
    readTimeout = "1s"
    # 写超时，默认1s
    writeTimeout = "1s"
```

## 代码实现

### 核心封装（redis/redis.go）

```go
package redis

import (
	"fmt"
	"time"

	"github.com/dobyte/due/v2/core/pool"
	"github.com/dobyte/due/v2/core/tls"
	"github.com/dobyte/due/v2/etc"
	"github.com/dobyte/due/v2/log"
	"github.com/go-redis/redis/v8"
)

var factory = pool.NewFactory(func(name string) (Redis, error) {
	return NewInstance(fmt.Sprintf("etc.redis.%s", name))
})

type (
	Redis  = redis.UniversalClient
	Script = redis.Script
)

type Config struct {
	Addrs        []string      `json:"addrs"`
	DB           int           `json:"db"`
	Username     string        `json:"username"`
	Password     string        `json:"password"`
	CertFile     string        `json:"certFile"`
	KeyFile      string        `json:"keyFile"`
	CaFile       string        `json:"caFile"`
	MaxRetries   int           `json:"maxRetries"`
	PoolSize     int           `json:"poolSize"`
	MinIdleConns int           `json:"minIdleConns"`
	IdleTimeout  time.Duration `json:"idleTimeout"`
	DialTimeout  time.Duration `json:"dialTimeout"`
	ReadTimeout  time.Duration `json:"readTimeout"`
	WriteTimeout time.Duration `json:"writeTimeout"`
}

// Instance 获取实例
func Instance(name ...string) Redis {
	var (
		err error
		ins Redis
	)

	if len(name) == 0 {
		ins, err = factory.Get("default")
	} else {
		ins, err = factory.Get(name[0])
	}

	if err != nil {
		log.Fatalf("create redis instance failed: %v", err)
	}

	return ins
}

// NewInstance 新建实例
func NewInstance[T string | Config | *Config](config T) (Redis, error) {
	var (
		conf *Config
		v    any = config
	)

	switch c := v.(type) {
	case string:
		conf = &Config{
			Addrs:        etc.Get(fmt.Sprintf("%s.addrs", c)).Strings(),
			DB:           etc.Get(fmt.Sprintf("%s.db", c)).Int(),
			CertFile:     etc.Get(fmt.Sprintf("%s.certFile", c)).String(),
			KeyFile:      etc.Get(fmt.Sprintf("%s.keyFile", c)).String(),
			CaFile:       etc.Get(fmt.Sprintf("%s.caFile", c)).String(),
			Username:     etc.Get(fmt.Sprintf("%s.username", c)).String(),
			Password:     etc.Get(fmt.Sprintf("%s.password", c)).String(),
			MaxRetries:   etc.Get(fmt.Sprintf("%s.maxRetries", c), 3).Int(),
			PoolSize:     etc.Get(fmt.Sprintf("%s.poolSize", c), 200).Int(),
			MinIdleConns: etc.Get(fmt.Sprintf("%s.minIdleConns", c), 20).Int(),
			DialTimeout:  etc.Get(fmt.Sprintf("%s.dialTimeout", c), "3s").Duration(),
			IdleTimeout:  etc.Get(fmt.Sprintf("%s.idleTimeout", c)).Duration(),
			ReadTimeout:  etc.Get(fmt.Sprintf("%s.readTimeout", c), "1s").Duration(),
			WriteTimeout: etc.Get(fmt.Sprintf("%s.writeTimeout", c), "1s").Duration(),
		}
	case Config:
		conf = &c
	case *Config:
		conf = c
	}

	options := &redis.UniversalOptions{
		Addrs:        conf.Addrs,
		DB:           conf.DB,
		Username:     conf.Username,
		Password:     conf.Password,
		MaxRetries:   conf.MaxRetries,
		PoolSize:     conf.PoolSize,
		MinIdleConns: conf.MinIdleConns,
		IdleTimeout:  conf.IdleTimeout,
		DialTimeout:  conf.DialTimeout,
		ReadTimeout:  conf.ReadTimeout,
		WriteTimeout: conf.WriteTimeout,
	}

	if conf.CertFile != "" && conf.KeyFile != "" && conf.CaFile != "" {
		if tlsConfig, err := tls.MakeRedisTLSConfig(conf.CertFile, conf.KeyFile, conf.CaFile); err != nil {
			return nil, err
		} else {
			options.TLSConfig = tlsConfig
		}
	}

	return redis.NewUniversalClient(options), nil
}
```

## 使用方式

### 基本使用

```go
package main

import (
	"context"
	"third-redis-example/redis"

	"github.com/dobyte/due/v2/log"
)

func main() {
	rds := redis.Instance("default")

	if result, err := rds.Ping(context.Background()).Result(); err != nil {
		log.Errorf("redis connection error: %v", err)
	} else {
		log.Infof("redis ping result: %v", result)
	}
}
```

### 常用操作示例

```go
ctx := context.Background()
rds := redis.Instance("default")

// 设置键值对
rds.Set(ctx, "key", "value", 10*time.Minute)

// 获取值
val, err := rds.Get(ctx, "key").Result()

// 哈希操作
rds.HSet(ctx, "hash", "field1", "value1")
rds.HGet(ctx, "hash", "field1").Result()

// 列表操作
rds.LPush(ctx, "list", "item1", "item2")
rds.LRange(ctx, "list", 0, -1).Result()

// Lua 脚本
script := redis.NewScript(`return redis.call("get", KEYS[1])`)
result, _ := script.Run(ctx, rds, []string{"key"}).Result()
```

### TLS 加密连接

当配置了 `certFile`、`keyFile` 和 `caFile` 三个 TLS 参数时，会自动启用 TLS 加密连接：

```toml
[redis.secure]
    addrs = ["redis.example.com:6380"]
    certFile = "/path/to/client.crt"
    keyFile = "/path/to/client.key"
    caFile = "/path/to/ca.crt"
```

### 多实例配置

```toml
[redis.default]
    addrs = ["127.0.0.1:6379"]
    db = 0
    poolSize = 200

[redis.cache]
    addrs = ["127.0.0.1:6379"]
    db = 1
    poolSize = 100

[redis.session]
    addrs = ["127.0.0.1:6379"]
    db = 2
    poolSize = 50
```

```go
defaultRds := redis.Instance("default")
cacheRds := redis.Instance("cache")
sessionRds := redis.Instance("session")
```

## 设计要点

- **UniversalClient**：使用 `redis.UniversalClient` 统一接口，自动适配单机、哨兵、集群模式（根据 `addrs` 数量和格式）
- **连接池管理**：通过 Due 的 `pool.Factory` 管理 Redis 实例，支持按名称获取
- **TLS 支持**：使用 Due 内置的 `tls.MakeRedisTLSConfig` 工具函数创建 TLS 配置
- **泛型配置**：`NewInstance` 使用泛型，支持字符串配置路径、Config 结构体和 Config 指针三种方式
- **Script 类型导出**：导出 `Script` 类型别名，方便在业务代码中使用 Lua 脚本

## 示例项目

完整示例代码请参考：[third-redis-example](https://github.com/dobyte/due-docs/tree/master/examples/third-redis-example)

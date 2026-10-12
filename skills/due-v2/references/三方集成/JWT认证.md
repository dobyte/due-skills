# JWT 认证集成

## 概述

Due 框架通过 [dobyte/jwt](https://github.com/dobyte/jwt) 库集成 JWT（JSON Web Token）认证功能。支持 Token 生成、验证、提取载荷等操作，并提供基于 Redis 的 Token 存储后端，实现 Token 的集中管理和过期控制。

## 第三方依赖

| 库名 | 版本 | 说明 |
|------|------|------|
| [github.com/dobyte/jwt](https://github.com/dobyte/jwt) | v0.1.4 | JWT 认证库 |
| [github.com/go-redis/redis/v8](https://github.com/go-redis/redis/v8) | v8.11.5 | Redis 客户端（Token 存储后端） |

## 配置参数

### JWT 核心配置

| 名称 | 类型 | 描述 |
|------|------|------|
| `issuer` | string | JWT 发行方标识 |
| `validDuration` | int | Token 有效时长（秒），默认 7200s（2小时） |
| `secretKey` | string | 签名秘钥 KEY |
| `identityKey` | string | 身份认证 KEY（载荷中标识用户身份的字段名） |
| `locations` | string | Token 查找位置，多个位置用逗号分隔 |

### Token 存储配置（store）

| 名称 | 类型 | 描述 |
|------|------|------|
| `store.addrs` | []string | Redis 连接地址 |
| `store.db` | int | Redis 数据库号，默认为 0 |
| `store.username` | string | Redis 用户名，默认空 |
| `store.password` | string | Redis 密码，默认空 |
| `store.keyFile` | string | TLS 私钥文件路径，默认空 |
| `store.certFile` | string | TLS 证书文件路径，默认空 |
| `store.caFile` | string | TLS CA 证书文件路径，默认空 |
| `store.maxRetries` | int | 网络错误最大重试次数，默认 3 次 |
| `store.poolSize` | int | 最大连接池大小，默认 200 |
| `store.minIdleConns` | int | 最小空闲连接数，默认 10 |
| `store.dialTimeout` | string | 拨号超时时间，默认 `5s` |
| `store.idleTimeout` | string | 连接最大空闲时间，默认 `0s` |
| `store.readTimeout` | string | 读超时时间，默认 `1s` |
| `store.writeTimeout` | string | 写超时时间，默认 `1s` |

## 配置文件示例

```toml
[jwt.default]
    # jwt发行方
    issuer = "due"
    # 过期时间（秒）
    validDuration = 7200
    # 秘钥KEY
    secretKey = "xxxx"
    # 身份认证KEY
    identityKey = "uid"
    # TOKEN查找位置
    locations = "query:token,header:Authorization"
    # 存储组件
    [jwt.default.store]
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
        # 最小空闲连接数，默认10个连接
        minIdleConns = 10
        # 拨号超时时间，默认5s
        dialTimeout = "5s"
        # 连接最大空闲时间，默认0s
        idleTimeout = "0s"
        # 读超时，默认1s
        readTimeout = "1s"
        # 写超时，默认1s
        writeTimeout = "1s"
```

## Token 查找位置

`locations` 配置项定义从请求中查找 Token 的位置，支持以下格式：

- `query:参数名` — 从 URL 查询参数中获取
- `header:请求头名` — 从 HTTP 请求头中获取
- `cookie:Cookie名` — 从 Cookie 中获取

多个位置用逗号分隔，按顺序查找：

```
locations = "query:token,header:Authorization"
```

上述配置表示先查找 URL 参数 `token`，未找到则查找请求头 `Authorization`。

## 代码实现

### 1. JWT 封装（jwt/jwt.go）

```go
package jwt

import (
	"fmt"

	"github.com/dobyte/due/v2/core/pool"
	"github.com/dobyte/due/v2/etc"
	"github.com/dobyte/due/v2/log"
	"github.com/dobyte/jwt"
)

var factory = pool.NewFactory(func(name string) (*JWT, error) {
	return NewInstance(fmt.Sprintf("etc.jwt.%s", name))
})

type (
	JWT     = jwt.JWT
	Token   = jwt.Token
	Payload = jwt.Payload
)

type Config struct {
	Issuer        string       `json:"issuer"`
	SecretKey     string       `json:"secretKey"`
	IdentityKey   string       `json:"identityKey"`
	Locations     string       `json:"locations"`
	ValidDuration int          `json:"validDuration"`
	Store         *StoreConfig `json:"store"`
}

// Instance JWT实例
func Instance(name ...string) *JWT {
	var (
		err error
		ins *JWT
	)

	if len(name) == 0 {
		ins, err = factory.Get("default")
	} else {
		ins, err = factory.Get(name[0])
	}

	if err != nil {
		log.Fatalf("create jwt instance failed: %v", err)
	}

	return ins
}

// NewInstance 创建实例
func NewInstance[T string | Config | *Config](config T) (*JWT, error) {
	var (
		conf *Config
		v    any = config
	)

	switch c := v.(type) {
	case string:
		conf = &Config{
			Issuer:        etc.Get(fmt.Sprintf("%s.issuer", c)).String(),
			SecretKey:     etc.Get(fmt.Sprintf("%s.secretKey", c)).String(),
			IdentityKey:   etc.Get(fmt.Sprintf("%s.identityKey", c)).String(),
			Locations:     etc.Get(fmt.Sprintf("%s.locations", c)).String(),
			ValidDuration: etc.Get(fmt.Sprintf("%s.validDuration", c)).Int(),
		}

		if etc.Has(fmt.Sprintf("%s.store", c)) {
			conf.Store = &StoreConfig{
				Addrs:        etc.Get(fmt.Sprintf("%s.store.addrs", c)).Strings(),
				DB:           etc.Get(fmt.Sprintf("%s.store.db", c)).Int(),
				CertFile:     etc.Get(fmt.Sprintf("%s.store.certFile", c)).String(),
				KeyFile:      etc.Get(fmt.Sprintf("%s.store.keyFile", c)).String(),
				CaFile:       etc.Get(fmt.Sprintf("%s.store.caFile", c)).String(),
				Username:     etc.Get(fmt.Sprintf("%s.store.username", c)).String(),
				Password:     etc.Get(fmt.Sprintf("%s.store.password", c)).String(),
				MaxRetries:   etc.Get(fmt.Sprintf("%s.store.maxRetries", c), 3).Int(),
				PoolSize:     etc.Get(fmt.Sprintf("%s.store.poolSize", c), 200).Int(),
				MinIdleConns: etc.Get(fmt.Sprintf("%s.store.minIdleConns", c), 20).Int(),
				DialTimeout:  etc.Get(fmt.Sprintf("%s.store.dialTimeout", c), "3s").Duration(),
				IdleTimeout:  etc.Get(fmt.Sprintf("%s.store.idleTimeout", c)).Duration(),
				ReadTimeout:  etc.Get(fmt.Sprintf("%s.store.readTimeout", c), "1s").Duration(),
				WriteTimeout: etc.Get(fmt.Sprintf("%s.store.writeTimeout", c), "1s").Duration(),
			}
		}
	case Config:
		conf = &c
	case *Config:
		conf = c
	}

	opts := make([]jwt.Option, 0, 6)
	opts = append(opts, jwt.WithIssuer(conf.Issuer))
	opts = append(opts, jwt.WithIdentityKey(conf.IdentityKey))
	opts = append(opts, jwt.WithSecretKey(conf.SecretKey))
	opts = append(opts, jwt.WithValidDuration(conf.ValidDuration))
	opts = append(opts, jwt.WithLookupLocations(conf.Locations))

	if conf.Store != nil {
		store, err := NewStore(conf.Store)
		if err != nil {
			return nil, err
		}

		opts = append(opts, jwt.WithStore(store))
	}

	return jwt.NewJWT(opts...)
}
```

### 2. Redis 存储后端（jwt/store.go）

```go
package jwt

import (
	"context"
	"time"

	"github.com/dobyte/due/v2/core/tls"
	"github.com/dobyte/due/v2/utils/xconv"
	"github.com/go-redis/redis/v8"
)

type StoreConfig struct {
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

type Store struct {
	redis redis.UniversalClient
}

func NewStore(conf *StoreConfig) (*Store, error) {
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

	return &Store{redis: redis.NewUniversalClient(options)}, nil
}

func (s *Store) Get(ctx context.Context, key any) (any, error) {
	return s.redis.Get(ctx, xconv.String(key)).Result()
}

func (s *Store) Set(ctx context.Context, key any, value any, duration time.Duration) error {
	return s.redis.Set(ctx, xconv.String(key), value, duration).Err()
}

func (s *Store) Remove(ctx context.Context, keys ...any) (value any, err error) {
	list := make([]string, 0, len(keys))
	for _, key := range keys {
		list = append(list, xconv.String(key))
	}

	return s.redis.Del(ctx, list...).Result()
}
```

## 使用方式

### 生成与验证 Token

```go
package main

import (
	"third-jwt-example/jwt"

	"github.com/dobyte/due/v2/log"
)

func main() {
	ins := jwt.Instance("default")

	// 生成 Token
	token, err := ins.GenerateToken(jwt.Payload{
		ins.IdentityKey(): 1,
		"nickname":        "fuxiao",
	})
	if err != nil {
		log.Errorf("generate token error: %v", err)
	} else {
		log.Infof("generate token success: %s", token.Token)
	}

	// 提取载荷
	payload, err := ins.ExtractPayload(token.Token)
	if err != nil {
		log.Errorf("extract payload error: %v", err)
	} else {
		log.Infof("extract payload success: %v", payload)
	}
}
```

### 在 HTTP 中间件中使用

```go
func AuthMiddleware(j *jwt.JWT) func(http.Handler) http.Handler {
	return func(next http.Handler) http.Handler {
		return http.HandlerFunc(func(w http.ResponseWriter, r *http.Request) {
			token, err := j.Http().ExtractToken(r)
			if err != nil {
				http.Error(w, "unauthorized", http.StatusUnauthorized)
				return
			}

			payload, err := j.ExtractPayload(token.Token)
			if err != nil {
				http.Error(w, "invalid token", http.StatusUnauthorized)
				return
			}

			// 将用户信息注入上下文
			ctx := context.WithValue(r.Context(), "payload", payload)
			next.ServeHTTP(w, r.WithContext(ctx))
		})
	}
}
```

## 设计要点

- **Token 存储**：可选配置 Redis 存储后端，用于 Token 的集中管理和主动失效控制
- **查找位置灵活**：`locations` 支持从 query 参数、header、cookie 等多种位置查找 Token
- **身份标识**：`identityKey` 定义载荷中标识用户身份的主键字段名（如 `uid`）
- **Store 接口**：实现 `Get`、`Set`、`Remove` 三个方法，对接 Redis 存储
- **可选存储**：当未配置 `store` 时，JWT 仅做无状态验证；配置后支持服务端主动撤销 Token
- **泛型配置**：`NewInstance` 使用泛型，支持配置路径字符串、Config 结构体和指针三种方式

## 示例项目

完整示例代码请参考：[third-jwt-example](https://github.com/dobyte/due-docs/tree/master/examples/third-jwt-example)

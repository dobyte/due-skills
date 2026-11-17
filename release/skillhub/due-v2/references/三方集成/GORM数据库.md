# GORM 数据库集成

## 概述

Due 框架通过第三方库集成 GORM，提供对 MySQL 等关系型数据库的支持。GORM 是 Go 语言中最流行的 ORM 框架之一，Due 对其进行了封装，支持连接池管理、日志集成、慢查询监控等功能。

## 第三方依赖

| 库名 | 版本 | 说明 |
|------|------|------|
| [gorm.io/gorm](https://github.com/go-gorm/gorm) | v1.31.0 | GORM 核心库 |
| [gorm.io/driver/mysql](https://github.com/go-gorm/mysql) | v1.6.0 | MySQL 驱动 |

## 配置参数

| 名称 | 类型 | 描述 |
|------|------|------|
| `dsn` | string | 数据库连接串 |
| `logLevel` | string | 日志级别，可选值：`silent`、`error`、`warn`、`info` |
| `maxIdleConns` | int | 最大空闲连接数，默认为 50 |
| `maxOpenConns` | int | 最大打开连接数，默认为 50 |
| `slowThreshold` | string | 慢查询阈值，支持单位：纳秒（ns）、微秒（us 或 µs）、毫秒（ms）、秒（s）、分（m）、小时（h）、天（d）。默认 `2s` |
| `connMaxLifetime` | string | 连接最大生命周期，支持单位：纳秒（ns）、微秒（us 或 µs）、毫秒（ms）、秒（s）、分（m）、小时（h）、天（d）。默认 `1h` |

## 配置文件示例

```toml
[mysql.default]
    # dsn连接信息
    dsn = "root:123456@tcp(127.0.0.1:3306)/due_default?charset=utf8mb4&parseTime=True&loc=Local"
    # 日志级别; silent | error | warn | info
    logLevel = "info"
    # 最大空闲连接数，默认为50
    maxIdleConns = 50
    # 最大打开连接数，默认为50
    maxOpenConns = 50
    # 慢查询阈值，支持单位：纳秒（ns）、微秒（us | µs）、毫秒（ms）、秒（s）、分（m）、小时（h）、天（d）。默认2s
    slowThreshold = "2s"
    # 连接最大生命周期，支持单位：纳秒（ns）、微秒（us | µs）、毫秒（ms）、秒（s）、分（m）、小时（h）、天（d）。默认1h
    connMaxLifetime = "1h"
```

## 代码实现

### 1. 核心封装（gorm/mysql.go）

```go
package gorm

import (
	"fmt"
	"strings"
	"time"

	_ "third-gorm-example/gorm/serializer"

	"github.com/dobyte/due/v2/core/pool"
	"github.com/dobyte/due/v2/etc"
	"github.com/dobyte/due/v2/log"
	"gorm.io/driver/mysql"
	"gorm.io/gorm"
	loggers "gorm.io/gorm/logger"
)

var factory = pool.NewFactory(func(name string) (*gorm.DB, error) {
	return NewInstance(fmt.Sprintf("etc.mysql.%s", name))
})

type Config struct {
	DSN             string        `json:"dsn"`
	LogLevel        string        `json:"logLevel"`
	MaxIdleConns    int           `json:"maxIdleConns"`
	MaxOpenConns    int           `json:"maxOpenConns"`
	SlowThreshold   time.Duration `json:"slowThreshold"`
	ConnMaxLifetime time.Duration `json:"connMaxLifetime"`
}

// Instance 获取实例
func Instance(name ...string) *gorm.DB {
	var (
		err error
		ins *gorm.DB
	)

	if len(name) == 0 {
		ins, err = factory.Get("default")
	} else {
		ins, err = factory.Get(name[0])
	}

	if err != nil {
		log.Fatalf("create mysql instance failed: %v", err)
	}

	return ins
}

// NewInstance 新建实例
func NewInstance[T string | Config | *Config](config T) (*gorm.DB, error) {
	var (
		conf *Config
		v    any = config
	)

	switch c := v.(type) {
	case string:
		conf = &Config{
			DSN:             etc.Get(fmt.Sprintf("%s.dsn", c)).String(),
			LogLevel:        etc.Get(fmt.Sprintf("%s.logLevel", c)).String(),
			MaxIdleConns:    etc.Get(fmt.Sprintf("%s.maxIdleConns", c)).Int(),
			MaxOpenConns:    etc.Get(fmt.Sprintf("%s.maxOpenConns", c)).Int(),
			SlowThreshold:   etc.Get(fmt.Sprintf("%s.slowThreshold", c), "2s").Duration(),
			ConnMaxLifetime: etc.Get(fmt.Sprintf("%s.connMaxLifetime", c), "1h").Duration(),
		}
	case Config:
		conf = &c
	case *Config:
		conf = c
	}

	var logLevel loggers.LogLevel
	switch strings.ToLower(conf.LogLevel) {
	case "silent":
		logLevel = loggers.Silent
	case "error":
		logLevel = loggers.Error
	case "warn":
		logLevel = loggers.Warn
	case "info":
		logLevel = loggers.Info
	default:
		logLevel = loggers.Warn
	}

	db, err := gorm.Open(mysql.New(mysql.Config{
		DSN: conf.DSN,
	}), &gorm.Config{Logger: &logger{
		logLevel:                  logLevel,
		ignoreRecordNotFoundError: true,
		slowThreshold:             conf.SlowThreshold,
	}})
	if err != nil {
		return nil, err
	}

	database, err := db.DB()
	if err != nil {
		return nil, err
	}

	if conf.MaxIdleConns > 0 {
		database.SetMaxIdleConns(conf.MaxIdleConns)
	}

	if conf.MaxOpenConns > 0 {
		database.SetMaxOpenConns(conf.MaxOpenConns)
	}

	if conf.ConnMaxLifetime > 0 {
		database.SetConnMaxLifetime(conf.ConnMaxLifetime)
	}

	return db, nil
}
```

### 2. 日志适配器（gorm/logger.go）

GORM 日志适配器将 GORM 的日志输出集成到 Due 的日志系统中，支持：

- **SQL 执行追踪**：记录每条 SQL 的执行时间、影响行数和具体 SQL 语句
- **慢查询告警**：超过 `slowThreshold` 阈值的 SQL 会被标记为 SLOW SQL 并以 Warn 级别输出
- **错误记录**：SQL 执行错误会以 Error 级别输出（可选择忽略 RecordNotFound 错误）
- **日志级别控制**：支持 Silent、Error、Warn、Info 四个级别

```go
package gorm

import (
	"context"
	"fmt"
	"time"

	"github.com/dobyte/due/v2/errors"
	"github.com/dobyte/due/v2/log"
	loggers "gorm.io/gorm/logger"
)

const traceStr = "%s\n[%.3fms] [rows:%v] %s"

type logger struct {
	logLevel                  loggers.LogLevel
	ignoreRecordNotFoundError bool
	slowThreshold             time.Duration
}

var _ loggers.Interface = &logger{}

func (l *logger) LogMode(level loggers.LogLevel) loggers.Interface {
	newLogger := *l
	newLogger.logLevel = level
	return &newLogger
}

func (l *logger) Info(ctx context.Context, msg string, data ...any) {
	if l.logLevel >= loggers.Info {
		log.Printf(log.LevelInfo, msg, data)
	}
}

func (l *logger) Warn(ctx context.Context, msg string, data ...any) {
	if l.logLevel >= loggers.Warn {
		log.Printf(log.LevelWarn, msg, data)
	}
}

func (l *logger) Error(ctx context.Context, msg string, data ...any) {
	if l.logLevel >= loggers.Error {
		log.Printf(log.LevelError, msg, data)
	}
}

// Trace print sql message
func (l *logger) Trace(ctx context.Context, begin time.Time, fc func() (string, int64), err error) {
	if l.logLevel <= loggers.Silent {
		return
	}

	switch elapsed := time.Since(begin); {
	case err != nil && l.logLevel >= loggers.Error && (!errors.Is(err, loggers.ErrRecordNotFound) || !l.ignoreRecordNotFoundError):
		sql, rows := fc()
		if rows == -1 {
			log.Printf(log.LevelError, traceStr, err, float64(elapsed.Nanoseconds())/1e6, "-", sql)
		} else {
			log.Printf(log.LevelError, traceStr, err, float64(elapsed.Nanoseconds())/1e6, rows, sql)
		}
	case elapsed > l.slowThreshold && l.slowThreshold != 0 && l.logLevel >= loggers.Error:
		sql, rows := fc()
		slowLog := fmt.Sprintf("SLOW SQL >= %v", l.slowThreshold)
		if rows == -1 {
			log.Printf(log.LevelWarn, traceStr, slowLog, float64(elapsed.Nanoseconds())/1e6, "-", sql)
		} else {
			log.Printf(log.LevelWarn, traceStr, slowLog, float64(elapsed.Nanoseconds())/1e6, rows, sql)
		}
	case l.logLevel == loggers.Info:
		sql, rows := fc()
		if rows == -1 {
			log.Printf(log.LevelInfo, traceStr, "", float64(elapsed.Nanoseconds())/1e6, "-", sql)
		} else {
			log.Printf(log.LevelInfo, traceStr, "", float64(elapsed.Nanoseconds())/1e6, rows, sql)
		}
	}
}
```

### 3. JSON 序列化器（gorm/serializer/json.go）

自定义 JSON 序列化器，使用 Due 框架内置的 JSON 编码器替代 GORM 默认的序列化方式：

```go
package serializer

import (
	"context"
	"reflect"

	"github.com/dobyte/due/v2/encoding/json"
	"gorm.io/gorm/schema"
)

func init() {
	schema.RegisterSerializer("json", JSONSerializer{})
}

type JSONSerializer struct {
}

// Scan implements serializer interface
func (JSONSerializer) Scan(ctx context.Context, field *schema.Field, dst reflect.Value, dbValue any) (err error) {
	fieldValue := reflect.New(field.FieldType)

	if dbValue != nil {
		var bytes []byte
		switch v := dbValue.(type) {
		case []byte:
			bytes = v
		case string:
			bytes = []byte(v)
		default:
			bytes, err = json.Marshal(v)
			if err != nil {
				return err
			}
		}

		if len(bytes) > 0 {
			err = json.Unmarshal(bytes, fieldValue.Interface())
		}
	}

	field.ReflectValueOf(ctx, dst).Set(fieldValue.Elem())
	return
}

// Value implements serializer interface
func (JSONSerializer) Value(ctx context.Context, field *schema.Field, dst reflect.Value, fieldValue any) (any, error) {
	result, err := json.Marshal(fieldValue)
	if err != nil {
		return "", err
	}

	if string(result) == "null" {
		switch field.FieldType.Kind() {
		case reflect.Array, reflect.Slice:
			return "[]", nil
		default:
			return "{}", nil
		}
	}

	return string(result), nil
}
```

## 使用方式

### 获取数据库实例

```go
package main

import (
	gormcomp "third-gorm-example/gorm"

	"github.com/dobyte/due/v2/log"
	"gorm.io/gorm"
)

func main() {
	// 获取默认实例
	db := gormcomp.Instance("default")

	// 使用事务
	if err := db.Connection(func(tx *gorm.DB) error {
		return nil
	}); err != nil {
		log.Errorf("db connection error: %v", err)
	}
}
```

### 多实例配置

可以在配置文件中定义多个 MySQL 实例：

```toml
[mysql.default]
    dsn = "root:123456@tcp(127.0.0.1:3306)/due_default?charset=utf8mb4&parseTime=True&loc=Local"
    logLevel = "info"
    maxIdleConns = 50
    maxOpenConns = 50
    slowThreshold = "2s"
    connMaxLifetime = "1h"

[mysql.secondary]
    dsn = "root:123456@tcp(127.0.0.1:3306)/due_secondary?charset=utf8mb4&parseTime=True&loc=Local"
    logLevel = "warn"
    maxIdleConns = 20
    maxOpenConns = 30
    slowThreshold = "1s"
    connMaxLifetime = "30m"
```

使用时通过名称获取对应实例：

```go
defaultDB := gormcomp.Instance("default")
secondaryDB := gormcomp.Instance("secondary")
```

## 设计要点

- **连接池管理**：使用 Due 的 `pool.Factory` 管理 GORM 实例，支持按名称获取不同数据库实例
- **泛型配置**：`NewInstance` 使用泛型，支持字符串（配置路径）、Config 结构体、Config 指针三种配置方式
- **日志集成**：自定义 Logger 将 GORM 的 SQL 日志桥接到 Due 的日志系统
- **慢查询监控**：可配置慢查询阈值，超时 SQL 以 Warn 级别输出
- **JSON 序列化**：自定义序列化器使用 Due 内置的 JSON 编码器，保持框架一致性
- **RecordNotFound 过滤**：可选择忽略记录未找到的错误，避免日志噪音

## 示例项目

完整示例代码请参考：[third-gorm-example](https://github.com/dobyte/due-docs/tree/master/examples/third-gorm-example)

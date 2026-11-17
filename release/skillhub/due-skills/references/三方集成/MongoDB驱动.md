# MongoDB 驱动集成

## 概述

Due 框架通过官方 MongoDB Go Driver 集成 MongoDB 支持。封装层提供连接管理和多实例支持，通过 Due 的 `pool.Factory` 实现按名称获取 MongoDB 客户端实例。

## 第三方依赖

| 库名 | 版本 | 说明 |
|------|------|------|
| [go.mongodb.org/mongo-driver](https://github.com/mongodb/mongo-go-driver) | v1.17.4 | MongoDB 官方 Go 驱动 |

## 配置参数

| 名称 | 类型 | 描述 |
|------|------|------|
| `dsn` | string | MongoDB 连接串（URI 格式） |

## 配置文件示例

```toml
[mongo.default]
    # 连接串
    dsn = "mongodb://root:***@127.0.0.1:27017"
```

### 连接串格式说明

MongoDB 连接串遵循标准 URI 格式：

```
mongodb://[username:password@]host1[:port1][,...hostN[:portN]][/[database][?options]]
```

常见示例：

```
# 单机连接
mongodb://127.0.0.1:27017

# 带认证
mongodb://root:password@127.0.0.1:27017

# 指定数据库
mongodb://root:password@127.0.0.1:27017/mydb

# 副本集
mongodb://host1:27017,host2:27017,host3:27017/?replicaSet=myReplicaSet

# 带连接参数
mongodb://root:password@127.0.0.1:27017/?maxPoolSize=100&connectTimeoutMS=5000
```

## 代码实现

### 核心封装（mongo/mongo.go）

```go
package mongo

import (
	"context"
	"fmt"
	"log"

	"github.com/dobyte/due/v2/core/pool"
	"github.com/dobyte/due/v2/etc"
	"go.mongodb.org/mongo-driver/mongo"
	"go.mongodb.org/mongo-driver/mongo/options"
)

var factory = pool.NewFactory(func(name string) (*Client, error) {
	return NewInstance(fmt.Sprintf("etc.mongo.%s", name))
})

type (
	Client = mongo.Client
)

type Config struct {
	DSN string `json:"dsn"` // 连接串
}

// Instance 获取实例
func Instance(name ...string) *Client {
	var (
		err error
		ins *Client
	)

	if len(name) == 0 {
		ins, err = factory.Get("default")
	} else {
		ins, err = factory.Get(name[0])
	}

	if err != nil {
		log.Fatalf("create mongo instance failed: %v", err)
	}

	return ins
}

// NewInstance 新建实例
func NewInstance[T string | Config | *Config](config T) (*Client, error) {
	var (
		conf *Config
		v    any = config
		ctx      = context.Background()
	)

	switch c := v.(type) {
	case string:
		conf = &Config{DSN: etc.Get(fmt.Sprintf("%s.dsn", c)).String()}
	case Config:
		conf = &c
	case *Config:
		conf = c
	}

	opts := options.Client().ApplyURI(conf.DSN)

	client, err := mongo.Connect(ctx, opts)
	if err != nil {
		return nil, err
	}

	return client, nil
}
```

## 使用方式

### 连接测试

```go
package main

import (
	"context"
	"third-mongo-example/mongo"

	"github.com/dobyte/due/v2/log"
	"go.mongodb.org/mongo-driver/mongo/readpref"
)

func main() {
	client := mongo.Instance("default")

	if err := client.Ping(context.Background(), readpref.Primary()); err != nil {
		log.Errorf("mongo connection error: %v", err)
	} else {
		log.Infof("mongo connection success")
	}
}
```

### CRUD 操作示例

```go
ctx := context.Background()
client := mongo.Instance("default")

// 获取集合
collection := client.Database("mydb").Collection("users")

// 插入文档
result, err := collection.InsertOne(ctx, bson.M{
	"name":  "张三",
	"age":   28,
	"email": "zhangsan@example.com",
})
insertedID := result.InsertedID

// 查询文档
var user bson.M
err = collection.FindOne(ctx, bson.M{"name": "张三"}).Decode(&user)

// 更新文档
filter := bson.M{"name": "张三"}
update := bson.M{"$set": bson.M{"age": 29}}
collection.UpdateOne(ctx, filter, update)

// 删除文档
collection.DeleteOne(ctx, bson.M{"name": "张三"})

// 批量查询
cursor, err := collection.Find(ctx, bson.M{"age": bson.M{"$gt": 25}})
defer cursor.Close(ctx)
var users []bson.M
cursor.All(ctx, &users)
```

### 多实例配置

```toml
[mongo.default]
    dsn = "mongodb://root:password@127.0.0.1:27017"

[mongo.analytics]
    dsn = "mongodb://analytics:password@192.168.1.100:27017"
```

```go
defaultClient := mongo.Instance("default")
analyticsClient := mongo.Instance("analytics")
```

## 设计要点

- **轻量封装**：MongoDB 配置简洁，仅需 DSN 连接串，驱动本身提供了丰富的 URI 参数支持
- **连接池管理**：使用 Due 的 `pool.Factory` 管理 MongoDB 客户端实例
- **泛型配置**：`NewInstance` 使用泛型，支持字符串配置路径、Config 结构体和 Config 指针
- **Client 类型导出**：导出 `Client` 类型别名，方便在业务代码中直接使用
- **标准 URI**：所有连接参数通过 DSN URI 传递，充分利用 MongoDB 驱动的内置能力

## 示例项目

完整示例代码请参考：[third-mongo-example](https://github.com/dobyte/due-docs/tree/master/examples/third-mongo-example)

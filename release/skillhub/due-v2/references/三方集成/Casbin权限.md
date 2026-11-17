# Casbin 权限管理集成

## 概述

Due 框架通过 [dobyte/gorm-casbin](https://github.com/dobyte/gorm-casbin) 库集成 Casbin 权限管理框架。Casbin 是一个强大的访问控制库，支持 ACL、RBAC、ABAC 等多种权限模型。Due 的集成方案使用 GORM + MySQL 作为策略存储后端，支持策略的持久化和自动加载。

## 第三方依赖

| 库名 | 版本 | 说明 |
|------|------|------|
| [gorm.io/gorm](https://github.com/go-gorm/gorm) | v1.31.0 | GORM ORM 框架 |
| [gorm.io/driver/mysql](https://github.com/go-gorm/mysql) | v1.6.0 | MySQL 驱动 |
| [github.com/dobyte/gorm-casbin](https://github.com/dobyte/gorm-casbin) | v0.0.2 | GORM Casbin 适配器 |

## 配置参数

| 名称 | 类型 | 描述 |
|------|------|------|
| `dsn` | string | MySQL 数据库连接串 |
| `table` | string | 存储权限策略的数据库表名称 |
| `model` | string | Casbin 模型配置文件路径 |

## 配置文件示例

```toml
[casbin.default]
    # dsn连接信息
    dsn = "root:123456@tcp(127.0.0.1:3306)/due_admin?charset=utf8mb4&parseTime=True&loc=Local"
    # casbin策略表
    table = "casbin_policy"
    # casbin权限模型
    model = "./resource/model.conf"
```

## Casbin 模型配置

模型文件定义了权限系统的核心规则，包括请求定义、策略定义、角色定义、策略效果和匹配器。

### 模型文件示例（resource/model.conf）

```conf
[request_definition]
r = sub, obj

[policy_definition]
p = sub, obj

[role_definition]
g = _, _

[policy_effect]
e = some(where (p.eft == allow))

[matchers]
m = g(r.sub, p.sub) == true && keyMatch2(r.obj, p.obj) == true || r.sub == "1"
```

### 模型配置说明

| 部分 | 说明 |
|------|------|
| `request_definition` | 定义权限请求的参数格式。`r = sub, obj` 表示请求包含主体（sub）和对象（obj） |
| `policy_definition` | 定义策略规则的字段。`p = sub, obj` 表示策略包含主体和对象 |
| `role_definition` | 定义角色继承关系。`g = _, _` 表示支持用户到角色的映射 |
| `policy_effect` | 定义策略效果。`some(where (p.eft == allow))` 表示只要有一条策略允许即通过 |
| `matchers` | 定义匹配规则，支持多种内置函数 |

### 常用匹配函数

| 函数 | 说明 | 示例 |
|------|------|------|
| `keyMatch2` | URL 路径匹配（支持 `:param`） | `keyMatch2("/users/123", "/users/:id")` → true |
| `keyMatch` | URL 路径匹配（支持 `*`） | `keyMatch("/users/123", "/users/*")` → true |
| `regexMatch` | 正则表达式匹配 | `regexMatch("/users/123", "/users/\\d+")` → true |
| `globMatch` | Glob 模式匹配 | `globMatch("/users/123", "/users/*")` → true |

## 代码实现

### 核心封装（casbin/casbin.go）

```go
package casbin

import (
	"fmt"
	"log"

	"github.com/dobyte/due/v2/core/pool"
	"github.com/dobyte/due/v2/etc"
	casbin "github.com/dobyte/gorm-casbin"
	"gorm.io/driver/mysql"
	"gorm.io/gorm"
)

var factory = pool.NewFactory(func(name string) (*Enforcer, error) {
	return NewInstance(fmt.Sprintf("etc.casbin.%s", name))
})

type Enforcer = casbin.Enforcer

type Config struct {
	DSN   string `json:"dsn"`
	Table string `json:"table"`
	Model string `json:"model"`
}

// Instance 获取实例
func Instance(name ...string) *Enforcer {
	var (
		err error
		ins *Enforcer
	)

	if len(name) == 0 {
		ins, err = factory.Get("default")
	} else {
		ins, err = factory.Get(name[0])
	}

	if err != nil {
		log.Fatalf("create casbin instance failed: %v", err)
	}

	return ins
}

// NewInstance 新建实例
func NewInstance[T string | Config | *Config](config T) (*Enforcer, error) {
	var (
		conf *Config
		v    any = config
	)

	switch c := v.(type) {
	case string:
		conf = &Config{
			DSN:   etc.Get(fmt.Sprintf("%s.dsn", c)).String(),
			Table: etc.Get(fmt.Sprintf("%s.table", c)).String(),
			Model: etc.Get(fmt.Sprintf("%s.model", c)).String(),
		}
	case Config:
		conf = &c
	case *Config:
		conf = c
	}

	db, err := gorm.Open(mysql.New(mysql.Config{
		DSN: conf.DSN,
	}))
	if err != nil {
		return nil, err
	}

	return casbin.NewEnforcer(&casbin.Options{
		Model:    conf.Model,
		Enable:   true,
		Autoload: true,
		Table:    conf.Table,
		Database: db,
	})
}
```

### Enforcer 初始化参数

`casbin.NewEnforcer` 接收以下选项：

| 参数 | 说明 |
|------|------|
| `Model` | 模型配置文件路径 |
| `Enable` | 是否启用权限检查（设为 `true`） |
| `Autoload` | 是否自动加载策略（设为 `true`） |
| `Table` | 策略存储的数据库表名 |
| `Database` | GORM 数据库实例 |

## 使用方式

### 基本使用

```go
package main

import (
	casbincomp "third-casbin-example/casbin"

	"github.com/dobyte/due/v2/log"
)

func main() {
	enforcer := casbincomp.Instance("default")

	// 为角色添加权限节点
	ok, err := enforcer.AddPolicy("role_1", "node_1")
	if err != nil {
		log.Fatalf("Add policy exception: %s\n", err.Error())
	}

	if ok {
		log.Info("Add policy successful")
	} else {
		log.Info("Add policy failure")
	}
}
```

### 常用 API

```go
enforcer := casbincomp.Instance("default")

// 添加策略规则
enforcer.AddPolicy("admin", "/api/users")

// 删除策略规则
enforcer.RemovePolicy("admin", "/api/users")

// 为用户分配角色
enforcer.AddGroupingPolicy("user_1", "admin")

// 检查权限
allowed, _ := enforcer.Enforce("user_1", "/api/users")
if allowed {
    // 允许访问
}

// 获取用户的所有角色
roles, _ := enforcer.GetRolesForUser("user_1")

// 获取角色的所有权限
permissions, _ := enforcer.GetPermissionsForUser("admin")

// 批量添加策略
enforcer.AddPolicies([][]string{
    {"role_1", "node_1"},
    {"role_1", "node_2"},
    {"role_2", "node_3"},
})
```

### RBAC 权限模型示例

上述模型配置实现了一个 RBAC（基于角色的访问控制）系统：

- **用户** 通过 `g(r.sub, p.sub)` 关联到 **角色**
- **角色** 通过策略规则关联到 **资源节点**
- 使用 `keyMatch2` 进行 URL 路径匹配
- 用户 ID 为 `"1"` 的用户拥有超级管理员权限（`r.sub == "1"`）

### 在 HTTP 中间件中使用

```go
func CasbinMiddleware(enforcer *casbin.Enforcer) func(http.Handler) http.Handler {
	return func(next http.Handler) http.Handler {
		return http.HandlerFunc(func(w http.ResponseWriter, r *http.Request) {
			// 从上下文获取用户ID
			userID := getUserIDFromContext(r)
			path := r.URL.Path

			allowed, err := enforcer.Enforce(userID, path)
			if err != nil {
				http.Error(w, "internal error", http.StatusInternalServerError)
				return
			}

			if !allowed {
				http.Error(w, "forbidden", http.StatusForbidden)
				return
			}

			next.ServeHTTP(w, r)
		})
	}
}
```

## 设计要点

- **GORM 存储后端**：使用 MySQL 持久化存储策略规则，支持多实例共享策略数据
- **自动加载**：`Autoload: true` 确保策略规则在启动时自动从数据库加载
- **模型驱动**：通过 `.conf` 文件定义权限模型，支持灵活修改而无需改代码
- **连接池管理**：使用 Due 的 `pool.Factory` 管理 Casbin 实例
- **泛型配置**：`NewInstance` 使用泛型，支持配置路径、Config 结构体和指针三种方式
- **Enforcer 类型导出**：导出 `Enforcer` 类型别名，直接使用 Casbin 的所有 API

## 示例项目

完整示例代码请参考：[third-casbin-example](https://github.com/dobyte/due-docs/tree/master/examples/third-casbin-example)

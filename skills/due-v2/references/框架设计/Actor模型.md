# Actor 模型

## 概述

Due v2 框架提供了独特的 Actor 并发模型，将并发执行的任务封装为独立的 Actor 实体，每个 Actor 拥有自己的状态和行为，Actor 之间通过消息传递通信而非直接共享内存，从根本上避免数据竞争。

Due 的 Actor 模型不仅提供基于查找（`ctx.Actor()`）的传统手动消息分发功能，还提供通过 `ctx.BindActor()` 绑定用户（UID）与 Actor 的自动消息分发功能。

## 基本概念

### Actor

Actor 是并发编程中的独立实体，具有以下特征：
- 拥有独立的状态和行为
- 通过消息传递与其他 Actor 通信
- 内部消息严格按顺序处理
- 不共享内存，天然避免数据竞争

### Processor（处理器）

每个 Actor 关联一个 Processor。Processor 接口只定义三个生命周期回调，自定义处理器通常嵌入 `node.BaseProcessor` 以省略不需要实现的回调：

```go
type Processor interface {
    Init()    // 初始化回调
    Start()   // 启动回调
    Destroy() // 销毁回调
}
```

在 `Init()` 中通过 `actor.AddRouteHandler()` 为 Actor 注册消息路由：

```go
type roomProcessor struct {
    node.BaseProcessor
    actor *node.Actor
    room  *room
}

func newRoomProcessor(actor *node.Actor, args ...any) node.Processor {
    return &roomProcessor{
        actor: actor,
        room:  args[0].(*room),
    }
}

func (p *roomProcessor) Init() {
    p.actor.AddRouteHandler(route.Join, p.join)
    p.actor.AddRouteHandler(route.Play, p.play)
}
```

## 核心特点

- **数据隔离：** 每个 Actor 拥有独立状态，无共享内存
- **消息传递：** Actor 间通过消息通信，避免锁竞争
- **顺序保证：** 单个 Actor 内部消息严格按顺序处理
- **自动分发：** 通过 BindActor 绑定 UID 后，消息自动路由到对应 Actor
- **手动分发：** 通过 ctx.Actor() 查找 Actor 后手动投递消息

## 适用场景

- 避免数据竞争的高并发场景
- 房间类游戏（棋牌、对战）
- 帧同步游戏
- 状态同步游戏
- 需要维护独立状态实体的场景

## 核心 API

### 创建 Actor（Spawn）

通过 `proxy.Spawn()`（也可用 `ctx.Spawn()`、`actor.Spawn()`）创建 Actor 实例。第一个参数是 `Creator`，签名为 `func(actor *Actor, args ...any) Processor`，用于创建 Actor 的处理器；后续是可变参数 `ActorOption`：

```go
actor, err := proxy.Spawn(
    newRoomProcessor,                          // Processor 构造函数
    node.WithActorKind(roomActor),              // Actor 类型标识（必填）
    node.WithActorID(xconv.String(room.id)),   // Actor ID（必填）
    node.WithActorArgs(room),                   // 传递给 Processor 的参数
)
```

常用 `ActorOption`：

| 选项 | 说明 |
|------|------|
| `WithActorKind(kind string)` | 设置 Actor 类型（必填） |
| `WithActorID(id string)` | 设置 Actor ID（必填） |
| `WithActorArgs(args ...any)` | 设置传递给 Creator 的参数 |
| `WithActorNonWait()` | 节点关闭时不等候该 Actor |
| `WithActorNonDispatch()` | 该 Actor 不参与调度器的消息分发 |
| `WithActorTaskQueueSize(size int32)` | 设置任务队列容量 |
| `WithActorTaskWriteTimeout(timeout time.Duration)` | 设置任务写入超时 |
| `WithActorMessageQueueSize(size int32)` | 设置消息队列容量 |
| `WithActorMessageWriteTimeout(timeout time.Duration)` | 设置消息写入超时 |

Actor 的类型（kind）与 ID 组合唯一，重复创建会返回错误。

### 绑定 Actor（BindActor）

将当前用户（UID）绑定到指定 Actor，后续该用户的有状态消息自动分发到此 Actor：

```go
if err = ctx.BindActor(actor.Kind(), actor.ID()); err != nil {
    log.Errorf("bind actor failed: %v", err)
}
```

### 解绑 Actor（UnbindActor）

解除用户与 Actor 的绑定关系：

```go
ctx.UnbindActor(actor.Kind())
```

### 查找 Actor（ctx.Actor）

通过类型和 ID 查找 Actor：

```go
actor, ok := ctx.Actor(roomActor, xconv.String(req.RoomID))
if !ok {
    res.Code = codes.NotFound.Code()
    return
}
```

### 消息投递（actor.Next）

将上下文消息投递到指定 Actor 处理：

```go
actor.Next(ctx)
```

### 销毁 Actor（actor.Destroy / ctx.Kill）

销毁 Actor 实例并释放资源，`actor.Destroy()` 返回是否销毁成功；也可以按类型和 ID 通过 `ctx.Kill()`（或 `proxy.Kill()`）销毁：

```go
actor.Destroy()

ok := ctx.Kill(roomActor, xconv.String(roomID))
```

### Actor 内的线程安全调用（Invoke / AfterFunc / AfterInvoke）

在 Actor 处理器内调用 `ctx.Invoke()` / `ctx.AfterFunc()` / `ctx.AfterInvoke()` 时，会自动转发到当前 Actor 的对应方法，把函数写入 Actor 的任务队列串行执行，从而保证线程安全；在全局处理器中则转发到 `proxy`：

```go
// Actor 处理器内：函数被投递到该 Actor 的任务队列，串行执行
if err := ctx.Invoke(func() {
    // 安全地修改 Actor 内部状态
}, true); err != nil { // 第二个参数为 true 时同步等待执行完成，默认非阻塞
    log.Errorf("invoke failed: %v", err)
}

// 延时调用，同样在 Actor 内串行执行
timer, err := ctx.AfterInvoke(time.Second, func() {
    // ...
})
```

`proxy.Invoke()`、`actor.Invoke()` 等也提供了对应的线程安全调用入口；`actor.AfterFunc()` 只是延时执行、不保证与 Actor 内部状态串行，`actor.AfterInvoke()` 则经任务队列串行执行。

### Actor 生命周期

Actor 由 `spawn` 创建后即处于 started 状态，只有一个 dispatch 协程串行消费它的消息队列与任务队列；调用 `Destroy()` / `Kill()` 会将其置为 destroyed，解绑所有绑定的用户、关闭队列并回调 `Processor.Destroy()`。Actor 没有单独的“空闲”状态——空闲时其 dispatch 协程只是阻塞等待队列。默认情况下节点关闭会等待其 Actor 结束，可用 `WithActorNonWait()` 让节点不再等候；`WithActorNonDispatch()` 创建的 Actor 不参与调度器的消息分发。

## 消息路由模式

### 有状态路由（StatefulRoute）

`node.StatefulRoute` 保证消息被网关路由到用户所绑定的节点服（依赖 `ctx.BindNode()` 建立的绑定）。到达节点服后，处理器调用 `ctx.Next()` 触发调度器的二次分发：调度器根据路由号找到注册了该路由的 Actor 类型，再根据当前 UID 找到与之绑定的 Actor（由 `ctx.BindActor()` 建立），最终把消息投递到该 Actor 的消息队列串行处理：

```go
group.AddRouteHandler(route.Play, c.play, node.StatefulRoute)
```

处理器中通过 `ctx.Next()` 将消息交给调度器分发给 Actor：

```go
func (c *core) play(ctx node.Context) {
    res := &base.Res{}
    ctx.Defer(func() {
        if err := ctx.Response(res); err != nil {
            log.Errorf("response message failed: %v", err)
        }
    })

    if err := ctx.Next(); err != nil {
        log.Errorf("request next failed: uid = %v route = %v err = %v", ctx.UID(), ctx.Route(), err)
        res.Code = codes.IllegalRequest.Code()
    }
}
```

可见 Actor 的分发依赖两个条件：Actor 在 `Init()` 中通过 `actor.AddRouteHandler()` 注册了对应路由号，且当前用户通过 `ctx.BindActor()` 绑定到了该 Actor。

### 已认证路由（AuthorizedRoute）

消息跨集群流转（客户端 → 网关 → 节点）时必须携带 UID，否则无法投递；网关可据此提前拦截未认证连接：

```go
group.AddRouteHandler(route.Create, c.create, node.AuthorizedRoute)
```

## 完整示例

### 项目初始化

```bash
mkdir actor-example
cd actor-example
go mod init actor-example
go get github.com/dobyte/due/v2@v2.6.2
go get github.com/dobyte/due/locate/redis/v2
go get github.com/dobyte/due/registry/consul/v2
```

### 路由定义

```go
package route

const (
    Login  = 1 // 登录
    Create = 2 // 创建房间
    Join   = 3 // 加入房间
    Play   = 4 // 游戏操作
)
```

### 核心逻辑（部分）

```go
func (c *core) Init() {
    c.proxy.Router().Group(func(group *node.RouterGroup) {
        group.AddRouteHandler(route.Login, c.login)
        group.Middleware(middleware.Auth)
        group.AddRouteHandler(route.Create, c.create, node.AuthorizedRoute)
        group.AddRouteHandler(route.Join, c.join, node.AuthorizedRoute)
        group.AddRouteHandler(route.Play, c.play, node.StatefulRoute)
    })
}

// 创建房间：Spawn Actor + BindActor + BindNode
func (c *core) doCreate(ctx node.Context, req *createReq) (*room, error) {
    r := newRoom(int64(len(c.rooms)+1), req.Name, ctx.UID())

    actor, err := c.proxy.Spawn(
        newRoomProcessor,
        node.WithActorID(xconv.String(r.id)),
        node.WithActorArgs(r),
        node.WithActorKind(roomActor),
    )
    if err != nil {
        return nil, errors.NewError(err, codes.InternalError)
    }

    if err = ctx.BindActor(actor.Kind(), actor.ID()); err != nil {
        actor.Destroy()
        return nil, errors.NewError(err, codes.InternalError)
    }

    if err = ctx.BindNode(); err != nil {
        ctx.UnbindActor(actor.Kind())
        actor.Destroy()
        return nil, errors.NewError(err, codes.InternalError)
    }

    c.rooms[r.id] = r
    return r, nil
}

// 加入房间：通过 ctx.Actor 查找 Actor，然后 actor.Next(ctx) 投递消息
func (c *core) join(ctx node.Context) {
    req := &joinReq{}
    res := &joinRes{}
    ctx.Defer(func() {
        if err := ctx.Response(res); err != nil {
            log.Errorf("response message failed: %v", err)
        }
    })

    if err := ctx.Parse(req); err != nil {
        res.Code = codes.InternalError.Code()
        return
    }

    actor, ok := ctx.Actor(roomActor, xconv.String(req.RoomID))
    if !ok {
        res.Code = codes.NotFound.Code()
        return
    }

    actor.Next(ctx)
}
```

### Actor Processor 实现

```go
type roomProcessor struct {
    node.BaseProcessor
    actor *node.Actor
    room  *room
}

func (p *roomProcessor) Init() {
    p.actor.AddRouteHandler(route.Join, p.join)
    p.actor.AddRouteHandler(route.Play, p.play)
}

func (p *roomProcessor) join(ctx node.Context) {
    res := &joinRes{}
    ctx.Defer(func() {
        if err := ctx.Response(res); err != nil {
            log.Errorf("response message failed: %v", err)
        }
    })

    if err := p.room.doJoin(ctx); err != nil {
        res.Code = codes.Convert(err).Code()
        return
    }

    res.Code = codes.OK.Code()
}

func (p *roomProcessor) play(ctx node.Context) {
    req := &playReq{}
    res := &playRes{}
    ctx.Defer(func() {
        if err := ctx.Response(res); err != nil {
            log.Errorf("response message failed: %v", err)
        }
    })

    if err := ctx.Parse(req); err != nil {
        res.Code = codes.InternalError.Code()
        return
    }

    if err := p.room.doPlay(ctx, req); err != nil {
        res.Code = codes.Convert(err).Code()
        return
    }

    res.Code = codes.OK.Code()
}
```

## 多节点注意事项

多节点场景下，需要借助共享存储（如 Redis）来存储房间信息，以便能够通过房间 ID 找到对应房间所在的节点，并将消息转发至对应节点服进行处理。

## 与其他模型的对比

| 特性 | 单线程模型 | 多协程模型 | Actor 模型 |
|------|-----------|-----------|-----------|
| 执行顺序 | 严格有序 | 无序 | Actor 内有序 |
| 并发安全 | 天然安全 | 需同步原语 | 天然安全 |
| 阻塞影响 | 阻塞分发协程 | 仅阻塞当前协程 | 仅阻塞当前 Actor |
| 适用场景 | 帧同步/状态同步 | IO 密集型 | 房间类游戏 |
| 实现复杂度 | 低 | 中 | 中高 |

## 源码参考

完整示例代码：[actor-example](https://github.com/dobyte/due-docs/tree/master/examples/actor-example)

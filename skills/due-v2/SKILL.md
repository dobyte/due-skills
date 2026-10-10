---
name: due-v2
description: Due v2 高性能分布式游戏服务器框架完整开发指南。涵盖框架设计(架构、协议、路由、并发模型、滚动更新)、核心模块(网络、注册中心、用户定位、RPC传输、加密、分布式锁、缓存、配置中心、事件总线、日志)、集群服务(网关服务器、节点服务器、网格服务器、Web服务器、客户端)、三方集成(GORM、Redis、MongoDB、JWT、Casbin)。为Go语言分布式游戏服务器开发者提供完整的框架设计理念、最佳实践和丰富示例。
license: MIT
---

# Due v2 框架开发参考

本技能包提供 Due v2 框架的完整参考文档和示例代码,帮助开发者深入理解框架的设计理念和核心机制,并快速上手开发。

## 关键约定(速查)

> 以下约定已对照框架源码(当前版本 `v2.6.2`)核实,编写代码前请先确认,避免使用不存在的 API:

- **集群实例类型**:`Gate` / `Node` / `Mesh`(另有预留的 `Master`)。
- **实例状态**:`Shut` / `Work` / `Busy` / `Hang`;`SetState` 只在 `Work`/`Busy` 间切换,`Close` → `Hang`,`Destroy` → `Shut`。
- **生命周期 Hook**:`cluster.Init` / `cluster.Start` / `cluster.Close` / `cluster.Destroy`。
- **集群事件**:`cluster.Connect` / `cluster.Reconnect` / `cluster.Disconnect`。
- **路由选项**:`node.RouteOptions{Internal, Stateful, Authorized, Middlewares}`,预设 `node.InternalRoute` / `node.StatefulRoute` / `node.AuthorizedRoute`;**不存在 `StatelessRoute`**,默认即无状态路由。
- **路由注册**:`proxy.AddRouteHandler(route int32, handler, opts ...RouteOptions)`;中间件签名为 `func(mw *node.Middleware, ctx node.Context)`,用 `mw.Next(ctx)` 继续;**不存在 `Router.Use` 与 `ctx.Abort()`**。
- **网关分发策略**:`etc.cluster.gate.dispatch` = `random`(默认)/ `round-robin` / `weighted-round-robin`。
- **并发模型**:节点默认单线程分发(dispatch 协程);`ctx.Task` 投递到全局协程池;`ctx.Next` 交调度器二次分发到 Actor。
- **通信协议**:数据包 `size(4)|header(1)|route(n)|seq(m)|message(x)`,其中 `size = 1 + n + m + len(message)`(不含 4 字节 size 自身);header bit7=心跳、bit6=心跳时间;配置键前缀 `etc.packet.*`。
- **会话类型**:`session.Conn` / `session.User`。
- **用户定位**:`locate` 包,默认 Redis 实现;配置前缀 `locate.redis`(默认 `prefix = "due:locate"`)。

## 框架设计(references/框架设计/)

| 文档 | 说明 |
|------|------|
| [架构设计](references/框架设计/架构设计.md) | Due v2 整体架构概览,核心组件与分层设计 |
| [通信协议](references/框架设计/通信协议.md) | 心跳包与数据包的协议格式设计 |
| [路由设计](references/框架设计/路由设计.md) | 无状态路由与有状态路由的分发机制 |
| [配置管理](references/框架设计/配置管理.md) | 启动配置(etc)的读取、格式支持与全部配置项 |
| [绑定网关](references/框架设计/绑定网关.md) | GID/CID/UID 三者绑定关系与消息流转 |
| [绑定节点](references/框架设计/绑定节点.md) | NID/UID 绑定关系与有状态路由定向 |
| [单线程模型](references/框架设计/单线程模型.md) | 顺序执行的单线程消息处理模型 |
| [多协程模型](references/框架设计/多协程模型.md) | 基于协程池的并发消息处理模型 |
| [Actor模型](references/框架设计/Actor模型.md) | 基于消息传递的Actor并发编程模型 |
| [运行模式](references/框架设计/运行模式.md) | debug/test/release 三种运行模式 |
| [错误处理](references/框架设计/错误处理.md) | 框架错误与错误码的设计与使用 |
| [滚动更新](references/框架设计/滚动更新.md) | 网关服、节点服、网格服的滚动更新方案 |

## 核心模块(references/核心模块/)

| 文档 | 说明 |
|------|------|
| [网络通信](references/核心模块/网络通信.md) | TCP/KCP/WebSocket 网络层抽象与实现 |
| [服务注册](references/核心模块/服务注册.md) | Consul/Etcd/Nacos 服务发现与注册 |
| [用户定位](references/核心模块/用户定位.md) | Redis 用户网关/节点绑定信息定位 |
| [RPC传输](references/核心模块/RPC传输.md) | gRPC/RPCX RPC 通信传输层 |
| [加密签名](references/核心模块/加密签名.md) | RSA/ECC 加密与签名算法 |
| [分布式锁](references/核心模块/分布式锁.md) | Redis/Memcache 分布式锁实现 |
| [缓存方案](references/核心模块/缓存方案.md) | Redis/Memcache 缓存方案 |
| [配置中心](references/核心模块/配置中心.md) | File/Consul/Etcd/Nacos 配置中心 |
| [事件总线](references/核心模块/事件总线.md) | Process/NATS/Redis/Kafka 事件总线 |
| [日志组件](references/核心模块/日志组件.md) | 多终端日志组件(控制台、文件、云日志) |

## 集群服务(references/集群服务/)

| 文档 | 说明 |
|------|------|
| [网关服务器](references/集群服务/网关服务器.md) | Gate 网关服务器,处理客户端连接与消息转发 |
| [节点服务器](references/集群服务/节点服务器.md) | Node 节点服务器,处理游戏业务逻辑 |
| [网格服务器](references/集群服务/网格服务器.md) | Mesh 网格服务器,提供微服务 RPC 调用 |
| [Web服务器](references/集群服务/Web服务器.md) | Web HTTP 服务器,支持 Swagger 文档 |
| [客户端](references/集群服务/客户端.md) | TCP/WebSocket 客户端实现 |

## 三方集成(references/三方集成/)

| 文档 | 说明 |
|------|------|
| [GORM数据库](references/三方集成/GORM数据库.md) | GORM ORM 框架集成,支持连接池与多实例 |
| [Redis客户端](references/三方集成/Redis客户端.md) | Redis 客户端集成,支持单机/集群/哨兵模式 |
| [MongoDB驱动](references/三方集成/MongoDB驱动.md) | MongoDB 驱动集成,支持 DSN 配置 |
| [JWT认证](references/三方集成/JWT认证.md) | JWT 认证集成,支持 Redis 存储与 Token 管理 |
| [Casbin权限](references/三方集成/Casbin权限.md) | Casbin 权限控制集成,支持 RBAC 模型 |

## 示例代码(examples/)

提供 17+ 个完整可运行的示例项目,涵盖框架所有核心功能:

| 示例 | 说明 |
|------|------|
| [快速开始](examples/quick-start/) | 最简节点服务器示例 |
| [节点服务器](examples/node-server/) | 完整节点服务器与路由处理 |
| [Actor模型](examples/actor-model/) | Actor 并发模型示例 |
| [绑定网关](examples/bind-gate/) | 网关绑定流程示例 |
| [绑定节点](examples/bind-node/) | 节点绑定流程示例 |
| [TCP网关](examples/gate-tcp/) | TCP 网关服务器 |
| [WebSocket网关](examples/gate-ws/) | WebSocket 网关服务器 |
| [gRPC网格](examples/mesh-grpc/) | gRPC 网格服务器与客户端 |
| [TCP客户端](examples/client-tcp/) | TCP 客户端连接 |
| [WebSocket客户端](examples/client-ws/) | WebSocket 客户端连接 |
| [Redis缓存](examples/cache-redis/) | Redis 缓存使用 |
| [Redis分布式锁](examples/lock-redis/) | Redis 分布式锁使用 |
| [文件配置](examples/config-file/) | 文件配置中心 |
| [NATS事件总线](examples/eventbus-nats/) | NATS 事件总线 |
| [GORM集成](examples/third-gorm/) | GORM ORM 集成 |
| [Redis集成](examples/third-redis/) | Redis 客户端集成 |
| [JWT集成](examples/third-jwt/) | JWT 认证集成 |

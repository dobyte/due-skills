# Web服务器 (Web)

## 概述

Web服务器是 Due 框架的HTTP服务组件，基于 Fiber v3 框架二次封装，提供高性能的Web服务能力。支持跨域、Swagger文档、中间件等特性。

## 包路径

```go
import "github.com/dobyte/due/component/http/v2"
```

## 配置参数

```toml
[http]
    # 服务器名称
    name = "http"
    # 服务器监听地址，默认为:8080
    addr = ":8080"
    # 是否启用控制台输出，默认为false
    console = false
    # body大小，支持单位： B | K | KB | M | MB | G | GB | T | TB | P | PB | E | EB | Z | ZB，默认为4M
    bodyLimit = "4M"
    # 最大并发连接数，默认为262144
    concurrency = 262144
    # 是否启用严格路由模式，默认为false
    strictRouting = false
    # 是否区分路由大小写，默认为false
    caseSensitive = false
    # 秘钥文件
    keyFile = ""
    # 证书文件
    certFile = ""
    # 是否禁用HEAD方法自动注册，默认为false
    disableHeadAutoRegister = false
    # 是否启用不可变路由，默认为false
    immutable = false
    # 是否unescape路径参数，默认为false
    unescapePath = false
    # 视图布局
    viewsLayout = ""
    # 是否将上下文 locals 传递给视图引擎
    passLocalsToViews = false
    # 读取缓冲区大小，默认为4096
    readBufferSize = 4096
    # 写入缓冲区大小，默认为4096
    writeBufferSize = 4096
    # 是否禁用keepalive，默认为false
    disableKeepalive = false
    # 是否禁用默认日期，默认为false
    disableDefaultDate = false
    # 是否禁用默认Content-Type，默认为false
    disableDefaultContentType = false
    # 是否禁用默认头部归一化，默认为false
    disableHeaderNormalizing = false
    # 是否流式请求体，默认为false
    streamRequestBody = false
    # 是否禁用预解析multipart/form-data，默认为false
    disablePreParseMultipartForm = false
    # 是否减少内存占用，默认为false
    reduceMemoryUsage = false
    # 是否启用IP验证，默认为false
    enableIPValidation = false
    # 是否启用在解析器上拆分请求体，默认为false
    enableSplittingOnParsers = false

    # 代理配置
    [http.proxy]
        # 代理头部，默认为 X-Forwarded-For
        proxyHeader = "X-Forwarded-For"
        # 信任代理配置
        [http.proxy.trustProxy]
            # 是否信任代理，默认为false
            enable = false
            # 受信任代理 IP 地址或 CIDR 范围的列表
            proxies = []
            # 是否信任所有链路本地 IP 范围
            linkLocal = false
            # 是否信任所有环回 IP 范围
            loopback = false
            # 是否信任所有私有 IP 范围
            private = false
    
    # 跨域配置
    [http.cors]
        # 是否启用跨域
        enable = false
        # 允许跨域的请求源
        allowOrigins = []
        # 允许跨域的请求方法
        allowMethods = []
        # 允许跨域的请求头部
        allowHeaders = []
        # 当允许所有源时，是否允许携带凭据
        allowCredentials = false
        # 允许暴露给客户端的头部
        exposeHeaders = []
        # 浏览器缓存预检请求结果的时间
        maxAge = 0
        # 是否允许来自私有网络的请求
        allowPrivateNetwork = false
    
    # swagger文档配置
    [http.swagger]
        # 是否启用文档
        enable = true
        # API文档标题
        title = "API文档"
        # URL访问基础路径
        basePath = "/swagger"
        # swagger文件路径
        filePath = "./docs/swagger.json"
        # swagger-ui-bundle.js地址
        swaggerBundleUrl = ""
        # swagger-ui-standalone-preset.js地址
        swaggerPresetUrl = ""
        # swagger-ui.css地址
        swaggerStylesUrl = ""
```

## 核心 API

### 创建Web服务器

```go
// 创建Web服务器
func NewServer(opts ...Option) *Server

// 常用选项函数
func WithName(name string) Option
func WithAddr(addr string) Option
func WithCredentials(certFile, keyFile string) Option
func WithConsole(enable bool) Option
func WithRegistry(r registry.Registry) Option
func WithTransporter(transporter transport.Transporter) Option
func WithCorsOptions(corsOpts CorsOptions) Option
func WithSwagOptions(swagOpts SwagOptions) Option
func WithProxyOptions(proxyOpts ProxyOptions) Option
func WithMiddlewares(middlewares ...any) Option
func WithStrictRouting(enable bool) Option
func WithCaseSensitive(enable bool) Option
func WithBodyLimit(bodyLimit int) Option
func WithConcurrency(concurrency int) Option
func WithErrorHandler(errorHandler fiber.ErrorHandler) Option
```

### 服务器代理

```go
type Proxy struct {
    // 获取底层fiber应用
    App() *fiber.App
    // 获取路由器
    Router() Router
    // 创建网格客户端
    NewMeshClient(target string) (transport.Client, error)
}
```

### 路由器

```go
type Router interface {
    // 注册路由，handlers 支持 due、fiber、express、net/http、fasthttp 等多种风格
    Get(path string, handlers ...any) Router
    Post(path string, handlers ...any) Router
    Head(path string, handlers ...any) Router
    Put(path string, handlers ...any) Router
    Delete(path string, handlers ...any) Router
    Connect(path string, handlers ...any) Router
    Options(path string, handlers ...any) Router
    Trace(path string, handlers ...any) Router
    Patch(path string, handlers ...any) Router
    All(path string, handlers ...any) Router
    Add(methods []string, path string, handlers ...any) Router
    // 路由分组
    Group(prefix string, middlewares ...any) Router
}
```

### 上下文

```go
type Context interface {
    // 内嵌 fiber.Ctx，可直接使用 fiber 上下文能力（如 Bind、Params、Query 等）
    fiber.Ctx
    // 返回底层 fiber.Ctx
    CTX() fiber.Ctx
    // 返回代理对象
    Proxy() *Proxy
    // 成功响应
    Success(data ...any) error
    // 失败响应（rst 支持 error、codes.Code、*codes.Code）
    Failure(rst any) error
    // 返回等价的 net/http 请求
    StdRequest() *http.Request
}
```

## 使用示例

### 基础Web服务器

```go
package main

import (
    "fmt"
    "github.com/dobyte/due/component/http/v2"
    "github.com/dobyte/due/v2"
    "github.com/dobyte/due/v2/codes"
    "github.com/dobyte/due/v2/log"
    "github.com/dobyte/due/v2/utils/xtime"
)

// @title API文档
// @version 1.0
// @host localhost:8080
// @BasePath /
func main() {
    // 创建容器
    container := due.NewContainer()
    // 创建HTTP组件
    component := http.NewServer()
    // 初始化应用
    initApp(component.Proxy())
    // 添加HTTP组件
    container.Add(component)
    // 启动容器
    container.Serve()
}

// 初始化应用
func initApp(proxy *http.Proxy) {
    // 路由器
    router := proxy.Router()
    // 注册路由
    router.Get("/greet", greetHandler)
}

// 请求
type greetReq struct {
    Message string `json:"message"`
}

// 响应
type greetRes struct {
    Message string `json:"message"`
}

// 路由处理器
// @Summary 测试接口
// @Tags 测试
// @Schemes
// @Accept json
// @Produce json
// @Param request body greetReq true "请求参数"
// @Response 200 {object} http.Resp{Data=greetRes} "响应参数"
// @Router /greet [get]
func greetHandler(ctx http.Context) error {
    req := &greetReq{}

    if err := ctx.Bind().JSON(req); err != nil {
        return ctx.Failure(codes.InvalidArgument)
    }

    log.Info(req.Message)

    return ctx.Success(&greetRes{
        Message: fmt.Sprintf("I'm server, and the current time is: %s", xtime.Now().Format(xtime.DateTime)),
    })
}
```

### 跨域配置

```toml
[http.cors]
    enable = true
    allowOrigins = ["http://localhost:3000"]
    allowMethods = ["GET", "POST", "PUT", "DELETE"]
    allowHeaders = ["Content-Type", "Authorization"]
    allowCredentials = true
    maxAge = 3600
```

### Swagger文档

1. 安装 swag

```bash
$ go install github.com/swaggo/swag/cmd/swag@latest
```

2. 生成 swagger 文件

```bash
$ swag init --parseDependency
$ rm -rf ./docs/docs.go
```

3. 配置 Swagger

```toml
[http.swagger]
    enable = true
    title = "API文档"
    basePath = "/swagger"
    filePath = "./docs/swagger.json"
```

### 中间件

```go
package main

import (
    "github.com/dobyte/due/component/http/v2"
    "github.com/dobyte/due/v2/log"
    "github.com/gofiber/fiber/v3"
)

func main() {
    // 创建HTTP组件并添加中间件
    component := http.NewServer(
        http.WithMiddlewares(
            loggerMiddleware,
            authMiddleware,
        ),
    )
    
    // ...
}

// 日志中间件
func loggerMiddleware(ctx fiber.Ctx) error {
    log.Infof("Request: %s %s", ctx.Method(), ctx.Path())
    return ctx.Next()
}

// 认证中间件
func authMiddleware(ctx fiber.Ctx) error {
    token := ctx.Get("Authorization")
    if token == "" {
        return ctx.Status(401).JSON(fiber.Map{
            "error": "Unauthorized",
        })
    }
    return ctx.Next()
}
```

框架还内置了基于 RFC 2617 的 Digest 认证中间件（`github.com/dobyte/due/component/http/v2/middleware/digestauth`），可通过 `digestauth.New(digestauth.Config{...})` 创建后作为中间件或路由分组中间件使用。

## 最佳实践

1. **路由设计**:
   - 使用RESTful风格设计API
   - 合理组织路由层级

2. **跨域处理**:
   - 生产环境明确指定允许的源
   - 合理设置预检请求缓存时间

3. **文档管理**:
   - 使用Swagger自动生成API文档
   - 保持文档与代码同步

4. **中间件**:
   - 合理使用中间件处理通用逻辑
   - 注意中间件执行顺序

5. **性能优化**:
   - 合理设置body大小限制
   - 根据服务器配置调整并发数

## 相关文件

- Web源码：`github.com/dobyte/due/component/http/`
- Swagger中间件：`github.com/dobyte/due/component/http/swagger/`
- Digest认证中间件：`github.com/dobyte/due/component/http/middleware/digestauth/`
- Fiber文档：https://docs.gofiber.io/

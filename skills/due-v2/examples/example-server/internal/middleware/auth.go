package middleware

import (
	"example-server/internal/code"
	"example-server/internal/protocol/base"

	"github.com/dobyte/due/v2/cluster/node"
	"github.com/dobyte/due/v2/log"
)

// Auth 授权检测中间件：未携带 UID 的请求直接拒绝，挂载后其后的路由均为授权路由。
func Auth(middleware *node.Middleware, ctx node.Context) {
	if ctx.UID() == 0 {
		if err := ctx.Response(&base.Res{Code: int32(code.Unauthorized.Code())}); err != nil {
			log.Errorf("response message failed, err: %v", err)
		}
		return
	}

	middleware.Next(ctx)
}

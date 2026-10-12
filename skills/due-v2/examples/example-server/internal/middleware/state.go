package middleware

import (
	"sync/atomic"

	"example-server/internal/code"
	"example-server/internal/protocol/base"

	"github.com/dobyte/due/v2/cluster/node"
	"github.com/dobyte/due/v2/log"
)

var maintained atomic.Bool

// SetMaintained 设置维护状态
func SetMaintained(flag bool) {
	maintained.Store(flag)
}

// State 服务器状态检测中间件：维护中直接拒绝请求。
func State(middleware *node.Middleware, ctx node.Context) {
	if maintained.Load() {
		if err := ctx.Response(&base.Res{Code: int32(code.ServerIsMaintain.Code())}); err != nil {
			log.Errorf("response message failed, err: %v", err)
		}
		return
	}

	middleware.Next(ctx)
}

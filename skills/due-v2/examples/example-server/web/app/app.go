package app

import (
	basicapi "example-server/web/app/api/basic"

	"github.com/dobyte/due/component/http/v2"
)

// Init 应用装配入口。只做装配，不写业务逻辑。
func Init(proxy *http.Proxy) {
	// 健康探测
	proxy.Router().Get("/devops/health", func(ctx http.Context) error {
		return ctx.Success("ok")
	})

	// 基础模块
	{
		api := basicapi.NewAPI(proxy)
		group := proxy.Router().Group("/basic")
		// 拉取用户信息
		group.Post("/fetch-user", api.FetchUser)
	}
}

package basic

import (
	"example-server/internal/code"
	usersvc "example-server/internal/service/user/client"
	userpb "example-server/internal/service/user/pb"

	"github.com/dobyte/due/component/http/v2"
	"github.com/dobyte/due/v2/log"
)

type API struct {
	proxy *http.Proxy
}

func NewAPI(proxy *http.Proxy) *API {
	return &API{proxy: proxy}
}

// FetchUser 拉取用户信息
// @Summary 拉取用户信息
// @Tags 基础模块
// @Accept json
// @Produce json
// @Param request body FetchUserReq true "请求参数"
// @Success 200 {object} http.Resp "响应参数"
// @Router /basic/fetch-user [post]
func (a *API) FetchUser(ctx http.Context) error {
	req := &FetchUserReq{}

	if err := ctx.Bind().JSON(req); err != nil {
		return ctx.Failure(code.InvalidArgument)
	}

	client, err := usersvc.NewClient(a.proxy.NewMeshClient)
	if err != nil {
		log.Errorf("create user client failed, err: %v", err)
		return ctx.Failure(code.InternalError)
	}

	reply, err := client.FetchUser(ctx.Context(), &userpb.FetchUserArgs{Uid: req.UID})
	if err != nil {
		return ctx.Failure(err)
	}

	return ctx.Success(reply)
}

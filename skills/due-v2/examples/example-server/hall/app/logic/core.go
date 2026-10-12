package logic

import (
	"example-server/internal/code"
	"example-server/internal/middleware"
	"example-server/internal/protocol/base"
	"example-server/internal/protocol/common"
	"example-server/internal/protocol/hall"
	usersvc "example-server/internal/service/user/client"
	userpb "example-server/internal/service/user/pb"

	"github.com/dobyte/due/v2/cluster/node"
	"github.com/dobyte/due/v2/log"
)

type core struct {
	proxy *node.Proxy
}

func NewCore(proxy *node.Proxy) *core {
	return &core{proxy: proxy}
}

func (c *core) Init() {
	c.proxy.Router().Group(func(group *node.RouterGroup) {
		// 注册状态检测中间件
		group.Middleware(middleware.State)
		// 校验TOKEN：无状态路由，可并发处理
		group.AddRouteHandler(int32(hall.Route_ValidateToken), c.validateToken)
		// 注入授权检测中间件，其后的路由均为授权路由
		group.Middleware(middleware.Auth)
		// 拉取个人资料
		group.AddRouteHandler(int32(hall.Route_FetchProfile), c.fetchProfile, node.AuthorizedRoute)
		// 修改昵称
		group.AddRouteHandler(int32(hall.Route_ModifyNickname), c.modifyNickname, node.AuthorizedRoute)
	})
}

// validateToken 校验TOKEN
func (c *core) validateToken(ctx node.Context) {
	req := &hall.ValidateTokenReq{}
	res := &hall.ValidateTokenRes{}
	ctx.Defer(func() {
		if err := ctx.Response(res); err != nil {
			log.Errorf("response message failed, err: %v", err)
		}
	})

	if err := ctx.Parse(req); err != nil {
		res.Res = &base.Res{Code: int32(code.InvalidArgument.Code())}
		return
	}

	res.Res = &base.Res{Code: int32(code.OK.Code())}
}

// fetchProfile 拉取个人资料
func (c *core) fetchProfile(ctx node.Context) {
	res := &hall.FetchProfileRes{}
	ctx.Defer(func() {
		if err := ctx.Response(res); err != nil {
			log.Errorf("response message failed, err: %v", err)
		}
	})

	// 业务层不直连他人数据，统一走 mesh
	client, err := usersvc.NewClient(c.proxy.NewMeshClient)
	if err != nil {
		log.Errorf("create user client failed, err: %v", err)
		res.Res = &base.Res{Code: int32(code.InternalError.Code())}
		return
	}

	reply, err := client.FetchUser(ctx.Context(), &userpb.FetchUserArgs{Uid: ctx.UID()})
	if err != nil {
		res.Res = &base.Res{Code: int32(code.UserNotExists.Code())}
		return
	}

	res.Res = &base.Res{Code: int32(code.OK.Code())}
	res.User = &common.UserInfo{Uid: reply.GetUid(), Nickname: reply.GetNickname(), Avatar: reply.GetAvatar()}
}

// modifyNickname 修改昵称
func (c *core) modifyNickname(ctx node.Context) {
	req := &hall.ModifyNicknameReq{}
	res := &hall.ModifyNicknameRes{}
	ctx.Defer(func() {
		if err := ctx.Response(res); err != nil {
			log.Errorf("response message failed, err: %v", err)
		}
	})

	if err := ctx.Parse(req); err != nil {
		res.Res = &base.Res{Code: int32(code.InvalidArgument.Code())}
		return
	}

	client, err := usersvc.NewClient(c.proxy.NewMeshClient)
	if err != nil {
		log.Errorf("create user client failed, err: %v", err)
		res.Res = &base.Res{Code: int32(code.InternalError.Code())}
		return
	}

	if _, err = client.UpdateNickname(ctx.Context(), &userpb.UpdateNicknameArgs{
		Uid:      ctx.UID(),
		Nickname: req.GetNickname(),
	}); err != nil {
		res.Res = &base.Res{Code: int32(code.InternalError.Code())}
		return
	}

	res.Res = &base.Res{Code: int32(code.OK.Code())}
}

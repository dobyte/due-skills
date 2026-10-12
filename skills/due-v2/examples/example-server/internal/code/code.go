package code

import (
	"example-server/internal/protocol/common"

	"github.com/dobyte/due/v2/codes"
)

// 统一错误码：编号源为 protocol/common.proto 的 enum Code，禁止在业务代码里硬编码数字。
var (
	OK               = codes.NewCode(int(common.Code_OK), "成功")
	InvalidArgument  = codes.NewCode(int(common.Code_InvalidArgument), "无效参数")
	NotFound         = codes.NewCode(int(common.Code_NotFound), "未找到资源")
	InternalError    = codes.NewCode(int(common.Code_InternalError), "服务器内部错误")
	Unauthorized     = codes.NewCode(int(common.Code_Unauthorized), "未授权")
	TooManyRequests  = codes.NewCode(int(common.Code_TooManyRequests), "请求过于频繁")
	ServerIsMaintain = codes.NewCode(int(common.Code_ServerIsMaintain), "服务器维护中")
	UserNotExists    = codes.NewCode(int(common.Code_UserNotExists), "用户不存在")
)

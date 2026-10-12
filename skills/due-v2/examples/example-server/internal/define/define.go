package define

// 路由号段规划。号段一经分配禁止复用，新增模块须先在本文登记。
const (
	SegmentHallMin     = 1000 // 大厅：[1000, 1999]
	SegmentHallMax     = 1999
	SegmentActivityMin = 2000 // 活动：[2000, 2999]
	SegmentActivityMax = 2999
	SegmentNotifyMin   = 3000 // 通知：[3000, 3999]
	SegmentNotifyMax   = 3999
	SegmentGameBase    = 10000 // 游戏：自 10000 起，每个游戏独占 1000
	SegmentGameStep    = 1000
)

// 分页默认值
const (
	DefaultPage     = 1
	DefaultLimit    = 10
	DefaultMaxLimit = 100
)

// 调用方类型
const (
	CallerClient = 0 // 客户端
	CallerAdmin  = 1 // 后台
)

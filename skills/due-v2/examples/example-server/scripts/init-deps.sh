#!/bin/bash
# 依赖版本解析：不固化版本，一律拉取当刻最新。
# 用法：在项目根目录执行 bash scripts/init-deps.sh [module-name]
set -e

MODULE="${1:-}"

# 尚无 go.mod 时，按传入名（缺省取目录名）初始化模块
if [ ! -f go.mod ]; then
  if [ -z "${MODULE}" ]; then
    MODULE="$(basename "$PWD")"
  fi
  go mod init "${MODULE}"
fi

# due 主模块
go get github.com/dobyte/due/v2@latest

# 按项目实际使用的子模块勾选；未使用的可删行，缺少的按同样格式补上
SUBMODULES=(
  "network/ws"
  "registry/nacos"
  "config/nacos"
  "locate/redis"
  "transport/grpc"
  "lock/redis"
  "cache/redis"
  "eventbus/redis"
  "component/http"
)

for m in "${SUBMODULES[@]}"; do
  mod="github.com/dobyte/due/${m}/v2"
  # due 的子模块没有打 tag，直接 @latest 会报 "no matching versions for query latest"；
  # 此时退回默认分支 main，其 HEAD 即最新提交（解析为伪版本）。
  if ! go get "${mod}@latest" 2>/dev/null; then
    go get "${mod}@main"
  fi
done

# 定稿：收敛依赖并写入 go.mod / go.sum
# 注意：若协议生成物（*.pb.go）尚未生成，tidy 会因缺失导入而失败，此处不阻断流程，
#       请在执行 protoc.sh 之后，再跑一次 go mod tidy。
go mod tidy || echo "提示：go mod tidy 未完成，请在生成协议（protoc.sh）后再执行一次。"

echo "deps resolved to latest."

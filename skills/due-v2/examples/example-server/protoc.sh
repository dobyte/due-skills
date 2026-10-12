#!/bin/bash
# 统一协议生成脚本：所有 .proto 生成物均由本脚本产出，禁止手改生成物。
set -e

ROOT=$(cd "$(dirname "$0")" && pwd)
MODULE=example-server

# Windows（Git Bash / MSYS）下 protoc 为原生程序，需传 Windows 风格路径
OUT="${ROOT}"
if command -v cygpath >/dev/null 2>&1; then
  OUT=$(cygpath -w "${ROOT}")
fi

# 1) 客户端协议：internal/protocol/*.proto
cd "${ROOT}/internal/protocol"
for file in *.proto; do
  protoc --proto_path=. \
    --go_out="${OUT}" --go_opt=module="${MODULE}" \
    "${file}"
done

# 2) 微服务协议：internal/service/*/pb/*.mesh.svc.proto
cd "${ROOT}"
for file in $(find internal/service -name '*.mesh.svc.proto'); do
  dir=$(dirname "${file}")
  protoc --proto_path=internal/protocol --proto_path="${dir}" \
    --go_out="${OUT}" --go_opt=module="${MODULE}" \
    --go-grpc_out="${OUT}" --go-grpc_opt=module="${MODULE}" \
    "${file}"
done

echo "protoc done."

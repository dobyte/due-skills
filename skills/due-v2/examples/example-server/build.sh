#!/bin/bash
# 单服务构建与发布：宿主机编译 + 运行时打包 + 推镜像。
# 用法：bash build.sh <project> <services-parent-dir> <service> <environment>
# 示例：bash build.sh demo . hall test
set -e

readonly project="${1}"
readonly dir="${2}/${3}"
readonly app="${3}"
readonly environment="${4}"
# 共享配置源：构建期复制为 <service>/etc/etc.<env>.toml（该文件不入库）
readonly share="internal/share/etc/etc.${project}.${environment}.toml"
readonly alone="etc/etc.${environment}.toml"
readonly registry="${REGISTRY:-registry.example.com}/${project}-server"
readonly image="${registry}/${app}:${project}-${environment}-${BUILD_NUMBER}"

echo "检测应用目录"
if [ ! -d "${dir}" ]; then
  echo "app dir not found: ${dir}"
  exit 1
fi

echo "检测共享配置"
if [ ! -e "${share}" ]; then
  echo "share etc file not found: ${share}"
  exit 1
fi

echo "复制配置"
cp "${share}" "${dir}/${alone}"

echo "编译（宿主工具链，不写死在镜像里；CI 应固定工具链版本）"
cd "./${dir}"
CGO_ENABLED=0 GOOS=linux GOARCH=amd64 go build -o main .
cd - >/dev/null

echo "打包（构建上下文 = 服务目录）"
docker build --build-arg ENV="${environment}" -t "${image}" "./${dir}"

echo "推送"
docker push "${image}"

echo "清理本地镜像与中间产物"
docker rmi "${image}"
rm -f "${dir}/main" "${dir}/${alone}"

# 部署（按需启用）
# kubectl set image deployment/${app} ${app}=${image} -n ${project}-server

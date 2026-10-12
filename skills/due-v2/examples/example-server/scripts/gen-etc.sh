#!/bin/bash
# 从框架最新版自带的 etc 模板，按进程角色动态生成 <service>/etc/etc.toml。
# 模板来源：go list -m 解析出的框架模块目录下的 testdata/etc/etc.toml
#          （版本由 init-deps.sh 决定的"当刻最新版"，本脚本不固化版本号）
# 用法：bash scripts/gen-etc.sh [role ...]     # 默认 gate hall mesh web
set -e

ROOT=$(cd "$(dirname "$0")/.." && pwd)
cd "$ROOT"

# 解析框架模块目录
DUE_DIR=$(go list -m -f '{{.Dir}}' github.com/dobyte/due/v2)
if command -v cygpath >/dev/null 2>&1; then
  DUE_DIR=$(cygpath -u "$DUE_DIR")
fi
TEMPLATE="$DUE_DIR/testdata/etc/etc.toml"
if [ ! -f "$TEMPLATE" ]; then
  echo "框架 etc 模板不存在：$TEMPLATE"
  exit 1
fi

roles="${*:-gate hall mesh web}"

for role in $roles; do
  case "$role" in
    gate|hall|mesh|web) ;;
    *) echo "未知角色：$role（可选 gate/hall/mesh/web）"; exit 1 ;;
  esac

  out="$role/etc/etc.toml"
  if [ ! -d "$role/etc" ]; then
    echo "跳过：目录不存在 $role/etc"
    continue
  fi

  {
    echo "# 本文件由 scripts/gen-etc.sh 依据框架最新版自带的 etc 模板动态生成。"
    echo "# 角色：$role。按角色裁剪 section 并保留配置项注释。请勿手工编辑；"
    echo "# 需要调整时请改裁剪规则或升级框架版本后重新生成。"
    echo
    awk -v role="$role" '
      BEGIN {
        # 各角色保留的 section（前缀匹配：选中 cluster.node 会一并带上 cluster.node.linker）
        keep["gate"] = "cluster.gate,packet,log,registry.nacos,network.ws.server,locate.redis"
        keep["hall"] = "cluster.node,task,pprof,transport.grpc.client,packet,log,registry.nacos,config.nacos,locate.redis,lock.redis,eventbus.redis"
        keep["mesh"] = "cluster.mesh,task,pprof,transport.grpc,packet,log,registry.nacos,config.nacos,locate.redis,cache.redis,lock.redis,eventbus.redis"
        keep["web"]  = "http,log,registry.nacos,transport.grpc.client"

        # 模板中的示例项、按需裁剪项、以及与本版代码不一致的滞后项，一律丢弃：
        #  - cluster.*.metadata     模板里的 key=value 示例会注入假元数据
        #  - log.terminals          模板同时用数组与表声明，严格 TOML 会报重复
        #  - log.aliyun / log.tencent  仅当 terminals 含云端日志时才需要
        #  - network.ws.server.proxy   本版代码读的是 proxyMode / proxyOptions，该块无效
        drop["cluster.gate.metadata"] = 1
        drop["cluster.node.metadata"] = 1
        drop["cluster.mesh.metadata"] = 1
        drop["log.terminals"] = 1
        drop["log.aliyun"] = 1
        drop["log.tencent"] = 1
        drop["network.ws.server.proxy"] = 1

        n = split(keep[role], arr, ",")
        for (i = 1; i <= n; i++) keepTab[arr[i]] = 1

        # 该角色自身的实例名所在 section
        kind["gate"] = "cluster.gate"
        kind["hall"] = "cluster.node"
        kind["mesh"] = "cluster.mesh"
        kind["web"] = "http"
        roleSec = kind[role]

        cur = ""
        seenHeader = 0
        keyIndent = -1
        buf = ""
        hasBuf = 0
        printed = 0
        lastBlank = 0
      }

      function selected(path,   k) {
        for (k in drop) {
          if (path == k || substr(path, 1, length(k) + 1) == k ".") return 0
        }
        for (k in keepTab) {
          if (path == k || substr(path, 1, length(k) + 1) == k ".") return 1
        }
        return 0
      }

      # 计算 path 在"保留下来的结构"中的层级：只统计被保留的祖先，
      # 因此父表被丢弃时，子表会自动顶格，不会残留原缩进。
      function keptDepth(path,   i, n, seg, prefix, d) {
        n = split(path, seg, ".")
        d = 0
        prefix = ""
        for (i = 1; i < n; i++) {
          prefix = (prefix == "" ? seg[i] : prefix "." seg[i])
          if (selected(prefix)) d++
        }
        return d
      }

      # 取出缓存的注释块，去掉首尾空行（内部空行保留），避免与自动空行叠加
      function takeBuf(   n, i, arr, out, started) {
        if (!hasBuf) return ""
        n = split(buf, arr, "\n")
        while (n > 0 && arr[n] == "") n--
        out = ""
        started = 0
        for (i = 1; i <= n; i++) {
          if (!started) {
            if (arr[i] == "") continue
            started = 1
          }
          out = (out == "" ? arr[i] : out "\n" arr[i])
        }
        buf = ""
        hasBuf = 0
        return out
      }

      function emitBlock(indent,   t, n, i, arr, s) {
        t = takeBuf()
        if (t == "") return
        n = split(t, arr, "\n")
        for (i = 1; i <= n; i++) {
          s = arr[i]
          if (s == "") { print "" } else { print sprintf("%*s%s", indent, "", s) }
        }
        printed = 1
        lastBlank = 0
      }

      {
        line = $0

        # 表头
        if (line ~ /^[ \t]*\[/) {
          p = line
          sub(/^[ \t]*\[/, "", p)
          sub(/\][ \t]*$/, "", p)
          gsub(/[ \t]/, "", p)
          cur = p
          seenHeader = 1
          if (selected(p)) {
            keyIndent = keptDepth(p) * 4
            # 顶层模块之间空一行（子表属于同一模块，保持紧凑）
            if (keyIndent == 0 && printed && !lastBlank) print ""
            emitBlock(keyIndent)
            print sprintf("%*s[%s]", keyIndent, "", p)
            printed = 1
            lastBlank = 0
          } else {
            buf = ""
            hasBuf = 0
            keyIndent = -1
          }
          next
        }

        # 注释 / 空行：先缓存，等确定后继元素被保留时再输出
        if (line ~ /^[ \t]*#/ || line ~ /^[ \t]*$/) {
          t = line
          sub(/^[ \t]+/, "", t)
          sub(/[ \t]+$/, "", t)
          if (hasBuf) { buf = buf "\n" t } else { buf = t; hasBuf = 1 }
          next
        }

        # 键值行
        if (!seenHeader || keyIndent >= 0) {
          ind = (!seenHeader ? 0 : keyIndent + 4)
          emitBlock(ind)
          t = line
          sub(/^[ \t]+/, "", t)
          if (!seenHeader && t ~ /^pid[ \t]*=/) {
            sub(/"[^"]*"/, "\"./run/" role ".pid\"", t)
          } else if (seenHeader && cur == roleSec && t ~ /^name[ \t]*=/) {
            sub(/"[^"]*"/, "\"" role "\"", t)
          }
          print sprintf("%*s%s", ind, "", t)
          printed = 1
          lastBlank = 0
        } else {
          buf = ""
          hasBuf = 0
        }
      }
    ' "$TEMPLATE"
  } > "$out"

  echo "已生成：$out"
done

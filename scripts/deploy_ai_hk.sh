#!/usr/bin/env bash
# 从当前本机工作树发布到 ai-hk。运行中的 ArcReel 任务在切换时直接中断。
set -Eeuo pipefail

repo_root=$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)
host=ai-hk
release_id="$(date -u +%Y%m%dT%H%M%SZ)-$(git -C "$repo_root" rev-parse --short HEAD)-$$"
manifest=$(mktemp)
remote_stage=

cleanup() {
    if [[ -f "$manifest" ]]; then
        rm -- "$manifest"
    fi
    if [[ -n "$remote_stage" ]]; then
        ssh -o BatchMode=yes "$host" python3 - "$remote_stage" <<'PY' || true
import pathlib
import shutil
import sys

stage = pathlib.Path(sys.argv[1])
if stage.parent == pathlib.Path('/tmp') and stage.name.startswith('arcreel-deploy.'):
    shutil.rmtree(stage, ignore_errors=True)
PY
    fi
}
trap cleanup EXIT

for command in git pnpm rsync ssh curl python3; do
    command -v "$command" >/dev/null || { echo "缺少本机命令: $command" >&2; exit 1; }
done

node_supported() {
    node -e 'const [major, minor] = process.versions.node.split(".").map(Number); process.exit(major > 24 || (major === 24 && minor >= 12) ? 0 : 1)'
}
if ! node_supported; then
    for node_bin in "$HOME"/.nvm/versions/node/v24*/bin; do
        if [[ -x "$node_bin/node" ]]; then
            export PATH="$node_bin:$PATH"
            node_supported && break
        fi
    done
fi
node_supported || { echo '需要 Node.js 24.12 或更高版本' >&2; exit 1; }

ssh -o BatchMode=yes "$host" 'sudo -n test -x /opt/arcreel/bin/uv && sudo -n test -f /etc/arcreel/arcreel.env && sudo -n test -d /var/lib/arcreel && sudo -n systemctl cat arcreel.service >/dev/null'

echo "构建本机前端..."
(cd "$repo_root/frontend" && pnpm install --frozen-lockfile && pnpm build)
test -s "$repo_root/frontend/dist/index.html"

cd "$repo_root"
while IFS= read -r -d '' path; do
    if [[ -e "$path" || -L "$path" ]]; then
        printf '%s\0' "$path" >> "$manifest"
    fi
done < <(git ls-files -z --cached --others --exclude-standard -- \
    pyproject.toml uv.lock README.md LICENSE NOTICE LICENSES \
    packages lib server alembic alembic.ini scripts agent_runtime_profile public)
find frontend/dist \( -type f -o -type l \) -print0 >> "$manifest"

remote_stage=$(ssh -o BatchMode=yes "$host" 'mktemp -d /tmp/arcreel-deploy.XXXXXXXX')
echo "上传发布文件到 $host..."
rsync -a --from0 --files-from="$manifest" ./ "$host:$remote_stage/"

echo "准备服务器依赖并立即切换..."
ssh -o BatchMode=yes "$host" sudo -n bash -s -- "$release_id" "$remote_stage" <<'REMOTE'
set -Eeuo pipefail
release_id=$1
stage=$2
base=/opt/arcreel
release="$base/releases/$release_id"
backup="$base/backups/$release_id"
current="$base/current"

exec 9>/run/lock/arcreel-deploy.lock
flock -n 9 || { echo '已有 ArcReel 部署正在执行' >&2; exit 1; }
test ! -e "$release"
test -s "$stage/frontend/dist/index.html"
test -f "$stage/uv.lock"
old=$(readlink -f "$current")
test -d "$old"

mv "$stage" "$release"
chown -R arcreel:arcreel "$release"
ln -s /etc/arcreel/arcreel.env "$release/.env"

# 在旧服务运行时安装依赖，缩短中断时间。
sudo -u arcreel -H sh -c 'cd "$1" && exec /opt/arcreel/bin/uv sync --frozen --no-dev' sh "$release"
test -x "$release/.venv/bin/python"

install -d -m 0700 "$backup"
printf '%s\n' "$old" > "$backup/current.before"

rollback() {
    trap - ERR
    echo '切换失败，恢复原发布目录并重启服务' >&2
    ln -s "$old" "$base/.current-rollback-$release_id"
    mv -Tf "$base/.current-rollback-$release_id" "$current"
    systemctl start arcreel.service || true
}
trap rollback ERR

# 不等待运行中的任务；停止后再备份一致的 SQLite 数据库。
systemctl stop --no-block arcreel.service
systemctl kill --signal=SIGKILL arcreel.service 2>/dev/null || true
systemctl stop arcreel.service
python3 - "$backup/arcreel.db" <<'PY'
import sqlite3
import sys

with sqlite3.connect('file:/var/lib/arcreel/arcreel.db?mode=ro', uri=True) as source:
    with sqlite3.connect(sys.argv[1]) as target:
        source.backup(target)
PY
chmod 0600 "$backup/arcreel.db"

ln -s "$release" "$base/.current-next-$release_id"
mv -Tf "$base/.current-next-$release_id" "$current"
systemctl start arcreel.service

healthy=0
for attempt in $(seq 1 40); do
    if systemctl is-active --quiet arcreel.service && curl -fsS --max-time 3 -o /dev/null http://127.0.0.1:1241/health; then
        healthy=1
        break
    fi
    sleep 1
done
test "$healthy" -eq 1
trap - ERR
echo "已发布: $release"
echo "旧版本: $old"
echo "SQLite 备份: $backup/arcreel.db"
REMOTE
remote_stage=

curl -fsS --max-time 10 -o /dev/null https://43.154.247.11/
echo '公网 HTTPS 首页正常；部署完成。'

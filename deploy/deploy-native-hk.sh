#!/usr/bin/env bash
# 将当前 ArcReel 工作树原子发布到 veo-hk 的原生 systemd 部署，不触碰生产数据和 nginx 配置。

set -Eeuo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
readonly SCRIPT_DIR
PROJECT_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"
readonly PROJECT_ROOT
readonly SSH_HOST="veo-hk"
readonly PUBLIC_URL="http://43.154.247.11"
readonly REMOTE_ROOT="/opt/arcreel"
readonly REMOTE_UV="$REMOTE_ROOT/bin/uv"
readonly REMOTE_ENV="/etc/arcreel/arcreel.env"
readonly SERVICE="arcreel.service"
readonly KEEP_RELEASES=3

for command_name in git pnpm tar scp ssh curl; do
    command -v "$command_name" >/dev/null || {
        echo "缺少本机命令: $command_name" >&2
        exit 1
    }
done

cd "$PROJECT_ROOT"

commit="$(git rev-parse --short=8 HEAD)"
suffix=""
if [[ -n "$(git status --porcelain)" ]]; then
    suffix="-working"
fi
release_id="$(date +%Y%m%d-%H%M%S)-${commit}${suffix}"
remote_archive="/tmp/arcreel-${release_id}.tar.gz"
temp_dir="$(mktemp -d "${TMPDIR:-/tmp}/arcreel-deploy.XXXXXX")"
archive="$temp_dir/arcreel.tar.gz"

cleanup() {
    rm -rf -- "$temp_dir"
}
trap cleanup EXIT

echo "[1/5] 构建前端"
(
    cd frontend
    pnpm install --frozen-lockfile
    pnpm build
)

echo "[2/5] 打包当前工作树: $release_id"
mkdir -p "$temp_dir/app"
COPYFILE_DISABLE=1 tar \
    --exclude='._*' \
    --exclude='.DS_Store' \
    --exclude='__pycache__' \
    --exclude='*.pyc' \
    -cf - \
    pyproject.toml uv.lock README.md \
    lib server alembic alembic.ini scripts agent_runtime_profile public frontend/dist \
    | tar -xf - -C "$temp_dir/app"
printf '%s\n' "$release_id" > "$temp_dir/app/.deployment-version"
COPYFILE_DISABLE=1 tar -C "$temp_dir/app" -czf "$archive" .

echo "[3/5] 检查服务器部署基础设施"
ssh -o BatchMode=yes "$SSH_HOST" "sudo test -x '$REMOTE_UV' \
    && sudo test -r '$REMOTE_ENV' \
    && sudo systemctl cat '$SERVICE' >/dev/null \
    && sudo grep -q '127.0.0.1:1241' /etc/nginx/nginx.conf \
    && sudo -u arcreel bwrap --unshare-user --unshare-net --unshare-pid --ro-bind / / /bin/true"

echo "[4/5] 上传并切换版本"
scp -q "$archive" "$SSH_HOST:$remote_archive"
ssh -o BatchMode=yes "$SSH_HOST" "sudo bash -s -- '$release_id' '$remote_archive' '$KEEP_RELEASES'" <<'REMOTE'
set -Eeuo pipefail
umask 027

release_id="$1"
archive="$2"
keep_releases="$3"
root="/opt/arcreel"
releases="$root/releases"
current="$root/current"
release_dir="$releases/$release_id"
service="arcreel.service"
previous="$(readlink -f "$current" 2>/dev/null || true)"
switched=0

rollback() {
    rc=$?
    rm -f -- "$archive"
    if ((switched)) && [[ -n "$previous" && -d "$previous" && "$previous" == "$releases/"* ]]; then
        ln -sfn "$previous" "$current"
        systemctl restart "$service" || true
    fi
    if [[ -d "$release_dir" && "$release_dir" == "$releases/"* ]]; then
        rm -rf -- "$release_dir"
    fi
    exit "$rc"
}
trap rollback ERR

[[ ! -e "$release_dir" ]] || {
    echo "版本目录已存在: $release_dir" >&2
    false
}

install -d -o root -g arcreel -m 0750 "$release_dir"
tar -xzf "$archive" -C "$release_dir"
find "$release_dir" -type f -name '._*' -delete
chown -R root:arcreel "$release_dir"
chmod -R u=rwX,g=rX,o= "$release_dir"

cd "$release_dir"
/opt/arcreel/bin/uv sync --frozen --no-dev
chown -R root:arcreel "$release_dir/.venv"
chmod -R u=rwX,g=rX,o= "$release_dir/.venv"

ln -sfn "$release_dir" "$current"
switched=1
systemctl restart "$service"

healthy=0
for _ in $(seq 1 60); do
    if curl -fsS --max-time 2 http://127.0.0.1:1241/health >/dev/null 2>&1; then
        healthy=1
        break
    fi
    sleep 1
done
[[ "$healthy" == 1 ]] || {
    systemctl status "$service" --no-pager -l >&2 || true
    journalctl -u "$service" -n 100 --no-pager >&2 || true
    false
}

username="$(sed -n 's/^AUTH_USERNAME=//p' /etc/arcreel/arcreel.env | head -1)"
password="$(sed -n 's/^AUTH_PASSWORD=//p' /etc/arcreel/arcreel.env | head -1)"
curl -fsS --max-time 10 \
    --data-urlencode "username=$username" \
    --data-urlencode "password=$password" \
    http://127.0.0.1:1241/api/v1/auth/token >/dev/null

rm -f -- "$archive"
switched=0
trap - ERR

mapfile -t all_releases < <(
    find "$releases" -mindepth 1 -maxdepth 1 -type d -printf '%T@ %p\n' \
        | sort -nr \
        | cut -d' ' -f2-
)
for ((i = keep_releases; i < ${#all_releases[@]}; i++)); do
    old_release="${all_releases[$i]}"
    if [[ "$old_release" == "$releases/"* && "$old_release" != "$release_dir" ]]; then
        rm -rf -- "$old_release"
    fi
done

printf '已部署版本: %s\n' "$release_id"
REMOTE

echo "[5/5] 验证公网入口和原网关"
curl -fsS --max-time 15 "$PUBLIC_URL/" >/dev/null
curl -fsS --max-time 15 "$PUBLIC_URL/login" >/dev/null
curl -fsS --max-time 15 "$PUBLIC_URL/api/v1/auth/status" >/dev/null
curl -fsS --max-time 15 "$PUBLIC_URL/readyz" >/dev/null

echo "部署完成: $PUBLIC_URL/"

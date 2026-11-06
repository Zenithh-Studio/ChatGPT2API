"""验证 OAuth 账号的自动刷新是否生效。

用法（在容器内，工作目录 /app）：
    uv run python scripts/verify_oauth_refresh.py            # 只读诊断，安全
    uv run python scripts/verify_oauth_refresh.py --force    # 真正触发一次刷新

只读模式：列出每个账号的 access_token 剩余有效期、是否带 refresh_token、
          上次刷新时间与上次刷新错误，判断"有没有料可刷"。
--force ：对每个带 refresh_token 的账号强制走一次 force_refresh_access_token，
          直接验证 refresh_token + 本项目 client_id 能否从 OpenAI 换出新 access_token。
          这会真实轮换 access_token（新 token 有效，不损坏账号）。
"""
from __future__ import annotations

import sys

from services.account_service import (
    RefreshCredentialsChangedError,
    TerminalRefreshTokenError,
    account_service,
)


def _fmt_remaining(seconds: int | None) -> str:
    if seconds is None:
        return 'Could not parse exp'
    if seconds <= 0:
        return f'Expired {-seconds // 3600}h'
    return f'{seconds // 3600}h{seconds % 3600 // 60}m until expiration'


def diagnose() -> list[str]:
    """只读：打印每个账号的刷新就绪状态，返回带 refresh_token 的 token 列表。"""
    tokens = account_service.list_tokens()
    print(f'Total accounts: {len(tokens)}\n')
    refreshable: list[str] = []
    for token in tokens:
        account = account_service.get_account(token) or {}
        remaining = account_service._token_expires_in(token)
        has_rt = bool(str(account.get("refresh_token") or "").strip())
        if has_rt:
            refreshable.append(token)
        print(f"- email={account.get('email') or '(unknown)'}")
        print(f"    access_token[:20]   = {token[:20]}...")
        print(f'    Time until expiry = {_fmt_remaining(remaining)}')
        print(f"    refresh_token       = {('available ✅' if has_rt else 'unavailable ❌ (automatic refresh not possible)')}")
        print(f"    last_token_refresh_at    = {account.get('last_token_refresh_at')}")
        print(f"    last_token_refresh_error = {account.get('last_token_refresh_error')}")
        print()
    return refreshable


def force_refresh(tokens: list[str]) -> None:
    """对每个账号 force 刷新一次，并对比前后状态判断成败。"""
    if not tokens:
        print('No accounts with a refresh_token were found. Cannot verify token refresh.')
        return
    print("=" * 60)
    print(f'Starting forced refresh for {len(tokens)} accounts (this makes a real request to OpenAI)...\n')
    ok = 0
    for token in tokens:
        before = account_service.get_account(token) or {}
        try:
            new_token = account_service.force_refresh_access_token(token, event="manual_verify")
        except TerminalRefreshTokenError as exc:
            print(f"- email={before.get('email') or '(unknown)'}")
            print(f'    old access_token[:20] = {token[:20]}...')
            print(f'    >>> Refresh result = terminal invalid ❌ ({exc})')
            print()
            continue
        except RefreshCredentialsChangedError as exc:
            print(f"- email={before.get('email') or '(unknown)'}")
            print(f'    old access_token[:20] = {token[:20]}...')
            print(f'    >>> Refresh result = credentials changed; skipped ({exc})')
            print()
            continue
        after = account_service.get_account(new_token) or {}
        err = str(after.get("last_token_refresh_error") or "").strip()
        rotated = new_token != token
        success = bool(new_token) and not err
        if success:
            ok += 1
        print(f"- email={before.get('email') or '(unknown)'}")
        print(f'    old access_token[:20] = {token[:20]}...')
        print(f'    new access_token[:20] = {new_token[:20]}...')
        print(f"    token rotated = {('Yes' if rotated else 'No (the existing token may be returned until exp reaches the refresh window)')}")
        print(f"    last_token_refresh_at    = {after.get('last_token_refresh_at')}")
        print(f"    last_token_refresh_error = {after.get('last_token_refresh_error') or 'None'}")
        print(f"    >>> Refresh result = {('Success ✅' if success else 'Failed ❌')}")
        print()
    print("=" * 60)
    print(f'Summary: {ok}/{len(tokens)} accounts refreshed successfully')
    if ok == len(tokens):
        print('✅ Automatic refresh works for these accounts: the refresh_token and client_id match.')
    else:
        print('❌ Some account refreshes failed. See last_token_refresh_error above or the [oauth-login]/refresh logs in docker logs.')


def main() -> None:
    do_force = "--force" in sys.argv[1:]
    refreshable = diagnose()
    if do_force:
        force_refresh(refreshable)
    else:
        print('Tip: add --force to trigger a real refresh and verify that it succeeds.')


if __name__ == "__main__":
    main()

#!/usr/bin/env python3
"""
argonpass.py  -  Deterministic password generator (Argon2id)

使い方:
  $ python3 argonpass.py example.com
  Master: ******
  (クリップボードにコピー＋標準出力にも表示)

オプション:
  -l, --length N   パスワード長 (デフォ 20)
  -s, --symbols    記号必須モードをオン
  -q, --quiet      画面に出さずクリップボードだけ
  -t N             Argon2 time_cost  (デフォ 3)
  -m KB            Argon2 memory_cost KB (デフォ 32768 = 32 MB)
"""

import argparse, base64, getpass, sys, os
from argon2.low_level import hash_secret_raw, Type     # argon2-cffi
try:
    import pyperclip
    CLIP_OK = True
except ImportError:
    CLIP_OK = False

LOWER   = "abcdefghijklmnopqrstuvwxyz"
UPPER   = "ABCDEFGHIJKLMNOPQRSTUVWXYZ"
DIGITS  = "0123456789"
SYMBOLS = "!@#$%^&*()-_=+[]{}|;:,.<>?/~"

REQ_BASE = {
    "lower":  LOWER,
    "upper":  UPPER,
    "digit":  DIGITS,
}

def derive_key(master: str, site: str,
               time_cost: int, mem_kb: int, parallel: int = 2,
               dklen: int = 64) -> bytes:
    """Argon2idで鍵導出 (戻り値: raw bytes)"""
    # 塩を最低8バイトに拡張
    salt = site.encode()
    while len(salt) < 8:
        salt += b'\x00'
    
    print(f"🔐 パスワード生成中... (time_cost={time_cost}, memory={mem_kb}KB)")
    print("⏳ 数分お待ちください...", end="", flush=True)
    
    result = hash_secret_raw(master.encode(), salt,
                           time_cost=time_cost,
                           memory_cost=mem_kb,
                           parallelism=parallel,
                           hash_len=dklen,
                           type=Type.ID)
    
    print(" ✅ 完了!")
    return result

def sift_chars(dk: bytes, length: int,
               required_sets: dict[str, str]) -> str:
    """派生バイト列→パスワード文字列 (必須集合を保証)"""
    full_pool = ''.join(required_sets.values())
    if length < len(required_sets):
        raise ValueError("length が必須文字種数より短いよ")

    # まず pool から順番に埋める
    pw = [full_pool[b % len(full_pool)] for b in dk][:length]

    # 各必須集合を確認、欠けていたら順次上書き
    idx = 0
    for charset in required_sets.values():
        if not any(c in charset for c in pw):
            pw[idx % length] = charset[dk[idx] % len(charset)]
        idx += 1
    return ''.join(pw)

def main() -> None:
    ap = argparse.ArgumentParser(add_help=False)
    ap.add_argument("site",           help="サイト識別子 (例: github.com)")
    ap.add_argument("-l", "--length", type=int, default=64)
    ap.add_argument("-s", "--symbols", action="store_true",
                    help="記号必須モード (SYMBOLS から1文字)")
    ap.add_argument("-t", type=int, default=42,
                    help="Argon2 time_cost (デフォ 42)")
    ap.add_argument("-m", type=int, default=256*1024,
                    help="Argon2 memory_cost KB (デフォ 262144=256MB)")
    ap.add_argument("-q", "--quiet", action="store_true",
                    help="標準出力を抑制 (クリップボードのみ)")
    if "-h" in sys.argv or "--help" in sys.argv:
        print(__doc__)
        sys.exit(0)
    args = ap.parse_args()

    # 必須文字集合セットアップ
    req_sets = REQ_BASE.copy()
    if args.symbols:
        req_sets["symbol"] = SYMBOLS

    master = getpass.getpass("Master: ")
    dk = derive_key(master, args.site, args.t, args.m)
    # urlsafe base64 → = 削除 → bytes→文字列化
    b64 = base64.urlsafe_b64encode(dk).decode().replace("=", "")
    pw = sift_chars(b64.encode(), args.length, req_sets)

    if CLIP_OK:
        try:
            pyperclip.copy(pw)
            if not args.quiet:
                print(pw, "(copied to clipboard)")
        except:
            print(pw)
    else:
        print(pw)

if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        print("エラー:", e, file=sys.stderr)
        sys.exit(1)

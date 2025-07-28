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

def show_security_profile(time_cost: int, mem_kb: int) -> None:
    """セキュリティプロファイルを表示"""
    profile_name = "Custom"
    estimated_time = "数分"
    
    if time_cost <= 10 and mem_kb <= 65536:
        profile_name = "Fast"
        estimated_time = "30秒～1分"
    elif time_cost <= 25 and mem_kb <= 131072:
        profile_name = "Balanced"  
        estimated_time = "1～2分"
    elif time_cost >= 42:
        profile_name = "Paranoid"
        estimated_time = "2～5分"
    
    print(f"🔒 Security Profile: {profile_name} (time_cost={time_cost}, memory={mem_kb//1024}MB)")
    print(f"⏱️  Estimated wait: ~{estimated_time}")
    print()

def derive_key(master: str, site: str,
               time_cost: int, mem_kb: int, parallel: int = 2,
               dklen: int = 64) -> bytes:
    """Argon2idで鍵導出 (戻り値: raw bytes)"""
    # 塩を最低8バイトに拡張
    salt = site.encode()
    while len(salt) < 8:
        salt += b'\x00'
    
    print("🔐 パスワード生成中...", end="", flush=True)
    
    result = hash_secret_raw(master.encode(), salt,
                           time_cost=time_cost,
                           memory_cost=mem_kb,
                           parallelism=parallel,
                           hash_len=dklen,
                           type=Type.ID)
    
    print(" ✅ 完了!")
    print(f"📋 Generated with: t={time_cost}, m={mem_kb//1024}MB (keep these settings for reproduction)")
    print()
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
    ap.add_argument("--mode", choices=["fast", "balanced", "paranoid"], 
                    help="セキュリティモード: fast(30秒), balanced(1-2分), paranoid(2-5分)")
    ap.add_argument("-t", type=int, 
                    help="Argon2 time_cost (デフォ 42, --modeで上書き可)")
    ap.add_argument("-m", type=int,
                    help="Argon2 memory_cost KB (デフォ 262144=256MB, --modeで上書き可)")
    ap.add_argument("-q", "--quiet", action="store_true",
                    help="標準出力を抑制 (クリップボードのみ)")
    if "-h" in sys.argv or "--help" in sys.argv:
        print(__doc__)
        sys.exit(0)
    args = ap.parse_args()
    
    # モード別デフォルト設定
    if args.mode == "fast":
        time_cost = args.t if args.t else 10
        mem_cost = args.m if args.m else 65536  # 64MB
    elif args.mode == "balanced":
        time_cost = args.t if args.t else 25
        mem_cost = args.m if args.m else 131072  # 128MB
    elif args.mode == "paranoid":
        time_cost = args.t if args.t else 50
        mem_cost = args.m if args.m else 524288  # 512MB
    else:
        # デフォルト（従来のParanoid相当）
        time_cost = args.t if args.t else 42
        mem_cost = args.m if args.m else 256*1024  # 256MB

    # セキュリティプロファイル表示
    if not args.quiet:
        show_security_profile(time_cost, mem_cost)

    # 必須文字集合セットアップ
    req_sets = REQ_BASE.copy()
    if args.symbols:
        req_sets["symbol"] = SYMBOLS

    # マスターパスワードの確認入力
    while True:
        master = getpass.getpass("Master: ")
        master_confirm = getpass.getpass("Confirm Master: ")
        
        if master == master_confirm:
            break
        else:
            print("❌ パスワードが一致しません。再入力してください。")
    
    dk = derive_key(master, args.site, time_cost, mem_cost)
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

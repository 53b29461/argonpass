# argonpass – 強力なパスワード生成器

固定文字列（マスターキー）と任意文字列（サービス名やURLなど）から強力なパスワードを生成する

コアには **Argon2id**（メモリハードな KDF）を採用しています

---

## 特長

* **オフライン完結**: ネットワークにもクラウドにも依存しない
* **超強力なArgon2id**: 既定で *time_cost 42*・*メモリ 256 MB*（数分の計算時間）
* **64文字デフォルト**: より強固なパスワード長
* **記号必須スイッチ**: パスワードポリシーに合わせて簡単切替
* **進行表示**: 重い計算中もプログレス表示で安心
* **クリップボード自動コピー**（pyperclip）バックエンドが無い場合は標準出力へフォールバック
* Python 3.8 以降、仮想環境でもグローバルでも動作

---

## クイックスタート

```bash
# 1) リポジトリをクローン
git clone https://github.com/53b29461/argonpass.git
cd argonpass

# 2) 依存パッケージをインストール
pip install argon2-cffi pyperclip

# 3) 強力なパスワード生成（64文字・記号付き）
python3 argonpass.py "your-service" -s
🔒 Security Profile: Paranoid (time_cost=42, memory=256MB)
⏱️  Estimated wait: ~2～5分

Master: [覚えやすい秘密の文字列]
🔐 パスワード生成中... ✅ 完了!
📋 Generated with: t=42, m=256MB (keep these settings for reproduction)

aB3$xY9#mN2kP8qR... (copied to clipboard)
```

---

## 使用例

| 目的                                       | コマンド例                                       |
| ---------------------------------------- | ------------------------------------------- |
| **1. 標準の強力パスワード（64文字・記号付き）**        | `python3 argonpass.py "github.com" -s`          |
| **2. 高速生成モード（30秒～1分）**                | `python3 argonpass.py "test.local" --mode fast -s`    |
| **3. バランスモード（1～2分）**                   | `python3 argonpass.py "work.com" --mode balanced -s`        |
| **4. 超強力モード（10分級）**                   | `python3 argonpass.py "bank.jp" --mode paranoid -s` |
| **5. カスタム設定**              | `python3 argonpass.py "custom" -t 30 -m 400000 -s` |

> 同じ **マスターキー** と **サイト識別子** を入力すれば、常に同じパスワードが得られます

---

## コマンドラインオプション

```text
-l, --length N      パスワード長を設定（既定 64）
-s, --symbols       記号を含める（推奨）
--mode MODE         セキュリティモード：fast(30秒), balanced(1-2分), paranoid(2-5分)
-q, --quiet         画面に生成パスワードを表示しない
-t N                Argon2 time_cost（既定 42、--modeで上書き可）
-m KB               Argon2 memory_cost（KB単位、既定 262144=256MB、--modeで上書き可）
```

### セキュリティモード詳細

| モード      | time_cost | memory | 推定時間  | 用途           |
| ---------- | --------- | ------ | -------- | -------------- |
| fast       | 10        | 64MB   | 30秒～1分 | テスト・軽量用途 |
| balanced   | 25        | 128MB  | 1～2分   | 日常的な用途    |
| paranoid   | 50        | 512MB  | 2～10分  | 最重要アカウント |
| デフォルト   | 42        | 256MB  | 2～5分   | 推奨設定       |

---

## クリップボードについて

一部環境ではクリップボードへのコピーが行われない場合があります

`pyperclip` は OS ごとのバックエンドを自動検出します

| 環境          | 必要パッケージ                             | 備考                           |
| ----------- | ----------------------------------- | ---------------------------- |
| X11 系 Linux | `sudo apt install xclip` または `xsel` | 最も手軽な方法                      |
| Wayland     | `sudo apt install wl-clipboard`     | `wl-copy` / `wl-paste` が利用可能 |
| WSL2        | `sudo apt install wsl-clipboard`    | Windows のクリップボードと連携          |

バックエンドが見つからない場合、スクリプトは自動で標準出力のみを使います。

---

## セキュリティ運用ヒント

* **マスターキー**: 覚えやすく他人に推測されない文字列を推奨
* **公共PC使用**: ネットカフェ等では使用後にプログラムとファイルを完全削除
* **パラメータ調整**: `-t` と `-m` で計算時間を調整可能（重いほど安全）
* **記号必須**: `-s` オプションでパスワード強度が大幅向上
* **履歴対策**: マスターキーをシェル履歴やソースコードに残さない
* **デバイス別運用**: 各デバイスで同じマスター+サイト名で同一パスワード生成可能
* **ブルートフォース耐性**: デフォルト設定で攻撃者に数年〜数十年の計算時間を強制

---

## 実用的な運用例

### 重要アカウント用の超強力パスワード
```bash
python3 argonpass.py "my-bank-account" -s
# → 銀行など重要サービス用の64文字超強力パスワード
```

### 複数デバイスでの同期運用
```bash
# 全デバイスで同じコマンド・同じマスターキー
python3 argonpass.py "gmail" -s
# → どのデバイスでも同じパスワードが生成される
```

### 日常的なパスワード管理

**📝 サイト一覧メモ（password_sites.txt）**
```
# サービス名 | ログインURL | サイト識別子
Gmail       | https://gmail.com           | gmail
GitHub      | https://github.com/login    | github  
Amazon      | https://amazon.co.jp        | amazon-jp
Netflix     | https://netflix.com         | netflix
銀行        | https://bank.example.jp     | mybank
楽天        | https://rakuten.co.jp       | rakuten
```

**🔐 パスワード生成（必要な時だけ）**
```bash
# ログイン時にメモを見ながら生成
python3 argonpass.py "gmail" -s
python3 argonpass.py "github" -s  
python3 argonpass.py "amazon-jp" -s
```

**💡 運用のコツ**
- メモは**サイト識別子だけ**記録（パスワードは書かない）
- 同じマスターキーで全サービス管理
- ログイン時に毎回生成すれば記憶不要
- メモが漏れても識別子だけなので安全

### セキュリティレベル別設定
```bash
# 高速（テスト・開発用）
python3 argonpass.py "test" --mode fast -s

# バランス（日常的なサービス）
python3 argonpass.py "service" --mode balanced -s

# 最強（銀行・重要アカウント）
python3 argonpass.py "bank" --mode paranoid -s

# デフォルト（推奨設定）
python3 argonpass.py "gmail" -s
```

### 実行例と設定記録
```bash
$ python3 argonpass.py "my-bank" --mode paranoid -s
🔒 Security Profile: Paranoid (time_cost=50, memory=512MB)
⏱️  Estimated wait: ~2～10分

Master: ********
🔐 パスワード生成中... ✅ 完了!
📋 Generated with: t=50, m=512MB (keep these settings for reproduction)

aB3$xY9#mN2kP8qR7wX4... (copied to clipboard)
```

**💡 再現時のメモ:**
- サイト識別子: `my-bank` 
- 設定: `t=50, m=512MB`
- 別デバイスでも同じ設定で同一パスワード生成可能

---

## ライセンス

MIT License © 2025 53b29461
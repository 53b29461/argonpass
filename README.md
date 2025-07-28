# pwgen.py – 強力なパスワード生成器

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
git clone https://github.com/53b29461/pass_gene.git
cd pass_gene

# 2) 依存パッケージをインストール
pip install argon2-cffi pyperclip

# 3) 強力なパスワード生成（64文字・記号付き）
python3 pwgen.py "your-service" -s
Master: [覚えやすい秘密の文字列]
🔐 パスワード生成中... (time_cost=42, memory=262144KB)
⏳ 数分お待ちください... ✅ 完了!
aB3$xY9#mN2kP8qR... (copied to clipboard)
```

---

## 使用例

| 目的                                       | コマンド例                                       |
| ---------------------------------------- | ------------------------------------------- |
| **1. 標準の強力パスワード（64文字・記号付き）**        | `python3 pwgen.py "github.com" -s`          |
| **2. パスワード長を32文字にする**                | `python3 pwgen.py "reddit.com" -s -l 32`    |
| **3. 画面に結果を表示しない**                   | `python3 pwgen.py "bank.jp" --quiet`        |
| **4. 軽量版（短時間で生成）**                   | `python3 pwgen.py "test.local" -t 10 -m 32768` |
| **5. 超強力版（10分級の計算時間）**              | `python3 pwgen.py "critical.app" -t 50 -m 1048576` |

> 同じ **マスターキー** と **サイト識別子** を入力すれば、常に同じパスワードが得られます

---

## コマンドラインオプション

```text
-l, --length N      パスワード長を設定（既定 64）
-s, --symbols       記号を含める（推奨）
-q, --quiet         画面に生成パスワードを表示しない
-t N                Argon2 time_cost（既定 42、数分の計算時間）
-m KB               Argon2 memory_cost（KB 単位、既定 262144 = 256 MB）
```

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
python3 pwgen.py "my-bank-account" -s
# → 銀行など重要サービス用の64文字超強力パスワード
```

### 複数デバイスでの同期運用
```bash
# 全デバイスで同じコマンド・同じマスターキー
python3 pwgen.py "gmail" -s
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
python3 pwgen.py "gmail" -s
python3 pwgen.py "github" -s  
python3 pwgen.py "amazon-jp" -s
```

**💡 運用のコツ**
- メモは**サイト識別子だけ**記録（パスワードは書かない）
- 同じマスターキーで全サービス管理
- ログイン時に毎回生成すれば記憶不要
- メモが漏れても識別子だけなので安全

### セキュリティレベル別設定
```bash
# 軽量（テスト用）
python3 pwgen.py "test" -t 5 -m 16384

# 標準（日常用）
python3 pwgen.py "service" -s

# 最強（重要アカウント用）
python3 pwgen.py "bank" -s -t 50 -m 1048576
```

---

## ライセンス

MIT License © 2025 53b29461
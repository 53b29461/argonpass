# pwgen.py – パスワード生成

固定文字列（マスターキー）と任意文字列（サービス名やURLなど）からパスワードを生成する

コアには **Argon2id**（メモリハードな KDF）を採用しています

---

## 特長

* **オフライン完結**: ネットワークにもクラウドにも依存しない
* **Argon2id**: 既定で *time\_cost 3*・*メモリ 32 MB*
* **記号必須スイッチ**: パスワードポリシーに合わせて簡単切替
* **クリップボード自動コピー**（pyperclip）バックエンドが無い場合は標準出力へフォールバック
* Python 3.8 以降、仮想環境でもグローバルでも動作

---

## インストール手順

```bash
# 1) 仮想環境を作成（推奨）
python3 -m venv .venv
source .venv/bin/activate   # Windows は .venv\Scripts\Activate.ps1

# 2) 依存パッケージをインストール
pip install --upgrade pip
pip install argon2-cffi pyperclip
```

---

## 使い方（最短）

```bash
python pwgen.py github.com
Master: ******** ********
F6uJbX8KzEjcNQoIgTLa (copied to clipboard)
```

---

## 使用例

| 目的                                       | コマンド例                                       |
| ---------------------------------------- | ------------------------------------------- |
| **1. 一番シンプルな起動**                       | `python pwgen.py example.com`               |
| **2. パスワード長を24文字にする**                        | `python pwgen.py reddit.com -s -l 24`       |
| **3. クリップボードにコピーしない**                   | `python pwgen.py bank.jp --quiet`           |
| **4. より頑丈なパスワード（time\_cost 5・メモリ 64 MB）** | `python pwgen.py vault.local -t 5 -m 65536` |

> 同じ **マスターキー** と **サイト識別子** を入力すれば、常に同じパスワードが得られます

---

## コマンドラインオプション

```text
-l, --length N      パスワード長を設定（既定 20）
-s, --symbols       記号を含める
-q, --quiet         画面に生成パスワードを表示しない
-t N                Argon2 time_cost（既定 3）
-m KB               Argon2 memory_cost（KB 単位、既定 32768 = 32 MB）
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

* 覚えやすく長めのマスターキーを推奨。
* 公共 PC での使用は避け、自宅や業務端末でも画面覗き見に注意。
* KDF パラメータは端末性能を見ながら `-t` と `-m` で重く調整可能。
* マスターキーをソースや履歴に埋め込まないこと。

---

## ライセンス

MIT License © 2025 53b29461

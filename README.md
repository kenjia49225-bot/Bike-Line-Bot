# Bike-Line-Bot

自転車販売・修理店向けの LINE 問い合わせ Bot です。店舗に届く問い合わせの一部を AI で自動回答し、AI で回答できない問い合わせは人間（店舗スタッフ）へ引き継ぐことを想定しています。

## 現在の実装状況

現時点で実装済みの内容は以下のとおりです。

- Django プロジェクト初期構築（`config`）
- MySQL 接続（環境変数による接続設定）
- `stores` アプリ（店舗情報）
  - `Store` モデル（店舗名・営業時間・定休日・アクセス・支払い方法・電話番号・住所）
  - Django Admin への登録（一覧表示・検索）
  - `Store` モデルのテスト

LINE Messaging API・AI API 連携、FAQ・会話履歴などは**まだ実装されていません**。

## 技術スタック

- Python 3.12
- Django 5.2.17
- MySQL（本番想定）
- LINE Messaging API（未実装）
- AI API（未実装）

## ディレクトリ構成

```
Bike-Line-Bot/
├── config/                    # Django プロジェクト本体
│   ├── __init__.py
│   ├── settings.py            # プロジェクト設定
│   ├── urls.py                # URL ルーティング
│   ├── wsgi.py
│   └── asgi.py
├── stores/                    # 店舗情報アプリ（実装済み）
│   ├── __init__.py
│   ├── apps.py                # アプリ設定
│   ├── models.py              # Store モデル
│   ├── admin.py               # Django Admin 登録
│   ├── tests.py               # Store モデルのテスト
│   └── migrations/            # マイグレーション
│       ├── __init__.py
│       └── 0001_initial.py
├── manage.py
├── requirements.txt
├── .env.example               # 環境変数の雛形
└── .gitignore
```

以下のファイルはローカル環境のみに存在し、Git では管理していません。

- `.env`（実際の環境変数。秘密情報を含むためコミットしない）
- `.venv/`（Python 仮想環境）

### 今後のアプリ分割方針（予定）

以下のアプリは**今後追加予定**です（現時点では存在しません）。

- `faqs` … FAQ 管理
- `bot` … LINE 連携・Webhook
- `conversations` … 会話履歴

## セットアップ手順

```bash
# 1. リポジトリをクローン
git clone <repository-url>
cd Bike-Line-Bot

# 2. 仮想環境を作成して有効化
python3 -m venv .venv
source .venv/bin/activate

# 3. 依存パッケージをインストール
pip install -r requirements.txt

# 4. 環境変数を設定（.env.example をコピーして実値を入力）
cp .env.example .env
# .env の DJANGO_SECRET_KEY と MYSQL_* を実際の値に置き換える

# 5. マイグレーション
python manage.py migrate

# 6. 管理ユーザーを作成（Django Admin ログイン用）
python manage.py createsuperuser

# 7. 開発サーバー起動
python manage.py runserver
```

`http://127.0.0.1:8000/` にアクセスすると起動確認できます。
Django Admin は `http://127.0.0.1:8000/admin/` から利用できます。

> 秘密情報（`.env`）は Git にコミットしないでください。実値は共有せず、`.env.example` を雛形として使用します。

## 環境変数

`.env` に設定する環境変数です（雛形は `.env.example`）。実際の値は README に記載しません。

| 変数名 | 説明 |
| --- | --- |
| `DJANGO_SECRET_KEY` | Django のシークレットキー |
| `DEBUG` | デバッグモードの有効化（`True` / `False`） |
| `ALLOWED_HOSTS` | 許可するホスト（カンマ区切り） |
| `MYSQL_DATABASE` | MySQL のデータベース名 |
| `MYSQL_USER` | MySQL のユーザー名 |
| `MYSQL_PASSWORD` | MySQL のパスワード |
| `MYSQL_HOST` | MySQL のホスト |
| `MYSQL_PORT` | MySQL のポート |

## 開発コマンド

```bash
# マイグレーションファイルの作成
python manage.py makemigrations

# マイグレーションの適用
python manage.py migrate

# プロジェクト設定のチェック
python manage.py check

# テストの実行
python manage.py test

# 開発サーバーの起動
python manage.py runserver
```

## 今後の開発予定

優先順位の高い順に記載しています（内容は今後変更される可能性があります）。

1. **FAQ 管理** … 店舗に寄せられるよくある質問と回答の管理（`faqs` アプリ）
2. **会話履歴** … ユーザーとの会話ログの保存（`conversations` アプリ）
3. **LINE Webhook** … LINE Messaging API との連携（`bot` アプリ）
4. **AI 自動回答** … FAQ・店舗情報を参照した AI による自動応答
5. **人間への引き継ぎ** … AI で回答できない問い合わせを店舗スタッフへ引き継ぐ仕組み
6. **テスト・エラー処理** … テストの充実とエラーハンドリングの整備

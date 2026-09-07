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
- `faqs` アプリ（FAQ 管理）
  - `FAQ` モデル（質問文・回答文・公開状態・作成/更新日時）
  - Django Admin への登録（検索・公開状態の一覧切替）
  - `FAQ` モデルのテスト
- `conversations` アプリ（会話履歴）
  - `Conversation` モデル（ユーザー識別子・発言者・内容・要引き継ぎ・対応状況・作成日時）
  - Django Admin への登録（要引き継ぎ・対応状況の一覧切替）
  - `Conversation` モデルのテスト
- `bot` アプリ（LINE 連携・AI 回答）
  - LINE Messaging API の Webhook 受信（`/bot/webhook/`）
  - 受信メッセージの会話履歴への保存
  - AI（OpenAI）による自動回答（FAQ・店舗情報を参照）
  - 直近の会話履歴を文脈として AI に渡すマルチターン対応
  - FAQ の簡易セマンティック検索（関連 FAQ のみ AI に注入）
  - 営業時間・定休日の動的判定（`Store.is_open_now`）
  - AI で回答できない場合は人間（店舗スタッフ）への引き継ぎメッセージを返す
  - 画像メッセージの受信（要引き継ぎとして保存）
  - ユーザー単位のレート制限（スパム対策）
  - LINE プッシュメッセージ送信（管理コマンド `send_line_message`）
  - Webhook・AI・引き継ぎのテスト

## 技術スタック

- Python 3.12
- Django 5.2.17
- MySQL（本番想定）
- LINE Messaging API（`line-bot-sdk`）
- AI API（OpenAI）

## ディレクトリ構成

```
Bike-Line-Bot/
├── config/                    # Django プロジェクト本体
│   ├── __init__.py
│   ├── settings.py            # プロジェクト設定
│   ├── urls.py                # URL ルーティング
│   ├── wsgi.py
│   └── asgi.py
├── stores/                    # 店舗情報アプリ
│   ├── models.py              # Store モデル
│   ├── admin.py               # Django Admin 登録
│   ├── tests.py
│   └── migrations/
├── faqs/                      # FAQ 管理アプリ
│   ├── models.py              # FAQ モデル
│   ├── admin.py               # Django Admin 登録
│   ├── tests.py
│   └── migrations/
├── conversations/             # 会話履歴アプリ
│   ├── models.py              # Conversation モデル
│   ├── admin.py               # Django Admin 登録
│   ├── tests.py
│   └── migrations/
├── bot/                       # LINE 連携・AI 回答アプリ
│   ├── views.py               # Webhook 受信
│   ├── urls.py                # Webhook URL ルーティング
│   ├── services.py            # メッセージ保存・応答の振り分け
│   ├── ai.py                  # AI 回答生成・人間への引き継ぎ判定
│   └── tests.py               # Webhook・AI・引き継ぎのテスト
├── manage.py
├── requirements.txt
├── .env.example               # 環境変数の雛形
└── .gitignore
```

以下のファイルはローカル環境のみに存在し、Git では管理していません。

- `.env`（実際の環境変数。秘密情報を含むためコミットしない）
- `.venv/`（Python 仮想環境）

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
| `LINE_CHANNEL_SECRET` | LINE チャネルシークレット |
| `LINE_CHANNEL_ACCESS_TOKEN` | LINE チャネルアクセストークン |
| `OPENAI_API_KEY` | OpenAI API キー |
| `OPENAI_MODEL` | 使用する OpenAI モデル（デフォルト: `gpt-4o-mini`） |
| `RATE_LIMIT_MAX` | 1ユーザーあたりの最大メッセージ数（デフォルト: `10`） |
| `RATE_LIMIT_WINDOW` | レート制限のウィンドウ秒数（デフォルト: `60`） |

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

# LINE プッシュメッセージ送信（人間からの返信など）
python manage.py send_line_message <LINEユーザーID> <本文>
```

## 今後の開発予定

優先順位の高い順に記載しています（内容は今後変更される可能性があります）。

1. **人間への引き継ぎの実運用** … 引き継ぎ先スタッフへの通知（LINE Notify 等）・Admin からの返信 UI
2. **FAQ のセマンティック検索強化** … 埋め込みベースの検索（現状は簡易的な文字オーバーラップ）
3. **予約・修理受付** … 日時指定の予約フロー
4. **エラー処理の強化** … リトライ・ログ・監視の整備
5. **本番デプロイ** … WSGI サーバー移行・`DEBUG=False`・固定ドメイン設定

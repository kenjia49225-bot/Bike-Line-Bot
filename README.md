# Bike-Line-Bot

自転車販売・修理店向けの LINE 問い合わせ Bot です。店舗に届く問い合わせの一部を AI で自動回答し、回答できない問い合わせは店舗スタッフへ引き継ぎます。

## 技術スタック

- Python 3.12 / Django 5.2
- MySQL（本番想定）
- LINE Messaging API（未実装）
- AI API（未実装）

## ディレクトリ構成

```
config/   # Django プロジェクト本体（settings, urls, wsgi, asgi）
```

### 今後のアプリ分割方針

- `stores` … 店舗情報（営業時間・定休日・アクセス等）
- `faqs` … FAQ
- `bot` … LINE 連携・Webhook
- `conversations` … 会話履歴

## ローカル開発環境の起動方法

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

# 6. 開発サーバー起動
python manage.py runserver
```

`http://127.0.0.1:8000/` にアクセスすると起動確認できます。

> 秘密情報（`.env`）は Git にコミットしないでください。実値は共有せず、`.env.example` を雛形として使用します。

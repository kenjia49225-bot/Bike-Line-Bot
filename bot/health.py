from django.db import connection
from django.http import JsonResponse


def health(request):
    """ヘルスチェック。DB 接続も確認する。"""
    try:
        with connection.cursor() as cursor:
            cursor.execute('SELECT 1')
            cursor.fetchone()
        db_ok = True
    except Exception:  # noqa: BLE001
        db_ok = False

    status = 200 if db_ok else 503
    return JsonResponse({'status': 'ok' if db_ok else 'error', 'database': 'ok' if db_ok else 'unavailable'}, status=status)

from django.contrib.auth.models import AnonymousUser

from auth_api.authentication import decode_and_validate


class JWTAuthMiddleware:
    """Устанавливает request.user по JWT до обработки view.

    Полезно для не-DRF view и соответствует требованиям ТЗ по middleware.
    """

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        auth_header = request.headers.get('Authorization') or ''
        auth_header = auth_header.strip()

        if auth_header.lower().startswith('bearer '):
            token = auth_header.split(' ', 1)[1].strip()
            try:
                user, _session = decode_and_validate(token)
                request.user = user
                request.auth = token
            except Exception:
                # Не ломаем весь сайт: DRF сам отдаст 401/403 в API.
                # Здесь оставляем анонимного.
                request.user = getattr(request, 'user', AnonymousUser())
                request.auth = None

        return self.get_response(request)

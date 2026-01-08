# Мок-хранилище бизнес-объектов (без БД).
# По ТЗ допускается имитация ресурсов без таблиц.

from typing import Dict, List

MOCK_DATA: Dict[str, List[dict]] = {
    'recipes': [
        {'id': 1, 'owner_id': 1, 'title': 'Mock recipe #1'},
        {'id': 2, 'owner_id': 2, 'title': 'Mock recipe #2'},
    ],
    'orders': [
        {'id': 1, 'owner_id': 2, 'status': 'created'},
    ],
    'shops': [
        {'id': 1, 'owner_id': 1, 'name': 'Mock shop'},
    ],
    'users': [
        {'id': 1, 'owner_id': 1, 'email': 'admin@example.com'},
    ],
}


def get_next_id(element: str) -> int:
    items = MOCK_DATA.get(element, [])
    return (max([i['id'] for i in items]) + 1) if items else 1

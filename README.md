## Обзор архитектуры

Система управления доступом на основе ролей с JWT аутентификацией и разрешениями.

## Структура базы данных

User (1) ──── (m) UserToRole (m) ──── (1) Role (1) ──── (m) RoleToPermission (m) ──── (1) Permission

## Основные компоненты

### 1. **Слой аутентификации**
- **JWT токены**: Access + Refresh токены с ролями пользователя
- **Middleware**: `JWTAuthMiddleware` проверяет токены и извлекает роли и разрешения для пользователя
- **Типы токенов**:
  - Access Token (короткоживущий)
  - Refresh Token (долгоживущий)

### 2. **Декораторы авторизации**

```python
@requires_authenticated()              # Любой аутентифицированный пользователь
@requires_permission("user", "read")   # Конкретное разрешение: ресурс:действие
@requires_role("admin")                # Конкретная роль
@requires_any_role("admin", "moderator") # Любая из нескольких ролей
```

- **Пример использования:**
```python
@router.post("/create", response_model=RoleResponse)
@requires_permission("role", "create")
async def create_role(request: Request, role_data: RoleCreate):
    role = await RoleService().create(role_data)
    return role
```

### 3. **Процесс проверки доступа**

- **Логин пользователя**: Генерация JWT токенов с ролями пользователя
- **API запрос**: Middleware проверяет токен и извлекает разрешения
- **Доступ к endpoint**: Декораторы проверяют требуемые разрешения
- **Решение о доступе**: Разрешение/запрет на основе учетных данных пользователя 

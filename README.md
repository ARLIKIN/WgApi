# WireGuard User Management API

API для управления пользователями WireGuard и их конфигурациями. 

## Версия
- **OpenAPI**: 3.0.0
- **Версия API**: 1.0.0

<h2>Быстрая установка WireGuard и API:</h2>

```bash
sudo wget https://github.com/ARLIKIN/WgApi/releases/download/download/Wireguard-installer-with-Adminpanel.sh && chmod 774 Wireguard-installer-with-Adminpanel.sh && ./Wireguard-installer-with-Adminpanel.sh
```
- после настройки WireGuard появится окно выбора: `Hotite li ustanovit' srazu API(1 - Da, 0 - Net)::` Нажмите 1 если хотите установить API

<h3>Управление API:</h3>

```bash
sudo systemctl status ApiWg
```

<h3>Start</h3>

```bash
sudo systemctl start ApiWg
```

<h3>Stop</h3>

```bash
sudo systemctl stop ApiWg
```

<h3>Restart</h3>

```bash
sudo systemctl restart ApiWg
```

## Сервер
- **URL**: `http://localhost:8080`
- **Описание**: Сервер разработки

## Методы API

### 1. GET `/len`
Возвращает количество пользователей, основываясь на файлах конфигурации в директории `wg/static`.

- **Аутентификация**: требуется
- **Ответы**:
  - `200 OK`:
    ```json
    {
      "success": true,
      "user_count": 5
    }
    ```
  - `401 UNAUTHORIZED`: если аутентификация не пройдена.
  - `500 INTERNAL SERVER ERROR`: если возникает ошибка при подсчёте.

### 2. POST `/createWG`
Создаёт нового пользователя WireGuard и генерирует его конфигурацию.

- **Тело запроса (JSON)**:
    ```json
    {
      "name_key": "имя_пользователя"
    }
    ```
- **Аутентификация**: требуется
- **Ответы**:
  - `200 OK`: успешное создание и возвращение конфигурации.
    ```json
    {
      "success": true,
      "config": "содержимое конфигурации"
    }
    ```
  - `400 BAD REQUEST`: если `name_key` не указан.
  - `404 NOT FOUND`: если шаблон конфигурации не найден.
  - `500 INTERNAL SERVER ERROR`: если команда создания пользователя не выполнена.

### 3. DELETE `/deleteWG`
Удаляет пользователя WireGuard и его конфигурацию.

- **Тело запроса (JSON)**:
    ```json
    {
      "name_key": "имя_пользователя"
    }
    ```
- **Аутентификация**: требуется
- **Ответы**:
  - `200 OK`: успешное удаление пользователя.
    ```json
    {
      "success": true
    }
    ```
  - `400 BAD REQUEST`: если `name_key` не указан.
  - `500 INTERNAL SERVER ERROR`: если команда удаления пользователя не выполнена.

### 4. GET `/getConfig`
Возвращает конфигурацию пользователя по имени.

- **Тело запроса (JSON)**:
    ```json
    {
      "name_key": "имя_пользователя"
    }
    ```
- **Аутентификация**: требуется
- **Ответы**:
  - `200 OK`: 
    ```json
    {
      "success": true,
      "config": "содержимое конфигурации"
    }
    ```
  - `400 BAD REQUEST`: если `name_key` не указан.
  - `404 NOT FOUND`: если конфигурация не найдена.

### 5. GET `/users`
Возвращает список имен всех файлов конфигураций из директории `wg/static`.

- **Аутентификация**: требуется
- **Ответы**:
  - `200 OK`:
    ```json
    {
      "success": true,
      "users": ["wg0-client-1", "wg0-client-2", "wg0-client-2"]
    }
    ```
  - `500 INTERNAL SERVER ERROR`: если возникает ошибка при получении пользователей.

## Компоненты

### Схемы безопасности
- **Basic Auth**: HTTP Basic Authentication используется для всех маршрутов, требующих аутентификации.

## Декораторы и функции

### `auth_required`
Проверяет базовую авторизацию для доступа к маршрутам. Если аутентификация не пройдена, возвращает `401 UNAUTHORIZED`.

### `execute_command(command, app)`
Выполняет команду в shell. Если возникает ошибку, логирует её и возвращает `False`.

### `read_config(key)`
Читает и возвращает содержимое конфигурационного файла пользователя по его ключу (`name_key`). Если файл не найден, возвращает `None`.

### `error_check_exist_user_id()`
Возвращает ошибку `400 BAD REQUEST`, если идентификатор пользователя (`name_key`) не указан.

### `error_not_found_config()`
Возвращает ошибку `404 NOT FOUND`, если конфигурация пользователя не найдена.

### `return_config(config_content)`
Возвращает содержимое конфигурации пользователя с кодом `200 OK`.

---


### Сэк используемых технологий
 * [**Python 3.11**](https://www.python.org/downloads/release/python-390/)
 * [**Flask 3.0.3**](https://flask.palletsprojects.com/en/3.0.x/)


### Список разработчиков проекта:
* [**ARLIKIN**](https://github.com/ARLIKIN)
* [**Obi0Wan0Kenobi**](https://github.com/Obi0Wan0Kenobi)
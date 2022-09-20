## Инструкция по разворачиванию локального сервера

1. Создать виртуальное окружение `pipenv --python 3.9 shell`
2. Установить зависимости `pipenv install`
(Если возникнут проблемы с lock файлом, то можно сгенерировать pipfile.lock файл `pipenv lock` после чего повторить 2 пункт)
3. Запустить Docker контейнеры `docker-compose up`
4. Создать .env файл на основе .env.template и заполнить
(P.S. креды не должны попадать в репозиторий, но для быстрой локальной проверки приложил
`DATABASE_URL=postgresql://postgres:postgres@localhost:5431/webdb`)


Для активации pre-commit хуков выполнить команду:
`pre-commit install`

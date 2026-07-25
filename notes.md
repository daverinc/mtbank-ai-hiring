### Что нужно сделать

#### 1. Установи `ffmpeg`

**Для Ubuntu / Debian / Linux (самый частый случай):**

```bash
sudo apt update
sudo apt install ffmpeg -y
```

**Для macOS:**

```bash
brew install ffmpeg
```

**Для Arch / Manjaro:**

```bash
sudo pacman -S ffmpeg
```

#### 2. Проверь установку

После установки выполни:

```bash
ffmpeg -version
ffprobe -version
```
```
dockerdeployer@demo:~/mtbank-ai-hiring$ git push origin dev
git@github.com: Permission denied (publickey).
fatal: Could not read from remote repository.

Please make sure you have the correct access rights
and the repository exists.
dockerdeployer@demo:~/mtbank-ai-hiring$ eval "$(ssh-agent -s)"
Agent pid 16919
dockerdeployer@demo:~/mtbank-ai-hiring$ ssh-add ~/.ssh/
demo             demo.pub         demobank         demobank.pub     known_hosts      known_hosts.old  
dockerdeployer@demo:~/mtbank-ai-hiring$ ssh-add ~/.ssh/
demo             demo.pub         demobank         demobank.pub     known_hosts      known_hosts.old  
dockerdeployer@demo:~/mtbank-ai-hiring$ ssh-add ~/.ssh/demobank
```

### Как пользоваться `Makefile`

`Makefile` — это удобный способ запускать часто используемые команды одной короткой командой (`make something`), вместо того чтобы каждый раз писать длинные команды.

### 1. Как посмотреть все доступные команды

Самый простой способ — выполнить:

```bash
make help
```

Эта команда выведет список всех доступных целей (команд) с описанием.

### 2. Основные команды

Вот самые часто используемые команды из твоего `Makefile`:

| Команда                    | Что делает                                      | Когда использовать                  |
|---------------------------|--------------------------------------------------|-------------------------------------|
| `make up`                 | Запускает все сервисы в фоне                     | Основная команда запуска проекта    |
| `make down`               | Останавливает все сервисы                        | Остановка проекта                   |
| `make restart`            | Перезапускает все сервисы                        | После изменения конфигурации        |
| `make build`              | Пересобирает образы без кэша                     | После изменения Dockerfile          |
| `make logs`               | Показывает логи контейнера `api`                 | Отладка API                         |
| `make logs-pipelines`     | Показывает логи Pipeline                         | Отладка Pipeline                    |
| `make logs-webui`         | Показывает логи OpenWebUI                        | Отладка OpenWebUI                   |
| `make clean`              | Полностью останавливает проект и удаляет volumes | Полная очистка                      |
| `make test`               | Запускает все тесты                              | Проверка тестов                     |
| `make coverage`           | Запускает тесты + генерирует HTML-отчёт покрытия | Анализ покрытия тестами             |
| `make wer`                | Считает WER по тестовым файлам                   | Проверка качества ASR               |

### 3. Примеры использования

```bash
# Запустить проект
make up

# Посмотреть логи Pipeline
make logs-pipelines

# Перезапустить проект
make restart

# Запустить тесты
make test

# Посмотреть покрытие тестами
make coverage

# Посчитать WER
make wer

# Полностью очистить проект
make clean
```

### 4. Полезные советы

- **Всегда начинай с `make help`** — это самый быстрый способ понять, какие команды доступны.
- Если команда не работает, убедись, что ты находишься в папке с `Makefile`.
- Можно запускать несколько команд подряд:
  ```bash
  make down && make build && make up
  ```
- `make` по умолчанию выполняет первую цель в файле. У тебя это `help`, поэтому `make` без аргументов покажет справку.

### 5. Как посмотреть все цели без `help`

Можно также выполнить:

```bash
make -qp | grep "^[a-zA-Z0-9][^$#\/\t=]*:.*$" | sort
```

Но удобнее всего пользоваться `make help`.

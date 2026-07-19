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

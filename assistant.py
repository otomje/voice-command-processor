# v4
import sounddevice as sd
import vosk
import json
import queue
import webbrowser
import subprocess
import sys
import os
import logging
import shutil
import threading
from pathlib import Path
from typing import Callable, Optional, Tuple
from dataclasses import dataclass
import time

# ═══════════════════════════════════════════════════════════════
#   ЛОГУВАННЯ
# ═══════════════════════════════════════════════════════════════

logging.basicConfig(
    level=logging.INFO,
    format='  [%(levelname)s] %(message)s'
)
logger = logging.getLogger(__name__)

# ═══════════════════════════════════════════════════════════════
#   НАСТРОЙКИ
# ═══════════════════════════════════════════════════════════════

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
MODEL_PATH = os.path.join(BASE_DIR, "vosk-model-small-ru-0.22")
SAMPLERATE = 24000
BLOCKSIZE = 2000
DEBOUNCE_BLOCKS = 30

# ═══════════════════════════════════════════════════════════════
#   УТІЛІТИ ДЛЯ КРОССПЛАТФОРМЕННОСТІ
# ═══════════════════════════════════════════════════════════════

def get_platform() -> str:
    if sys.platform == "win32":
        return "windows"
    elif sys.platform == "darwin":
        return "macos"
    else:
        return "linux"

def find_executable(name: str) -> Optional[str]:
    return shutil.which(name)

def open_application(
    windows_path: Optional[str] = None,
    macos_app: Optional[str] = None,
    linux_cmd: Optional[str] = None,
    web_url: Optional[str] = None,
    fallback_cmd: Optional[str] = None,
) -> bool:
    platform = get_platform()

    try:
        if platform == "windows" and windows_path:
            if os.path.exists(windows_path):
                subprocess.Popen(windows_path)
                return True
            app_name = Path(windows_path).stem
            if find_executable(app_name):
                subprocess.Popen(app_name, shell=True)
                return True

        elif platform == "macos" and macos_app:
            subprocess.Popen(["open", "-a", macos_app])
            return True

        elif platform == "linux" and linux_cmd:
            if find_executable(linux_cmd.split()[0]):
                subprocess.Popen(linux_cmd.split())
                return True

        if web_url:
            webbrowser.open(web_url)
            return True

        if fallback_cmd and find_executable(fallback_cmd.split()[0]):
            subprocess.Popen(fallback_cmd, shell=True)
            return True

        return False

    except Exception as e:
        logger.error(f"  → Помилка при відкриванні додатку: {e}")
        return False

# ═══════════════════════════════════════════════════════════════
#   КОМАНДИ
# ═══════════════════════════════════════════════════════════════

_assistant_ref: Optional["VoiceAssistant"] = None

def say_hello():
    if _assistant_ref:
        _assistant_ref.resume_listening()

def stop_program():
    if _assistant_ref:
        _assistant_ref.pause_listening()

def open_google():
    if open_application(web_url="https://google.com"):
        logger.info("  → Открываю Google")
    else:
        logger.warning("  → Не можу открыть Google")

def open_classroom():
    if open_application(web_url="https://classroom.google.com/u/1/h?hl=uk"):
        logger.info("  → Открываю Classroom")
    else:
        logger.warning("  → Не можу открыть Classroom")

def open_youtube():
    if open_application(web_url="https://youtube.com"):
        logger.info("  → Открываю YouTube")
    else:
        logger.warning("  → Не можу открыть YouTube")

def open_github():
    if open_application(web_url="https://github.com"):
        logger.info("  → Открываю GitHub")
    else:
        logger.warning("  → Не можу открыть GitHub")

def open_gpt():
    if open_application(web_url="https://chatgpt.com"):
        logger.info("  → Открываю ChatGPT")
    else:
        logger.warning("  → Не можу открыть ChatGPT")

def open_steam():
    success = open_application(
        windows_path=r"C:\Program Files (x86)\Steam\steam.exe",
        macos_app="Steam",
        linux_cmd="steam",
        fallback_cmd="steam"
    )
    if success:
        logger.info("  → Открываю Steam")
    else:
        logger.warning("  → Steam не найден")

def open_viber():
    success = open_application(
        windows_path=r"C:\Users\user\AppData\Local\Viber\Viber.exe",
        macos_app="Viber",
        linux_cmd="viber",
        fallback_cmd="viber"
    )
    if success:
        logger.info("  → Открываю Viber")
    else:
        logger.warning("  → Viber не найден")

def open_telegram():
    success = open_application(
        windows_path=r"C:\Program Files (x86)\Telegram\Telegram.exe",
        macos_app="Telegram",
        linux_cmd="telegram-desktop",
        fallback_cmd="telegram-desktop"
    )
    if success:
        logger.info("  → Открываю Telegram")
    else:
        logger.warning("  → Telegram не найден")

def open_browser():
    success = open_application(
        windows_path=r"C:\Program Files\Google\Chrome\Application\chrome.exe",
        macos_app="Google Chrome",
        linux_cmd="google-chrome",
        fallback_cmd="chromium"
    )
    if success:
        logger.info("  → Открываю Chrome")
    else:
        logger.warning("  → Chrome не найден")

def open_figma():
    success = open_application(
        windows_path=r"C:\Users\user\AppData\Local\Figma\Figma.exe",
        macos_app="Figma",
        linux_cmd="figma",
    )
    if success:
        logger.info("  → Открываю Figma")
    else:
        logger.warning("  → Figma не найдена")

def open_code():
    success = open_application(
        windows_path="code.exe",
        macos_app="Visual Studio Code",
        linux_cmd="code",
        fallback_cmd="code"
    )
    if success:
        logger.info("  → Открываю Visual Studio Code")
    else:
        logger.warning("  → Visual Studio Code не найден")

def open_calculator():
    success = open_application(
        windows_path="calc.exe",
        macos_app="Calculator",
        linux_cmd="gnome-calculator",
        fallback_cmd="gnome-calculator"
    )
    if success:
        logger.info("  → Открываю калькулятор")
    else:
        logger.warning("  → Калькулятор не найден")

def open_notepad():
    success = open_application(
        windows_path="notepad.exe",
        macos_app="TextEdit",
        linux_cmd="gedit",
        fallback_cmd="nano"
    )
    if success:
        logger.info("  → Открываю блокнот")
    else:
        logger.warning("  → Блокнот не найден")

def open_cmd():
    success = open_application(
        windows_path="cmd.exe",
        macos_app="Terminal",
        linux_cmd="gnome-terminal",
        fallback_cmd="x-terminal-emulator"
    )
    if success:
        logger.info("  → Открываю CMD")
    else:
        logger.warning("  → CMD не смог запуститься")

def open_obs():
    success = open_application(
        windows_path=r"C:\Program Files (x86)\Steam\steamapps\common\OBS Studio\bin\64bit\obs64.exe",
        macos_app="OBS",
        linux_cmd="obs",
        fallback_cmd="obs"
    )
    if success:
        logger.info("  → Открываю OBS Studio")
    else:
        logger.warning("  → OBS Studio не найден")

def open_explorer():
    success = open_application(
        windows_path="explorer.exe",
        macos_app="Finder",
        linux_cmd="nautilus",
        fallback_cmd="xdg-open ."
    )
    if success:
        logger.info("  → Открываю проводник")
    else:
        logger.warning("  → Проводник не смог запуститься")

# ═══════════════════════════════════════════════════════════════
#   СЛОВНИК КОМАНД
# ═══════════════════════════════════════════════════════════════

@dataclass
class Command:
    name: str
    keywords: list[str]
    action: Callable[[], None]
    works_when_paused: bool = False  # якщо True — спрацює навіть на паузі

COMMANDS = [
    Command("hello", ["привет", "слушай", "здарова", "доров"], say_hello, works_when_paused=True),
    Command("stop", ["стоп", "хватит", "харе", "офнись", "пока"], stop_program),
    Command("google", ["гугл", "гугол", "поиск", "найди", "найти"], open_google),
    Command("classroom", ["классрум", "класрум", "уроки", "урок", "задача", "задачи", "задачу", "домашка", "домашку"], open_classroom),
    Command("youtube", ["ютуб", "ютюб"], open_youtube),
    Command("github", ["гитхаб", "гит", "репозиторий", "профиль", "работа"], open_github),
    Command("gpt", ["искусственный интеллект", "джипити", "джпт", "гепете", "чат гпт", "чатгпт", "чат"], open_gpt),
    Command("steam", ["стим", "стиам", "играть", "игры"], open_steam),
    Command("viber", ["вайбер"], open_viber),
    Command("telegram", ["телеграм", "телега"], open_telegram),
    Command("browser", ["браузер", "хром", "интернет"], open_browser),
    Command("figma", ["фигма", "макет", "дизайн"], open_figma),
    Command("code", ["вскод", "вс код", "визуал студио код", "визуал студио", "студио код", "код", "скрипт", "верстка", "сверстать"], open_code),
    Command("calculator", ["калькулятор", "посчитать", "посчитай"], open_calculator),
    Command("notepad", ["блокнот", "заметки", "текст", "написать"], open_notepad),
    Command("cmd", ["командная строка", "виндовс строка"], open_cmd),
    Command("obs studio", ["записать", "запись", "записать екран"], open_obs),
    Command("explorer", ["проводник", "папки", "папка"], open_explorer),
]

# ═══════════════════════════════════════════════════════════════
#   ЯДРО
# ═══════════════════════════════════════════════════════════════

class VoiceAssistant:

    def __init__(self, model_path: str, samplerate: int = 24000, blocksize: int = 2000):
        self.model_path = model_path
        self.samplerate = samplerate
        self.blocksize = blocksize

        self.audio_queue: queue.Queue = queue.Queue()
        self.current_block = 0
        self.last_triggered = {"keyword": None, "block": 0}

        self.is_listening = True  # True = активне; False = на паузі

        self.model = None
        self.recognizer = None

    # ── пауза / відновлення ─────────────────────────────────────

    def pause_listening(self):
        if self.is_listening:
            self.is_listening = False
            logger.info("  → Прослуховування на паузі. Скажи «привет» щоб продовжити.")

    def resume_listening(self):
        if not self.is_listening:
            self.is_listening = True
            logger.info("  → Прослуховування відновлено")
        else:
            logger.info("  → Привіт! Слухаю вас")

    # ── завантаження моделі ─────────────────────────────────────

    def load_model(self) -> bool:
        if not os.path.exists(self.model_path):
            logger.error(f"  → Модель не знайдена: {self.model_path}")
            return False
        try:
            logger.info("  → Завантажую модель...")
            self.model = vosk.Model(self.model_path)
            self.recognizer = vosk.KaldiRecognizer(self.model, self.samplerate)
            self.recognizer.SetMaxAlternatives(0)
            self.recognizer.SetWords(False)
            logger.info("  → Модель завантажена")
            return True
        except Exception as e:
            logger.error(f"  → Помилка завантаження моделі: {e}")
            return False

    # ── аудіо ───────────────────────────────────────────────────

    def audio_callback(self, indata, frames, time, status):
        if status:
            logger.warning(f"  → Аудіо статус: {status}")
        self.audio_queue.put(bytes(indata))
        self.current_block += 1

    # ── пошук команди ───────────────────────────────────────────

    def find_command(self, text: str) -> Tuple[Optional[str], Optional[Command]]:
        text = text.lower().strip()
        for cmd in COMMANDS:
            for keyword in cmd.keywords:
                if keyword in text:
                    return keyword, cmd
        return None, None

    # ── дебаунс ─────────────────────────────────────────────────

    def should_debounce(self, keyword: str) -> bool:
        if self.last_triggered["keyword"] != keyword:
            return False
        return (self.current_block - self.last_triggered["block"]) < DEBOUNCE_BLOCKS

    # ── обробка тексту ──────────────────────────────────────────

    def process_text(self, text: str, is_partial: bool = False) -> bool:
        if not text.strip():
            return False

        keyword, cmd = self.find_command(text)
        if cmd is None:
            return False

        # Якщо на паузі — реагуємо тільки на команди з works_when_paused=True
        if not self.is_listening and not cmd.works_when_paused:
            return False

        if self.should_debounce(keyword):
            return True

        label = "Ви сказали"
        logger.info(f"{label}: «{text.strip()}»")

        self.last_triggered["keyword"] = keyword
        self.last_triggered["block"] = self.current_block

        thread = threading.Thread(target=cmd.action, daemon=True)
        thread.start()
        return True

    # ── вивід команд ────────────────────────────────────────────

    def print_commands(self):
        print("\n┌─────────────────────────────────────────────┐")
        print("│                 Всі команди                 │")
        print("└─────────────────────────────────────────────┘")
        for cmd in COMMANDS:
            tag = " [завжди]" if cmd.works_when_paused else ""
            print(f"  • [{cmd.name}]{tag}  {', '.join(cmd.keywords)}")
        print("\n  → Зупинити програму: Ctrl + C\n")

    # ── головна петля ───────────────────────────────────────────

    def run(self):
        if not self.load_model():
            input("  → Натисніть «Enter» щоб вийти")
            return

        self.print_commands()
        logger.info("  → Слухаю вас\n")

        try:
            with sd.RawInputStream(
                samplerate=self.samplerate,
                blocksize=self.blocksize,
                dtype="int16",
                channels=1,
                callback=self.audio_callback,
            ):
                while True:
                    data = self.audio_queue.get()

                    if self.recognizer.AcceptWaveform(data):
                        result = json.loads(self.recognizer.Result())
                        text = result.get("text", "")
                        if text:
                            self.process_text(text, is_partial=False)
                            self.recognizer.Reset()
                    else:
                        partial = json.loads(self.recognizer.PartialResult()).get("partial", "")
                        if partial:
                            self.process_text(partial, is_partial=True)

        except KeyboardInterrupt:
            logger.info("  → Зупинено користувачем")
        except Exception as e:
            logger.error(f"  → Критична помилка: {e}", exc_info=True)
        finally:
            logger.info("  → Зупинено")
            sys.exit(0)

# ═══════════════════════════════════════════════════════════════
#   ТОЧКА ВХОДУ
# ═══════════════════════════════════════════════════════════════

def main():
    global _assistant_ref

    assistant = VoiceAssistant(
        model_path=MODEL_PATH,
        samplerate=SAMPLERATE,
        blocksize=BLOCKSIZE
    )
    _assistant_ref = assistant
    assistant.run()

if __name__ == "__main__":
    main()
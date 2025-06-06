import subprocess

from .config import Config

from .logger import get_logger
from .logger import LogType
from .logger import GenericTextLogHandler

logger = get_logger(__name__, filename="ffmpeg_log.csv", logType=LogType.BOTH, handler=GenericTextLogHandler)


class FFMPEGController:
    def __init__(self, config: Config):
        self.process = None
        self.current_profile = None
        self.resolution = config.resolution
        self.bitrate = config.bitrate
        self.fps = config.fps
        self.input_device = config.input_device
        self.output = config.output
        logger.info(
            f"[FFMPEG] Инициализация с разрешением: {self.resolution}, битрейтом: {self.bitrate}, частотой кадров: {self.fps}"
        )
        logger.info(f"[FFMPEG] Устройство ввода: {self.input_device}, выход: {self.output}")
        logger.info("[FFMPEG] Инициализация завершена")

    def start(self, profile):
        if self.process:
            self.stop()
        cmd = self.build_command(profile)
        self.process = subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        if self.process.poll() is not None:
            logger.error(f"[FFMPEG] Ошибка запуска процесса: {self.process.stderr.read().decode()}")
            return
        logger.info(f"[FFMPEG] Процесс запущен с командой: {cmd}")
        self.current_profile = profile
        logger.info(f"[FFMPEG] Процесс запущен с профилем: {profile}")

    def stop(self):
        if self.process:
            logger.info("[FFMPEG] Остановка текущего процесса")
            self.process.terminate()
            self.process.wait()
            self.process = None

    def restart_if_needed(self, new_profile):
        if new_profile != self.current_profile:
            logger.info(f"[FFMPEG] Профиль изменился: {self.current_profile} → {new_profile}")
            self.start(new_profile)

    def build_command(self, profile: dict[str, str]) -> str:
        if self.input_device == "testsrc":
            logger.info(
                f"[FFMPEG] Построение команды для тестового источника с разрешением: {profile['resolution']}, fps: {self.fps}, битрейтом: {self.bitrate}"
            )
            return (
                f"ffmpeg -f lavfi -i testsrc=rate={profile['fps']}:size={profile['resolution']} "
                f"-vcodec libx264 -preset ultrafast -b:v {profile['bitrate']} -f mpegts {self.output}"
            )
        else:
            logger.info(
                f"[FFMPEG] Построение команды для устройства ввода: {self.input_device} с разрешением: {profile['resolution']}, частотой кадров: {profile['fps']}, битрейтом: {profile['bitrate']}"
            )
            return (
                f"ffmpeg -f v4l2 -framerate {profile['fps']} -video_size {profile['resolution']} "
                f"-i {self.input_device} -b:v {profile['bitrate']} -f mpegts {self.output}"
            )

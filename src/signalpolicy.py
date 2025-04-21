from .rciclient import KeeneticRCIClient
from .ffmpeg import FFMPEGController

from .config import Config
from .logger import LogType
from .logger import GenericTextLogHandler
from .logger import get_logger


logger = get_logger(__name__, filename="signalpolicy_log.csv", logType=LogType.FILE, handler=GenericTextLogHandler)


class SignalPolicyEngine:
    def __init__(self, ffmpeg: FFMPEGController, config: Config):
        self.ffmpeg = ffmpeg
        self.config = config

        base_profile = {"resolution": config.resolution, "bitrate": config.bitrate, "fps": config.fps}
        logger.info(f"[POLICY] Инициализация с базовым профилем: {base_profile}")
        # Degradation steps
        degradation_steps = config.degradation_steps
        if degradation_steps < 1:
            logger.error("[POLICY] Количество шагов деградации должно быть больше 0")
            raise ValueError("Количество шагов деградации должно быть больше 0")

        self.profiles = []
        for step in range(degradation_steps + 1):
            width, height = base_profile["resolution"].split("x")
            width = int(width) - step * (int(width) // degradation_steps)
            height = int(height) - step * (int(height) // degradation_steps)
            if width <= 1:
                width = 320
            if height <= 1:
                height = 240
            resolution = f"{width}x{height}"
            bitrate = f"{int(int(base_profile['bitrate'].split('k')[0]) * ((degradation_steps - step) / degradation_steps))}k"
            if int(bitrate.split('k')[0]) < 300:
                bitrate = "300k"
            fps = str(int(base_profile["fps"]) - step * 3 if int(base_profile["fps"]) - step * 3 > 0 else 1)
            if int(fps) < 10:
                fps = "12"
            self.profiles.append({"resolution": resolution, "bitrate": bitrate, "fps": fps})

        if not self.config.input_device:
            logger.info("[POLICY] Используется тестовый источник")
            self.ffmpeg.input_device = "testsrc"
        else:
            logger.info(f"[POLICY] Используется устройство ввода: {self.config.input_device}")
        logger.info(f"[POLICY] Инициализация завершена с профилями: {self.profiles}")

    def evaluate_and_apply(self, signal_level: int= None):
        profile = self.profiles[signal_level.get("level")]
        self.ffmpeg.restart_if_needed(profile)

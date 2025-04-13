from .rciclient import KeeneticRCIClient
from .ffmpeg import FFMPEGController
from datetime import datetime

from .config import Config
from .logger import LogType
from .logger import GenericTextLogHandler
from .logger import get_logger


logger = get_logger(__name__, logType=LogType.FILE, handler=GenericTextLogHandler)


class SignalPolicyEngine:
    def __init__(self, client: KeeneticRCIClient, ffmpeg: FFMPEGController, config: Config):
        self.client = client
        self.ffmpeg = ffmpeg
        self.config = config
        ## TODO: Убрать это в конфиг
        self.profiles = [
            {"resolution": "320x240", "bitrate": "600k",  "fps": "12"},
            {"resolution": "640x480", "bitrate": "600k",  "fps": "15"},
            {"resolution": "854x480", "bitrate": "1000k", "fps": "20"},
            {"resolution": "1280x720", "bitrate": "2000k", "fps": "25"},
            {"resolution": "1600x900", "bitrate": "3000k", "fps": "30"},
            {"resolution": "1920x1080", "bitrate": "4500k", "fps": "30"},
        ]

        if not self.config.input_device:
            logger.info("[POLICY] Используется тестовый источник")
            self.ffmpeg.input_device = "testsrc"
        else:
            logger.info(f"[POLICY] Используется устройство ввода: {self.config.input_device}")
        logger.info(f"[POLICY] Инициализация завершена с профилями: {self.profiles}")

    def evaluate_and_apply(self, signal_data: dict):
        """
        Evaluates the signal-to-noise ratio (SNR) based on the provided signal data
        and applies the appropriate profile settings.

        Args:
            signal_data (dict): A dictionary containing signal information. Expected keys:
                - "rssi" (int): Received Signal Strength Indicator. Defaults to -100 if not provided.
                - "noise" (int): Noise level. Defaults to -100 if not provided.

        Behavior:
            - Calculates the SNR as the difference between RSSI and noise.
            - Logs the SNR, RSSI, and noise values with a timestamp.
            - Selects a profile based on the SNR value:
                - SNR < 5: Selects the first profile.
                - 5 <= SNR < 10: Selects the second profile.
                - 10 <= SNR < 20: Selects the third profile.
                - 20 <= SNR < 30: Selects the fourth profile.
                - 30 <= SNR < 40: Selects the fifth profile.
                - SNR >= 40: Selects the sixth profile.
            - Logs the selected profile's resolution, bitrate, and frame rate.
            - Restarts the ffmpeg process with the selected profile if needed.

        Returns:
            None
        """
        rssi = int(signal_data.get("rssi", -100))
        noise = int(signal_data.get("noise", -100))
        snr = rssi - noise

        ts = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        logger.info(f"[{ts}] SNR: {snr}, RSSI: {rssi}, NOISE: {noise}")

        if snr < 5:
            profile = self.profiles[0]
        elif snr < 10:
            profile = self.profiles[1]
        elif snr < 20:
            profile = self.profiles[2]
        elif snr < 30:
            profile = self.profiles[3]
        elif snr < 40:
            profile = self.profiles[4]
        else:
            profile = self.profiles[5]

        logger.info(f"[POLICY] Выбран профиль: {profile['resolution']} @ {profile['bitrate']} {profile['fps']}fps")
        self.ffmpeg.restart_if_needed(profile)
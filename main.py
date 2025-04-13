from src.ffmpeg import FFMPEGController
from src.rciclient import KeeneticRCIClient
from src.signalpolicy import SignalPolicyEngine
from src.connection_checker import ConnectionChecker
from src.config import Config
from src.logger import LogType
from src.logger import GenericTextLogHandler
import time

from src.logger import get_logger
import signal
import sys
logger = get_logger(__name__, logType=LogType.BOTH, handler=GenericTextLogHandler)


def check_init_connection(config: Config = None):
    try:
        connection_check = ConnectionChecker(config)
        connection = connection_check.check_all()
        if connection:
            logger.info("[CONNECTION CHECKER] Initial connection check passed.")
        else:
            logger.error("[CONNECTION CHECKER] Initial connection check failed.")
    except Exception as e:
        logger.error(f"[CONNECTION CHECKER] Error during initial connection check: {e}")


def graceful_shutdown(signum, frame):
    logger.info("[MAIN] Graceful shutdown initiated.")
    sys.exit(0)

if __name__ == "__main__":
    signal.signal(signal.SIGINT, graceful_shutdown)
    signal.signal(signal.SIGTERM, graceful_shutdown)

    config = Config()
    client = KeeneticRCIClient(config)
    if client.authenticate():
        check_init_connection(config)
        ffmpeg = FFMPEGController(config)
        policy = SignalPolicyEngine(client, ffmpeg, config)
        logger.info("[MAIN] Starting signal evaluation loop.")
        while True:
            signal_info = client.get_signal_info()
            if signal_info:
                policy.evaluate_and_apply(signal_info)
            else:
                logger.error("[SIGNAL POLICY] Failed to get signal information.")
                break
            time.sleep(config.timeout)
    else:
        logger.error("[MAIN] Authentication failed. Exiting.")

import configparser
from dataclasses import dataclass

@dataclass
class Config:
    def __init__(self, config_path="main.conf"):
        self._load_config(config_path)

    def _load_config(self, config_path):
        config = configparser.ConfigParser()
        config.read(config_path)
        # Router settings
        self.ip = config["Router"]["ip_addr"]
        self.login = config["Router"]["login"]
        self.password = config["Router"]["password"]
        # Connection settings
        self.connection_type = config["settings"]["connection_type"]
        self.connection_mode = config["settings"]["connection_mode"]
        self.connection_check = config["settings"]["connection_check"]
        self.timeout = config["settings"]["timeout"]
        self.logfile = config["settings"]["logfile"]
        # Video settings
        profile = config["Profile"]
        self.resolution = profile["resolution"]
        self.bitrate = profile["bitrate"]
        self.fps = profile["fps"]
        self.degradation_steps = int(profile.get("degradation_steps", 5))
        # FFMPEG settings
        self.input_device = profile.get("input", "testsrc")
        self.output = profile.get("output", "udp://127.0.0.1:1234")
        # ConnCheck settings
        self.ping_ip = config["connection_check"]["ping_ip"]
        self.curl_url = config["connection_check"]["curl_url"]
import os
import random
from datetime import datetime


class DummySensor:
    def __init__(self, log_path=None):
        self.env_values = {
            "mars_base_internal_temperature": None,
            "mars_base_external_temperature": None,
            "mars_base_internal_humidity": None,
            "mars_base_external_illuminance": None,
            "mars_base_internal_co2": None,
            "mars_base_internal_oxygen": None,
        }
        self.log_path = log_path or os.path.join(
            os.path.dirname(os.path.abspath(__file__)),
            "artifacts",
            "env_log.txt",
        )

    def set_env(self):
        self.env_values["mars_base_internal_temperature"] = round(
            random.uniform(18, 30), 2
        )
        self.env_values["mars_base_external_temperature"] = round(
            random.uniform(0, 21), 2
        )
        self.env_values["mars_base_internal_humidity"] = round(
            random.uniform(50, 60), 2
        )
        self.env_values["mars_base_external_illuminance"] = round(
            random.uniform(500, 715), 2
        )
        self.env_values["mars_base_internal_co2"] = round(
            random.uniform(0.02, 0.1), 4
        )
        self.env_values["mars_base_internal_oxygen"] = round(
            random.uniform(4, 7), 2
        )

    def get_env(self):
        os.makedirs(os.path.dirname(self.log_path), exist_ok=True)
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        log_line = (
            f"{timestamp}, "
            f"{self.env_values['mars_base_internal_temperature']}, "
            f"{self.env_values['mars_base_external_temperature']}, "
            f"{self.env_values['mars_base_internal_humidity']}, "
            f"{self.env_values['mars_base_external_illuminance']}, "
            f"{self.env_values['mars_base_internal_co2']}, "
            f"{self.env_values['mars_base_internal_oxygen']}\n"
        )

        with open(self.log_path, "a", encoding="utf-8") as log_file:
            log_file.write(log_line)

        return self.env_values

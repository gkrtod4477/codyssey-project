import json
import random
import threading
import time


class DummySensor:
    def __init__(self):
        self.env_values = {
            "mars_base_internal_temperature": None,
            "mars_base_external_temperature": None,
            "mars_base_internal_humidity": None,
            "mars_base_external_illuminance": None,
            "mars_base_internal_co2": None,
            "mars_base_internal_oxygen": None,
        }

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
        self.set_env()
        return dict(self.env_values)


class MissionComputer:
    def __init__(self):
        self.env_values = {
            "mars_base_internal_temperature": None,
            "mars_base_external_temperature": None,
            "mars_base_internal_humidity": None,
            "mars_base_external_illuminance": None,
            "mars_base_internal_co2": None,
            "mars_base_internal_oxygen": None,
        }
        self.ds = DummySensor()
        self.stop_event = threading.Event()
        self.average_interval = 300
        self.sample_interval = 5
        self.samples = []
        self.last_average_time = time.time()

    def _wait_for_stop_input(self):
        while not self.stop_event.is_set():
            try:
                user_input = input()
            except EOFError:
                self.stop_event.set()
                return

            if user_input.strip().lower() == "q":
                self.stop_event.set()
                print("Sytem stoped....")
                return

    def _print_average_values(self):
        if not self.samples:
            return

        average_values = {}

        for key in self.env_values:
            total = 0
            for sample in self.samples:
                total += sample[key]
            average_values[key] = round(total / len(self.samples), 4)

        print(json.dumps({"5_min_average": average_values}, ensure_ascii=False))
        self.samples = []
        self.last_average_time = time.time()

    def get_sensor_data(self):
        input_thread = threading.Thread(target=self._wait_for_stop_input, daemon=True)
        input_thread.start()

        try:
            print("Press 'q' and Enter to stop.")

            while not self.stop_event.is_set():
                current_time = time.time()
                if current_time - self.last_average_time >= self.average_interval:
                    self._print_average_values()

                sensor_data = self.ds.get_env()
                self.env_values.update(sensor_data)
                self.samples.append(dict(self.env_values))

                print(json.dumps(self.env_values, ensure_ascii=False))

                for _ in range(self.sample_interval):
                    if self.stop_event.is_set():
                        break
                    time.sleep(1)

        except KeyboardInterrupt:
            self.stop_event.set()
            print("Sytem stoped....")


RunComputer = MissionComputer()

import json
import os
import platform
import re
import subprocess
import time
import ctypes
from pathlib import Path


try:
    import psutil
except ImportError:  # pragma: no cover
    psutil = None


class MissionComputer:
    def __init__(self, setting_file="setting.txt"):
        self.setting_path = Path(__file__).resolve().parent / setting_file
        self.settings = self._load_settings()

    def _load_settings(self):
        default_settings = {
            "operating_system": True,
            "operating_system_version": True,
            "cpu_type": True,
            "cpu_core_count": True,
            "memory_size": True,
            "cpu_usage": True,
            "memory_usage": True,
        }

        if not self.setting_path.exists():
            return default_settings

        loaded = dict(default_settings)
        try:
            with self.setting_path.open("r", encoding="utf-8") as file:
                for raw_line in file:
                    line = raw_line.strip()
                    if not line or line.startswith("#") or "=" not in line:
                        continue

                    key, value = line.split("=", 1)
                    key = key.strip()
                    value = value.strip().lower()

                    if key in loaded:
                        loaded[key] = value in {"true", "1", "yes", "y", "on"}
        except OSError:
            return default_settings

        return loaded

    def _filter_by_settings(self, data):
        return {k: v for k, v in data.items() if self.settings.get(k, False)}

    def _get_total_memory_bytes(self):
        if psutil is not None:
            return psutil.virtual_memory().total

        system = platform.system()
        try:
            if system in {"Linux", "Darwin"} and hasattr(os, "sysconf"):
                page_size = os.sysconf("SC_PAGE_SIZE")
                physical_pages = os.sysconf("SC_PHYS_PAGES")
                return int(page_size * physical_pages)

            if system == "Darwin":
                output = subprocess.check_output(
                    ["sysctl", "-n", "hw.memsize"], text=True
                ).strip()
                return int(output)

            if system == "Windows":
                class MEMORYSTATUSEX(ctypes.Structure):
                    _fields_ = [
                        ("dwLength", ctypes.c_ulonglong),
                        ("dwMemoryLoad", ctypes.c_ulonglong),
                        ("ullTotalPhys", ctypes.c_ulonglong),
                        ("ullAvailPhys", ctypes.c_ulonglong),
                        ("ullTotalPageFile", ctypes.c_ulonglong),
                        ("ullAvailPageFile", ctypes.c_ulonglong),
                        ("ullTotalVirtual", ctypes.c_ulonglong),
                        ("ullAvailVirtual", ctypes.c_ulonglong),
                        ("ullAvailExtendedVirtual", ctypes.c_ulonglong),
                    ]

                memory_status = MEMORYSTATUSEX()
                memory_status.dwLength = ctypes.sizeof(MEMORYSTATUSEX)
                ctypes.windll.kernel32.GlobalMemoryStatusEx(ctypes.byref(memory_status))
                return int(memory_status.ullTotalPhys)
        except Exception:
            return None

        return None

    def _get_cpu_usage_without_psutil(self):
        system = platform.system()

        if system == "Linux":
            try:
                def read_cpu_times():
                    with open("/proc/stat", "r", encoding="utf-8") as file:
                        fields = file.readline().strip().split()[1:]
                    values = [int(v) for v in fields]
                    idle = values[3] + (values[4] if len(values) > 4 else 0)
                    total = sum(values)
                    return idle, total

                idle1, total1 = read_cpu_times()
                time.sleep(1)
                idle2, total2 = read_cpu_times()
                total_diff = total2 - total1
                idle_diff = idle2 - idle1
                if total_diff <= 0:
                    return None
                return round((1 - idle_diff / total_diff) * 100, 2)
            except Exception:
                return None

        if system == "Darwin":
            try:
                output = subprocess.check_output(
                    ["top", "-l", "2", "-n", "0", "-s", "1"], text=True
                )
                cpu_lines = [line for line in output.splitlines() if "CPU usage" in line]
                if cpu_lines:
                    latest_line = cpu_lines[-1]
                    match = re.search(r"(\d+(\.\d+)?)%\s*idle", latest_line)
                    if match:
                        idle = float(match.group(1))
                        return round(100 - idle, 2)
            except Exception:
                pass

            try:
                core_count = os.cpu_count() or 1
                load_avg_1min = os.getloadavg()[0]
                return round(min(100.0, (load_avg_1min / core_count) * 100), 2)
            except Exception:
                return None

        if system == "Windows":
            try:
                output = subprocess.check_output(
                    ["wmic", "cpu", "get", "loadpercentage", "/value"], text=True
                )
                match = re.search(r"LoadPercentage=(\d+)", output)
                if match:
                    return float(match.group(1))
            except Exception:
                return None
            return None

        return None

    def _get_memory_usage_without_psutil(self):
        system = platform.system()

        if system == "Linux":
            try:
                mem_total = None
                mem_available = None
                with open("/proc/meminfo", "r", encoding="utf-8") as file:
                    for line in file:
                        if line.startswith("MemTotal:"):
                            mem_total = int(line.split()[1]) * 1024
                        elif line.startswith("MemAvailable:"):
                            mem_available = int(line.split()[1]) * 1024

                if not mem_total or mem_available is None:
                    return None
                used = mem_total - mem_available
                return round((used / mem_total) * 100, 2)
            except Exception:
                return None

        if system == "Darwin":
            try:
                vm_output = subprocess.check_output(["vm_stat"], text=True)
                header_match = re.search(r"page size of (\d+) bytes", vm_output)
                if not header_match:
                    return None
                page_size = int(header_match.group(1))

                values = {}
                for line in vm_output.splitlines():
                    if ":" not in line:
                        continue
                    key, value = line.split(":", 1)
                    number = re.sub(r"[^0-9]", "", value)
                    if number:
                        values[key.strip()] = int(number)

                total_bytes = self._get_total_memory_bytes()
                free_pages = values.get("Pages free", 0) + values.get("Pages speculative", 0)
                if not total_bytes:
                    return None
                used_bytes = total_bytes - (free_pages * page_size)
                return round((used_bytes / total_bytes) * 100, 2)
            except Exception:
                return None

        if system == "Windows":
            try:
                class MEMORYSTATUSEX(ctypes.Structure):
                    _fields_ = [
                        ("dwLength", ctypes.c_ulonglong),
                        ("dwMemoryLoad", ctypes.c_ulonglong),
                        ("ullTotalPhys", ctypes.c_ulonglong),
                        ("ullAvailPhys", ctypes.c_ulonglong),
                        ("ullTotalPageFile", ctypes.c_ulonglong),
                        ("ullAvailPageFile", ctypes.c_ulonglong),
                        ("ullTotalVirtual", ctypes.c_ulonglong),
                        ("ullAvailVirtual", ctypes.c_ulonglong),
                        ("ullAvailExtendedVirtual", ctypes.c_ulonglong),
                    ]

                memory_status = MEMORYSTATUSEX()
                memory_status.dwLength = ctypes.sizeof(MEMORYSTATUSEX)
                ctypes.windll.kernel32.GlobalMemoryStatusEx(ctypes.byref(memory_status))
                return float(memory_status.dwMemoryLoad)
            except Exception:
                return None

        return None

    def get_mission_computer_info(self):
        try:
            total_memory = self._get_total_memory_bytes()
            memory_gb = round(total_memory / (1024**3), 2) if total_memory else None
            cpu_core_count = (
                psutil.cpu_count(logical=False) if psutil is not None else os.cpu_count()
            )

            info = {
                "operating_system": platform.system(),
                "operating_system_version": platform.version(),
                "cpu_type": platform.processor() or platform.machine(),
                "cpu_core_count": cpu_core_count,
                "memory_size": f"{memory_gb} GB" if memory_gb is not None else None,
            }

            output = self._filter_by_settings(info)
            print(json.dumps(output, ensure_ascii=False, indent=2))
            return output
        except Exception as error:
            result = {"error": f"failed to get system information: {error}"}
            print(json.dumps(result, ensure_ascii=False, indent=2))
            return result

    def get_mission_computer_load(self):
        try:
            if psutil is not None:
                cpu_usage = round(psutil.cpu_percent(interval=1), 2)
                memory_usage = round(psutil.virtual_memory().percent, 2)
            else:
                cpu_usage = self._get_cpu_usage_without_psutil()
                memory_usage = self._get_memory_usage_without_psutil()

            load = {
                "cpu_usage": f"{cpu_usage}%" if cpu_usage is not None else None,
                "memory_usage": f"{memory_usage}%" if memory_usage is not None else None,
            }

            output = self._filter_by_settings(load)
            print(json.dumps(output, ensure_ascii=False, indent=2))
            return output
        except Exception as error:
            result = {"error": f"failed to get system load: {error}"}
            print(json.dumps(result, ensure_ascii=False, indent=2))
            return result


runComputer = MissionComputer()

import os

from mars_mission_computer import DummySensor


def main():
    base_dir = os.path.dirname(os.path.abspath(__file__))
    artifacts_dir = os.path.join(base_dir, "artifacts")
    log_path = os.path.join(artifacts_dir, "env_log.txt")

    os.makedirs(artifacts_dir, exist_ok=True)
    for artifact_name in os.listdir(artifacts_dir):
        artifact_path = os.path.join(artifacts_dir, artifact_name)
        if os.path.isfile(artifact_path):
            os.remove(artifact_path)

    ds = DummySensor(log_path=log_path)
    ds.set_env()
    env_values = ds.get_env()

    print(env_values)

if __name__ == "__main__":
    main()

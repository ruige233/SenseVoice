import yaml


class DatabaseManager:
    def __init__(self):
        # 读取配置文件
        with open('resource/config.yaml', 'r') as file:
            config = yaml.safe_load(file)
            self.download_path = config['download']['path']
            self.convert_log = config['convert_log']['path']

    def __str__(self):
        return f"DatabaseManager(config={self.download_path})"

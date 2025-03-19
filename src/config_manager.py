import os
import json

class ConfigManager:
    def __init__(self, app_dir):
        self.app_dir = app_dir
        self.config_file = os.path.join(app_dir, "config.json")
        self.config = self.load_config()
    
    def load_config(self):
        """加载配置文件"""
        default_config = {
            "data_dir": os.path.join(self.app_dir, "data")
        }
        
        if os.path.exists(self.config_file):
            try:
                with open(self.config_file, 'r', encoding='utf-8') as f:
                    config = json.load(f)
                    # 确保所有默认配置项都存在
                    for key, value in default_config.items():
                        if key not in config:
                            config[key] = value
                    return config
            except Exception:
                # 如果配置文件损坏，使用默认配置
                return default_config
        else:
            # 如果配置文件不存在，创建默认配置
            self.save_config(default_config)
            return default_config
    
    def save_config(self, config=None):
        """保存配置文件"""
        if config is not None:
            self.config = config
        
        try:
            with open(self.config_file, 'w', encoding='utf-8') as f:
                json.dump(self.config, f, ensure_ascii=False, indent=2)
            return True
        except Exception:
            return False
    
    def get(self, key, default=None):
        """获取配置项"""
        return self.config.get(key, default)
    
    def set(self, key, value):
        """设置配置项"""
        self.config[key] = value
        return self.save_config()
"""
Configuration module for the application.
"""
import os
from pathlib import Path

# 项目根目录
ROOT_DIR = Path(__file__).parent.parent.parent

# 配置文件路径
CONFIG_FILE = ROOT_DIR / '.env'

def load_config():
    """Load configuration from .env file"""
    config = {}
    if os.path.exists(CONFIG_FILE):
        with open(CONFIG_FILE, 'r') as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith('#'):
                    key, value = line.split('=', 1)
                    config[key.strip()] = value.strip()
    return config

def save_config(config):
    """Save configuration to .env file"""
    with open(CONFIG_FILE, 'w') as f:
        for key, value in config.items():
            f.write(f"{key}={value}\n")

def get_deepseek_api_key():
    """Get DeepSeek API key from configuration"""
    config = load_config()
    return config.get('DEEPSEEK_API_KEY', '')

def set_deepseek_api_key(api_key):
    """Set DeepSeek API key in configuration"""
    config = load_config()
    config['DEEPSEEK_API_KEY'] = api_key
    save_config(config) 
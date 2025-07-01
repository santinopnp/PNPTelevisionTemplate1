# -*- coding: utf-8 -*-
# bot/services/config_service.py
import os
import json
from typing import Dict, List, Optional
from pathlib import Path
import logging

logger = logging.getLogger(__name__)

class ConfigService:
    """Service for managing bot configuration"""
    
    def __init__(self):
        self.project_root = Path(__file__).parent.parent.parent
        self.config_file = self.project_root / "config.json"
        self._load_config()
    
    def _load_config(self):
        """Load configuration from environment variables and config file"""
        # Bot Token - MUST be set in .env file
        self.BOT_TOKEN = os.getenv("BOT_TOKEN")
        if not self.BOT_TOKEN:
            raise ValueError("BOT_TOKEN environment variable is required")
        
        # Admin configuration - from environment
        admin_ids_str = os.getenv("ADMIN_IDS", "")
        if admin_ids_str:
            try:
                self.ADMIN_USER_IDS = [int(id.strip()) for id in admin_ids_str.split(",") if id.strip()]
            except ValueError:
                self.ADMIN_USER_IDS = []
        else:
            self.ADMIN_USER_IDS = []
        
        # Bot settings
        self.BOT_NAME = "PNP Television Bot Ultimate"
        self.BOT_VERSION = "2.0.0"
        self.BOT_DESCRIPTION = "Bot para ver television peruana en vivo"
        
        # Load additional config from file if exists
        if self.config_file.exists():
            try:
                with open(self.config_file, 'r', encoding='utf-8') as f:
                    file_config = json.load(f)
                    self._update_from_file_config(file_config)
            except Exception as e:
                logger.warning("Could not load config file: %s", e)
        
        # Initialize default channel configuration
        self._init_channels_config()
        self._init_categories_config()
    
    def _update_from_file_config(self, file_config: dict):
        """Update configuration from file"""
        if "admin_user_ids" in file_config:
            self.ADMIN_USER_IDS.extend(file_config["admin_user_ids"])
    
    def _init_channels_config(self):
        """Initialize TV channels configuration"""
        self.CHANNELS = {
            # Canales Nacionales
            "nacional": {
                "America TV": {
                    "url": "https://www.americatv.com.pe/tvenvivo",
                    "logo": "📺",
                    "description": "Señal en vivo de America Television",
                    "category": "nacional",
                    "working": True
                },
                "Latina": {
                    "url": "https://www.latina.pe/tvenvivo",
                    "logo": "📺",
                    "description": "Señal en vivo de Latina",
                    "category": "nacional",
                    "working": True
                },
                "Panamericana": {
                    "url": "https://www.panamericana.pe/tvenvivo",
                    "logo": "📺",
                    "description": "Señal en vivo de Panamericana",
                    "category": "nacional",
                    "working": True
                },
                "ATV": {
                    "url": "https://www.atv.pe/envivo",
                    "logo": "📺",
                    "description": "Señal en vivo de ATV",
                    "category": "nacional",
                    "working": True
                },
                "TV Peru": {
                    "url": "https://www.tvperu.gob.pe/play",
                    "logo": "📺",
                    "description": "Television Nacional del Peru",
                    "category": "nacional",
                    "working": True
                }
            },
            
            # Canales de Noticias
            "noticias": {
                "Canal N": {
                    "url": "https://www.canaln.pe/envivo",
                    "logo": "📰",
                    "description": "Noticias 24/7",
                    "category": "noticias",
                    "working": True
                },
                "RPP Noticias": {
                    "url": "https://rpp.pe/tvenvivo",
                    "logo": "📢",
                    "description": "RPP Television en vivo",
                    "category": "noticias",
                    "working": True
                },
                "Exitosa Noticias": {
                    "url": "https://exitosanoticias.pe/envivo",
                    "logo": "📺",
                    "description": "Exitosa Noticias TV",
                    "category": "noticias",
                    "working": True
                }
            },
            
            # Canales Deportivos
            "deportes": {
                "Movistar Deportes": {
                    "url": "https://www.movistarplus.com.pe/deportes",
                    "logo": "⚽",
                    "description": "Deportes en vivo",
                    "category": "deportes",
                    "working": True
                },
                "Liga 1 MAX": {
                    "url": "https://www.liga1max.pe/",
                    "logo": "🏆",
                    "description": "Futbol peruano en vivo",
                    "category": "deportes",
                    "working": True
                },
                "Gol Peru": {
                    "url": "https://www.golperu.pe/envivo",
                    "logo": "⚽",
                    "description": "Canal deportivo",
                    "category": "deportes",
                    "working": True
                }
            },
            
            # Canales Regionales
            "regionales": {
                "TVPE Norte": {
                    "url": "https://www.tvpenorte.pe/envivo",
                    "logo": "🌎",
                    "description": "Television regional del norte",
                    "category": "regionales",
                    "working": True
                },
                "TVPE Centro": {
                    "url": "https://www.tvpecentro.pe/envivo",
                    "logo": "🏔️",
                    "description": "Television regional del centro",
                    "category": "regionales",
                    "working": True
                },
                "TVPE Sur": {
                    "url": "https://www.tvpesur.pe/envivo",
                    "logo": "🦙",
                    "description": "Television regional del sur",
                    "category": "regionales",
                    "working": True
                }
            },
            
            # Canales Internacionales
            "internacionales": {
                "CNN en Espanol": {
                    "url": "https://cnnespanol.cnn.com/cnne-live-tv/",
                    "logo": "🌍",
                    "description": "Noticias internacionales",
                    "category": "internacionales",
                    "working": True
                },
                "BBC News": {
                    "url": "https://www.bbc.com/news/live",
                    "logo": "🇬🇧",
                    "description": "Noticias BBC en vivo",
                    "category": "internacionales",
                    "working": True
                },
                "RT en Espanol": {
                    "url": "https://actualidad.rt.com/live",
                    "logo": "🇷🇺",
                    "description": "RT en espanol",
                    "category": "internacionales",
                    "working": True
                }
            }
        }
    
    def _init_categories_config(self):
        """Initialize categories configuration"""
        self.CATEGORIES = {
            "nacional": {
                "name": "📺 Canales Nacionales",
                "description": "Television abierta peruana",
                "emoji": "📺"
            },
            "noticias": {
                "name": "📰 Noticias",
                "description": "Canales de noticias 24/7",
                "emoji": "📰"
            },
            "deportes": {
                "name": "⚽ Deportes",
                "description": "Canales deportivos",
                "emoji": "⚽"
            },
            "regionales": {
                "name": "🌎 Regionales",
                "description": "Television regional del Peru",
                "emoji": "🌎"
            },
            "internacionales": {
                "name": "🌍 Internacionales",
                "description": "Canales internacionales",
                "emoji": "🌍"
            }
        }
    
    def get_channel(self, category: str, channel_name: str) -> Optional[Dict]:
        """Get specific channel information"""
        if category in self.CHANNELS and channel_name in self.CHANNELS[category]:
            return self.CHANNELS[category][channel_name]
        return None
    
    def get_channels_by_category(self, category: str) -> Dict:
        """Get all channels in a category"""
        return self.CHANNELS.get(category, {})
    
    def get_all_channels(self) -> Dict:
        """Get all channels"""
        return self.CHANNELS
    
    def get_working_channels(self) -> Dict:
        """Get only working channels"""
        working_channels = {}
        for category, channels in self.CHANNELS.items():
            working_channels[category] = {
                name: channel for name, channel in channels.items()
                if channel.get("working", True)
            }
        return working_channels
    
    def search_channels(self, query: str) -> List[Dict]:
        """Search channels by name or description"""
        results = []
        query_lower = query.lower()
        
        for category, channels in self.CHANNELS.items():
            for name, channel in channels.items():
                if (query_lower in name.lower() or 
                    query_lower in channel.get("description", "").lower()):
                    results.append({
                        "name": name,
                        "category": category,
                        "channel": channel
                    })
        
        return results
    
    def is_admin(self, user_id: int) -> bool:
        """Check if user is admin"""
        return user_id in self.ADMIN_USER_IDS
    
    def save_config(self):
        """Save current configuration to file"""
        config_data = {
            "admin_user_ids": self.ADMIN_USER_IDS,
            "bot_name": self.BOT_NAME,
            "bot_version": self.BOT_VERSION
        }
        
        try:
            with open(self.config_file, 'w', encoding='utf-8') as f:
                json.dump(config_data, f, indent=2, ensure_ascii=False)
            return True
        except Exception as e:
            logger.error("Error saving config: %s", e)
            return False

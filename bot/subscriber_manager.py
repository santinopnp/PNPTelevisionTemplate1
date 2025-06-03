# -*- coding: utf-8 -*-
import json
import os
from datetime import datetime, timedelta
from typing import Dict, List, Optional
from bot.config import CHANNELS, PLANS

class SubscriberManager:
    """Manage subscriber access to channels"""
    
    def __init__(self, db_file: str = "subscribers.json"):
        self.db_file = db_file
        self.subscribers = self._load_subscribers()
    
    def _load_subscribers(self) -> Dict:
        """Load subscribers from database"""
        if os.path.exists(self.db_file):
            try:
                with open(self.db_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except:
                pass
        return {"users": {}, "stats": {"total": 0, "active": 0}}
    
    def _save_subscribers(self):
        """Save subscribers to database"""
        try:
            with open(self.db_file, 'w', encoding='utf-8') as f:
                json.dump(self.subscribers, f, indent=2, ensure_ascii=False)
        except Exception as e:
            print(f"Error saving subscribers: {e}")
    
    async def add_subscriber(self, user_id: int, plan_name: str, transaction_id: str = None) -> bool:
        """Add subscriber with plan access and send channel links"""
        try:
            user_id_str = str(user_id)
            
            # Find plan by name
            plan_info = None
            plan_key = None
            for key, info in PLANS.items():
                if info["name"] == plan_name:
                    plan_info = info
                    plan_key = key
                    break
            
            if not plan_info:
                return False
            
            # Calculate expiry date
            duration_days = plan_info["duration_days"]
            start_date = datetime.now()
            expiry_date = start_date + timedelta(days=duration_days)
            
            # All plans give access to same channels
            channels = list(CHANNELS.values())
            
            # Add/update subscriber
            self.subscribers["users"][user_id_str] = {
                "plan": plan_key,
                "plan_name": plan_name,
                "status": "active",
                "start_date": start_date.isoformat(),
                "expiry_date": expiry_date.isoformat(),
                "transaction_id": transaction_id,
                "channels": channels,
                "created_at": datetime.now().isoformat()
            }
            
            # Update stats
            self.subscribers["stats"]["total"] = len(self.subscribers["users"])
            self.subscribers["stats"]["active"] = sum(1 for u in self.subscribers["users"].values() 
                                                    if u["status"] == "active")
            
            self._save_subscribers()
            
            # Send channel access links
            from bot.channel_manager import channel_manager
            expiry_str = expiry_date.strftime("%Y-%m-%d")
            await channel_manager.send_channel_access(user_id, plan_name, expiry_str)
            
            return True
            
        except Exception as e:
            print(f"Error adding subscriber: {e}")
            return False
    
    async def remove_subscriber(self, user_id: int) -> bool:
        """Remove subscriber access and kick from channels"""
        try:
            user_id_str = str(user_id)
            
            if user_id_str in self.subscribers["users"]:
                self.subscribers["users"][user_id_str]["status"] = "inactive"
                self.subscribers["users"][user_id_str]["removed_at"] = datetime.now().isoformat()
                
                # Update stats
                self.subscribers["stats"]["active"] = sum(1 for u in self.subscribers["users"].values() 
                                                        if u["status"] == "active")
                
                self._save_subscribers()
                
                # Remove from all channels
                from bot.channel_manager import channel_manager
                await channel_manager.remove_user_from_all_channels(user_id)
                
                return True
            
            return False
            
        except Exception as e:
            print(f"Error removing subscriber: {e}")
            return False
    
    def check_subscription(self, user_id: int) -> Optional[Dict]:
        """Check if user has active subscription"""
        user_id_str = str(user_id)
        
        if user_id_str not in self.subscribers["users"]:
            return None
        
        user_data = self.subscribers["users"][user_id_str]
        
        # Check if subscription expired
        if user_data["status"] == "active":
            expiry_date = datetime.fromisoformat(user_data["expiry_date"])
            if datetime.now() > expiry_date:
                # Auto-expire
                user_data["status"] = "expired"
                self._save_subscribers()
                return None
        
        return user_data if user_data["status"] == "active" else None
    
    def extend_subscription(self, user_id: int, days: int) -> bool:
        """Extend subscription by specified days"""
        try:
            user_id_str = str(user_id)
            
            if user_id_str in self.subscribers["users"]:
                user_data = self.subscribers["users"][user_id_str]
                current_expiry = datetime.fromisoformat(user_data["expiry_date"])
                new_expiry = current_expiry + timedelta(days=days)
                
                user_data["expiry_date"] = new_expiry.isoformat()
                user_data["status"] = "active"
                
                self._save_subscribers()
                return True
            
            return False
            
        except Exception as e:
            print(f"Error extending subscription: {e}")
            return False
    
    def get_subscribers_by_plan(self, plan_name: str) -> List[Dict]:
        """Get all subscribers for a specific plan"""
        return [
            {"user_id": int(uid), **data} 
            for uid, data in self.subscribers["users"].items() 
            if data.get("plan_name") == plan_name and data.get("status") == "active"
        ]
    
    def get_active_subscribers(self) -> List[Dict]:
        """Get all active subscribers"""
        return [
            {"user_id": int(uid), **data} 
            for uid, data in self.subscribers["users"].items() 
            if data.get("status") == "active"
        ]
    
    def get_expiring_soon(self, days: int = 3) -> List[Dict]:
        """Get subscribers expiring within specified days"""
        expiring = []
        threshold_date = datetime.now() + timedelta(days=days)
        
        for uid, data in self.subscribers["users"].items():
            if data.get("status") == "active":
                expiry_date = datetime.fromisoformat(data["expiry_date"])
                if expiry_date <= threshold_date:
                    expiring.append({"user_id": int(uid), **data})
        
        return expiring
    
    def get_stats(self) -> Dict:
        """Get subscription statistics"""
        active_count = sum(1 for u in self.subscribers["users"].values() 
                          if u["status"] == "active")
        
        # Count by plan name
        plan_stats = {}
        for data in self.subscribers["users"].values():
            if data["status"] == "active":
                plan_name = data.get("plan_name", "unknown")
                plan_stats[plan_name] = plan_stats.get(plan_name, 0) + 1
        
        return {
            "total_users": len(self.subscribers["users"]),
            "active_subscriptions": active_count,
            "plan_distribution": plan_stats,
            "expiring_soon": len(self.get_expiring_soon())
        }

# Global instance
subscriber_manager = SubscriberManager()
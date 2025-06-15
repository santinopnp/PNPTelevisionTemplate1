import json
import os
from datetime import datetime
from typing import Dict, Any, List

class InteractionLogger:
    def __init__(self, file: str = "data/interactions.json"):
        self.file = file
        self._load()

    def _load(self) -> None:
        if os.path.exists(self.file):
            try:
                with open(self.file, "r", encoding="utf-8") as f:
                    self.data: List[Dict[str, Any]] = json.load(f)
            except Exception:
                self.data = []
        else:
            self.data = []

    def log(self, user_id: int, action: str, info: Dict[str, Any] | None = None) -> None:
        entry = {
            "timestamp": datetime.now().isoformat(),
            "user_id": user_id,
            "action": action,
            "info": info or {},
        }
        self.data.append(entry)
        try:
            os.makedirs(os.path.dirname(self.file), exist_ok=True)
            with open(self.file, "w", encoding="utf-8") as f:
                json.dump(self.data, f, indent=2, ensure_ascii=False)
        except Exception as e:
            print(f"Error logging interaction: {e}")

interaction_logger = InteractionLogger()

from typing import Dict, Any

class DialogManager:
    def __init__(self):
        self.context: Dict[str, Dict[str, Any]] = {}

    def update_context(self, user_id: str, key: str, value: Any) -> None:
        if user_id not in self.context:
            self.context[user_id] = {}
        self.context[user_id][key] = value

    def get_context(self, user_id: str) -> Dict[str, Any]:
        return self.context.get(user_id, {})

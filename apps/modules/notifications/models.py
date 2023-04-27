from typing import List, Dict, Any

from pydantic import BaseModel, EmailStr


class NotificationData(BaseModel):
    recepients: List[EmailStr]
    subject: str
    description: str
    template: str = None
    template_data: Dict[str, Any] = None

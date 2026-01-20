import uuid
from langchain_core.messages import HumanMessage, SystemMessage, AIMessage

def create_message(role, content):
    msg_id = str(uuid.uuid4())
    if role == "user":
        return HumanMessage(content=content, id=msg_id)
    elif role == "ai":
        return AIMessage(content=content, id=msg_id)
    elif role == "system":
        return SystemMessage(content=content, id=msg_id)


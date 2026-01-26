import uuid
from datetime import datetime
from langchain_core.messages import HumanMessage, SystemMessage, AIMessage

def create_message(role, content):
    msg_id = str(uuid.uuid4())
    timestamp = int(datetime.now().timestamp() * 1000)
    if role == "user":
        return HumanMessage(content=content, id=msg_id, additional_kwargs={"timestamp": timestamp})
    elif role == "ai":
        return AIMessage(content=content, id=msg_id, additional_kwargs={"timestamp": timestamp})
    elif role == "system":
        return SystemMessage(content=content, id=msg_id, additional_kwargs={"timestamp": timestamp})

# def format_message_with_excerpts(user_content:str, excerpts:list[str]):
#     if not excerpts:
#         return user_content
#     parts = ["**PDF Context:**\n"]
#     for i, excerpt in enumerate(excerpts, 1):
#         parts.append(
#             f"**[Excerpt {i}]**\n"
#             f"> {excerpt}\n"
#         )
    
#     parts.append(f"\n **Question:** {user_content}")
    
#     return "".join(parts)
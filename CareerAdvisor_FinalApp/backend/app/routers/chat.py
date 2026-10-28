from fastapi import APIRouter, Depends, HTTPException, status
from app.database import get_db, new_id, public_document, utc_now
from app.middleware.auth import get_current_user
from app.models import UserProfile
from app.schemas import (
    ChatRequest,
    ChatResponse,
    ChatSessionDetail,
    ChatSessionOut,
    MessageResponse,
)
from app.services.gemini import chat_with_advisor

router = APIRouter(prefix="/chat", tags=["AI Career Chatbot"])


@router.post(
    "/message",
    response_model=ChatResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Send a message to the AI career advisor",
)
async def send_message(
    body: ChatRequest,
    db=Depends(get_db),
    current_user: UserProfile = Depends(get_current_user),
):
    # Resolve the session (a new one is only saved after Gemini answers)
    new_session = None
    session = None
    if body.session_id:
        session = await db.chat_sessions.find_one({"id": body.session_id, "user_id": current_user.user_id})
        if not session:
            raise HTTPException(status_code=404, detail="Chat session not found")
        session_id = session["id"]
    else:
        title = body.message[:60] + ("…" if len(body.message) > 60 else "")
        now = utc_now()
        session_id = new_id()
        new_session = {
            "id": session_id, "user_id": current_user.user_id, "title": title,
            "created_at": now, "updated_at": now, "messages": [],
        }

    # Load recent history (last 20 messages)
    history = [
        {"role": m["role"], "content": m["content"]}
        for m in (session.get("messages", []) if session else [])[-20:]
    ]

    profile_dict = {
        "full_name": current_user.full_name,
        "degree": current_user.degree,
        "department": current_user.department,
        "skills": current_user.skills or [],
        "career_goals": current_user.career_goals,
    }

    # Get AI reply
    reply_text = await chat_with_advisor(body.message, history, profile_dict)

    # Persist user message + assistant reply
    now = utc_now()
    assistant_id = new_id()
    messages = [
        {"id": new_id(), "role": "user", "content": body.message, "created_at": now},
        {"id": assistant_id, "role": "assistant", "content": reply_text, "created_at": now},
    ]
    if new_session is not None:
        new_session["messages"] = messages
        new_session["updated_at"] = now
        await db.chat_sessions.insert_one(new_session)
    else:
        await db.chat_sessions.update_one(
            {"id": session_id, "user_id": current_user.user_id},
            {"$push": {"messages": {"$each": messages}}, "$set": {"updated_at": now}},
        )

    return ChatResponse(
        session_id=session_id,
        message_id=assistant_id,
        reply=reply_text,
        created_at=now,
    )


@router.get(
    "/sessions",
    response_model=list[ChatSessionOut],
    summary="List all chat sessions",
)
async def list_sessions(
    db=Depends(get_db),
    current_user: UserProfile = Depends(get_current_user),
):
    rows = await db.chat_sessions.find({"user_id": current_user.user_id}, {"messages": 0}).sort("updated_at", -1).to_list(length=None)
    return [public_document(row) for row in rows]


@router.get(
    "/sessions/{session_id}",
    response_model=ChatSessionDetail,
    summary="Get chat session with message history",
)
async def get_session(
    session_id: str,
    db=Depends(get_db),
    current_user: UserProfile = Depends(get_current_user),
):
    session = public_document(await db.chat_sessions.find_one({"id": session_id, "user_id": current_user.user_id}))
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")
    return session


@router.delete(
    "/sessions/{session_id}",
    response_model=MessageResponse,
    summary="Delete a chat session and its messages",
)
async def delete_session(
    session_id: str,
    db=Depends(get_db),
    current_user: UserProfile = Depends(get_current_user),
):
    session = await db.chat_sessions.find_one({"id": session_id, "user_id": current_user.user_id})
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")
    await db.chat_sessions.delete_one({"id": session_id, "user_id": current_user.user_id})
    return MessageResponse(message="Session deleted successfully")

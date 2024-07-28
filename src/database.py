import streamlit as st


def get_previous_chats(db, user_email):
    """Fetches previous chat records for a user from the database.

    Args:
        db: Deta Base instance.
        user_email (str): User's email address.

    Returns:
        list: List of previous chat records.
    """
    return db.fetch({"email": user_email}).items


def database(db, previous_key="key", previous_chat=None, max_chat_histories=5):
    """Manages user chat history in the database.

    Updates, adds, or removes chat history based on user interaction.

    Args:
        db: Deta Base instance.
        previous_key (str): Key for the previous chat in the database.
        previous_chat (list, optional): Previous chat messages.
        max_chat_histories (int, optional): Maximum number of chat histories to retain.

    Returns:
        None
    """
    user_email = st.session_state.user_email
    previous_chats = get_previous_chats(db, user_email)
    existing_chat = db.get(previous_key) if previous_key != "key" else None
    if (
        previous_chat is not None
        and existing_chat is not None
        and previous_key != "key"
    ):
        new_messages = [
            message
            for message in previous_chat
            if message not in existing_chat["chat"]
        ]
        existing_chat["chat"].extend(new_messages)
        db.update({"chat": existing_chat["chat"]}, key=previous_key)
        return
    previous_chat = (
        st.session_state.messages if previous_chat is None else previous_chat
    )
    if len(previous_chat) > 1 and previous_key == "key":
        title = previous_chat[1]["content"]
        db.put(
            {
                "email": user_email,
                "chat": previous_chat,
                "title": title[:25] + "....." if len(title) > 25 else title,
            }
        )

        if len(previous_chats) >= max_chat_histories:
            db.delete(previous_chats[0]["key"])
            st.warning(
                f"Chat '{previous_chats[0]['title']}' has been removed as you reached the limit of {max_chat_histories} chat histories."
            )

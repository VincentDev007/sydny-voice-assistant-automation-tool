"""
Command Parser
Parses natural language text into intent and target.
Does NOT execute — just figures out what the user wants.
"""


# Words to strip from commands
FILLER_WORDS = [
    "please", "could", "you", "can", "would", "will",
    "up", "the", "a", "an", "for", "me", "my"
]


def parse_command(text: str) -> dict:
    """
    Parse text into an intent and target.
    Returns: {"intent": str, "target": str or None, "needs_confirm": bool}
    """
    words = text.lower().strip().rstrip(".").split()
    cleaned = [w for w in words if w not in FILLER_WORDS]

    # --- OPEN FILE (check before general "open") ---
    if "file" in cleaned and "open" in cleaned:
        remaining = [w for w in cleaned if w not in ["open", "file"]]
        if remaining:
            return {"intent": "open-file", "target": " ".join(remaining), "needs_confirm": False}

    # --- OPEN APP ---
    if "open" in cleaned:
        cleaned.remove("open")
        if cleaned:
            return {"intent": "open-app", "target": " ".join(cleaned), "needs_confirm": False}

    # --- CLOSE APP ---
    if "close" in cleaned:
        cleaned.remove("close")
        if cleaned:
            return {"intent": "close-app", "target": " ".join(cleaned), "needs_confirm": False}

    # --- SEARCH / FIND FILE ---
    if "search" in cleaned or "find" in cleaned:
        remaining = [w for w in cleaned if w not in ["search", "find", "file"]]
        if remaining:
            return {"intent": "search-file", "target": " ".join(remaining), "needs_confirm": False}

    # --- DELETE FILE ---
    if "delete" in cleaned and "task" not in cleaned and "tasks" not in cleaned:
        remaining = [w for w in cleaned if w not in ["delete", "file"]]
        if remaining:
            return {"intent": "delete-file", "target": " ".join(remaining), "needs_confirm": True}

    # --- VOLUME ---
    if "volume" in cleaned:
        cleaned.remove("volume")
        for word in cleaned:
            if word.isdigit():
                return {"intent": "set-volume", "target": word, "needs_confirm": False}
        return {"intent": "set-volume", "target": None, "needs_confirm": False}

    if "mute" in cleaned:
        return {"intent": "mute", "target": None, "needs_confirm": False}

    if "unmute" in cleaned:
        return {"intent": "unmute", "target": None, "needs_confirm": False}

    # --- POWER ---
    if "shutdown" in cleaned or "shut" in cleaned:
        return {"intent": "shutdown", "target": None, "needs_confirm": True}

    if "restart" in cleaned:
        return {"intent": "restart", "target": None, "needs_confirm": True}

    if "sleep" in cleaned:
        return {"intent": "sleep", "target": None, "needs_confirm": True}

    # --- TASKS ---
    if "task" in cleaned or "tasks" in cleaned:
        # ADD TASK
        if "add" in cleaned or "create" in cleaned or "new" in cleaned:
            remove = ["add", "create", "new", "task", "tasks"]
            task_words = [w for w in cleaned if w not in remove]

            priority = "normal"
            if "high" in task_words or "important" in task_words or "urgent" in task_words:
                priority = "high"
                task_words = [w for w in task_words if w not in ["high", "important", "urgent", "priority"]]
            elif "low" in task_words:
                priority = "low"
                task_words = [w for w in task_words if w not in ["low", "priority"]]

            if task_words:
                return {"intent": "add-task", "target": f"{' '.join(task_words)}|{priority}", "needs_confirm": False}
            return {"intent": "add-task", "target": None, "needs_confirm": False}

        # LIST TASKS
        if "list" in cleaned or "show" in cleaned or "what" in cleaned:
            if "all" in cleaned or "completed" in cleaned:
                return {"intent": "list-all-tasks", "target": None, "needs_confirm": False}
            return {"intent": "list-tasks", "target": None, "needs_confirm": False}

        # COMPLETE TASK
        if "complete" in cleaned or "finish" in cleaned or "done" in cleaned:
            for word in cleaned:
                if word.isdigit():
                    return {"intent": "complete-task", "target": word, "needs_confirm": False}
            return {"intent": "complete-task", "target": None, "needs_confirm": False}

        # DELETE TASK
        if "delete" in cleaned or "remove" in cleaned or "cancel" in cleaned:
            for word in cleaned:
                if word.isdigit():
                    return {"intent": "delete-task", "target": word, "needs_confirm": True}
            return {"intent": "delete-task", "target": None, "needs_confirm": True}

    # --- TASK COUNT ---
    if ("how" in cleaned and "many" in cleaned) or "count" in cleaned:
        if "task" in cleaned or "tasks" in cleaned:
            return {"intent": "task-count", "target": None, "needs_confirm": False}

    # --- EXIT ---
    if "exit" in cleaned or "quit" in cleaned:
        return {"intent": "exit", "target": None, "needs_confirm": False}

    # --- UNKNOWN ---
    return {"intent": None, "target": None, "needs_confirm": False}

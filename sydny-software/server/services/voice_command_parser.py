"""
Command Parser — services/command_parser.py
=============================================
Parses natural language text into a structured command.
Does NOT execute anything — just figures out what the user wants.

WHAT IT DOES:
  Takes a string like "open Safari please" and returns:
    {"intent": "open-app", "target": "safari", "needs_confirm": false}

  The frontend (App.tsx) then uses the intent to decide what to execute.

HOW IT WORKS:
  1. Convert text to lowercase, strip punctuation
  2. Remove filler words ("please", "could", "you", etc.)
  3. Check for keywords in a specific order (most specific first)
  4. Extract the intent (what to do), target (what to do it on), and needs_confirm flag

WHY KEYWORD-BASED (not AI)?
  Simple, fast, predictable, and works offline.
  No API calls, no model loading, no latency.
  The tradeoff is that it only understands specific phrase patterns.
  A future upgrade could use an LLM for more flexible parsing.

SUPPORTED INTENTS (18 total):
  Apps:   open-app, close-app
  Files:  open-file, search-file, delete-file
  Volume: set-volume, mute, unmute
  Power:  shutdown, restart, sleep
  Tasks:  add-task, list-tasks, list-all-tasks, complete-task, delete-task, task-count
  Other:  exit

needs_confirm FLAG:
  Set to True for destructive/dangerous operations:
    shutdown, restart, sleep, delete-file, delete-task
  When True, the frontend shows a confirmation dialog before executing.

HOW IT CONNECTS:
  User speaks → Whisper transcribes → THIS FILE parses → App.tsx executes
  routes/voice.py calls parse_command() for both voice and text input
"""


# ============================================================
# FILLER WORDS
# ============================================================
# Common words that add no meaning to a command.
# "Please open the Safari for me" → after stripping: ["open", "safari"]
# This helps the parser focus on the important words (the intent and target).
FILLER_WORDS = [
    "please", "could", "you", "can", "would", "will",
    "up", "the", "a", "an", "for", "me", "my"
]


def parse_command(text: str) -> dict:
    """
    Parse natural language text into a structured command.

    Args:
        text: Raw text from voice transcription or typed input
              e.g., "Please open Safari for me."

    Returns:
        dict with three keys:
          - intent: str or None — what action to take (e.g., "open-app", "mute")
          - target: str or None — what to act on (e.g., "safari", "50")
          - needs_confirm: bool — whether to show confirmation dialog first

    PARSING ORDER MATTERS:
      We check "open file" BEFORE "open" because "open file report.pdf"
      should match open-file, not open-app. Most specific patterns first.
    """

    # ── STEP 1: Normalize the input ──
    # Convert to lowercase, strip whitespace and trailing periods, split into words
    words = text.lower().strip().rstrip(".").split()

    # ── STEP 2: Remove filler words ──
    # "Please open the Safari" → ["open", "safari"]
    cleaned = [w for w in words if w not in FILLER_WORDS]


    # ================================================================
    # OPEN FILE — checked BEFORE "open app" because "open file X" contains "open"
    # ================================================================
    # "Open file report.pdf" → intent: "open-file", target: "report.pdf"
    if "file" in cleaned and "open" in cleaned:
        remaining = [w for w in cleaned if w not in ["open", "file"]]
        if remaining:
            return {"intent": "open-file", "target": " ".join(remaining), "needs_confirm": False}


    # ================================================================
    # OPEN APP
    # ================================================================
    # "Open Safari" → intent: "open-app", target: "safari"
    if "open" in cleaned:
        cleaned.remove("open")   # Remove "open", everything left is the app name
        if cleaned:
            return {"intent": "open-app", "target": " ".join(cleaned), "needs_confirm": False}


    # ================================================================
    # CLOSE APP
    # ================================================================
    # "Close Safari" → intent: "close-app", target: "safari"
    if "close" in cleaned:
        cleaned.remove("close")
        if cleaned:
            return {"intent": "close-app", "target": " ".join(cleaned), "needs_confirm": False}


    # ================================================================
    # SEARCH / FIND FILE
    # ================================================================
    # "Search for report.txt" → intent: "search-file", target: "report.txt"
    # "Find homework" → intent: "search-file", target: "homework"
    if "search" in cleaned or "find" in cleaned:
        remaining = [w for w in cleaned if w not in ["search", "find", "file"]]
        if remaining:
            return {"intent": "search-file", "target": " ".join(remaining), "needs_confirm": False}


    # ================================================================
    # DELETE FILE (but NOT delete task — that's handled in the TASKS section)
    # ================================================================
    # "Delete old-notes.txt" → intent: "delete-file", target: "old-notes.txt"
    # needs_confirm=True because file deletion is irreversible
    if "delete" in cleaned and "task" not in cleaned and "tasks" not in cleaned:
        remaining = [w for w in cleaned if w not in ["delete", "file"]]
        if remaining:
            return {"intent": "delete-file", "target": " ".join(remaining), "needs_confirm": True}


    # ================================================================
    # VOLUME
    # ================================================================
    # "Set volume to 50" → intent: "set-volume", target: "50"
    # "Volume 75"        → intent: "set-volume", target: "75"
    if "volume" in cleaned:
        cleaned.remove("volume")
        for word in cleaned:
            if word.isdigit():   # Find the first number → that's the volume level
                return {"intent": "set-volume", "target": word, "needs_confirm": False}
        return {"intent": "set-volume", "target": None, "needs_confirm": False}

    # "Mute" → intent: "mute"
    if "mute" in cleaned:
        return {"intent": "mute", "target": None, "needs_confirm": False}

    # "Unmute" → intent: "unmute"
    if "unmute" in cleaned:
        return {"intent": "unmute", "target": None, "needs_confirm": False}


    # ================================================================
    # POWER — all flagged with needs_confirm=True (dangerous!)
    # ================================================================
    # "Shutdown" or "Shut down" → intent: "shutdown"
    if "shutdown" in cleaned or "shut" in cleaned:
        return {"intent": "shutdown", "target": None, "needs_confirm": True}

    # "Restart" → intent: "restart"
    if "restart" in cleaned:
        return {"intent": "restart", "target": None, "needs_confirm": True}

    # "Sleep" → intent: "sleep"
    if "sleep" in cleaned:
        return {"intent": "sleep", "target": None, "needs_confirm": True}


    # ================================================================
    # TASKS — only enters this block if "task" or "tasks" is in the command
    # ================================================================
    if "task" in cleaned or "tasks" in cleaned:

        # ── ADD TASK ──
        # "Add task buy groceries"           → target: "buy groceries|normal"
        # "Add task urgent fix the bug"      → target: "fix bug|high"
        # "Create new task low priority walk" → target: "walk|low"
        #
        # The target format is "description|priority" — App.tsx splits on "|"
        if "add" in cleaned or "create" in cleaned or "new" in cleaned:
            # Remove action words to isolate the task description
            remove = ["add", "create", "new", "task", "tasks"]
            task_words = [w for w in cleaned if w not in remove]

            # Extract priority from keywords (default: "normal")
            priority = "normal"
            if "high" in task_words or "important" in task_words or "urgent" in task_words:
                priority = "high"
                task_words = [w for w in task_words if w not in ["high", "important", "urgent", "priority"]]
            elif "low" in task_words:
                priority = "low"
                task_words = [w for w in task_words if w not in ["low", "priority"]]

            if task_words:
                # Format: "description|priority" — split by App.tsx when creating the task
                return {"intent": "add-task", "target": f"{' '.join(task_words)}|{priority}", "needs_confirm": False}
            return {"intent": "add-task", "target": None, "needs_confirm": False}

        # ── LIST TASKS ──
        # "List tasks"     → intent: "list-tasks"
        # "Show all tasks" → intent: "list-all-tasks"
        # "What are my tasks" → intent: "list-tasks"
        if "list" in cleaned or "show" in cleaned or "what" in cleaned:
            if "all" in cleaned or "completed" in cleaned:
                return {"intent": "list-all-tasks", "target": None, "needs_confirm": False}
            return {"intent": "list-tasks", "target": None, "needs_confirm": False}

        # ── COMPLETE TASK ──
        # "Complete task 3" → intent: "complete-task", target: "3"
        # "Finish task 1"   → intent: "complete-task", target: "1"
        if "complete" in cleaned or "finish" in cleaned or "done" in cleaned:
            for word in cleaned:
                if word.isdigit():   # Find the task ID number
                    return {"intent": "complete-task", "target": word, "needs_confirm": False}
            return {"intent": "complete-task", "target": None, "needs_confirm": False}

        # ── DELETE TASK ──
        # "Delete task 5" → intent: "delete-task", target: "5"
        # needs_confirm=True because deletion is permanent
        if "delete" in cleaned or "remove" in cleaned or "cancel" in cleaned:
            for word in cleaned:
                if word.isdigit():   # Find the task ID number
                    return {"intent": "delete-task", "target": word, "needs_confirm": True}
            return {"intent": "delete-task", "target": None, "needs_confirm": True}


    # ================================================================
    # TASK COUNT
    # ================================================================
    # "How many tasks do I have?" → intent: "task-count"
    # "Count tasks" → intent: "task-count"
    if ("how" in cleaned and "many" in cleaned) or "count" in cleaned:
        if "task" in cleaned or "tasks" in cleaned:
            return {"intent": "task-count", "target": None, "needs_confirm": False}


    # ================================================================
    # EXIT
    # ================================================================
    # "Exit" or "Quit" → intent: "exit"
    if "exit" in cleaned or "quit" in cleaned:
        return {"intent": "exit", "target": None, "needs_confirm": False}


    # ================================================================
    # UNKNOWN — no matching intent found
    # ================================================================
    # If we get here, the parser couldn't understand the command.
    # The frontend shows: "I heard you, but I don't know how to do that."
    return {"intent": None, "target": None, "needs_confirm": False}

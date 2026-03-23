// ============================================================
// useStore.ts — Global State Management (Zustand)
// ============================================================
// This is SYDNY's single source of truth for all UI state.
// Every component reads from here and writes back here.
//
// WHY ZUSTAND (not Redux or Context)?
//   Zustand is minimal, no boilerplate, and doesn't require providers.
//   Any component can read specific slices of state with selectors,
//   and only re-renders when THOSE specific values change.
//   `create()` returns both a hook (for components) and a `.getState()` method
//   (for reading state outside of React — like inside useCallback closures).
//
// HOW TO USE IT IN A COMPONENT:
//   const status = useStore((s) => s.status);         // reads only status
//   const addMessage = useStore((s) => s.addMessage);  // reads only addMessage
//   Component only re-renders when status or addMessage changes, not all state.
//
// HOW TO USE IT OUTSIDE REACT (in callbacks):
//   useStore.getState().safeMode        → read current value
//   useStore.getState().setPendingCommand(cmd) → call action
//
// STATE OVERVIEW:
//   status        → voice pipeline state (idle/listening/speaking)
//   tasks         → task list from the database
//   messages      → terminal message log (user/sydny/system)
//   confirmMessage/confirmAction → confirm dialog content
//   safeMode      → safe vs live mode flag
//   pendingCommand → parsed command waiting to be executed by App.tsx
// ============================================================

// create — Zustand's store factory function
import { create } from "zustand";

// api — all backend HTTP calls (used inside store actions)
import * as api from "../services/api";


// ============================================================
// TYPE DEFINITIONS
// ============================================================
// TypeScript interfaces that define the shape of each data type

// A task from the database
interface Task {
  id: number;
  description: string;
  priority: string;               // "low" | "normal" | "high"
  completed: boolean;
  created_at: string;             // ISO date string from the API
  completed_at: string | null;    // null if not yet completed
}

// A message in the terminal log
interface Message {
  text: string;
  type: "user" | "sydny" | "system"; // Controls color: green | red | gray
}

// The parsed result from the command parser
// This is what command_parser.py returns, mirrored here in TypeScript
interface ParsedCommand {
  intent: string;          // What to do (e.g., "open-app", "mute")
  target: string | null;   // What to do it on (e.g., "safari", "50")
  needs_confirm: boolean;  // True for dangerous operations → show ConfirmDialog
}


// ============================================================
// FULL STATE INTERFACE
// ============================================================
// Defines EVERY piece of state and EVERY action in the store.
// TypeScript uses this to enforce that the store implementation is complete.
interface AppState {
  // ── Voice status ──
  status: "idle" | "listening" | "speaking";
  setStatus: (status: "idle" | "listening" | "speaking") => void;

  // ── Tasks ──
  tasks: Task[];
  loadTasks: () => Promise<void>;                                  // Fetch all tasks from backend
  addTask: (description: string, priority: string) => Promise<void>; // Create new task
  completeTask: (taskId: number) => Promise<void>;                 // Mark task as done
  removeTask: (taskId: number) => Promise<void>;                   // Delete task

  // ── Terminal messages ──
  messages: Message[];
  addMessage: (text: string, type: "user" | "sydny" | "system") => void;

  // ── Confirm dialog ──
  confirmMessage: string | null;           // Text shown in the dialog (null = dialog hidden)
  confirmAction: (() => void) | null;      // Function to call when user clicks Confirm
  showConfirm: (message: string, action: () => void) => void; // Opens the dialog
  hideConfirm: () => void;                 // Closes and clears the dialog

  // ── Safe mode ──
  safeMode: boolean;           // true = safe (announce only), false = live (execute for real)
  toggleSafeMode: () => void;  // Flips between safe and live

  // ── Pending command ──
  // Set by useVoice.ts or sendTextCommand() when a parsed result arrives.
  // Watched by App.tsx's useEffect, which then calls executeCommand().
  pendingCommand: ParsedCommand | null;
  setPendingCommand: (cmd: ParsedCommand | null) => void;

  // ── Text command entry (typed input) ──
  sendTextCommand: (text: string) => Promise<void>;
}


// ============================================================
// STORE IMPLEMENTATION
// ============================================================
// create<AppState>() creates a Zustand store that matches the AppState interface.
// (set, get) are Zustand's built-in helpers:
//   set(partialState) → merges new values into the store (triggers re-renders)
//   get()             → reads the CURRENT state (use inside async functions)
const useStore = create<AppState>((set, get) => ({

  // ── Voice status ──
  status: "idle",
  setStatus: (status) => set({ status }), // Simple setter — merges {status: newValue}


  // ── Tasks ──
  tasks: [],

  loadTasks: async () => {
    // Fetch all tasks from GET /api/tasks
    // Response is an array of Task objects — store them directly
    const tasks = await api.fetchTasks();
    set({ tasks });
  },

  addTask: async (description, priority) => {
    // Create the task via POST /api/tasks, then reload the list
    // We reload instead of manually appending because the backend assigns the ID
    await api.createTask(description, priority);
    await get().loadTasks(); // Reload to get the new task with its server-assigned ID
  },

  completeTask: async (taskId) => {
    // Mark task as completed via PUT /api/tasks/{id} with {completed: true}
    // The backend also records completed_at timestamp
    await api.updateTask(taskId, { completed: true });
    await get().loadTasks(); // Reload to reflect the updated state
  },

  removeTask: async (taskId) => {
    // Delete task via DELETE /api/tasks/{id}
    await api.deleteTask(taskId);
    await get().loadTasks(); // Reload to remove the task from the UI
  },


  // ── Terminal messages ──
  messages: [],

  addMessage: (text, type) =>
    // Spread existing messages and append the new one
    // We never mutate the array — always create a new one (React immutability requirement)
    set((state) => ({ messages: [...state.messages, { text, type }] })),


  // ── Confirm dialog ──
  confirmMessage: null,
  confirmAction: null,

  showConfirm: (message, action) =>
    // Set both the message and the action to show the dialog
    // App.tsx renders ConfirmDialog when confirmMessage is not null
    set({ confirmMessage: message, confirmAction: action }),

  hideConfirm: () =>
    // Clear both to hide the dialog and discard the pending action
    set({ confirmMessage: null, confirmAction: null }),


  // ── Safe mode ──
  // Default is TRUE — safe mode is ON when the app starts.
  // This means commands are announced but not executed until the user switches to LIVE MODE.
  safeMode: true,

  toggleSafeMode: () =>
    // Flip the current value: true → false (live), false → true (safe)
    set((state) => ({ safeMode: !state.safeMode })),


  // ── Pending command ──
  pendingCommand: null,

  setPendingCommand: (cmd) =>
    // Set the pending command (triggers App.tsx's useEffect)
    // Pass null to clear it after execution
    set({ pendingCommand: cmd }),


  // ── Text command (typed input) ──
  sendTextCommand: async (text) => {
    const { addMessage, setPendingCommand } = get();

    // Show the typed text in the terminal as a user message
    addMessage(text, "user");

    // Send to /api/voice/text → command_parser → returns {intent, target, needs_confirm}
    const result = await api.sendText(text);

    // If the parser returned no intent, the text wasn't understood
    if (result.intent === null) {
      addMessage(`I heard you, but I don't know how to do that.`, "sydny");
      return;
    }

    // Show the parsed command as a system message
    addMessage(`Command: ${result.intent}${result.target ? ` → ${result.target}` : ""}`, "system");

    // Hand off to App.tsx for execution via the pendingCommand pipeline
    setPendingCommand(result);
  },
}));

export default useStore;

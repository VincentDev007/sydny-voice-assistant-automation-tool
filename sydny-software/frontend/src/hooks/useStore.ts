import { create } from "zustand";
import * as api from "../services/api";

interface Task {
  id: number;
  description: string;
  priority: string;
  completed: boolean;
  created_at: string;
  completed_at: string | null;
}

interface Message {
  text: string;
  type: "user" | "sydny" | "system";
}

interface ParsedCommand {
  intent: string;
  target: string | null;
  needs_confirm: boolean;
}

interface AppState {
  // Voice status
  status: "idle" | "listening" | "speaking";
  setStatus: (status: "idle" | "listening" | "speaking") => void;

  // Tasks
  tasks: Task[];
  loadTasks: () => Promise<void>;
  addTask: (description: string, priority: string) => Promise<void>;
  completeTask: (taskId: number) => Promise<void>;
  removeTask: (taskId: number) => Promise<void>;

  // Terminal messages
  messages: Message[];
  addMessage: (text: string, type: "user" | "sydny" | "system") => void;

  // Confirm dialog
  confirmMessage: string | null;
  confirmAction: (() => void) | null;
  showConfirm: (message: string, action: () => void) => void;
  hideConfirm: () => void;

  // Safe mode
  safeMode: boolean;
  toggleSafeMode: () => void;

  // Pending command from voice
  pendingCommand: ParsedCommand | null;
  setPendingCommand: (cmd: ParsedCommand | null) => void;

  // Send text command
  sendTextCommand: (text: string) => Promise<void>;
}

const useStore = create<AppState>((set, get) => ({
  // Voice status
  status: "idle",
  setStatus: (status) => set({ status }),

  // Tasks
  tasks: [],
  loadTasks: async () => {
    const tasks = await api.fetchTasks();
    set({ tasks });
  },
  addTask: async (description, priority) => {
    await api.createTask(description, priority);
    await get().loadTasks();
  },
  completeTask: async (taskId) => {
    await api.updateTask(taskId, { completed: true });
    await get().loadTasks();
  },
  removeTask: async (taskId) => {
    await api.deleteTask(taskId);
    await get().loadTasks();
  },

  // Terminal messages
  messages: [],
  addMessage: (text, type) =>
    set((state) => ({ messages: [...state.messages, { text, type }] })),

  // Confirm dialog
  confirmMessage: null,
  confirmAction: null,
  showConfirm: (message, action) =>
    set({ confirmMessage: message, confirmAction: action }),
  hideConfirm: () => set({ confirmMessage: null, confirmAction: null }),

  // Safe mode
  safeMode: true,
  toggleSafeMode: () => set((state) => ({ safeMode: !state.safeMode })),

  // Pending command from voice
  pendingCommand: null,
  setPendingCommand: (cmd) => set({ pendingCommand: cmd }),

  // Send text command
  sendTextCommand: async (text) => {
    const { addMessage, setPendingCommand } = get();
    addMessage(text, "user");

    const result = await api.sendText(text);

    if (result.intent === null) {
      addMessage(`I heard you, but I don't know how to do that.`, "sydny");
      return;
    }

    addMessage(`Command: ${result.intent}${result.target ? ` → ${result.target}` : ""}`, "system");
    setPendingCommand(result);
  },
}));

export default useStore;

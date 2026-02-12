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

  // Send text command
  sendTextCommand: async (text) => {
    const { addMessage } = get();
    addMessage(text, "user");

    const result = await api.sendText(text);

    if (result.intent === null) {
      addMessage(`You said: ${text}`, "sydny");
      return;
    }

    addMessage(`Command: ${result.intent}${result.target ? ` → ${result.target}` : ""}`, "system");
  },
}));

export default useStore;

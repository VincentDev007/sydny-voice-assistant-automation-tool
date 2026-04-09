import { create } from "zustand";

export type OrbState = "idle" | "wake" | "user" | "thinking" | "speak" | "confirm";

interface ConfirmPayload {
  intent: string;
  target: string | null;
  response: string;
}

interface AppState {
  orbState: OrbState;
  setOrbState: (state: OrbState) => void;

  confirmPayload: ConfirmPayload | null;
  showConfirm: (payload: ConfirmPayload) => void;
  hideConfirm: () => void;

  sessionActive: boolean;
  setSessionActive: (active: boolean) => void;
}

const useStore = create<AppState>((set) => ({
  orbState: "idle",
  setOrbState: (orbState) => set({ orbState }),

  confirmPayload: null,
  showConfirm: (payload) => set({ confirmPayload: payload, orbState: "confirm" }),
  hideConfirm: () => set({ confirmPayload: null, orbState: "idle" }),

  sessionActive: false,
  setSessionActive: (sessionActive) => set({ sessionActive }),
}));

export default useStore;

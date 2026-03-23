// ============================================================
// App.tsx — Root Component (The Brain of the Frontend)
// ============================================================
// This is the top-level React component. It:
//   1. Wires together all hooks, state, and components
//   2. Contains executeCommand() — the switch that routes every intent to an API call
//   3. Contains sydnySay() — adds a message to the terminal AND speaks it via TTS
//   4. Watches pendingCommand — runs commands or shows a confirm dialog when needed
//   5. Renders the full UI: HAL eye, status, terminal, task list, confirm dialog, mode toggle
//
// DATA FLOW (voice pipeline, summarized):
//   User clicks eye → useVoice records → /transcribe → /command → setPendingCommand
//   → useEffect here → executeCommand() → api call → backend action → sydnySay(response)
//
// SAFE MODE vs LIVE MODE:
//   Safe Mode (default ON):  executeCommand() announces the command but does NOT call any API
//   Live Mode:               executeCommand() actually calls the backend API and runs the command
// ============================================================

import { useEffect, useCallback } from "react";
import "./App.css";

// Components — UI building blocks
import HalEye from "./components/HalEye";           // Animated HAL eye, click to record
import Terminal from "./components/Terminal";       // Scrolling message log
import StatusLabel from "./components/StatusLabel"; // SYDNY / LISTENING / SPEAKING label
import TaskList from "./components/TaskList";       // Task list display
import ConfirmDialog from "./components/ConfirmDialog"; // Confirmation modal for dangerous ops

// Hooks — logic and state
import useStore from "./hooks/useStore";   // Zustand global state store
import useVoice from "./hooks/useVoice";   // Microphone recording hook

// API — all backend HTTP calls
import * as api from "./services/api";


function App() {
  // ── Pull state and actions from the Zustand store ──
  // We select individual pieces of state to avoid unnecessary re-renders.
  // If we did `const store = useStore()`, every state change would re-render the whole component.
  const status = useStore((s) => s.status);                     // "idle" | "listening" | "speaking"
  const messages = useStore((s) => s.messages);                 // Array of terminal messages
  const tasks = useStore((s) => s.tasks);                       // Array of Task objects from DB
  const confirmMessage = useStore((s) => s.confirmMessage);     // Text for confirm dialog (or null)
  const confirmAction = useStore((s) => s.confirmAction);       // Function to run on confirm (or null)
  const hideConfirm = useStore((s) => s.hideConfirm);           // Function to close confirm dialog
  const loadTasks = useStore((s) => s.loadTasks);               // Fetches tasks from backend
  const addMessage = useStore((s) => s.addMessage);             // Adds a message to the terminal
  const pendingCommand = useStore((s) => s.pendingCommand);     // Parsed command waiting to be executed
  const setPendingCommand = useStore((s) => s.setPendingCommand); // Sets or clears the pending command
  const showConfirm = useStore((s) => s.showConfirm);           // Shows the confirm dialog
  const safeMode = useStore((s) => s.safeMode);                 // true = safe, false = live
  const toggleSafeMode = useStore((s) => s.toggleSafeMode);    // Flips safe/live mode

  // ── Voice hook ──
  // toggleRecording: idle → start recording, listening → stop recording, speaking → ignore
  const { toggleRecording } = useVoice();


  // ============================================================
  // sydnySay — Sydny's "voice" function
  // ============================================================
  // Adds text to the terminal as a "sydny" message (shown in red)
  // AND sends it to the backend /api/voice/speak to be spoken out loud via macOS `say`.
  //
  // useCallback with [addMessage] as dependency:
  //   React will reuse the same function reference unless `addMessage` changes.
  //   This prevents unnecessary re-renders and keeps useEffect dependencies stable.
  //
  // .catch(() => {}) — silently ignore TTS errors (if the backend is down, UI still works)
  const sydnySay = useCallback(
    (text: string) => {
      addMessage(text, "sydny");           // Add to terminal display
      api.speakText(text).catch(() => {}); // Speak via macOS `say` (fire and forget)
    },
    [addMessage]
  );


  // ============================================================
  // STARTUP — runs once when the component first mounts
  // ============================================================
  // [] as dependency = only runs once on mount (like componentDidMount in class components)
  useEffect(() => {
    loadTasks();                                    // Fetch saved tasks from the database
    sydnySay("SYDNY online. Awaiting commands.");   // Greeting message + TTS
  }, []);


  // ============================================================
  // executeCommand — Routes intents to API calls
  // ============================================================
  // This is the heart of the command execution system.
  // It receives a parsed intent (e.g., "open-app") and target (e.g., "safari")
  // and calls the appropriate backend API endpoint.
  //
  // SAFE MODE GUARD (first check):
  //   If safe mode is ON, we skip ALL api calls and just announce what would happen.
  //   This is the key testing feature — you can speak commands safely without executing them.
  //
  // WHY useStore.getState() instead of the selector above?
  //   Inside useCallback, the `safeMode` selector value is captured at creation time.
  //   useStore.getState() always reads the CURRENT state, avoiding stale closure issues.
  const executeCommand = useCallback(
    async (intent: string, target: string | null) => {

      // ── SAFE MODE GUARD ──
      // If safe mode is enabled, just announce what would happen — don't call the API
      if (useStore.getState().safeMode) {
        const label = target ? `${intent} → ${target}` : intent;
        sydnySay(`[SAFE] Would execute: ${label}`);
        return; // Stop here — nothing gets executed
      }

      try {
        switch (intent) {
          // ── APPS ──
          case "open-app": {
            // "Open Safari" → api.openApp("safari") → backend runs `open -a safari`
            if (!target) { sydnySay("No app specified."); break; }
            await api.openApp(target);
            sydnySay(`Opening ${target}.`);
            break;
          }
          case "close-app": {
            // "Close Safari" → api.closeApp("safari") → backend runs AppleScript quit
            if (!target) { sydnySay("No app specified."); break; }
            await api.closeApp(target);
            sydnySay(`Closing ${target}.`);
            break;
          }

          // ── VOLUME ──
          case "set-volume": {
            // "Set volume to 50" → target is "50" → parseInt("50") = 50 → api.setVolume(50)
            if (!target) { sydnySay("No volume level specified."); break; }
            await api.setVolume(parseInt(target));
            sydnySay(`Volume set to ${target}.`);
            break;
          }
          case "mute": {
            // "Mute" → api.mute() → backend runs `osascript -e "set volume with output muted"`
            await api.mute();
            sydnySay("Muted.");
            break;
          }
          case "unmute": {
            // "Unmute" → api.unmute() → backend unmutes
            await api.unmute();
            sydnySay("Unmuted.");
            break;
          }

          // ── POWER ──
          // These are only reached if the user confirmed in the ConfirmDialog
          case "shutdown": {
            await api.shutdownSystem();
            sydnySay("Shutting down.");
            break;
          }
          case "restart": {
            await api.restartSystem();
            sydnySay("Restarting.");
            break;
          }
          case "sleep": {
            await api.sleepSystem();
            sydnySay("Going to sleep.");
            break;
          }

          // ── FILES ──
          case "open-file": {
            if (!target) { sydnySay("No file specified."); break; }
            await api.openFile(target);
            sydnySay(`Opening file: ${target}`);
            break;
          }
          case "search-file": {
            if (!target) { sydnySay("No filename specified."); break; }
            const searchResult = await api.searchFile(target);
            if (searchResult.results && searchResult.results.length > 0) {
              sydnySay(`Found ${searchResult.results.length} result(s).`);
              // Show the first 5 file paths as system messages in the terminal
              searchResult.results.slice(0, 5).forEach((path: string) => {
                addMessage(path, "system");
              });
            } else {
              sydnySay(`No files found matching "${target}".`);
            }
            break;
          }
          case "delete-file": {
            // Only reached after ConfirmDialog confirms (needs_confirm=true for this intent)
            if (!target) { sydnySay("No file specified."); break; }
            await api.deleteFile(target);
            sydnySay(`Deleted: ${target}`);
            break;
          }

          // ── TASKS ──
          case "add-task": {
            // target format from command_parser: "description|priority"
            // Example: "buy groceries|high"
            // We split on "|" to get description and priority separately
            if (!target) { sydnySay("No task description given."); break; }
            const [description, priority] = target.split("|");
            await useStore.getState().addTask(description, priority || "normal");
            sydnySay(`Task added: ${description}`);
            break;
          }
          case "list-tasks":
          case "list-all-tasks": {
            // Reload tasks from DB then display them in the terminal
            await loadTasks();
            const currentTasks = useStore.getState().tasks; // Get fresh state
            if (currentTasks.length === 0) {
              sydnySay("No tasks.");
            } else {
              sydnySay(`You have ${currentTasks.length} task(s).`);
              // Show each task as a system message
              currentTasks.forEach((t) => {
                const check = t.completed ? "[done]" : "[    ]";
                addMessage(`${check} #${t.id} ${t.description}`, "system");
              });
            }
            break;
          }
          case "complete-task": {
            // target is the task ID as a string (e.g., "3")
            if (!target) { sydnySay("No task ID given."); break; }
            await useStore.getState().completeTask(parseInt(target));
            sydnySay(`Task ${target} completed.`);
            break;
          }
          case "delete-task": {
            // Only reached after ConfirmDialog confirms
            if (!target) { sydnySay("No task ID given."); break; }
            await useStore.getState().removeTask(parseInt(target));
            sydnySay(`Task ${target} deleted.`);
            break;
          }
          case "task-count": {
            await loadTasks();
            const count = useStore.getState().tasks.length;
            sydnySay(`You have ${count} task(s).`);
            break;
          }

          // ── EXIT ──
          case "exit": {
            // We say goodbye but the app stays open (Tauri window stays)
            sydnySay("Goodbye.");
            break;
          }

          // ── UNKNOWN INTENT ──
          default:
            sydnySay(`Unknown command: ${intent}`);
        }
      } catch (err) {
        console.error("Execution error:", err);
        sydnySay("Failed to execute command.");
      }
    },
    [sydnySay, addMessage, loadTasks]
  );


  // ============================================================
  // PENDING COMMAND REACTOR — watches for new parsed commands
  // ============================================================
  // This useEffect runs whenever `pendingCommand` changes.
  // useVoice.ts and useStore.sendTextCommand() both set pendingCommand
  // when a new parsed result arrives.
  //
  // FLOW:
  //   1. pendingCommand is set (by voice or text input)
  //   2. This effect fires
  //   3. We immediately clear pendingCommand (so it doesn't fire again)
  //   4. If needs_confirm → show ConfirmDialog first, execute on confirm
  //   5. If NOT needs_confirm → execute immediately
  useEffect(() => {
    if (!pendingCommand) return; // Nothing to do

    const { intent, target, needs_confirm } = pendingCommand;
    setPendingCommand(null); // Clear BEFORE executing to avoid double-execution

    if (needs_confirm) {
      // Dangerous operation — show confirmation dialog first
      // The callback passed to showConfirm runs ONLY if user clicks "CONFIRM"
      showConfirm(`Execute "${intent}"${target ? ` on ${target}` : ""}?`, () => {
        executeCommand(intent, target);
      });
    } else {
      // Safe operation — execute immediately
      executeCommand(intent, target);
    }
  }, [pendingCommand, setPendingCommand, showConfirm, executeCommand]);


  // ============================================================
  // RENDER — the actual UI
  // ============================================================
  return (
    // Full screen black background, vertical layout with flex
    <div className="min-h-screen bg-black flex flex-col items-center justify-between py-8 px-6">

      {/* ── SAFE/LIVE MODE TOGGLE (top-right corner) ── */}
      {/* Yellow = Safe Mode (safe to test), Green = Live Mode (real commands) */}
      <button
        onClick={toggleSafeMode}
        className={`absolute top-4 right-4 px-3 py-1 rounded font-mono text-xs tracking-widest border ${
          safeMode
            ? "border-yellow-500 text-yellow-500"  // Yellow = SAFE MODE
            : "border-green-500 text-green-500"    // Green = LIVE MODE
        }`}
      >
        {safeMode ? "SAFE MODE" : "LIVE MODE"}
      </button>

      {/* ── CENTER: HAL EYE + STATUS LABEL ── */}
      {/* The eye is clickable — each click toggles recording on/off */}
      <div className="flex-1 flex flex-col items-center justify-center gap-4">
        <HalEye status={status} onClick={toggleRecording} />
        <StatusLabel status={status} />
      </div>

      {/* ── BOTTOM: TERMINAL + TASK LIST ── */}
      <div className="w-full flex flex-col items-center gap-4">
        <Terminal messages={messages} />   {/* Shows conversation history */}
        <TaskList tasks={tasks} />         {/* Shows task list from DB */}
      </div>

      {/* ── CONFIRM DIALOG (modal overlay) ── */}
      {/* Only shown when confirmMessage is set (dangerous command needs confirmation) */}
      {confirmMessage && confirmAction && (
        <ConfirmDialog
          message={confirmMessage}
          onConfirm={() => {
            confirmAction(); // Execute the dangerous action
            hideConfirm();   // Close the dialog
          }}
          onCancel={hideConfirm} // Close without executing
        />
      )}
    </div>
  );
}

export default App;

import { useEffect, useCallback } from "react";
import "./App.css";
import HalEye from "./components/HalEye";
import Terminal from "./components/Terminal";
import StatusLabel from "./components/StatusLabel";
import TaskList from "./components/TaskList";
import ConfirmDialog from "./components/ConfirmDialog";
import useStore from "./hooks/useStore";
import useVoice from "./hooks/useVoice";
import * as api from "./services/api";

function App() {
  const status = useStore((s) => s.status);
  const messages = useStore((s) => s.messages);
  const tasks = useStore((s) => s.tasks);
  const confirmMessage = useStore((s) => s.confirmMessage);
  const confirmAction = useStore((s) => s.confirmAction);
  const hideConfirm = useStore((s) => s.hideConfirm);
  const loadTasks = useStore((s) => s.loadTasks);
  const addMessage = useStore((s) => s.addMessage);
  const pendingCommand = useStore((s) => s.pendingCommand);
  const setPendingCommand = useStore((s) => s.setPendingCommand);
  const showConfirm = useStore((s) => s.showConfirm);
  const safeMode = useStore((s) => s.safeMode);
  const toggleSafeMode = useStore((s) => s.toggleSafeMode);

  const { toggleRecording } = useVoice();

  // Add Sydny message to terminal and speak it
  const sydnySay = useCallback(
    (text: string) => {
      addMessage(text, "sydny");
      api.speakText(text).catch(() => {});
    },
    [addMessage]
  );

  // Load tasks on mount
  useEffect(() => {
    loadTasks();
    sydnySay("SYDNY online. Awaiting commands.");
  }, []);

  // Execute a parsed command intent
  const executeCommand = useCallback(
    async (intent: string, target: string | null) => {
      // Safe mode — announce but don't execute
      if (useStore.getState().safeMode) {
        const label = target ? `${intent} → ${target}` : intent;
        sydnySay(`[SAFE] Would execute: ${label}`);
        return;
      }

      try {
        switch (intent) {
          // --- Apps ---
          case "open-app": {
            if (!target) { sydnySay("No app specified."); break; }
            await api.openApp(target);
            sydnySay(`Opening ${target}.`);
            break;
          }
          case "close-app": {
            if (!target) { sydnySay("No app specified."); break; }
            await api.closeApp(target);
            sydnySay(`Closing ${target}.`);
            break;
          }

          // --- Volume ---
          case "set-volume": {
            if (!target) { sydnySay("No volume level specified."); break; }
            await api.setVolume(parseInt(target));
            sydnySay(`Volume set to ${target}.`);
            break;
          }
          case "mute": {
            await api.mute();
            sydnySay("Muted.");
            break;
          }
          case "unmute": {
            await api.unmute();
            sydnySay("Unmuted.");
            break;
          }

          // --- Power ---
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

          // --- Files ---
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
              searchResult.results.slice(0, 5).forEach((path: string) => {
                addMessage(path, "system");
              });
            } else {
              sydnySay(`No files found matching "${target}".`);
            }
            break;
          }
          case "delete-file": {
            if (!target) { sydnySay("No file specified."); break; }
            await api.deleteFile(target);
            sydnySay(`Deleted: ${target}`);
            break;
          }

          // --- Tasks ---
          case "add-task": {
            if (!target) { sydnySay("No task description given."); break; }
            const [description, priority] = target.split("|");
            await useStore.getState().addTask(description, priority || "normal");
            sydnySay(`Task added: ${description}`);
            break;
          }
          case "list-tasks":
          case "list-all-tasks": {
            await loadTasks();
            const currentTasks = useStore.getState().tasks;
            if (currentTasks.length === 0) {
              sydnySay("No tasks.");
            } else {
              sydnySay(`You have ${currentTasks.length} task(s).`);
              currentTasks.forEach((t) => {
                const check = t.completed ? "[done]" : "[    ]";
                addMessage(`${check} #${t.id} ${t.description}`, "system");
              });
            }
            break;
          }
          case "complete-task": {
            if (!target) { sydnySay("No task ID given."); break; }
            await useStore.getState().completeTask(parseInt(target));
            sydnySay(`Task ${target} completed.`);
            break;
          }
          case "delete-task": {
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

          // --- Exit ---
          case "exit": {
            sydnySay("Goodbye.");
            break;
          }

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

  // React to pending commands from voice or text
  useEffect(() => {
    if (!pendingCommand) return;

    const { intent, target, needs_confirm } = pendingCommand;
    setPendingCommand(null);

    if (needs_confirm) {
      showConfirm(`Execute "${intent}"${target ? ` on ${target}` : ""}?`, () => {
        executeCommand(intent, target);
      });
    } else {
      executeCommand(intent, target);
    }
  }, [pendingCommand, setPendingCommand, showConfirm, executeCommand]);

  return (
    <div className="min-h-screen bg-black flex flex-col items-center justify-between py-8 px-6">
      <button
        onClick={toggleSafeMode}
        className={`absolute top-4 right-4 px-3 py-1 rounded font-mono text-xs tracking-widest border ${
          safeMode
            ? "border-yellow-500 text-yellow-500"
            : "border-green-500 text-green-500"
        }`}
      >
        {safeMode ? "SAFE MODE" : "LIVE MODE"}
      </button>

      <div className="flex-1 flex flex-col items-center justify-center gap-4">
        <HalEye status={status} onClick={toggleRecording} />
        <StatusLabel status={status} />
      </div>

      <div className="w-full flex flex-col items-center gap-4">
        <Terminal messages={messages} />
        <TaskList tasks={tasks} />
      </div>

      {confirmMessage && confirmAction && (
        <ConfirmDialog
          message={confirmMessage}
          onConfirm={() => {
            confirmAction();
            hideConfirm();
          }}
          onCancel={hideConfirm}
        />
      )}
    </div>
  );
}

export default App;

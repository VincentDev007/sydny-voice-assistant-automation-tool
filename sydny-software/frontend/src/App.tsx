import { useEffect } from "react";
import "./App.css";
import HalEye from "./components/HalEye";
import Terminal from "./components/Terminal";
import StatusLabel from "./components/StatusLabel";
import TaskList from "./components/TaskList";
import ConfirmDialog from "./components/ConfirmDialog";
import useStore from "./hooks/useStore";

function App() {
  const status = useStore((s) => s.status);
  const messages = useStore((s) => s.messages);
  const tasks = useStore((s) => s.tasks);
  const confirmMessage = useStore((s) => s.confirmMessage);
  const confirmAction = useStore((s) => s.confirmAction);
  const hideConfirm = useStore((s) => s.hideConfirm);
  const loadTasks = useStore((s) => s.loadTasks);
  const addMessage = useStore((s) => s.addMessage);

  useEffect(() => {
    loadTasks();
    addMessage("SYDNY online. Awaiting commands.", "sydny");
  }, []);

  return (
    <div className="min-h-screen bg-black flex flex-col items-center justify-between py-8 px-6">
      <div className="flex-1 flex flex-col items-center justify-center gap-4">
        <HalEye status={status} />
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

import "./App.css";

import Orb from "./components/Orb";
import ConfirmDialog from "./components/ConfirmDialog";

import useStore from "./hooks/useStore";
import useVoice from "./hooks/useVoice";
import * as api from "./services/api";

function App() {
  const orbState = useStore((s) => s.orbState);
  const confirmPayload = useStore((s) => s.confirmPayload);
  const hideConfirm = useStore((s) => s.hideConfirm);
  const setOrbState = useStore((s) => s.setOrbState);

  const { toggleRecording } = useVoice();

  const handleConfirm = async () => {
    if (!confirmPayload) return;
    hideConfirm();
    setOrbState("thinking");
    await api.confirmCommand(confirmPayload.intent, confirmPayload.target);
    setOrbState("idle");
  };

  const handleCancel = () => {
    hideConfirm();
    setOrbState("idle");
  };

  return (
    <div className="min-h-screen bg-black flex flex-col items-center justify-center gap-6">

      <p className="text-orange-700 text-xs font-mono tracking-[6px]">SYDNY</p>

      <div onClick={toggleRecording} className="cursor-pointer">
        <Orb state={orbState} />
      </div>

      {confirmPayload && (
        <ConfirmDialog
          message={confirmPayload.response}
          onConfirm={handleConfirm}
          onCancel={handleCancel}
        />
      )}
    </div>
  );
}

export default App;

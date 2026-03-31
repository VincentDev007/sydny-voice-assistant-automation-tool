import { OrbState } from "../hooks/useStore";

interface StatusLabelProps {
  state: OrbState;
}

function StatusLabel({ state }: StatusLabelProps) {
  const labels: Record<OrbState, string> = {
    idle:     "",
    wake:     "Hey...",
    user:     "Listening...",
    thinking: "Thinking...",
    speak:    "Speaking...",
    confirm:  "Are you sure?",
  };

  return (
    <div className="text-center mt-4" style={{ letterSpacing: "4px" }}>
      <span className="text-orange-900 text-sm font-mono">
        {labels[state]}
      </span>
    </div>
  );
}

export default StatusLabel;

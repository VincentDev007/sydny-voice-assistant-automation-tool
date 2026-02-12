interface StatusLabelProps {
  status: "idle" | "listening" | "speaking";
}

function StatusLabel({ status }: StatusLabelProps) {
  const labels = {
    idle: "SYDNY",
    listening: "LISTENING",
    speaking: "SPEAKING",
  };

  return (
    <div className="text-center" style={{ letterSpacing: "10px" }}>
      <span className="text-gray-500 font-bold text-2xl font-mono">
        {labels[status]}
      </span>
    </div>
  );
}

export default StatusLabel;

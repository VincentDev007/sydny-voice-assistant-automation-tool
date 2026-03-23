// ============================================================
// StatusLabel.tsx — Voice State Indicator Text
// ============================================================
// A simple text label displayed below the HAL eye.
// Shows the current state of the voice pipeline in large monospace text.
//
// STATES AND LABELS:
//   idle      → "SYDNY"     — waiting, ready for input
//   listening → "LISTENING" — microphone is active, recording audio
//   speaking  → "SPEAKING"  — audio is being processed or TTS is playing
//
// DESIGN:
//   Wide letter-spacing (10px) gives it the "sci-fi terminal" aesthetic.
//   Gray color keeps it subtle — the HAL eye is the visual focus.
//   Font: monospace (font-mono) — consistent with the terminal aesthetic.
//
// PROPS:
//   status → the current voice state (from useStore)
// ============================================================


interface StatusLabelProps {
  status: "idle" | "listening" | "speaking"; // Determines which label to show
}


function StatusLabel({ status }: StatusLabelProps) {
  // Map each status to its display text
  // Using an object lookup is cleaner than if/else or a switch statement
  const labels = {
    idle: "SYDNY",         // Default state — Sydny is ready
    listening: "LISTENING", // Mic is open, recording in progress
    speaking: "SPEAKING",  // Processing audio or TTS is active
  };

  return (
    // Wide letter-spacing gives the sci-fi terminal look
    <div className="text-center" style={{ letterSpacing: "10px" }}>
      <span className="text-gray-500 font-bold text-2xl font-mono">
        {labels[status]} {/* Look up the label for the current status */}
      </span>
    </div>
  );
}

export default StatusLabel;

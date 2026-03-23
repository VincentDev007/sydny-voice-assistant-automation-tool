// ============================================================
// HalEye.tsx — The Visual Centerpiece
// ============================================================
// The animated HAL-9000-style glowing red eye that is SYDNY's face.
// It serves as the primary interaction element — clicking it starts/stops recording.
//
// WHY HAL-9000?
//   HAL 9000 is the iconic AI from "2001: A Space Odyssey" — a red glowing eye.
//   It fits SYDNY's voice assistant aesthetic: minimal, dark, slightly ominous.
//
// THE THREE LAYERS (innermost to outermost):
//   hal-eye-core  → the bright red center dot
//   hal-eye-glow  → the soft red glow radiating outward
//   hal-eye-ring  → the outer ring/border
//
// CSS CLASSES drive the visual states (see HalEye.css):
//   hal-eye-idle      → steady dim glow (waiting for input)
//   hal-eye-listening → pulsing/animated glow (recording audio)
//   hal-eye-speaking  → bright, intensified glow (processing/speaking)
//
// PROPS:
//   status  → current voice pipeline state (controls which CSS class is applied)
//   onClick → function to call when the eye is clicked (toggleRecording from useVoice)
//
// CURSOR BEHAVIOR:
//   "pointer" when idle or listening → clickable (can toggle recording)
//   "default" when speaking → not clickable (processing in progress, ignore clicks)
// ============================================================

import "./HalEye.css";


// Props interface — TypeScript requires explicit prop types for components
interface HalEyeProps {
  status: "idle" | "listening" | "speaking"; // Current voice state
  onClick?: () => void;                       // Optional click handler (? = not required)
}


function HalEye({ status, onClick }: HalEyeProps) {
  return (
    // Outer container — uses dynamic CSS class based on status
    // hal-eye-${status} applies the correct animation: hal-eye-idle, hal-eye-listening, hal-eye-speaking
    <div
      className={`hal-eye hal-eye-${status} flex items-center justify-center`}
      onClick={onClick}
      // Show pointer cursor when clickable, default cursor when processing
      style={{ cursor: status === "speaking" ? "default" : "pointer" }}
    >
      {/* Three concentric layers that combine to create the eye effect */}
      <div className="hal-eye-ring" />   {/* Outermost: the ring border */}
      <div className="hal-eye-glow" />   {/* Middle: soft radial glow */}
      <div className="hal-eye-core" />   {/* Innermost: the bright center */}
    </div>
  );
}

export default HalEye;

import "./HalEye.css";

interface HalEyeProps {
  status: "idle" | "listening" | "speaking";
  onClick?: () => void;
}

function HalEye({ status, onClick }: HalEyeProps) {
  return (
    <div
      className={`hal-eye hal-eye-${status} flex items-center justify-center`}
      onClick={onClick}
      style={{ cursor: status === "speaking" ? "default" : "pointer" }}
    >
      <div className="hal-eye-ring" />
      <div className="hal-eye-glow" />
      <div className="hal-eye-core" />
    </div>
  );
}

export default HalEye;

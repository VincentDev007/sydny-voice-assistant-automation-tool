import "./HalEye.css";

interface HalEyeProps {
  status: "idle" | "listening" | "speaking";
}

function HalEye({ status }: HalEyeProps) {
  return (
    <div className={`hal-eye hal-eye-${status} flex items-center justify-center`}>
      <div className="hal-eye-ring" />
      <div className="hal-eye-glow" />
      <div className="hal-eye-core" />
    </div>
  );
}

export default HalEye;

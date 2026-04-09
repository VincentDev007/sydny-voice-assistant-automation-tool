import React from "react";
import { OrbState } from "../hooks/useStore";

interface OrbProps {
  state: OrbState;
}

const orbAnim: Record<OrbState, string> = {
  idle: "breatheDim 5.5s ease-in-out infinite",
  wake: "wakeFlash 1s ease-out forwards",
  user: "breatheSlow 4s ease-in-out infinite",
  thinking: "thinkPulse 2.4s ease-in-out infinite",
  speak: "breatheFull 2.5s ease-in-out infinite",
  confirm: "breatheCalm 4.5s ease-in-out infinite",
};

const ring1Anim: Record<OrbState, string> = {
  idle: "softPulse 5.5s ease-in-out infinite",
  wake: "softPulse 1s ease-out forwards",
  user: "softPulse 3.5s ease-in-out infinite",
  thinking: "thinkRing 2.4s ease-in-out infinite",
  speak: "softPulse 2.5s ease-in-out infinite",
  confirm: "softPulse 4.5s ease-in-out infinite",
};

const ring2Anim: Record<OrbState, string> = {
  idle: "softPulse2 5.5s ease-in-out infinite .8s",
  wake: "softPulse2 3.5s ease-in-out infinite .8s",
  user: "softPulse2 3.5s ease-in-out infinite .8s",
  thinking: "thinkRing 2.4s ease-in-out infinite .5s",
  speak: "softPulse2 2.5s ease-in-out infinite .5s",
  confirm: "softPulse2 4.5s ease-in-out infinite .8s",
};

function Waveform({ color, maxH, count = 18 }: { color: string; maxH: number; count?: number }) {
  return (
    <div style={{ display: "flex", alignItems: "center", justifyContent: "center", gap: "2px", height: "26px", width: "100%" }}>
      {Array.from({ length: count }).map((_, i) => {
        const dist = Math.abs(i - count / 2) / (count / 2);
        const peak = Math.max(0.15, 1 - dist * 0.6);
        const height = Math.round(3 + peak * maxH);
        const duration = (0.45 + Math.random() * 0.4).toFixed(2) + "s";
        const delay = (i * 0.032).toFixed(3) + "s";
        return (
          <div
            key={i}
            style={{
              width: "2px",
              height: height + "px",
              borderRadius: "1px",
              background: color,
              transformOrigin: "center",
              animation: `barWave ${duration} ease-in-out infinite ${delay}`,
            }}
          />
        );
      })}
    </div>
  );
}

export default function Orb({ state }: OrbProps) {
  const wrapSize = 90;
  const orbSize = 58;

  const ringStyle = (size: number, anim: string, color: string): React.CSSProperties => ({
    position: "absolute",
    width: size,
    height: size,
    borderRadius: "50%",
    border: `1px solid ${color}`,
    animation: anim,
  });

  const shockStyle = (border: string): React.CSSProperties => ({
    position: "absolute",
    width: orbSize,
    height: orbSize,
    borderRadius: "50%",
    border,
    animation: "shockwave .9s ease-out forwards",
  });

  const rippleStyle = (anim: string): React.CSSProperties => ({
    position: "absolute",
    width: orbSize,
    height: orbSize,
    borderRadius: "50%",
    border: "1px solid rgba(210,95,30,.55)",
    animation: anim,
    zIndex: 0,
  });

  return (
    <div style={{ position: "relative", display: "flex", alignItems: "center", justifyContent: "center", width: wrapSize, height: wrapSize, flexShrink: 0 }}>

      <div style={ringStyle(96, ring2Anim[state], "rgba(210,95,30,.12)")} />
      <div style={ringStyle(78, ring1Anim[state], "rgba(210,95,30,.25)")} />

      {state === "wake" && (
        <>
          <div style={{ ...shockStyle("2px solid rgba(230,120,40,.72)"), zIndex: 0 }} />
          <div style={{ position: "absolute", width: orbSize, height: orbSize, borderRadius: "50%", border: "1px solid rgba(210,100,35,.45)", animation: "shockwave2 .9s ease-out .15s forwards", zIndex: 0 }} />
        </>
      )}

      {state === "user" && (
        <>
          <div style={rippleStyle("ringExpand 1.8s ease-out infinite")} />
          <div style={rippleStyle("ringExpand2 1.8s ease-out infinite .65s")} />
        </>
      )}

      <div style={{
        width: orbSize,
        height: orbSize,
        borderRadius: "50%",
        background: "radial-gradient(circle at 38% 36%, #f09060 0%, #c84010 48%, #7a1a00 100%)",
        position: "relative",
        zIndex: 1,
        animation: orbAnim[state],
      }} />

      {state === "user" && (
        <div style={{ position: "absolute", bottom: -32, width: "100%" }}>
          <Waveform color="rgba(175,88,28,.4)" maxH={12} />
        </div>
      )}
      {state === "speak" && (
        <div style={{ position: "absolute", bottom: -32, width: "100%" }}>
          <Waveform color="#c86030" maxH={26} />
        </div>
      )}
    </div>
  );
}

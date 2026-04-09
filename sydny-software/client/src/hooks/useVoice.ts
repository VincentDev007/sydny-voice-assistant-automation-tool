import { useRef, useCallback } from "react";
import useStore from "./useStore";
import * as api from "../services/api";

async function blobToWav(blob: Blob): Promise<Blob> {
  const arrayBuffer = await blob.arrayBuffer();
  const audioContext = new AudioContext({ sampleRate: 16000 });
  const audioBuffer = await audioContext.decodeAudioData(arrayBuffer);
  const pcmData = audioBuffer.getChannelData(0);
  const numSamples = pcmData.length;
  const wavBuffer = new ArrayBuffer(44 + numSamples * 2);
  const view = new DataView(wavBuffer);

  const writeString = (offset: number, str: string) => {
    for (let i = 0; i < str.length; i++) view.setUint8(offset + i, str.charCodeAt(i));
  };

  writeString(0, "RIFF");
  view.setUint32(4, 36 + numSamples * 2, true);
  writeString(8, "WAVE");
  writeString(12, "fmt ");
  view.setUint32(16, 16, true);
  view.setUint16(20, 1, true);
  view.setUint16(22, 1, true);
  view.setUint32(24, 16000, true);
  view.setUint32(28, 32000, true);
  view.setUint16(32, 2, true);
  view.setUint16(34, 16, true);
  writeString(36, "data");
  view.setUint32(40, numSamples * 2, true);

  for (let i = 0; i < numSamples; i++) {
    const sample = Math.max(-1, Math.min(1, pcmData[i]));
    view.setInt16(44 + i * 2, sample * 0x7fff, true);
  }

  await audioContext.close();
  return new Blob([wavBuffer], { type: "audio/wav" });
}

export default function useVoice() {
  const setOrbState = useStore((s) => s.setOrbState);
  const showConfirm = useStore((s) => s.showConfirm);
  const orbState = useStore((s) => s.orbState);

  const mediaRecorderRef = useRef<MediaRecorder | null>(null);
  const chunksRef = useRef<Blob[]>([]);


  const startRecording = useCallback(async () => {
    try {
      const stream = await navigator.mediaDevices.getUserMedia({ audio: true });

      const mimeType = MediaRecorder.isTypeSupported("audio/webm;codecs=opus")
        ? "audio/webm;codecs=opus"
        : MediaRecorder.isTypeSupported("audio/webm")
          ? "audio/webm"
          : "";

      const mediaRecorder = mimeType
        ? new MediaRecorder(stream, { mimeType })
        : new MediaRecorder(stream);

      mediaRecorderRef.current = mediaRecorder;
      chunksRef.current = [];

      mediaRecorder.ondataavailable = (e) => {
        if (e.data.size > 0) chunksRef.current.push(e.data);
      };

      mediaRecorder.onstop = async () => {
        stream.getTracks().forEach((track) => track.stop());

        const blob = new Blob(chunksRef.current, { type: mediaRecorder.mimeType });
        console.log("[useVoice] recorded blob:", blob.size, "bytes, type:", blob.type);

        setOrbState("thinking");

        try {
          const wavBlob = await blobToWav(blob);
          const result = await api.sendVoiceCommand(wavBlob);

          if (result.needs_confirm) {
            showConfirm({
              intent: result.intent,
              target: result.target ?? null,
              response: result.response,
            });
            return;
          }

          if (result.end_session) {
            useStore.getState().setSessionActive(false);
          }

        } catch (err) {
          console.error("Voice processing error:", err);
        }

        setOrbState("idle");
      };

      mediaRecorder.start();
      setOrbState("user");

    } catch (err) {
      console.error("Mic error:", err);
      setOrbState("idle");
    }
  }, [setOrbState, showConfirm]);

  const stopRecording = useCallback(() => {
    if (mediaRecorderRef.current?.state === "recording") {
      mediaRecorderRef.current.stop();
    }
  }, []);

  const toggleRecording = useCallback(() => {
    if (orbState === "user") {
      stopRecording();
    } else if (orbState === "idle") {
      startRecording();
    }
  }, [orbState, startRecording, stopRecording]);

  return { startRecording, stopRecording, toggleRecording };
}

import { useRef, useCallback } from "react";
import useStore from "./useStore";
import * as api from "../services/api";

// Convert a blob to proper WAV format using Web Audio API
async function blobToWav(blob: Blob): Promise<File> {
  const arrayBuffer = await blob.arrayBuffer();
  const audioContext = new AudioContext({ sampleRate: 16000 });
  const audioBuffer = await audioContext.decodeAudioData(arrayBuffer);

  // Get mono PCM data
  const pcmData = audioBuffer.getChannelData(0);
  const numSamples = pcmData.length;

  // Build WAV file
  const wavBuffer = new ArrayBuffer(44 + numSamples * 2);
  const view = new DataView(wavBuffer);

  // WAV header
  const writeString = (offset: number, str: string) => {
    for (let i = 0; i < str.length; i++) {
      view.setUint8(offset + i, str.charCodeAt(i));
    }
  };

  writeString(0, "RIFF");
  view.setUint32(4, 36 + numSamples * 2, true);
  writeString(8, "WAVE");
  writeString(12, "fmt ");
  view.setUint32(16, 16, true);           // chunk size
  view.setUint16(20, 1, true);            // PCM format
  view.setUint16(22, 1, true);            // mono
  view.setUint32(24, 16000, true);        // sample rate
  view.setUint32(28, 16000 * 2, true);    // byte rate
  view.setUint16(32, 2, true);            // block align
  view.setUint16(34, 16, true);           // bits per sample
  writeString(36, "data");
  view.setUint32(40, numSamples * 2, true);

  // Write PCM samples
  for (let i = 0; i < numSamples; i++) {
    const sample = Math.max(-1, Math.min(1, pcmData[i]));
    view.setInt16(44 + i * 2, sample * 0x7fff, true);
  }

  await audioContext.close();
  return new File([wavBuffer], "recording.wav", { type: "audio/wav" });
}

export default function useVoice() {
  const setStatus = useStore((s) => s.setStatus);
  const addMessage = useStore((s) => s.addMessage);
  const status = useStore((s) => s.status);

  const mediaRecorderRef = useRef<MediaRecorder | null>(null);
  const chunksRef = useRef<Blob[]>([]);

  const startRecording = useCallback(async () => {
    try {
      const stream = await navigator.mediaDevices.getUserMedia({ audio: true });

      // Pick a supported MIME type
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
        if (e.data.size > 0) {
          chunksRef.current.push(e.data);
        }
      };

      mediaRecorder.onstop = async () => {
        // Stop all tracks to release the mic
        stream.getTracks().forEach((track) => track.stop());

        const blob = new Blob(chunksRef.current, { type: mediaRecorder.mimeType });

        setStatus("speaking");
        addMessage("Processing...", "system");

        try {
          // Convert to WAV so Whisper/ffmpeg can always read it
          const wavFile = await blobToWav(blob);

          // Step 1: Transcribe audio
          const transcription = await api.transcribeAudio(wavFile);
          const transcript = transcription.transcript?.trim();

          if (!transcript) {
            addMessage("Could not understand audio.", "sydny");
            setStatus("idle");
            return;
          }

          addMessage(transcript, "user");

          // Step 2: Parse command
          const result = await api.sendCommand(transcript);

          if (!result.intent) {
            addMessage("I heard you, but I don't know how to do that.", "sydny");
            setStatus("idle");
            return;
          }

          addMessage(
            `Command: ${result.intent}${result.target ? ` → ${result.target}` : ""}`,
            "system"
          );

          // Store the parsed result for App.tsx to execute
          useStore.getState().setPendingCommand(result);
        } catch (err) {
          addMessage("Error processing voice command.", "sydny");
          console.error("Voice processing error:", err);
        }

        setStatus("idle");
      };

      mediaRecorder.start();
      setStatus("listening");
    } catch (err) {
      addMessage("Microphone access denied.", "sydny");
      console.error("Mic error:", err);
    }
  }, [setStatus, addMessage]);

  const stopRecording = useCallback(() => {
    if (mediaRecorderRef.current && mediaRecorderRef.current.state === "recording") {
      mediaRecorderRef.current.stop();
    }
  }, []);

  const toggleRecording = useCallback(() => {
    if (status === "listening") {
      stopRecording();
    } else if (status === "idle") {
      startRecording();
    }
    // If "speaking" (processing), ignore toggles
  }, [status, startRecording, stopRecording]);

  return { startRecording, stopRecording, toggleRecording };
}

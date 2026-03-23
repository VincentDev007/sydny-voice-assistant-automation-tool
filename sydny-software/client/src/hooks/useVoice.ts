// ============================================================
// useVoice.ts — Microphone Recording Hook
// ============================================================
// A custom React hook that manages the entire voice recording lifecycle:
//   1. Requests mic access from the browser
//   2. Records audio using MediaRecorder API
//   3. Converts the recorded audio (WebM) to WAV format (Whisper requires decodable audio)
//   4. Sends the WAV to the backend for transcription
//   5. Sends the transcript to the backend for command parsing
//   6. Stores the parsed result in the store for App.tsx to execute
//
// KEY TECHNOLOGY: MediaRecorder API
//   Browser built-in recording API. Records audio as WebM (Opus codec).
//   We store chunks of audio data as they come in, then assemble them on stop.
//
// WHY CONVERT TO WAV?
//   The browser records audio as WebM/Opus format. Whisper uses ffmpeg to decode audio,
//   but the WebM container produced by browsers sometimes has malformed headers that
//   ffmpeg can't parse (exit code 183, "EBML header parsing failed").
//   Solution: decode the audio in the browser using Web Audio API, then re-encode
//   it as a proper 16kHz mono PCM WAV — a format Whisper always handles correctly.
//
// THE blobToWav() FUNCTION:
//   Uses Web Audio API to decode the WebM blob into raw PCM samples,
//   then manually writes a WAV file with a 44-byte header.
//   WAV spec: 16kHz sample rate, 1 channel (mono), 16-bit PCM (s16le)
// ============================================================

import { useRef, useCallback } from "react";
import useStore from "./useStore";
import * as api from "../services/api";


// ============================================================
// blobToWav — Audio Format Converter
// ============================================================
// Converts a browser audio Blob (WebM/Opus) to a proper WAV File.
// This runs ENTIRELY in the browser — no server involved.
//
// STEPS:
//   1. blob.arrayBuffer() → convert Blob to raw bytes (ArrayBuffer)
//   2. AudioContext.decodeAudioData() → decode compressed audio to raw PCM samples
//   3. Build a WAV file manually: 44-byte header + raw PCM s16le samples
//   4. Return as a File object (which can be sent to the backend)
//
// WAV FILE STRUCTURE:
//   Bytes 0-3:   "RIFF"            — file format signature
//   Bytes 4-7:   file size - 8     — total file size minus 8 (the RIFF chunk header)
//   Bytes 8-11:  "WAVE"            — audio format
//   Bytes 12-15: "fmt "            — format sub-chunk marker
//   Bytes 16-19: 16               — size of format data (always 16 for PCM)
//   Bytes 20-21: 1                — audio format type (1 = PCM, uncompressed)
//   Bytes 22-23: 1                — number of channels (1 = mono)
//   Bytes 24-27: 16000            — sample rate (16,000 Hz = 16kHz)
//   Bytes 28-31: 32000            — byte rate (sampleRate × channels × bitsPerSample/8)
//   Bytes 32-33: 2                — block align (channels × bitsPerSample/8)
//   Bytes 34-35: 16               — bits per sample (16-bit = 2 bytes per sample)
//   Bytes 36-39: "data"           — data sub-chunk marker
//   Bytes 40-43: data size        — size of raw audio data
//   Bytes 44+:   PCM samples      — raw audio as signed 16-bit integers (little-endian)
async function blobToWav(blob: Blob): Promise<File> {
  // Step 1: Convert Blob to ArrayBuffer (raw bytes)
  const arrayBuffer = await blob.arrayBuffer();

  // Step 2: Decode the audio using Web Audio API
  // sampleRate: 16000 → Whisper is optimized for 16kHz input
  const audioContext = new AudioContext({ sampleRate: 16000 });
  const audioBuffer = await audioContext.decodeAudioData(arrayBuffer);

  // Step 3: Get mono PCM channel data (float32 values from -1.0 to 1.0)
  // getChannelData(0) = channel 0 = left channel (only channel in mono audio)
  const pcmData = audioBuffer.getChannelData(0);
  const numSamples = pcmData.length;

  // Step 4: Allocate buffer for WAV header (44 bytes) + PCM data (2 bytes per sample)
  const wavBuffer = new ArrayBuffer(44 + numSamples * 2);
  const view = new DataView(wavBuffer); // DataView lets us write specific byte types

  // Helper: write an ASCII string to the buffer at a given offset
  const writeString = (offset: number, str: string) => {
    for (let i = 0; i < str.length; i++) {
      view.setUint8(offset + i, str.charCodeAt(i));
    }
  };

  // Step 5: Write the 44-byte WAV header
  writeString(0, "RIFF");                            // Bytes 0-3: RIFF signature
  view.setUint32(4, 36 + numSamples * 2, true);      // Bytes 4-7: total file size - 8 (little-endian)
  writeString(8, "WAVE");                            // Bytes 8-11: WAVE format
  writeString(12, "fmt ");                           // Bytes 12-15: format sub-chunk
  view.setUint32(16, 16, true);                      // Bytes 16-19: PCM format data size = 16
  view.setUint16(20, 1, true);                       // Bytes 20-21: audio format = 1 (PCM)
  view.setUint16(22, 1, true);                       // Bytes 22-23: channels = 1 (mono)
  view.setUint32(24, 16000, true);                   // Bytes 24-27: sample rate = 16000 Hz
  view.setUint32(28, 16000 * 2, true);               // Bytes 28-31: byte rate = 32000 bytes/sec
  view.setUint16(32, 2, true);                       // Bytes 32-33: block align = 2 bytes/sample
  view.setUint16(34, 16, true);                      // Bytes 34-35: bits per sample = 16
  writeString(36, "data");                           // Bytes 36-39: data sub-chunk
  view.setUint32(40, numSamples * 2, true);          // Bytes 40-43: PCM data size in bytes

  // Step 6: Write PCM samples (convert float32 → signed int16)
  // Float32 PCM: values range from -1.0 to 1.0
  // Int16 PCM:   values range from -32768 to 32767 (0x7fff = 32767)
  for (let i = 0; i < numSamples; i++) {
    const sample = Math.max(-1, Math.min(1, pcmData[i])); // Clamp to [-1, 1]
    view.setInt16(44 + i * 2, sample * 0x7fff, true);    // Convert and write (little-endian)
  }

  // Step 7: Free the AudioContext resources
  await audioContext.close();

  // Return as a File object — same interface as a file input <input type="file">
  return new File([wavBuffer], "recording.wav", { type: "audio/wav" });
}


// ============================================================
// useVoice — The Recording Hook
// ============================================================
export default function useVoice() {
  // Pull what we need from the global store
  const setStatus = useStore((s) => s.setStatus);   // Updates "idle" | "listening" | "speaking"
  const addMessage = useStore((s) => s.addMessage); // Adds messages to the terminal
  const status = useStore((s) => s.status);         // Current status (needed for toggle logic)

  // useRef stores values that persist across renders WITHOUT causing re-renders
  // (unlike useState, which would cause a re-render every time it changes)
  const mediaRecorderRef = useRef<MediaRecorder | null>(null); // The active MediaRecorder instance
  const chunksRef = useRef<Blob[]>([]);                        // Accumulated audio chunks


  // ============================================================
  // startRecording — Begin capturing mic audio
  // ============================================================
  // useCallback memoizes the function so it only changes when dependencies change.
  // Without useCallback, a new function is created every render, which can cause
  // unnecessary re-renders in child components that receive it as a prop.
  const startRecording = useCallback(async () => {
    try {
      // Request mic access — browser shows permission prompt if not yet granted
      // getUserMedia() returns a MediaStream (live audio from the mic)
      const stream = await navigator.mediaDevices.getUserMedia({ audio: true });

      // Choose the best supported audio format
      // audio/webm;codecs=opus → best quality, widely supported
      // audio/webm → fallback if opus codec isn't available
      // "" → let the browser pick (last resort)
      const mimeType = MediaRecorder.isTypeSupported("audio/webm;codecs=opus")
        ? "audio/webm;codecs=opus"
        : MediaRecorder.isTypeSupported("audio/webm")
          ? "audio/webm"
          : "";

      // Create the MediaRecorder — if a mimeType was found, use it; otherwise use browser defaults
      const mediaRecorder = mimeType
        ? new MediaRecorder(stream, { mimeType })
        : new MediaRecorder(stream);

      // Store the recorder in ref so stopRecording() can access it
      mediaRecorderRef.current = mediaRecorder;
      chunksRef.current = []; // Clear any previous recording chunks

      // ondataavailable fires periodically while recording (or once when stopped)
      // Each event gives us a Blob chunk of audio data
      mediaRecorder.ondataavailable = (e) => {
        if (e.data.size > 0) {
          chunksRef.current.push(e.data); // Collect all audio chunks
        }
      };

      // onstop fires when mediaRecorder.stop() is called (user clicks eye again)
      // This is where all the processing happens
      mediaRecorder.onstop = async () => {
        // Release the microphone — stop all audio tracks so the mic indicator goes away
        stream.getTracks().forEach((track) => track.stop());

        // Combine all chunks into one Blob
        const blob = new Blob(chunksRef.current, { type: mediaRecorder.mimeType });

        setStatus("speaking"); // Visual feedback — show "SPEAKING" while processing
        addMessage("Processing...", "system");

        try {
          // ── STEP 1: Convert audio format ──
          // Convert WebM → WAV so Whisper can reliably decode it
          const wavFile = await blobToWav(blob);

          // ── STEP 2: Transcribe audio → text ──
          // POST the WAV file to /api/voice/transcribe
          // Backend runs Whisper and returns {"transcript": "open safari"}
          const transcription = await api.transcribeAudio(wavFile);
          const transcript = transcription.transcript?.trim();

          // If Whisper couldn't understand the audio, bail out
          if (!transcript) {
            addMessage("Could not understand audio.", "sydny");
            setStatus("idle");
            return;
          }

          // Show the user's transcript in the terminal (green "user" message)
          // The transcript is shown but NOT spoken — only Sydny's responses are spoken
          addMessage(transcript, "user");

          // ── STEP 3: Parse text → intent ──
          // POST the transcript to /api/voice/command
          // Backend runs command_parser.parse_command() and returns {intent, target, needs_confirm}
          const result = await api.sendCommand(transcript);

          // If the parser couldn't find a matching intent, bail out
          if (!result.intent) {
            addMessage("I heard you, but I don't know how to do that.", "sydny");
            setStatus("idle");
            return;
          }

          // Show the parsed command as a system message (gray)
          addMessage(
            `Command: ${result.intent}${result.target ? ` → ${result.target}` : ""}`,
            "system"
          );

          // ── STEP 4: Store result for App.tsx to execute ──
          // App.tsx has a useEffect watching pendingCommand.
          // When we set it here, that useEffect fires and calls executeCommand().
          // This separation keeps voice recording and command execution in different places.
          useStore.getState().setPendingCommand(result);

        } catch (err) {
          addMessage("Error processing voice command.", "sydny");
          console.error("Voice processing error:", err);
        }

        setStatus("idle"); // Return to idle when done
      };

      // Actually start recording
      mediaRecorder.start();
      setStatus("listening"); // Visual feedback — show "LISTENING"

    } catch (err) {
      // getUserMedia() throws if mic access is denied or not available
      addMessage("Microphone access denied.", "sydny");
      console.error("Mic error:", err);
    }
  }, [setStatus, addMessage]);


  // ============================================================
  // stopRecording — Stop the active recording
  // ============================================================
  // Calling .stop() on the MediaRecorder triggers the onstop callback above.
  const stopRecording = useCallback(() => {
    if (mediaRecorderRef.current && mediaRecorderRef.current.state === "recording") {
      mediaRecorderRef.current.stop(); // Triggers onstop handler
    }
  }, []);


  // ============================================================
  // toggleRecording — What happens when the user clicks the HAL eye
  // ============================================================
  // Implements a simple state machine:
  //   idle     → start recording
  //   listening → stop recording (triggers processing)
  //   speaking → ignore (can't start recording while processing)
  const toggleRecording = useCallback(() => {
    if (status === "listening") {
      stopRecording();        // Stop → triggers onstop → processing begins
    } else if (status === "idle") {
      startRecording();       // Start → mic opens → recording begins
    }
    // "speaking" state: do nothing (user must wait for processing to finish)
  }, [status, startRecording, stopRecording]);


  // Expose all three functions — App.tsx only needs toggleRecording
  return { startRecording, stopRecording, toggleRecording };
}

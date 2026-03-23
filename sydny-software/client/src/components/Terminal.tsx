// ============================================================
// Terminal.tsx — Scrolling Message Log
// ============================================================
// Displays the conversation history between the user and SYDNY.
// Styled like a terminal window — dark background, monospace font.
//
// MESSAGE TYPES AND COLORS (defined in Terminal.css):
//   "user"   → green text, prefixed with "> You: "   (what the user said)
//   "sydny"  → red text, prefixed with "> SYDNY: "   (Sydny's responses)
//   "system" → gray text, no prefix                  (status info, file paths, task lists)
//
// AUTO-SCROLL:
//   useRef + useEffect combination keeps the terminal scrolled to the bottom.
//   Every time a new message is added (messages array changes), useEffect fires
//   and calls scrollIntoView() on a dummy div at the end of the message list.
//   { behavior: "smooth" } animates the scroll instead of jumping instantly.
//
// PROPS:
//   messages → the array of Message objects from useStore
//              (read-only here — Terminal only displays, never modifies)
// ============================================================

import { useEffect, useRef } from "react";
import "./Terminal.css";


// Matches the Message interface in useStore.ts
interface Message {
  text: string;
  type: "user" | "sydny" | "system"; // Controls styling/color
}

interface TerminalProps {
  messages: Message[]; // The full message history to display
}


function Terminal({ messages }: TerminalProps) {
  // useRef creates a reference to a DOM element without causing re-renders
  // We attach this to an empty div at the bottom of the message list
  const bottomRef = useRef<HTMLDivElement>(null);

  // Auto-scroll to bottom whenever messages array changes (new message added)
  // [messages] as dependency → this effect runs every time messages changes
  useEffect(() => {
    // ?. is optional chaining — only calls scrollIntoView if bottomRef.current is not null
    bottomRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [messages]);

  return (
    <div className="terminal bg-black">
      {/* Render each message as a div with type-specific CSS class */}
      {messages.map((msg, i) => (
        // key={i} is the React list key — uses index since messages only append, never reorder
        <div key={i} className={`terminal-message terminal-message-${msg.type}`}>
          {/* Add prefix text based on who sent the message */}
          {msg.type === "user" && "> You: "}    {/* User's transcript (green) */}
          {msg.type === "sydny" && "> SYDNY: "} {/* Sydny's response (red) */}
          {/* "system" messages have no prefix — shown as plain gray text */}
          {msg.text}
        </div>
      ))}

      {/* Invisible anchor div at the very end — scroll target for auto-scroll */}
      <div ref={bottomRef} />
    </div>
  );
}

export default Terminal;

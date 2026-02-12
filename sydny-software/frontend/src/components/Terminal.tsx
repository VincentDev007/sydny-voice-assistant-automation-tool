import { useEffect, useRef } from "react";
import "./Terminal.css";

interface Message {
  text: string;
  type: "user" | "sydny" | "system";
}

interface TerminalProps {
  messages: Message[];
}

function Terminal({ messages }: TerminalProps) {
  const bottomRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    bottomRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [messages]);

  return (
    <div className="terminal bg-black">
      {messages.map((msg, i) => (
        <div key={i} className={`terminal-message terminal-message-${msg.type}`}>
          {msg.type === "user" && "> You: "}
          {msg.type === "sydny" && "> SYDNY: "}
          {msg.text}
        </div>
      ))}
      <div ref={bottomRef} />
    </div>
  );
}

export default Terminal;

import { useState, useRef, useEffect } from "react";
import { Send, Loader2, MessageSquare, Menu } from "lucide-react";
import { Message } from "@/types/workspace";
import { ChatMessage } from "./ChatMessage";
import { motion, AnimatePresence } from "framer-motion";

interface Props {
  messages: Message[];
  onSend: (content: string) => void;
  workspaceName: string;
  hasDocuments: boolean;
  isMobile?: boolean;
  onOpenSidebar?: () => void;
}

export function ChatArea({
  messages,
  onSend,
  workspaceName,
  hasDocuments,
  isMobile,
  onOpenSidebar,
}: Props) {
  const [input, setInput] = useState("");
  const [isTyping, setIsTyping] = useState(false);
  const bottomRef = useRef<HTMLDivElement>(null);
  const lastMsgCount = useRef(messages.length);

  useEffect(() => {
    if (messages.length > lastMsgCount.current) {
      const last = messages[messages.length - 1];
      if (last.role === "user") {
        setIsTyping(true);
      } else {
        setIsTyping(false);
      }
    }
    lastMsgCount.current = messages.length;
    bottomRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [messages]);

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    if (!input.trim()) return;
    onSend(input.trim());
    setInput("");
  };

  return (
    <div className="flex-1 flex flex-col min-w-0 bg-background">
      {/* Header */}
      <div className="h-14 border-b border-border flex items-center px-4 md:px-6 gap-3">
        {isMobile && onOpenSidebar && (
          <button
            onClick={onOpenSidebar}
            className="w-8 h-8 flex items-center justify-center rounded-lg hover:bg-secondary transition-colors"
          >
            <Menu className="w-5 h-5 text-foreground" />
          </button>
        )}
        <h1 className="text-sm font-semibold text-foreground truncate flex-1">
          {workspaceName}
        </h1>
      </div>

      {/* Messages */}
      <div className="flex-1 overflow-y-auto px-4 md:px-6 py-6">
        {messages.length === 0 ? (
          <div className="h-full flex flex-col items-center justify-center text-center">
            <div className="w-12 h-12 rounded-2xl bg-secondary flex items-center justify-center mb-4">
              <MessageSquare className="w-5 h-5 text-muted-foreground" />
            </div>
            <h2 className="text-lg font-semibold text-foreground mb-1">
              Start a conversation
            </h2>
            <p className="text-sm text-muted-foreground max-w-sm">
              {hasDocuments
                ? "Ask any question about your uploaded documents and get instant answers with citations."
                : "Upload some documents first, then ask questions to get insights."}
            </p>
          </div>
        ) : (
          <div className="max-w-3xl mx-auto space-y-1">
            <AnimatePresence initial={false}>
              {messages.map((msg) => (
                <motion.div
                  key={msg.id}
                  initial={{ opacity: 0, y: 12 }}
                  animate={{ opacity: 1, y: 0 }}
                  transition={{ duration: 0.25 }}
                >
                  <ChatMessage message={msg} />
                </motion.div>
              ))}
            </AnimatePresence>
            {isTyping && (
              <motion.div
                initial={{ opacity: 0 }}
                animate={{ opacity: 1 }}
                className="flex items-center gap-2 px-4 py-3"
              >
                <Loader2 className="w-4 h-4 text-muted-foreground animate-spin" />
                <span className="text-sm text-muted-foreground">
                  Analyzing documents…
                </span>
              </motion.div>
            )}
          </div>
        )}
        <div ref={bottomRef} />
      </div>

      {/* Input */}
      <div className="border-t border-border p-3 md:p-4">
        <form onSubmit={handleSubmit} className="max-w-3xl mx-auto">
          <div className="flex items-center gap-2 bg-secondary rounded-xl px-3 md:px-4 py-2 focus-within:ring-2 focus-within:ring-ring/20 transition-shadow">
            <input
              value={input}
              onChange={(e) => setInput(e.target.value)}
              placeholder="Ask something about your documents…"
              className="flex-1 bg-transparent text-sm text-foreground placeholder:text-muted-foreground outline-none py-1.5"
            />
            <button
              type="submit"
              disabled={!input.trim()}
              className="w-8 h-8 rounded-lg bg-accent flex items-center justify-center text-accent-foreground disabled:opacity-30 transition-opacity hover:opacity-90"
            >
              <Send className="w-4 h-4" />
            </button>
          </div>
        </form>
      </div>
    </div>
  );
}

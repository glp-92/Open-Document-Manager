import { useState, useCallback, useRef, useEffect } from "react";
import { useWorkspaces } from "@/hooks/useWorkspaces";
import { useIsMobile } from "@/hooks/use-mobile";
import { Sheet, SheetContent, SheetTitle } from "@/components/sheet";
import { VisuallyHidden } from "@radix-ui/react-visually-hidden";
import {
  Message,
  Chat,
  Document as DocType,
  Workspace,
} from "@/types/workspace";
import { AnimatePresence, motion } from "framer-motion";
import {
  Plus,
  FolderOpen,
  Layers,
  Upload,
  FileText,
  CheckCircle2,
  Loader2,
  MessageSquare,
  ChevronRight,
  ChevronDown,
  PlusCircle,
  Zap,
  Send,
  Menu,
} from "lucide-react";

// ── Page ────────────────────────────────────────────────────

export default function Index() {
  const ws = useWorkspaces();
  const isMobile = useIsMobile();
  const [sidebarOpen, setSidebarOpen] = useState(false);

  const sidebarProps = {
    ...ws,
    onSelectChat: isMobile
      ? (id: string) => {
          ws.selectChat(id);
          setSidebarOpen(false);
        }
      : ws.selectChat,
    onCreateChat: isMobile
      ? () => {
          ws.createChat();
          setSidebarOpen(false);
        }
      : () => ws.createChat(),
  };

  const sidebar = <Sidebar {...sidebarProps} />;

  return (
    <div className="flex h-screen overflow-hidden">
      {isMobile ? (
        <Sheet open={sidebarOpen} onOpenChange={setSidebarOpen}>
          <SheetContent side="left" className="p-0 w-[280px]">
            <VisuallyHidden>
              <SheetTitle>Workspaces</SheetTitle>
            </VisuallyHidden>
            {sidebar}
          </SheetContent>
        </Sheet>
      ) : (
        sidebar
      )}
      <ChatArea
        messages={ws.chatMessages}
        onSend={ws.sendMessage}
        title={ws.activeChat?.title ?? ws.activeWorkspace.name}
        hasDocuments={ws.workspaceDocs.length > 0}
        isMobile={isMobile}
        onOpenSidebar={() => setSidebarOpen(true)}
      />
    </div>
  );
}

// ── Sidebar ─────────────────────────────────────────────────

function Sidebar(
  ws: ReturnType<typeof useWorkspaces> & {
    onSelectChat: (id: string) => void;
    onCreateChat: () => void;
  },
) {
  return (
    <aside className="w-[280px] min-w-[280px] h-screen flex flex-col bg-sidebar border-r border-sidebar-border">
      <div className="p-4 flex items-center gap-2.5">
        <div className="w-8 h-8 rounded-lg bg-accent flex items-center justify-center">
          <Layers className="w-4 h-4 text-accent-foreground" />
        </div>
        <span className="font-semibold text-sm text-foreground tracking-tight">
          DocAssist
        </span>
      </div>

      <div className="px-3 mb-2">
        <button
          onClick={ws.createWorkspace}
          className="w-full flex items-center gap-2 px-3 py-2 text-sm text-muted-foreground rounded-lg hover:bg-secondary transition-colors"
        >
          <Plus className="w-4 h-4" /> New Workspace
        </button>
      </div>

      <div className="flex-1 overflow-y-auto px-3 space-y-1 pb-3">
        {ws.workspaces.map((w) => (
          <WorkspaceItem
            key={w.id}
            workspace={w}
            isActive={w.id === ws.activeWorkspaceId}
            activeChatId={ws.activeChatId}
            chats={
              ws.workspaceChats.length > 0 && w.id === ws.activeWorkspaceId
                ? ws.workspaceChats
                : []
            }
            docs={
              ws.workspaceDocs.length > 0 && w.id === ws.activeWorkspaceId
                ? ws.workspaceDocs
                : []
            }
            embeddingStatus={ws.getEmbeddingStatus(w.id)}
            onSelect={() => ws.selectWorkspace(w.id)}
            onSelectChat={ws.onSelectChat}
            onCreateChat={ws.onCreateChat}
            onUpload={ws.uploadDocument}
            onComputeEmbeddings={() => ws.computeEmbeddings(w.id)}
          />
        ))}
      </div>
    </aside>
  );
}

// ── Workspace Item ──────────────────────────────────────────

function WorkspaceItem({
  workspace,
  isActive,
  activeChatId,
  chats,
  docs,
  embeddingStatus,
  onSelect,
  onSelectChat,
  onCreateChat,
  onUpload,
  onComputeEmbeddings,
}: {
  workspace: Workspace;
  isActive: boolean;
  activeChatId: string | null;
  chats: Chat[];
  docs: DocType[];
  embeddingStatus: "idle" | "computing" | "done";
  onSelect: () => void;
  onSelectChat: (id: string) => void;
  onCreateChat: () => void;
  onUpload: (name: string) => void;
  onComputeEmbeddings: () => void;
}) {
  const [openSection, setOpenSection] = useState<"documents" | "chats" | null>(
    null,
  );
  const toggle = (s: "documents" | "chats") =>
    setOpenSection((prev) => (prev === s ? null : s));

  return (
    <div>
      <button
        onClick={onSelect}
        className={`w-full flex items-center gap-2.5 px-3 py-2.5 text-sm rounded-lg transition-colors ${isActive ? "bg-secondary text-foreground font-medium" : "text-muted-foreground hover:bg-secondary/60 hover:text-foreground"}`}
      >
        <ChevronRight
          className={`w-3.5 h-3.5 shrink-0 transition-transform ${isActive ? "rotate-90" : ""}`}
        />
        <FolderOpen className="w-4 h-4 shrink-0" />
        <span className="truncate flex-1 text-left">{workspace.name}</span>
        <div className="flex items-center gap-2 text-[10px] text-muted-foreground">
          {docs.length > 0 && (
            <span className="flex items-center gap-0.5">
              <FileText className="w-3 h-3" />
              {docs.length}
            </span>
          )}
          {chats.length > 0 && (
            <span className="flex items-center gap-0.5">
              <MessageSquare className="w-3 h-3" />
              {chats.length}
            </span>
          )}
        </div>
      </button>

      <AnimatePresence initial={false}>
        {isActive && (
          <motion.div
            initial={{ opacity: 0, height: 0 }}
            animate={{ opacity: 1, height: "auto" }}
            exit={{ opacity: 0, height: 0 }}
            transition={{ duration: 0.2 }}
            className="overflow-hidden"
          >
            <div className="ml-5 pl-3 border-l-2 border-border/60 py-1.5 space-y-0.5">
              {/* Documents toggle */}
              <SectionBtn
                label="Documents"
                icon={<FileText className="w-3.5 h-3.5" />}
                count={docs.length}
                isOpen={openSection === "documents"}
                onToggle={() => toggle("documents")}
              />
              <AnimatePresence initial={false}>
                {openSection === "documents" && (
                  <motion.div
                    initial={{ opacity: 0, height: 0 }}
                    animate={{ opacity: 1, height: "auto" }}
                    exit={{ opacity: 0, height: 0 }}
                    transition={{ duration: 0.15 }}
                    className="overflow-hidden"
                  >
                    <DocsSection
                      docs={docs}
                      onUpload={onUpload}
                      embeddingStatus={embeddingStatus}
                      onComputeEmbeddings={onComputeEmbeddings}
                    />
                  </motion.div>
                )}
              </AnimatePresence>

              {/* Chats toggle */}
              <SectionBtn
                label="Chats"
                icon={<MessageSquare className="w-3.5 h-3.5" />}
                count={chats.length}
                isOpen={openSection === "chats"}
                onToggle={() => toggle("chats")}
              />
              <AnimatePresence initial={false}>
                {openSection === "chats" && (
                  <motion.div
                    initial={{ opacity: 0, height: 0 }}
                    animate={{ opacity: 1, height: "auto" }}
                    exit={{ opacity: 0, height: 0 }}
                    transition={{ duration: 0.15 }}
                    className="overflow-hidden"
                  >
                    <div className="pl-5 space-y-0.5 py-1">
                      {chats.map((c) => (
                        <button
                          key={c.id}
                          onClick={() => onSelectChat(c.id)}
                          className={`w-full flex items-center gap-2 px-2 py-1.5 rounded-md text-xs transition-colors ${c.id === activeChatId ? "bg-accent/10 text-accent font-medium" : "hover:bg-secondary/50 text-foreground"}`}
                        >
                          <MessageSquare className="w-3.5 h-3.5 shrink-0 text-muted-foreground" />
                          <span className="truncate flex-1 text-left">
                            {c.title}
                          </span>
                        </button>
                      ))}
                      <button
                        onClick={onCreateChat}
                        className="w-full flex items-center gap-2 px-2 py-1.5 rounded-md text-xs text-muted-foreground hover:bg-secondary/50 hover:text-foreground transition-colors"
                      >
                        <PlusCircle className="w-3.5 h-3.5 shrink-0" />{" "}
                        <span>New chat</span>
                      </button>
                    </div>
                  </motion.div>
                )}
              </AnimatePresence>
            </div>
          </motion.div>
        )}
      </AnimatePresence>
    </div>
  );
}

function SectionBtn({
  label,
  icon,
  count,
  isOpen,
  onToggle,
}: {
  label: string;
  icon: React.ReactNode;
  count: number;
  isOpen: boolean;
  onToggle: () => void;
}) {
  return (
    <button
      onClick={onToggle}
      className="w-full flex items-center gap-2 px-2 py-1.5 rounded-md text-xs text-muted-foreground hover:bg-secondary/50 hover:text-foreground transition-colors"
    >
      {isOpen ? (
        <ChevronDown className="w-3 h-3" />
      ) : (
        <ChevronRight className="w-3 h-3" />
      )}
      {icon}
      <span className="flex-1 text-left font-medium">{label}</span>
      {count > 0 && (
        <span className="text-[10px] text-muted-foreground">{count}</span>
      )}
    </button>
  );
}

// ── Documents Section ───────────────────────────────────────

function DocsSection({
  docs,
  onUpload,
  embeddingStatus,
  onComputeEmbeddings,
}: {
  docs: DocType[];
  onUpload: (name: string) => void;
  embeddingStatus: "idle" | "computing" | "done";
  onComputeEmbeddings: () => void;
}) {
  const [dragOver, setDragOver] = useState(false);
  const handleDrop = useCallback(
    (e: React.DragEvent) => {
      e.preventDefault();
      setDragOver(false);
      Array.from(e.dataTransfer.files).forEach((f) => onUpload(f.name));
    },
    [onUpload],
  );
  const handleFile = useCallback(
    (e: React.ChangeEvent<HTMLInputElement>) => {
      Array.from(e.target.files ?? []).forEach((f) => onUpload(f.name));
      e.target.value = "";
    },
    [onUpload],
  );

  return (
    <div className="pl-5 space-y-1 py-1">
      {docs.map((d) => (
        <div
          key={d.id}
          className="flex items-center gap-2 px-2 py-1.5 rounded-md text-xs hover:bg-secondary/50 transition-colors"
        >
          <FileText className="w-3.5 h-3.5 text-muted-foreground shrink-0" />
          <span className="truncate flex-1 text-foreground">{d.name}</span>
          {d.status === "ready" ? (
            <CheckCircle2 className="w-3 h-3 text-status-ready shrink-0" />
          ) : (
            <Loader2 className="w-3 h-3 text-status-processing animate-spin shrink-0" />
          )}
        </div>
      ))}
      <div
        onDragOver={(e) => {
          e.preventDefault();
          setDragOver(true);
        }}
        onDragLeave={() => setDragOver(false)}
        onDrop={handleDrop}
        onClick={() => document.getElementById("file-upload")?.click()}
        className={`flex flex-col items-center gap-1 px-3 py-3 rounded-lg border border-dashed cursor-pointer transition-colors ${dragOver ? "border-accent bg-accent/5 text-accent" : "border-border text-muted-foreground hover:border-muted-foreground/40 hover:text-foreground"}`}
      >
        <Upload className="w-4 h-4" />
        <span className="text-[11px]">
          {docs.length === 0 ? "Upload documents" : "Add more files"}
        </span>
        <input
          id="file-upload"
          type="file"
          multiple
          accept=".pdf,.doc,.docx,.txt"
          className="hidden"
          onChange={handleFile}
        />
      </div>
      {docs.length > 0 && (
        <button
          onClick={onComputeEmbeddings}
          disabled={
            embeddingStatus === "computing" ||
            docs.every((d) => d.status !== "ready")
          }
          className={`w-full flex items-center justify-center gap-2 px-3 py-2.5 rounded-lg text-xs font-medium transition-all duration-200 ${
            embeddingStatus === "done"
              ? "bg-[hsl(var(--status-ready)/0.1)] text-[hsl(var(--status-ready))] border border-[hsl(var(--status-ready)/0.3)]"
              : embeddingStatus === "computing"
                ? "bg-secondary text-muted-foreground cursor-wait border border-border"
                : "bg-accent text-accent-foreground hover:bg-accent/90 shadow-sm hover:shadow-md"
          }`}
        >
          {embeddingStatus === "computing" ? (
            <>
              <Loader2 className="w-3.5 h-3.5 animate-spin" /> Computing…
            </>
          ) : embeddingStatus === "done" ? (
            <>
              <CheckCircle2 className="w-3.5 h-3.5" /> Ready
            </>
          ) : (
            <>
              <Zap className="w-3.5 h-3.5" /> Compute Embeddings
            </>
          )}
        </button>
      )}
    </div>
  );
}

// ── Chat Area ───────────────────────────────────────────────

function ChatArea({
  messages,
  onSend,
  title,
  hasDocuments,
  isMobile,
  onOpenSidebar,
}: {
  messages: Message[];
  onSend: (c: string) => void;
  title: string;
  hasDocuments: boolean;
  isMobile?: boolean;
  onOpenSidebar?: () => void;
}) {
  const [input, setInput] = useState("");
  const [typing, setTyping] = useState(false);
  const bottomRef = useRef<HTMLDivElement>(null);
  const lastCount = useRef(messages.length);

  useEffect(() => {
    if (messages.length > lastCount.current) {
      setTyping(messages[messages.length - 1].role === "user");
    }
    lastCount.current = messages.length;
    bottomRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [messages]);

  const submit = (e: React.FormEvent) => {
    e.preventDefault();
    if (!input.trim()) return;
    onSend(input.trim());
    setInput("");
  };

  return (
    <div className="flex-1 flex flex-col min-w-0 bg-background">
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
          {title}
        </h1>
      </div>

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
                ? "Ask any question about your uploaded documents."
                : "Upload some documents first, then ask questions."}
            </p>
          </div>
        ) : (
          <div className="max-w-3xl mx-auto space-y-1">
            <AnimatePresence initial={false}>
              {messages.map((m) => (
                <motion.div
                  key={m.id}
                  initial={{ opacity: 0, y: 12 }}
                  animate={{ opacity: 1, y: 0 }}
                  transition={{ duration: 0.25 }}
                >
                  <Bubble message={m} />
                </motion.div>
              ))}
            </AnimatePresence>
            {typing && (
              <motion.div
                initial={{ opacity: 0 }}
                animate={{ opacity: 1 }}
                className="flex items-center gap-2 px-4 py-3"
              >
                <Loader2 className="w-4 h-4 text-muted-foreground animate-spin" />
                <span className="text-sm text-muted-foreground">
                  Analyzing…
                </span>
              </motion.div>
            )}
          </div>
        )}
        <div ref={bottomRef} />
      </div>

      <div className="border-t border-border p-3 md:p-4">
        <form onSubmit={submit} className="max-w-3xl mx-auto">
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

// ── Chat Bubble ─────────────────────────────────────────────

function Bubble({ message }: { message: Message }) {
  const isUser = message.role === "user";
  return (
    <div className={`flex ${isUser ? "justify-end" : "justify-start"} mb-4`}>
      <div className="max-w-[85%]">
        <div
          className={`rounded-2xl px-4 py-3 text-sm leading-relaxed ${isUser ? "bg-bubble-user text-bubble-user-foreground rounded-br-md" : "bg-bubble-assistant text-bubble-assistant-foreground rounded-bl-md"}`}
        >
          <MdContent content={message.content} />
        </div>
        {message.citations && message.citations.length > 0 && (
          <div className="flex flex-wrap gap-1.5 mt-2">
            {message.citations.map((c, i) => (
              <span
                key={i}
                className="inline-flex items-center gap-1 text-[11px] px-2 py-1 rounded-md bg-citation text-citation-foreground border border-citation-border"
              >
                <FileText className="w-3 h-3" /> Page {c.page} —{" "}
                {c.documentName}
              </span>
            ))}
          </div>
        )}
      </div>
    </div>
  );
}

function MdContent({ content }: { content: string }) {
  const lines = content.split("\n");
  const els: React.ReactNode[] = [];
  let tableRows: string[][] = [];

  const flushTable = () => {
    if (!tableRows.length) return;
    els.push(
      <div key={`t${els.length}`} className="my-3 overflow-x-auto">
        <table className="w-full text-xs border-collapse">
          <thead>
            <tr>
              {tableRows[0].map((c, i) => (
                <th
                  key={i}
                  className="text-left px-3 py-1.5 border-b border-border font-medium text-muted-foreground"
                >
                  {c.trim()}
                </th>
              ))}
            </tr>
          </thead>
          <tbody>
            {tableRows.slice(2).map((r, ri) => (
              <tr key={ri}>
                {r.map((c, ci) => (
                  <td
                    key={ci}
                    className="px-3 py-1.5 border-b border-border/50"
                  >
                    {c.trim()}
                  </td>
                ))}
              </tr>
            ))}
          </tbody>
        </table>
      </div>,
    );
    tableRows = [];
  };

  let inTable = false;
  lines.forEach((line, i) => {
    if (line.startsWith("|")) {
      inTable = true;
      tableRows.push(line.split("|").filter(Boolean));
      return;
    }
    if (inTable) {
      flushTable();
      inTable = false;
    }
    if (!line.trim()) {
      els.push(<div key={i} className="h-2" />);
      return;
    }
    els.push(
      <p
        key={i}
        dangerouslySetInnerHTML={{
          __html: line
            .replace(/\*\*(.*?)\*\*/g, "<strong>$1</strong>")
            .replace(
              /`(.*?)`/g,
              '<code class="px-1 py-0.5 rounded bg-border/60 text-xs font-mono">$1</code>',
            ),
        }}
      />,
    );
  });
  if (inTable) flushTable();
  return <>{els}</>;
}

import { useState, useCallback } from "react";
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
} from "lucide-react";
import { Workspace, Chat, Document as DocType } from "@/types/workspace";
import { motion, AnimatePresence } from "framer-motion";

interface Props {
  workspaces: Workspace[];
  activeWorkspaceId: string;
  activeChatId: string | null;
  workspaceChats: Chat[];
  workspaceDocs: DocType[];
  onSelectWorkspace: (id: string) => void;
  onSelectChat: (chatId: string) => void;
  onCreate: () => void;
  onCreateChat: () => void;
  onUpload: (name: string) => void;
  allChats: Chat[];
  allDocs: DocType[];
}

export function WorkspaceSidebar({
  workspaces,
  activeWorkspaceId,
  activeChatId,
  onSelectWorkspace,
  onSelectChat,
  onCreate,
  onCreateChat,
  onUpload,
  allChats,
  allDocs,
}: Props) {
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
          onClick={onCreate}
          className="w-full flex items-center gap-2 px-3 py-2 text-sm text-muted-foreground rounded-lg hover:bg-secondary transition-colors"
        >
          <Plus className="w-4 h-4" />
          New Workspace
        </button>
      </div>

      <div className="flex-1 overflow-y-auto px-3 space-y-1 pb-3">
        {workspaces.map((ws) => (
          <WorkspaceItem
            key={ws.id}
            workspace={ws}
            isActive={ws.id === activeWorkspaceId}
            activeChatId={activeChatId}
            chats={allChats.filter((c) => c.workspaceId === ws.id)}
            docs={allDocs.filter((d) => d.workspaceId === ws.id)}
            onSelect={() => onSelectWorkspace(ws.id)}
            onSelectChat={onSelectChat}
            onCreateChat={onCreateChat}
            onUpload={onUpload}
          />
        ))}
      </div>
    </aside>
  );
}

function WorkspaceItem({
  workspace,
  isActive,
  activeChatId,
  chats,
  docs,
  onSelect,
  onSelectChat,
  onCreateChat,
  onUpload,
}: {
  workspace: Workspace;
  isActive: boolean;
  activeChatId: string | null;
  chats: Chat[];
  docs: DocType[];
  onSelect: () => void;
  onSelectChat: (chatId: string) => void;
  onCreateChat: () => void;
  onUpload: (name: string) => void;
}) {
  const [openSection, setOpenSection] = useState<"documents" | "chats" | null>(
    null,
  );

  const toggleSection = (section: "documents" | "chats") => {
    setOpenSection((prev) => (prev === section ? null : section));
  };

  return (
    <div>
      <button
        onClick={onSelect}
        className={`w-full flex items-center gap-2.5 px-3 py-2.5 text-sm rounded-lg transition-colors relative group ${
          isActive
            ? "bg-secondary text-foreground font-medium"
            : "text-muted-foreground hover:bg-secondary/60 hover:text-foreground"
        }`}
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
              {/* Documents */}
              <SectionToggle
                label="Documents"
                icon={<FileText className="w-3.5 h-3.5" />}
                count={docs.length}
                isOpen={openSection === "documents"}
                onToggle={() => toggleSection("documents")}
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
                    <DocumentsContent documents={docs} onUpload={onUpload} />
                  </motion.div>
                )}
              </AnimatePresence>

              {/* Chats */}
              <SectionToggle
                label="Chats"
                icon={<MessageSquare className="w-3.5 h-3.5" />}
                count={chats.length}
                isOpen={openSection === "chats"}
                onToggle={() => toggleSection("chats")}
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
                    <ChatsContent
                      chats={chats}
                      activeChatId={activeChatId}
                      onSelectChat={onSelectChat}
                      onCreateChat={onCreateChat}
                    />
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

function SectionToggle({
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
        <ChevronDown className="w-3 h-3 shrink-0" />
      ) : (
        <ChevronRight className="w-3 h-3 shrink-0" />
      )}
      {icon}
      <span className="flex-1 text-left font-medium">{label}</span>
      {count > 0 && (
        <span className="text-[10px] text-muted-foreground">{count}</span>
      )}
    </button>
  );
}

function DocumentsContent({
  documents,
  onUpload,
}: {
  documents: DocType[];
  onUpload: (name: string) => void;
}) {
  const [isDragOver, setIsDragOver] = useState(false);

  const handleDrop = useCallback(
    (e: React.DragEvent) => {
      e.preventDefault();
      setIsDragOver(false);
      Array.from(e.dataTransfer.files).forEach((f) => onUpload(f.name));
    },
    [onUpload],
  );

  const handleFileInput = useCallback(
    (e: React.ChangeEvent<HTMLInputElement>) => {
      Array.from(e.target.files ?? []).forEach((f) => onUpload(f.name));
      e.target.value = "";
    },
    [onUpload],
  );

  return (
    <div className="pl-5 space-y-1 py-1">
      {documents.map((doc) => (
        <div
          key={doc.id}
          className="flex items-center gap-2 px-2 py-1.5 rounded-md text-xs hover:bg-secondary/50 transition-colors"
        >
          <FileText className="w-3.5 h-3.5 text-muted-foreground shrink-0" />
          <span className="truncate flex-1 text-foreground">{doc.name}</span>
          {doc.status === "ready" ? (
            <CheckCircle2 className="w-3 h-3 text-status-ready shrink-0" />
          ) : (
            <Loader2 className="w-3 h-3 text-status-processing animate-spin shrink-0" />
          )}
        </div>
      ))}
      <div
        onDragOver={(e) => {
          e.preventDefault();
          setIsDragOver(true);
        }}
        onDragLeave={() => setIsDragOver(false)}
        onDrop={handleDrop}
        onClick={() => document.getElementById("file-upload")?.click()}
        className={`flex flex-col items-center gap-1 px-3 py-3 rounded-lg border border-dashed cursor-pointer transition-colors ${
          isDragOver
            ? "border-accent bg-accent/5 text-accent"
            : "border-border text-muted-foreground hover:border-muted-foreground/40 hover:text-foreground"
        }`}
      >
        <Upload className="w-4 h-4" />
        <span className="text-[11px]">
          {documents.length === 0 ? "Upload documents" : "Add more files"}
        </span>
        <input
          id="file-upload"
          type="file"
          multiple
          accept=".pdf,.doc,.docx,.txt"
          className="hidden"
          onChange={handleFileInput}
        />
      </div>
    </div>
  );
}

function ChatsContent({
  chats,
  activeChatId,
  onSelectChat,
  onCreateChat,
}: {
  chats: Chat[];
  activeChatId: string | null;
  onSelectChat: (chatId: string) => void;
  onCreateChat: () => void;
}) {
  return (
    <div className="pl-5 space-y-0.5 py-1">
      {chats.map((chat) => (
        <button
          key={chat.id}
          onClick={() => onSelectChat(chat.id)}
          className={`w-full flex items-center gap-2 px-2 py-1.5 rounded-md text-xs transition-colors ${
            chat.id === activeChatId
              ? "bg-accent/10 text-accent font-medium"
              : "hover:bg-secondary/50 text-foreground"
          }`}
        >
          <MessageSquare className="w-3.5 h-3.5 shrink-0 text-muted-foreground" />
          <span className="truncate flex-1 text-left">{chat.title}</span>
        </button>
      ))}
      <button
        onClick={onCreateChat}
        className="w-full flex items-center gap-2 px-2 py-1.5 rounded-md text-xs text-muted-foreground hover:bg-secondary/50 hover:text-foreground transition-colors"
      >
        <PlusCircle className="w-3.5 h-3.5 shrink-0" />
        <span>New chat</span>
      </button>
    </div>
  );
}

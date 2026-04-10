import { useState, useCallback } from "react";
import { Upload, FileText, CheckCircle2, Loader2, X } from "lucide-react";
import { Document as DocType } from "@/types/workspace";
import { motion, AnimatePresence } from "framer-motion";

interface Props {
  documents: DocType[];
  onUpload: (name: string) => void;
  lastCitedDocs?: string[];
}

export function DocumentsPanel({
  documents,
  onUpload,
  lastCitedDocs = [],
}: Props) {
  const [isDragOver, setIsDragOver] = useState(false);

  const handleDrop = useCallback(
    (e: React.DragEvent) => {
      e.preventDefault();
      setIsDragOver(false);
      const files = Array.from(e.dataTransfer.files);
      files.forEach((f) => onUpload(f.name));
    },
    [onUpload],
  );

  const handleFileInput = useCallback(
    (e: React.ChangeEvent<HTMLInputElement>) => {
      const files = Array.from(e.target.files ?? []);
      files.forEach((f) => onUpload(f.name));
      e.target.value = "";
    },
    [onUpload],
  );

  return (
    <aside className="w-[300px] min-w-[300px] h-screen flex flex-col border-l border-border bg-background">
      {/* Header */}
      <div className="h-14 border-b border-border flex items-center px-4">
        <h2 className="text-sm font-semibold text-foreground">Documents</h2>
        <span className="ml-auto text-[11px] text-muted-foreground">
          {documents.length} files
        </span>
      </div>

      {/* Upload area */}
      <div className="p-4">
        <div
          onDragOver={(e) => {
            e.preventDefault();
            setIsDragOver(true);
          }}
          onDragLeave={() => setIsDragOver(false)}
          onDrop={handleDrop}
          className={`border-2 border-dashed rounded-xl p-6 text-center transition-colors cursor-pointer ${
            isDragOver
              ? "border-accent bg-accent/5"
              : "border-border hover:border-muted-foreground/30"
          }`}
          onClick={() => document.getElementById("file-upload")?.click()}
        >
          <Upload
            className={`w-5 h-5 mx-auto mb-2 ${isDragOver ? "text-accent" : "text-muted-foreground"}`}
          />
          <p className="text-sm font-medium text-foreground">
            Upload Documents
          </p>
          <p className="text-xs text-muted-foreground mt-1">
            Drop files here or click to browse
          </p>
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

      {/* Document list */}
      <div className="flex-1 overflow-y-auto px-4 space-y-1">
        <AnimatePresence initial={false}>
          {documents.map((doc) => (
            <motion.div
              key={doc.id}
              initial={{ opacity: 0, height: 0 }}
              animate={{ opacity: 1, height: "auto" }}
              exit={{ opacity: 0, height: 0 }}
              className="overflow-hidden"
            >
              <DocumentItem
                doc={doc}
                isCited={lastCitedDocs.includes(doc.name)}
              />
            </motion.div>
          ))}
        </AnimatePresence>

        {documents.length === 0 && (
          <div className="text-center py-8">
            <FileText className="w-8 h-8 text-muted-foreground/40 mx-auto mb-2" />
            <p className="text-xs text-muted-foreground">No documents yet</p>
          </div>
        )}
      </div>

      {/* Relevant sources */}
      {lastCitedDocs.length > 0 && (
        <div className="border-t border-border p-4">
          <p className="text-[11px] font-medium text-muted-foreground uppercase tracking-wider mb-2">
            Relevant Sources
          </p>
          {lastCitedDocs.map((name, i) => (
            <div
              key={i}
              className="flex items-center gap-2 text-xs text-foreground py-1"
            >
              <FileText className="w-3 h-3 text-accent" />
              <span className="truncate">{name}</span>
            </div>
          ))}
        </div>
      )}
    </aside>
  );
}

function DocumentItem({ doc, isCited }: { doc: DocType; isCited: boolean }) {
  return (
    <div
      className={`flex items-center gap-3 px-3 py-2.5 rounded-lg transition-colors ${
        isCited ? "bg-accent/5" : "hover:bg-secondary"
      }`}
    >
      <div className="w-8 h-8 rounded-lg bg-secondary flex items-center justify-center shrink-0">
        <FileText className="w-4 h-4 text-muted-foreground" />
      </div>
      <div className="min-w-0 flex-1">
        <p className="text-sm text-foreground truncate">{doc.name}</p>
        <p className="text-[11px] text-muted-foreground">
          {doc.status === "ready" ? `${doc.pages ?? "?"} pages` : "Processing…"}
        </p>
      </div>
      {doc.status === "ready" ? (
        <CheckCircle2 className="w-4 h-4 text-status-ready shrink-0" />
      ) : (
        <Loader2 className="w-4 h-4 text-status-processing animate-spin shrink-0" />
      )}
    </div>
  );
}

import { Plus, FolderOpen, Layers } from 'lucide-react';
import { Workspace } from '@/types/workspace';
import { motion } from 'framer-motion';

interface Props {
  workspaces: Workspace[];
  activeId: string;
  onSelect: (id: string) => void;
  onCreate: () => void;
}

export function WorkspaceSidebar({ workspaces, activeId, onSelect, onCreate }: Props) {
  return (
    <aside className="w-[260px] min-w-[260px] h-screen flex flex-col bg-sidebar border-r border-sidebar-border">
      {/* Header */}
      <div className="p-4 flex items-center gap-2.5">
        <div className="w-8 h-8 rounded-lg bg-accent flex items-center justify-center">
          <Layers className="w-4 h-4 text-accent-foreground" />
        </div>
        <span className="font-semibold text-sm text-foreground tracking-tight">DocAssist</span>
      </div>

      {/* New workspace button */}
      <div className="px-3 mb-2">
        <button
          onClick={onCreate}
          className="w-full flex items-center gap-2 px-3 py-2 text-sm text-muted-foreground rounded-lg hover:bg-secondary transition-colors"
        >
          <Plus className="w-4 h-4" />
          New Workspace
        </button>
      </div>

      {/* Workspace list */}
      <div className="flex-1 overflow-y-auto px-3 space-y-0.5">
        <p className="text-[11px] font-medium text-muted-foreground uppercase tracking-wider px-3 py-2">
          Workspaces
        </p>
        {workspaces.map(ws => {
          const isActive = ws.id === activeId;
          return (
            <button
              key={ws.id}
              onClick={() => onSelect(ws.id)}
              className={`w-full flex items-center gap-2.5 px-3 py-2 text-sm rounded-lg transition-colors relative ${
                isActive
                  ? 'bg-secondary text-foreground font-medium'
                  : 'text-muted-foreground hover:bg-secondary/60 hover:text-foreground'
              }`}
            >
              {isActive && (
                <motion.div
                  layoutId="active-workspace"
                  className="absolute inset-0 rounded-lg bg-secondary"
                  transition={{ type: 'spring', bounce: 0.15, duration: 0.4 }}
                />
              )}
              <FolderOpen className="w-4 h-4 relative z-10 shrink-0" />
              <span className="relative z-10 truncate">{ws.name}</span>
              <span className="relative z-10 ml-auto text-[11px] text-muted-foreground">
                {ws.documents.length}
              </span>
            </button>
          );
        })}
      </div>
    </aside>
  );
}

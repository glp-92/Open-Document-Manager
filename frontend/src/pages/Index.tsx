import { WorkspaceSidebar } from '@/components/WorkspaceSidebar';
import { ChatArea } from '@/components/ChatArea';
import { DocumentsPanel } from '@/components/DocumentsPanel';
import { useWorkspaces } from '@/hooks/useWorkspaces';
import { useMemo } from 'react';

const Index = () => {
  const { workspaces, activeWorkspace, activeId, setActiveId, createWorkspace, sendMessage, uploadDocument } = useWorkspaces();

  const lastCitedDocs = useMemo(() => {
    const msgs = activeWorkspace.messages;
    for (let i = msgs.length - 1; i >= 0; i--) {
      if (msgs[i].citations?.length) {
        return [...new Set(msgs[i].citations!.map(c => c.documentName))];
      }
    }
    return [];
  }, [activeWorkspace.messages]);

  return (
    <div className="flex h-screen overflow-hidden">
      <WorkspaceSidebar
        workspaces={workspaces}
        activeId={activeId}
        onSelect={setActiveId}
        onCreate={createWorkspace}
      />
      <ChatArea
        messages={activeWorkspace.messages}
        onSend={sendMessage}
        workspaceName={activeWorkspace.name}
        hasDocuments={activeWorkspace.documents.length > 0}
      />
      <DocumentsPanel
        documents={activeWorkspace.documents}
        onUpload={uploadDocument}
        lastCitedDocs={lastCitedDocs}
      />
    </div>
  );
};

export default Index;

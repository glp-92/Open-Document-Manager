import { WorkspaceSidebar } from "@/components/WorkspaceSidebar";
import { ChatArea } from "@/components/ChatArea";
import { useWorkspaces } from "@/hooks/useWorkspaces";
import { useState } from "react";
import { useIsMobile } from "@/hooks/use-mobile";
import { Sheet, SheetContent, SheetTitle } from "@/components/ui/sheet";
import { VisuallyHidden } from "@radix-ui/react-visually-hidden";

const Index = () => {
  const ws = useWorkspaces();
  const isMobile = useIsMobile();
  const [sidebarOpen, setSidebarOpen] = useState(false);

  const sidebarProps = {
    workspaces: ws.workspaces,
    activeWorkspaceId: ws.activeWorkspaceId,
    activeChatId: ws.activeChatId,
    workspaceChats: ws.workspaceChats,
    workspaceDocs: ws.workspaceDocs,
    allChats: ws.workspaceChats,
    allDocs: ws.workspaceDocs,
    onSelectWorkspace: isMobile
      ? (id: string) => {
          ws.selectWorkspace(id);
        }
      : ws.selectWorkspace,
    onSelectChat: isMobile
      ? (id: string) => {
          ws.selectChat(id);
          setSidebarOpen(false);
        }
      : ws.selectChat,
    onCreate: isMobile
      ? () => {
          ws.createWorkspace();
        }
      : ws.createWorkspace,
    onCreateChat: isMobile
      ? () => {
          ws.createChat();
          setSidebarOpen(false);
        }
      : () => ws.createChat(),
    onUpload: ws.uploadDocument,
  };

  const chatAreaProps = {
    messages: ws.chatMessages,
    onSend: ws.sendMessage,
    workspaceName: ws.activeChat?.title ?? ws.activeWorkspace.name,
    hasDocuments: ws.workspaceDocs.length > 0,
    ...(isMobile
      ? { isMobile: true, onOpenSidebar: () => setSidebarOpen(true) }
      : {}),
  };

  if (isMobile) {
    return (
      <div className="flex flex-col h-screen overflow-hidden">
        <Sheet open={sidebarOpen} onOpenChange={setSidebarOpen}>
          <SheetContent side="left" className="p-0 w-[280px]">
            <VisuallyHidden>
              <SheetTitle>Workspaces</SheetTitle>
            </VisuallyHidden>
            <WorkspaceSidebar {...sidebarProps} />
          </SheetContent>
        </Sheet>
        <ChatArea {...chatAreaProps} />
      </div>
    );
  }

  return (
    <div className="flex h-screen overflow-hidden">
      <WorkspaceSidebar {...sidebarProps} />
      <ChatArea {...chatAreaProps} />
    </div>
  );
};

export default Index;

import { useState, useCallback } from "react";
import { Workspace, Chat, Message, Document } from "@/types/workspace";

const DEMO_DOCS: Document[] = [
  {
    id: "d1",
    workspaceId: "1",
    name: "Market Analysis 2024.pdf",
    status: "ready",
    pages: 42,
    uploadedAt: new Date("2024-03-01"),
  },
  {
    id: "d2",
    workspaceId: "1",
    name: "Competitor Report.pdf",
    status: "ready",
    pages: 18,
    uploadedAt: new Date("2024-03-02"),
  },
  {
    id: "d3",
    workspaceId: "1",
    name: "User Survey Results.pdf",
    status: "processing",
    uploadedAt: new Date("2024-03-10"),
  },
  {
    id: "d4",
    workspaceId: "2",
    name: "API Documentation v3.pdf",
    status: "ready",
    pages: 156,
    uploadedAt: new Date("2024-03-05"),
  },
  {
    id: "d5",
    workspaceId: "2",
    name: "System Architecture.pdf",
    status: "ready",
    pages: 34,
    uploadedAt: new Date("2024-03-06"),
  },
];

const DEMO_CHATS: Chat[] = [
  {
    id: "c1",
    workspaceId: "1",
    title: "Market insights",
    createdAt: new Date("2024-03-05"),
  },
  {
    id: "c2",
    workspaceId: "1",
    title: "Pricing comparison",
    createdAt: new Date("2024-03-06"),
  },
  {
    id: "c3",
    workspaceId: "2",
    title: "API endpoints review",
    createdAt: new Date("2024-03-07"),
  },
];

const DEMO_MESSAGES: Message[] = [
  {
    id: "m1",
    chatId: "c1",
    role: "user",
    content: "What are the key findings from the market analysis?",
    timestamp: new Date("2024-03-05T10:00:00"),
  },
  {
    id: "m2",
    chatId: "c1",
    role: "assistant",
    timestamp: new Date("2024-03-05T10:00:05"),
    content:
      "Based on the Market Analysis 2024, here are the key findings:\n\n1. **Market size** is projected to reach $4.2B by 2025, growing at 12% CAGR.\n2. **Customer segments** are shifting toward enterprise adoption.\n3. The **competitive landscape** shows consolidation among top 5 players.",
    citations: [
      { page: 12, documentName: "Market Analysis 2024.pdf" },
      { page: 28, documentName: "Market Analysis 2024.pdf" },
    ],
  },
  {
    id: "m3",
    chatId: "c2",
    role: "user",
    content: "How does our competitor pricing compare?",
    timestamp: new Date("2024-03-06T10:00:00"),
  },
  {
    id: "m4",
    chatId: "c2",
    role: "assistant",
    timestamp: new Date("2024-03-06T10:00:05"),
    content:
      "According to the Competitor Report, pricing varies significantly:\n\n| Competitor | Basic | Enterprise |\n|-----------|-------|------------|\n| Acme Corp | $29/mo | $199/mo |\n| Beta Inc | $39/mo | $299/mo |",
    citations: [{ page: 5, documentName: "Competitor Report.pdf" }],
  },
];

const DEMO_WORKSPACES: Workspace[] = [
  { id: "1", name: "Product Research", createdAt: new Date("2024-03-01") },
  { id: "2", name: "Technical Specs", createdAt: new Date("2024-03-05") },
  { id: "3", name: "Legal Review", createdAt: new Date("2024-03-10") },
];

export function useWorkspaces() {
  const [workspaces, setWorkspaces] = useState<Workspace[]>(DEMO_WORKSPACES);
  const [chats, setChats] = useState<Chat[]>(DEMO_CHATS);
  const [messages, setMessages] = useState<Message[]>(DEMO_MESSAGES);
  const [documents, setDocuments] = useState<Document[]>(DEMO_DOCS);

  const [activeWorkspaceId, setActiveWorkspaceId] = useState<string>("1");
  const [activeChatId, setActiveChatId] = useState<string | null>("c1");

  const activeWorkspace =
    workspaces.find((w) => w.id === activeWorkspaceId) ?? workspaces[0];
  const workspaceChats = chats.filter(
    (c) => c.workspaceId === activeWorkspaceId,
  );
  const workspaceDocs = documents.filter(
    (d) => d.workspaceId === activeWorkspaceId,
  );
  const activeChat = activeChatId
    ? chats.find((c) => c.id === activeChatId)
    : null;
  const chatMessages = activeChatId
    ? messages.filter((m) => m.chatId === activeChatId)
    : [];

  const selectWorkspace = useCallback(
    (id: string) => {
      setActiveWorkspaceId(id);
      // Auto-select first chat in workspace
      const firstChat = chats.find((c) => c.workspaceId === id);
      setActiveChatId(firstChat?.id ?? null);
    },
    [chats],
  );

  const selectChat = useCallback((chatId: string) => {
    setActiveChatId(chatId);
  }, []);

  const createWorkspace = useCallback(() => {
    const newWs: Workspace = {
      id: crypto.randomUUID(),
      name: `Workspace ${workspaces.length + 1}`,
      createdAt: new Date(),
    };
    setWorkspaces((prev) => [newWs, ...prev]);
    setActiveWorkspaceId(newWs.id);
    setActiveChatId(null);
  }, [workspaces.length]);

  const createChat = useCallback(
    (title?: string) => {
      const newChat: Chat = {
        id: crypto.randomUUID(),
        workspaceId: activeWorkspaceId,
        title: title || `Chat ${workspaceChats.length + 1}`,
        createdAt: new Date(),
      };
      setChats((prev) => [...prev, newChat]);
      setActiveChatId(newChat.id);
      return newChat;
    },
    [activeWorkspaceId, workspaceChats.length],
  );

  const sendMessage = useCallback(
    (content: string) => {
      let chatId = activeChatId;

      // Auto-create chat if none selected
      if (!chatId) {
        const newChat: Chat = {
          id: crypto.randomUUID(),
          workspaceId: activeWorkspaceId,
          title: content.slice(0, 40) + (content.length > 40 ? "…" : ""),
          createdAt: new Date(),
        };
        setChats((prev) => [...prev, newChat]);
        chatId = newChat.id;
        setActiveChatId(chatId);
      }

      const userMsg: Message = {
        id: crypto.randomUUID(),
        chatId,
        role: "user",
        content,
        timestamp: new Date(),
      };
      setMessages((prev) => [...prev, userMsg]);

      // Simulate assistant response
      const capturedChatId = chatId;
      setTimeout(() => {
        const assistantMsg: Message = {
          id: crypto.randomUUID(),
          chatId: capturedChatId,
          role: "assistant",
          content:
            "I've analyzed your documents and found relevant information. This is a demo response — in a real application, this would contain insights extracted from your uploaded documents.",
          citations: workspaceDocs
            .filter((d) => d.status === "ready")
            .slice(0, 1)
            .map((d) => ({
              page: Math.floor(Math.random() * 20) + 1,
              documentName: d.name,
            })),
          timestamp: new Date(),
        };
        setMessages((prev) => [...prev, assistantMsg]);
      }, 1500);
    },
    [activeChatId, activeWorkspaceId, workspaceDocs],
  );

  const [embeddingStatus, setEmbeddingStatus] = useState<
    Record<string, "idle" | "computing" | "done">
  >({});

  const computeEmbeddings = useCallback((workspaceId: string) => {
    setEmbeddingStatus((prev) => ({ ...prev, [workspaceId]: "computing" }));
    // Simulate embedding computation
    setTimeout(() => {
      setEmbeddingStatus((prev) => ({ ...prev, [workspaceId]: "done" }));
    }, 4000);
  }, []);

  const getEmbeddingStatus = useCallback(
    (workspaceId: string): "idle" | "computing" | "done" => {
      return embeddingStatus[workspaceId] ?? "idle";
    },
    [embeddingStatus],
  );

  const uploadDocument = useCallback(
    (name: string) => {
      const newDoc: Document = {
        id: crypto.randomUUID(),
        workspaceId: activeWorkspaceId,
        name,
        status: "processing",
        uploadedAt: new Date(),
      };
      setDocuments((prev) => [...prev, newDoc]);
      setTimeout(() => {
        setDocuments((prev) =>
          prev.map((d) =>
            d.id === newDoc.id
              ? {
                  ...d,
                  status: "ready" as const,
                  pages: Math.floor(Math.random() * 50) + 5,
                }
              : d,
          ),
        );
      }, 3000);
    },
    [activeWorkspaceId],
  );

  return {
    workspaces,
    activeWorkspace,
    activeWorkspaceId,
    activeChatId,
    activeChat,
    workspaceChats,
    workspaceDocs,
    chatMessages,
    selectWorkspace,
    selectChat,
    createWorkspace,
    createChat,
    sendMessage,
    uploadDocument,
    computeEmbeddings,
    getEmbeddingStatus,
  };
}

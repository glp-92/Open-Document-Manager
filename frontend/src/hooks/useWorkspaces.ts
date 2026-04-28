import { useState, useCallback, useEffect } from "react";
import {
  Workspace,
  Chat,
  Message,
  Document as DocType,
} from "@/types/workspace";
import * as api from "@/api/endpoints";
import {
  subscribeToDocumentEvents,
  subscribeToMessagesEvents,
  subscribeToRunEvents,
} from "@/api/endpoints";

export function useWorkspaces() {
  const [workspaces, setWorkspaces] = useState<Workspace[]>([]);
  const [chats, setChats] = useState<Chat[]>([]);
  const [messages, setMessages] = useState<Message[]>([]);
  const [documents, setDocuments] = useState<DocType[]>([]);
  const [loading, setLoading] = useState(true);
  const [editingWorkspaceId, setEditingWorkspaceId] = useState<string | null>(
    null,
  );

  const [activeWorkspaceId, setActiveWorkspaceId] = useState<string | null>(
    null,
  );
  const [activeChatId, setActiveChatId] = useState<string | null>(null);

  // Fetch workspaces on mount
  useEffect(() => {
    api
      .getWorkspaces()
      .then((res) => {
        const ws = res?.workspaces ?? [];
        setWorkspaces(ws);
        if (ws.length > 0) setActiveWorkspaceId(ws[0].id);
      })
      .catch(console.error)
      .finally(() => setLoading(false));
  }, []);

  // SSE for run status updates on realtime
  useEffect(() => {
    const sse = subscribeToRunEvents(
      (payload) => {
        console.log("Run event received", payload);
        setRunStatus((prev) => ({
          ...prev,
          [payload.data.workspace_id]: payload.data.status,
        }));
        if (payload.data.status !== "PENDING") {
          setRunRequestInFlight((prev) => ({
            ...prev,
            [payload.data.workspace_id]: false,
          }));
        }
      },
      (err) => console.error("SSE Connection failed", err),
    );
    return () => sse.close();
  }, []);

  // SSE for document status updates on realtime
  useEffect(() => {
    const sse = subscribeToDocumentEvents(
      (payload) => {
        console.log("Document event received", payload);
        setDocuments((prev) =>
          prev.map((doc) => {
            if (doc.id === payload.data.id) {
              return {
                ...doc,
                storage_status: payload.data.storage_status,
                updated_at: new Date().toISOString(),
              };
            }
            return doc;
          }),
        );
      },
      (err) => console.error("SSE Connection failed", err),
    );
    return () => sse.close();
  }, []);

  // SSE for message status updates on realtime
  useEffect(() => {
    const sse = subscribeToMessagesEvents(
      (payload) => {
        console.log("Message event received", payload);
        setMessages((prev) => {
          const existing = prev.find((m) => m.id === payload.data.id);
          if (existing) {
            return prev.map((msg) =>
              msg.id === payload.data.id
                ? {
                    ...msg,
                    content: payload.data.content,
                    owner: payload.data.owner,
                    created_at: payload.data.created_at,
                    updated_at: new Date().toISOString(),
                  }
                : msg,
            );
          }
          // append new message (AI reply or new server-created message)
          return [
            ...prev,
            {
              id: payload.data.id,
              chat_id: payload.data.chat_id,
              owner: payload.data.owner,
              content: payload.data.content,
              created_at: payload.data.created_at,
              updated_at: new Date().toISOString(),
            },
          ];
        });
      },
      (err) => console.error("SSE Connection failed", err),
    );
    return () => sse.close();
  }, []);

  // Fetch chats when active workspace changes
  useEffect(() => {
    if (!activeWorkspaceId) {
      setChats([]);
      setDocuments([]);
      return;
    }
    api
      .getChats({ workspace_id: activeWorkspaceId })
      .then((res) => {
        const c = res?.chats ?? [];
        setChats(c);
        setActiveChatId(c.length > 0 ? c[0].id : null);
      })
      .catch(console.error);
    api
      .getDocuments({ workspace_id: activeWorkspaceId })
      .then((res) => {
        const c = res?.documents ?? [];
        setDocuments(c);
      })
      .catch(console.error);
  }, [activeWorkspaceId]);

  // Fetch messages when active chat changes
  useEffect(() => {
    if (!activeChatId) {
      setMessages([]);
      return;
    }
    api
      .getMessages({ chat_id: activeChatId })
      .then((res) => setMessages(res?.messages ?? []))
      .catch(console.error);
  }, [activeChatId]);

  const activeWorkspace =
    workspaces.find((w) => w.id === activeWorkspaceId) ?? null;
  const workspaceChats = chats;
  const workspaceDocs = documents;
  const activeChat = activeChatId
    ? (chats.find((c) => c.id === activeChatId) ?? null)
    : null;
  const chatMessages = messages;

  const selectWorkspace = useCallback(
    (id: string) => setActiveWorkspaceId(id),
    [],
  );
  const selectChat = useCallback((id: string) => setActiveChatId(id), []);

  const createWorkspace = useCallback(async () => {
    try {
      const ws = await api.createWorkspace(
        `Workspace ${workspaces.length + 1}`,
      );
      setWorkspaces((prev) => [ws, ...prev]);
      setActiveWorkspaceId(ws.id);
      setActiveChatId(null);
    } catch (e) {
      console.error(e);
    }
  }, [workspaces.length]);

  const editWorkspace = useCallback(async (id: string, newName: string) => {
    try {
      const updatedWs = await api.editWorkspace(id, newName);
      setWorkspaces((prev) =>
        prev.map((ws) => (ws.id === id ? updatedWs : ws)),
      );
      setActiveWorkspaceId(updatedWs.id);
    } catch (e) {
      console.error(e);
    }
  }, []);

  const deleteWorkspace = useCallback(
    async (id: string) => {
      try {
        await api.deleteWorkspace(id);
        setWorkspaces((prev) => {
          const remaining = prev.filter((w) => w.id !== id);
          setActiveWorkspaceId((current) =>
            current === id ? (remaining[0]?.id ?? null) : current,
          );
          return remaining;
        });
      } catch (e) {
        console.error(e);
      }
    },
    [],
  );

  const deleteDocument = useCallback(async (docId: string) => {
    try {
      await api.deleteDocument(docId);
      setDocuments((prev) => prev.filter((d) => d.id !== docId));
    } catch (e) {
      console.error(e);
    }
  }, []);

  const createChat = useCallback(
    async (name?: string) => {
      if (!activeWorkspaceId) return;
      try {
        const chat = await api.createChat(
          activeWorkspaceId,
          name || `Chat ${chats.length + 1}`,
        );
        setChats((prev) => [...prev, chat]);
        setActiveChatId(chat.id);
        return chat;
      } catch (e) {
        console.error(e);
      }
    },
    [activeWorkspaceId, chats.length],
  );

  const deleteChat = useCallback(async (chatId: string) => {
    try {
      await api.deleteChat(chatId);
      setChats((prev) => prev.filter((c) => c.id !== chatId));
      setActiveChatId((currentActive) =>
        currentActive === chatId ? null : currentActive,
      );
    } catch (e) {
      console.error(e);
    }
  }, []);

  const sendMessage = useCallback(
    async (content: string) => {
      let chatId = activeChatId;

      // Auto-create chat if none active
      if (!chatId && activeWorkspaceId) {
        try {
          const newChat = await api.createChat(
            activeWorkspaceId,
            content.slice(0, 40) + (content.length > 40 ? "…" : ""),
          );
          setChats((prev) => [...prev, newChat]);
          chatId = newChat.id;
          setActiveChatId(chatId);
        } catch (e) {
          console.error(e);
          return;
        }
      }
      if (!chatId) return;

      // Optimistic user message
      const tempMsg: Message = {
        id: crypto.randomUUID(),
        chat_id: chatId,
        owner: "HUMAN",
        content,
        created_at: new Date().toISOString(),
        updated_at: new Date().toISOString(),
      };
      setMessages((prev) => [...prev, tempMsg]);

      try {
        const response = await api.createMessage(chatId, content, "HUMAN");
        setMessages((prev) => [
          ...prev.filter((m) => m.id !== tempMsg.id),
          response,
        ]);
        // Refetch to include any AI reply
        const fresh = await api.getMessages({ chat_id: chatId });
        setMessages(fresh?.messages ?? []);
      } catch (e) {
        console.error(e);
      }
    },
    [activeChatId, activeWorkspaceId],
  );

  // ── Runs (replaces embeddings) ────────────────────────────
  const [runStatus, setRunStatus] = useState<
    Record<string | null, null | "PENDING" | "COMPLETED" | "ERROR" | "DELETED">
  >({});
  const [runRequestInFlight, setRunRequestInFlight] = useState<
    Record<string, boolean>
  >({});

  const computeEmbeddings = useCallback(async (workspaceId: string) => {
    setRunRequestInFlight((prev) => ({ ...prev, [workspaceId]: true }));
    setRunStatus((prev) => ({ ...prev, [workspaceId]: "PENDING" }));
    try {
      await api.createRun(workspaceId);
      setRunStatus((prev) => ({ ...prev, [workspaceId]: "PENDING" }));
    } catch (e) {
      console.error(e);
      setRunRequestInFlight((prev) => ({ ...prev, [workspaceId]: false }));
      setRunStatus((prev) => ({ ...prev, [workspaceId]: "ERROR" }));
    }
  }, []);

  const getEmbeddingStatus = useCallback(async (workspaceId: string) => {
    try {
      const response = await api.getRuns({
        workspace_id: workspaceId,
        order_by: "created_at",
        order: "desc",
        limit: 1,
      });
      setRunStatus((prev) => ({
        ...prev,
        [workspaceId]: response.runs[0]?.status ?? null,
      }));
      if (response.runs[0]?.status !== "PENDING") {
        setRunRequestInFlight((prev) => ({ ...prev, [workspaceId]: false }));
      }
    } catch (e) {
      console.error(e);
      setRunRequestInFlight((prev) => ({ ...prev, [workspaceId]: false }));
      setRunStatus((prev) => ({ ...prev, [workspaceId]: "ERROR" }));
    }
  }, []);

  useEffect(() => {
    if (!activeWorkspaceId) return;
    void getEmbeddingStatus(activeWorkspaceId);
  }, [activeWorkspaceId, getEmbeddingStatus]);

  // ── Document upload (2-step: create → presigned PUT) ──────
  const uploadDocument = useCallback(
    async (file: File) => {
      if (!activeWorkspaceId) return;
      try {
        const res = await api.createDocument(activeWorkspaceId, file.name);
        // Upload to presigned URL
        await fetch(res.presigned_url, {
          method: "PUT",
          body: file,
          headers: { "Content-Type": file.type || "application/octet-stream" },
        });
        // Refetch documents for the chat
        const docs = await api.getDocuments({
          workspace_id: activeWorkspaceId,
        });
        setDocuments(docs?.documents ?? []);
      } catch (e) {
        console.error(e);
      }
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
    loading,
    editingWorkspaceId,
    selectWorkspace,
    selectChat,
    createWorkspace,
    editWorkspace,
    deleteWorkspace,
    createChat,
    deleteChat,
    deleteDocument,
    sendMessage,
    uploadDocument,
    computeEmbeddings,
    getEmbeddingStatus,
    runStatus,
    runRequestInFlight,
    setEditingWorkspaceId,
  };
}

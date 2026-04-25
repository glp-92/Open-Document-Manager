import {
  Workspace,
  Chat,
  Message,
  Document,
  Run,
  UploadDocumentResponse,
  WorkspaceFilters,
  ChatFilters,
  MessageFilters,
  DocumentFilters,
  RunFilters,
  DocumentEventPayload,
  RunEventPayload,
  MessageEventPayload,
} from "@/types/workspace";

const API_BASE = import.meta.env.VITE_API_BASE || "/api/v1";

// ── Helpers ─────────────────────────────────────────────────

function qs(
  params: Record<string, string | number | undefined | null>,
): string {
  const p = new URLSearchParams();
  for (const [k, v] of Object.entries(params)) {
    if (v != null && v !== "") p.set(k, String(v));
  }
  const s = p.toString();
  return s ? `?${s}` : "";
}

async function request<T>(
  method: string,
  path: string,
  body?: unknown,
): Promise<T> {
  const res = await fetch(`${API_BASE}${path}`, {
    method,
    headers: { "Content-Type": "application/json" },
    ...(body ? { body: JSON.stringify(body) } : {}),
  });
  if (!res.ok) throw new Error(`API ${method} ${path}: ${res.status}`);
  if (res.status === 204) return undefined as T;
  return res.json();
}

// ── Workspaces ──────────────────────────────────────────────

export async function getWorkspaces(
  f?: WorkspaceFilters,
): Promise<{ total: number; workspaces: Workspace[] }> {
  return request(
    "GET",
    `/workspaces${qs({ limit: f?.limit, offset: f?.offset, name: f?.name })}`,
  );
}

export async function createWorkspace(name: string): Promise<Workspace> {
  return request("POST", "/workspaces", { name });
}

export async function editWorkspace(
  id: string,
  name: string,
): Promise<Workspace> {
  return request("PATCH", `/workspaces/${id}`, { name });
}

export async function deleteWorkspace(id: string): Promise<void> {
  return request("DELETE", `/workspaces/${id}`);
}

// ── Chats ───────────────────────────────────────────────────

export async function getChats(
  f: ChatFilters,
): Promise<{ total: number; chats: Chat[] }> {
  return request(
    "GET",
    `/chats${qs({ limit: f.limit, offset: f.offset, workspace_id: f.workspace_id })}`,
  );
}

export async function createChat(
  workspace_id: string,
  name?: string,
): Promise<Chat> {
  return request("POST", "/chats", { workspace_id, name });
}

export async function deleteChat(id: string): Promise<void> {
  return request("DELETE", `/chats/${id}`);
}

// ── Messages ────────────────────────────────────────────────

export async function getMessages(
  f: MessageFilters,
): Promise<{ total: number; messages: Message[] }> {
  return request(
    "GET",
    `/messages${qs({ limit: f.limit, offset: f.offset, chat_id: f.chat_id, order_by: "created_at", order: "asc" })}`,
  );
}

export async function createMessage(
  chat_id: string,
  content: string,
  owner: "HUMAN" | "AI" = "HUMAN",
): Promise<Message> {
  return request("POST", "/messages", { chat_id, content, owner });
}

export async function deleteMessage(id: string): Promise<void> {
  return request("DELETE", `/messages/${id}`);
}

// ── Documents ───────────────────────────────────────────────

export async function getDocuments(
  f: DocumentFilters,
): Promise<{ total: number; documents: Document[] }> {
  return request(
    "GET",
    `/documents${qs({ limit: f.limit, offset: f.offset, workspace_id: f.workspace_id })}`,
  );
}

export async function createDocument(
  workspace_id: string,
  filename: string,
): Promise<UploadDocumentResponse> {
  return request("POST", "/documents", { workspace_id, filename });
}

export async function deleteDocument(id: string): Promise<void> {
  return request("DELETE", `/documents/${id}`);
}

// ── Runs (embeddings) ───────────────────────────────────────

export async function getRuns(
  f: RunFilters,
): Promise<{ total: number; runs: Run[] }> {
  return request(
    "GET",
    `/runs${qs({ limit: f.limit, offset: f.offset, workspace_id: f.workspace_id, status: f.status, order_by: f.order_by, order: f.order })}`,
  );
}

export async function createRun(workspace_id: string): Promise<Run> {
  return request("POST", "/runs", { workspace_id });
}

export async function deleteRun(id: string): Promise<void> {
  return request("DELETE", `/runs/${id}`);
}

// SSE server stream for runs finished
export function subscribeToRunEvents(
  onMessage: (payload: RunEventPayload) => void,
  onError?: (err: Event) => void,
): EventSource {
  const url = `${API_BASE}/events/runs`;
  const eventSource = new EventSource(url);
  eventSource.onmessage = (event) => {
    try {
      const parsedData: RunEventPayload = JSON.parse(event.data);
      onMessage(parsedData);
    } catch (e) {
      console.error("Error parsing SSE data", e);
    }
  };
  if (onError) {
    eventSource.onerror = onError;
  }
  return eventSource;
}

// SSE server stream  for documents uploaded
export function subscribeToDocumentEvents(
  onMessage: (payload: DocumentEventPayload) => void,
  onError?: (err: Event) => void,
): EventSource {
  const url = `${API_BASE}/events/documents`;
  const eventSource = new EventSource(url);
  eventSource.onmessage = (event) => {
    try {
      const parsedData: DocumentEventPayload = JSON.parse(event.data);
      onMessage(parsedData);
    } catch (e) {
      console.error("Error parsing SSE data", e);
    }
  };
  if (onError) {
    eventSource.onerror = onError;
  }
  return eventSource;
}

// SSE server stream  for AI messages
export function subscribeToMessagesEvents(
  onMessage: (payload: MessageEventPayload) => void,
  onError?: (err: Event) => void,
): EventSource {
  const url = `${API_BASE}/events/messages`;
  const eventSource = new EventSource(url);
  eventSource.onmessage = (event) => {
    try {
      const parsedData: MessageEventPayload = JSON.parse(event.data);
      onMessage(parsedData);
    } catch (e) {
      console.error("Error parsing SSE data", e);
    }
  };
  if (onError) {
    eventSource.onerror = onError;
  }
  return eventSource;
}

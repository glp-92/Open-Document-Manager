import {
  Workspace,
  Chat,
  Message,
  Document,
  WorkspaceFilters,
  ChatFilters,
  MessageFilters,
  FileFilters,
} from "@/types/workspace";

const API_BASE = "/api"; // Replace with actual base URL when backend is ready

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
  if (!res.ok) throw new Error(`API error: ${res.status}`);
  return res.json();
}

// ── Workspaces ──────────────────────────────────────────────

export async function getWorkspaces(
  filters?: WorkspaceFilters,
): Promise<Workspace[]> {
  const params = new URLSearchParams();
  if (filters?.page) params.set("page", String(filters.page));
  if (filters?.limit) params.set("limit", String(filters.limit));
  if (filters?.search) params.set("search", filters.search);
  const qs = params.toString();
  return request("GET", `/workspaces${qs ? `?${qs}` : ""}`);
}

export async function createWorkspace(data: {
  name: string;
}): Promise<Workspace> {
  return request("POST", "/workspaces", data);
}

// ── Chats ───────────────────────────────────────────────────

export async function getChats(filters: ChatFilters): Promise<Chat[]> {
  const params = new URLSearchParams();
  params.set("workspace_id", filters.workspaceId);
  if (filters.page) params.set("page", String(filters.page));
  if (filters.limit) params.set("limit", String(filters.limit));
  return request("GET", `/chats?${params.toString()}`);
}

export async function createChat(data: {
  workspaceId: string;
  title?: string;
}): Promise<Chat> {
  return request("POST", "/chats", {
    workspace_id: data.workspaceId,
    title: data.title,
  });
}

// ── Messages ────────────────────────────────────────────────

export async function getMessages(filters: MessageFilters): Promise<Message[]> {
  const params = new URLSearchParams();
  params.set("chat_id", filters.chatId);
  if (filters.page) params.set("page", String(filters.page));
  if (filters.limit) params.set("limit", String(filters.limit));
  return request("GET", `/messages?${params.toString()}`);
}

export async function createMessage(data: {
  chatId: string;
  content: string;
}): Promise<Message> {
  return request("POST", "/messages", {
    chat_id: data.chatId,
    content: data.content,
  });
}

// ── Files ───────────────────────────────────────────────────

export async function getFiles(filters: FileFilters): Promise<Document[]> {
  const params = new URLSearchParams();
  params.set("workspace_id", filters.workspaceId);
  if (filters.page) params.set("page", String(filters.page));
  if (filters.limit) params.set("limit", String(filters.limit));
  return request("GET", `/files?${params.toString()}`);
}

export async function uploadFile(data: {
  workspaceId: string;
  name: string;
  file?: File;
}): Promise<Document> {
  return request("POST", "/files", {
    workspace_id: data.workspaceId,
    name: data.name,
  });
}

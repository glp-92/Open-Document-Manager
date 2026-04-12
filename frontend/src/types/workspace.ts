// ── Response models (matching OpenAPI spec) ─────────────────

export interface Workspace {
  id: string;
  name: string;
  created_at: string;
  updated_at: string;
}

export interface Chat {
  id: string;
  workspace_id: string;
  name: string;
  created_at: string;
  updated_at: string;
}

export interface Message {
  id: string;
  chat_id: string;
  owner: "human" | "ai";
  content: string;
  created_at: string;
  updated_at: string;
}

export interface Document {
  id: string;
  worskpace_id: string;
  filename: string;
  url?: string | null;
  size?: number | null;
  mime?: string | null;
  created_at: string;
  updated_at: string;
}

export interface Run {
  id: string;
  workspace_id: string;
  status: "pending" | "completed" | "error" | "deleted";
  created_at: string;
  updated_at?: string | null;
  completed_at?: string | null;
}

export interface UploadDocumentResponse {
  id: string;
  worskpace_id: string;
  filename: string;
  presigned_url: string;
  created_at: string;
}

// ── List wrappers ───────────────────────────────────────────

export interface ListResponse<T> {
  total: number;
  items: T[];
}

// ── Filter types ────────────────────────────────────────────

export interface PaginationParams {
  limit?: number;
  offset?: number;
}

export interface WorkspaceFilters extends PaginationParams {
  name?: string;
}

export interface ChatFilters extends PaginationParams {
  workspace_id?: string;
}

export interface MessageFilters extends PaginationParams {
  chat_id?: string;
}

export interface DocumentFilters extends PaginationParams {
  workspace_id?: string;
}

export interface RunFilters extends PaginationParams {
  workspace_id?: string;
  status?: Run["status"];
}

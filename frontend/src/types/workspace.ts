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
  owner: "HUMAN" | "AI";
  content: string;
  created_at: string;
  updated_at: string;
}

export interface Document {
  id: string;
  workspace_id: string;
  filename: string;
  url?: string | null;
  size?: number | null;
  mime?: string | null;
  storage_status?: "PENDING" | "READY" | "ERROR" | "DELETED";
  created_at: string;
  updated_at: string;
}

export interface DocumentEventPayload {
  event: string;
  event_id: string;
  data: {
    id: string;
    storage_status: "PENDING" | "READY" | "ERROR" | "DELETED";
    workspace_id: string;
  };
}

export interface MessageEventPayload {
  event: string;
  event_id: string;
  data: {
    id: string;
    chat_id: string;
    owner: "HUMAN" | "AI";
    content: string;
    created_at: string;
  };
}

export interface RunEventPayload {
  event: string;
  event_id: string;
  data: {
    id: string;
    status: "PENDING" | "COMPLETED" | "ERROR" | "DELETED";
    workspace_id: string;
  };
}

export interface Run {
  id: string;
  workspace_id: string;
  status: "PENDING" | "COMPLETED" | "ERROR" | "DELETED";
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
  order_by?:
    | "workspace_id"
    | "created_at"
    | "updated_at"
    | "completed_at"
    | "status";
  order?: "asc" | "desc";
}

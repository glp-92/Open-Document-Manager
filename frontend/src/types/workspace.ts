export interface Document {
  id: string;
  name: string;
  status: "processing" | "ready";
  pages?: number;
  workspaceId: string;
  uploadedAt: Date;
}

export interface Citation {
  page: number;
  documentName: string;
}

export interface Message {
  id: string;
  chatId: string;
  role: "user" | "assistant";
  content: string;
  citations?: Citation[];
  timestamp: Date;
}

export interface Chat {
  id: string;
  workspaceId: string;
  title: string;
  createdAt: Date;
}

export interface Workspace {
  id: string;
  name: string;
  createdAt: Date;
}

// API filter types
export interface PaginationParams {
  page?: number;
  limit?: number;
}

export interface WorkspaceFilters extends PaginationParams {
  search?: string;
}

export interface ChatFilters extends PaginationParams {
  workspaceId: string;
}

export interface MessageFilters extends PaginationParams {
  chatId: string;
}

export interface FileFilters extends PaginationParams {
  workspaceId: string;
}

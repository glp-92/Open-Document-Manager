export interface Document {
  id: string;
  name: string;
  status: 'processing' | 'ready';
  pages?: number;
  uploadedAt: Date;
}

export interface Citation {
  page: number;
  documentName: string;
}

export interface Message {
  id: string;
  role: 'user' | 'assistant';
  content: string;
  citations?: Citation[];
  timestamp: Date;
}

export interface Workspace {
  id: string;
  name: string;
  documents: Document[];
  messages: Message[];
  createdAt: Date;
}

import { useState, useCallback } from 'react';
import { Workspace, Message, Document } from '@/types/workspace';

const DEMO_WORKSPACES: Workspace[] = [
  {
    id: '1',
    name: 'Product Research',
    createdAt: new Date('2024-03-01'),
    documents: [
      { id: 'd1', name: 'Market Analysis 2024.pdf', status: 'ready', pages: 42, uploadedAt: new Date('2024-03-01') },
      { id: 'd2', name: 'Competitor Report.pdf', status: 'ready', pages: 18, uploadedAt: new Date('2024-03-02') },
      { id: 'd3', name: 'User Survey Results.pdf', status: 'processing', uploadedAt: new Date('2024-03-10') },
    ],
    messages: [
      { id: 'm1', role: 'user', content: 'What are the key findings from the market analysis?', timestamp: new Date('2024-03-05T10:00:00') },
      {
        id: 'm2', role: 'assistant', timestamp: new Date('2024-03-05T10:00:05'),
        content: 'Based on the Market Analysis 2024, here are the key findings:\n\n1. **Market size** is projected to reach $4.2B by 2025, growing at 12% CAGR.\n2. **Customer segments** are shifting toward enterprise adoption.\n3. The **competitive landscape** shows consolidation among top 5 players.\n\nThe report also highlights emerging opportunities in the Asia-Pacific region, with a projected growth rate of 18%.',
        citations: [
          { page: 12, documentName: 'Market Analysis 2024.pdf' },
          { page: 28, documentName: 'Market Analysis 2024.pdf' },
        ],
      },
      { id: 'm3', role: 'user', content: 'How does our competitor pricing compare?', timestamp: new Date('2024-03-05T10:01:00') },
      {
        id: 'm4', role: 'assistant', timestamp: new Date('2024-03-05T10:01:05'),
        content: 'According to the Competitor Report, pricing varies significantly:\n\n| Competitor | Basic Plan | Enterprise Plan |\n|-----------|-----------|----------------|\n| Acme Corp | $29/mo | $199/mo |\n| Beta Inc | $39/mo | $299/mo |\n| Gamma Ltd | $19/mo | $149/mo |\n\nOur positioning falls in the mid-range, which aligns well with the value proposition outlined in the market analysis.',
        citations: [
          { page: 5, documentName: 'Competitor Report.pdf' },
          { page: 8, documentName: 'Competitor Report.pdf' },
        ],
      },
    ],
  },
  {
    id: '2',
    name: 'Technical Specs',
    createdAt: new Date('2024-03-05'),
    documents: [
      { id: 'd4', name: 'API Documentation v3.pdf', status: 'ready', pages: 156, uploadedAt: new Date('2024-03-05') },
      { id: 'd5', name: 'System Architecture.pdf', status: 'ready', pages: 34, uploadedAt: new Date('2024-03-06') },
    ],
    messages: [],
  },
  {
    id: '3',
    name: 'Legal Review',
    createdAt: new Date('2024-03-10'),
    documents: [],
    messages: [],
  },
];

export function useWorkspaces() {
  const [workspaces, setWorkspaces] = useState<Workspace[]>(DEMO_WORKSPACES);
  const [activeId, setActiveId] = useState<string>('1');

  const activeWorkspace = workspaces.find(w => w.id === activeId) ?? workspaces[0];

  const createWorkspace = useCallback(() => {
    const newWs: Workspace = {
      id: crypto.randomUUID(),
      name: `Workspace ${workspaces.length + 1}`,
      documents: [],
      messages: [],
      createdAt: new Date(),
    };
    setWorkspaces(prev => [newWs, ...prev]);
    setActiveId(newWs.id);
  }, [workspaces.length]);

  const sendMessage = useCallback((content: string) => {
    const userMsg: Message = {
      id: crypto.randomUUID(),
      role: 'user',
      content,
      timestamp: new Date(),
    };

    setWorkspaces(prev => prev.map(w =>
      w.id === activeId ? { ...w, messages: [...w.messages, userMsg] } : w
    ));

    // Simulate assistant response
    setTimeout(() => {
      const assistantMsg: Message = {
        id: crypto.randomUUID(),
        role: 'assistant',
        content: 'I\'ve analyzed your documents and found relevant information. This is a demo response — in a real application, this would contain insights extracted from your uploaded documents.',
        citations: activeWorkspace.documents.filter(d => d.status === 'ready').slice(0, 1).map(d => ({
          page: Math.floor(Math.random() * 20) + 1,
          documentName: d.name,
        })),
        timestamp: new Date(),
      };
      setWorkspaces(prev => prev.map(w =>
        w.id === activeId ? { ...w, messages: [...w.messages, assistantMsg] } : w
      ));
    }, 1500);
  }, [activeId, activeWorkspace]);

  const uploadDocument = useCallback((name: string) => {
    const newDoc: Document = {
      id: crypto.randomUUID(),
      name,
      status: 'processing',
      uploadedAt: new Date(),
    };
    setWorkspaces(prev => prev.map(w =>
      w.id === activeId ? { ...w, documents: [...w.documents, newDoc] } : w
    ));
    // Simulate processing
    setTimeout(() => {
      setWorkspaces(prev => prev.map(w =>
        w.id === activeId
          ? { ...w, documents: w.documents.map(d => d.id === newDoc.id ? { ...d, status: 'ready' as const, pages: Math.floor(Math.random() * 50) + 5 } : d) }
          : w
      ));
    }, 3000);
  }, [activeId]);

  return { workspaces, activeWorkspace, activeId, setActiveId, createWorkspace, sendMessage, uploadDocument };
}

import { FileText } from 'lucide-react';
import { Message } from '@/types/workspace';

interface Props {
  message: Message;
}

export function ChatMessage({ message }: Props) {
  const isUser = message.role === 'user';

  return (
    <div className={`flex ${isUser ? 'justify-end' : 'justify-start'} mb-4`}>
      <div className={`max-w-[85%] ${isUser ? '' : ''}`}>
        <div
          className={`rounded-2xl px-4 py-3 text-sm leading-relaxed ${
            isUser
              ? 'bg-bubble-user text-bubble-user-foreground rounded-br-md'
              : 'bg-bubble-assistant text-bubble-assistant-foreground rounded-bl-md'
          }`}
        >
          <MessageContent content={message.content} />
        </div>

        {/* Citations */}
        {message.citations && message.citations.length > 0 && (
          <div className="flex flex-wrap gap-1.5 mt-2">
            {message.citations.map((c, i) => (
              <span
                key={i}
                className="inline-flex items-center gap-1 text-[11px] px-2 py-1 rounded-md bg-citation text-citation-foreground border border-citation-border"
              >
                <FileText className="w-3 h-3" />
                Page {c.page} — {c.documentName}
              </span>
            ))}
          </div>
        )}
      </div>
    </div>
  );
}

function MessageContent({ content }: { content: string }) {
  // Simple markdown-like rendering
  const lines = content.split('\n');
  const elements: React.ReactNode[] = [];
  let inTable = false;
  let tableRows: string[][] = [];

  const flushTable = () => {
    if (tableRows.length > 0) {
      elements.push(
        <div key={`table-${elements.length}`} className="my-3 overflow-x-auto">
          <table className="w-full text-xs border-collapse">
            <thead>
              <tr>
                {tableRows[0].map((cell, i) => (
                  <th key={i} className="text-left px-3 py-1.5 border-b border-border font-medium text-muted-foreground">
                    {cell.trim()}
                  </th>
                ))}
              </tr>
            </thead>
            <tbody>
              {tableRows.slice(2).map((row, ri) => (
                <tr key={ri}>
                  {row.map((cell, ci) => (
                    <td key={ci} className="px-3 py-1.5 border-b border-border/50">
                      {cell.trim()}
                    </td>
                  ))}
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      );
      tableRows = [];
    }
    inTable = false;
  };

  lines.forEach((line, i) => {
    if (line.startsWith('|')) {
      inTable = true;
      tableRows.push(line.split('|').filter(Boolean));
      return;
    }
    if (inTable) flushTable();

    if (line.trim() === '') {
      elements.push(<div key={i} className="h-2" />);
    } else {
      elements.push(
        <p key={i} dangerouslySetInnerHTML={{
          __html: line
            .replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>')
            .replace(/`(.*?)`/g, '<code class="px-1 py-0.5 rounded bg-border/60 text-xs font-mono">$1</code>')
        }} />
      );
    }
  });
  if (inTable) flushTable();

  return <>{elements}</>;
}

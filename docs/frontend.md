# Frontend

React application providing chat UI with WebSocket streaming.

## Project Structure

```
frontend/
├── src/
│   ├── main.tsx            # App entry point
│   ├── App.tsx             # Root component
│   ├── components/
│   │   ├── Chat.tsx        # Main chat interface
│   │   ├── MessageList.tsx # Message rendering
│   │   ├── MessageInput.tsx # User input
│   │   ├── Message.tsx     # Single message component
│   │   ├── ToolCall.tsx    # Tool execution display
│   │   └── ModelSelector.tsx # Model selection
│   ├── hooks/
│   │   ├── useWebSocket.ts # WebSocket connection
│   │   ├── useAuth.ts      # JWT management
│   │   └── useChat.ts      # Chat state management
│   ├── types/
│   │   └── index.ts        # TypeScript types
│   ├── lib/
│   │   └── utils.ts        # Utility functions
│   └── styles/
│       └── index.css       # Global styles
├── public/
│   └── index.html
├── package.json
├── tsconfig.json
├── vite.config.ts
└── eslint.config.js
```

## Core Components

### App.tsx - Root Component

```typescript
import { useAuth } from "./hooks/useAuth";
import Chat from "./components/Chat";

export default function App() {
  const { user, loading } = useAuth();

  if (loading) {
    return <div>Loading...</div>;
  }

  if (!user) {
    // Redirect to Portal login
    window.location.href = "/login";
    return null;
  }

  return (
    <div className="app">
      <Chat user={user} />
    </div>
  );
}
```

**Responsibilities:**
- Check authentication status
- Redirect to login if needed
- Render chat interface

### Chat.tsx - Main Interface

```typescript
import { useState } from "react";
import { useWebSocket } from "../hooks/useWebSocket";
import { useChat } from "../hooks/useChat";
import MessageList from "./MessageList";
import MessageInput from "./MessageInput";
import ModelSelector from "./ModelSelector";
import type { User } from "../types";

interface ChatProps {
  user: User;
}

export default function Chat({ user }: ChatProps) {
  const { messages, addMessage, updateLastMessage } = useChat();
  const { sendMessage, connected } = useWebSocket({
    onMessage: (chunk) => {
      if (chunk.type === "content") {
        updateLastMessage(chunk.text);
      } else if (chunk.type === "tool_call") {
        addMessage({
          role: "tool",
          content: `Executing: ${chunk.tool}`,
          toolCall: chunk
        });
      } else if (chunk.type === "tool_result") {
        updateLastMessage(`Result: ${chunk.result}`);
      }
    }
  });

  const [input, setInput] = useState("");

  const handleSend = () => {
    if (!input.trim()) return;
    
    // Add user message
    addMessage({
      role: "user",
      content: input
    });
    
    // Add placeholder for assistant response
    addMessage({
      role: "assistant",
      content: ""
    });
    
    // Send to backend
    sendMessage(input);
    setInput("");
  };

  return (
    <div className="chat-container">
      <header className="chat-header">
        <h1>Faceplate</h1>
        <ModelSelector />
        <div className="connection-status">
          {connected ? "🟢" : "🔴"}
        </div>
      </header>
      
      <MessageList messages={messages} />
      
      <MessageInput
        value={input}
        onChange={setInput}
        onSend={handleSend}
        disabled={!connected}
      />
    </div>
  );
}
```

**Features:**
- WebSocket connection management
- Message state handling
- Streaming response updates
- Tool call visualization

### MessageList.tsx - Message Rendering

```typescript
import { useEffect, useRef } from "react";
import Message from "./Message";
import type { ChatMessage } from "../types";

interface MessageListProps {
  messages: ChatMessage[];
}

export default function MessageList({ messages }: MessageListProps) {
  const bottomRef = useRef<HTMLDivElement>(null);

  // Auto-scroll to bottom on new messages
  useEffect(() => {
    bottomRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [messages]);

  return (
    <div className="message-list">
      {messages.map((message, index) => (
        <Message key={index} message={message} />
      ))}
      <div ref={bottomRef} />
    </div>
  );
}
```

**Features:**
- Auto-scroll to latest message
- Virtualization for long conversations (future)

### Message.tsx - Single Message

```typescript
import ToolCall from "./ToolCall";
import type { ChatMessage } from "../types";

interface MessageProps {
  message: ChatMessage;
}

export default function Message({ message }: MessageProps) {
  const isUser = message.role === "user";
  
  return (
    <div className={`message ${message.role}`}>
      <div className="message-avatar">
        {isUser ? "👤" : "🤖"}
      </div>
      
      <div className="message-content">
        {message.toolCall ? (
          <ToolCall toolCall={message.toolCall} />
        ) : (
          <div className="message-text">
            {message.content}
          </div>
        )}
        
        <div className="message-timestamp">
          {new Date(message.timestamp).toLocaleTimeString()}
        </div>
      </div>
    </div>
  );
}
```

**Styling:**
- User messages right-aligned, blue background
- Assistant messages left-aligned, gray background
- Tool calls with special formatting

### ToolCall.tsx - Tool Execution Display

```typescript
import type { ToolCallData } from "../types";

interface ToolCallProps {
  toolCall: ToolCallData;
}

export default function ToolCall({ toolCall }: ToolCallProps) {
  return (
    <div className="tool-call">
      <div className="tool-call-header">
        🔧 {toolCall.tool}
      </div>
      
      <div className="tool-call-args">
        <code>{JSON.stringify(toolCall.arguments, null, 2)}</code>
      </div>
      
      {toolCall.result && (
        <div className="tool-call-result">
          <strong>Result:</strong>
          <pre>{toolCall.result}</pre>
        </div>
      )}
    </div>
  );
}
```

**Features:**
- Collapsible arguments/results (future)
- Syntax highlighting for code (future)

### MessageInput.tsx - User Input

```typescript
import { KeyboardEvent } from "react";

interface MessageInputProps {
  value: string;
  onChange: (value: string) => void;
  onSend: () => void;
  disabled: boolean;
}

export default function MessageInput({
  value,
  onChange,
  onSend,
  disabled
}: MessageInputProps) {
  const handleKeyDown = (e: KeyboardEvent<HTMLTextAreaElement>) => {
    if (e.key === "Enter" && !e.shiftKey) {
      e.preventDefault();
      onSend();
    }
  };

  return (
    <div className="message-input-container">
      <textarea
        value={value}
        onChange={(e) => onChange(e.target.value)}
        onKeyDown={handleKeyDown}
        placeholder="Type your message..."
        disabled={disabled}
        rows={3}
      />
      
      <button
        onClick={onSend}
        disabled={disabled || !value.trim()}
      >
        Send
      </button>
    </div>
  );
}
```

**Features:**
- Multi-line input with textarea
- Enter to send, Shift+Enter for newline
- Disabled when disconnected

### ModelSelector.tsx - Model Selection

```typescript
import { useState } from "react";

const MODELS = [
  { id: "claude-3-5-sonnet", name: "Claude 3.5 Sonnet" },
  { id: "claude-3-haiku", name: "Claude 3 Haiku" },
];

export default function ModelSelector() {
  const [model, setModel] = useState(MODELS[0].id);

  return (
    <select
      value={model}
      onChange={(e) => setModel(e.target.value)}
      className="model-selector"
    >
      {MODELS.map((m) => (
        <option key={m.id} value={m.id}>
          {m.name}
        </option>
      ))}
    </select>
  );
}
```

**Future:**
- Save model preference to localStorage
- Send model selection to backend

## Custom Hooks

### useWebSocket.ts - WebSocket Connection

```typescript
import { useEffect, useRef, useState } from "react";
import type { WebSocketChunk } from "../types";

interface UseWebSocketOptions {
  onMessage: (chunk: WebSocketChunk) => void;
}

export function useWebSocket({ onMessage }: UseWebSocketOptions) {
  const [connected, setConnected] = useState(false);
  const wsRef = useRef<WebSocket | null>(null);

  useEffect(() => {
    // Get JWT from cookie
    const token = document.cookie
      .split("; ")
      .find((row) => row.startsWith("jwt="))
      ?.split("=")[1];

    if (!token) {
      console.error("No JWT token found");
      return;
    }

    // Connect WebSocket
    const protocol = window.location.protocol === "https:" ? "wss:" : "ws:";
    const ws = new WebSocket(`${protocol}//${window.location.host}/ws/chat`);
    
    // Set Authorization header (non-standard, but works with FastAPI)
    ws.onopen = () => {
      // Send auth message
      ws.send(JSON.stringify({
        type: "auth",
        token: token
      }));
      setConnected(true);
    };

    ws.onmessage = (event) => {
      const chunk = JSON.parse(event.data);
      onMessage(chunk);
    };

    ws.onerror = (error) => {
      console.error("WebSocket error:", error);
      setConnected(false);
    };

    ws.onclose = () => {
      setConnected(false);
      
      // Reconnect after 3 seconds
      setTimeout(() => {
        window.location.reload();
      }, 3000);
    };

    wsRef.current = ws;

    return () => {
      ws.close();
    };
  }, [onMessage]);

  const sendMessage = (message: string) => {
    if (wsRef.current?.readyState === WebSocket.OPEN) {
      wsRef.current.send(JSON.stringify({ message }));
    }
  };

  return { sendMessage, connected };
}
```

**Features:**
- Automatic reconnection on disconnect
- JWT auth from cookie
- Message streaming

### useAuth.ts - Authentication

```typescript
import { useState, useEffect } from "react";
import type { User } from "../types";

export function useAuth() {
  const [user, setUser] = useState<User | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    // Parse JWT from cookie
    const token = document.cookie
      .split("; ")
      .find((row) => row.startsWith("jwt="))
      ?.split("=")[1];

    if (!token) {
      setLoading(false);
      return;
    }

    // Decode JWT payload (not validating, backend does that)
    try {
      const payload = JSON.parse(atob(token.split(".")[1]));
      setUser({
        email: payload.email,
        sub: payload.sub
      });
    } catch (error) {
      console.error("Failed to parse JWT:", error);
    }

    setLoading(false);
  }, []);

  return { user, loading };
}
```

**Features:**
- JWT parsing from cookie
- No validation (backend validates)
- Simple user state

### useChat.ts - Chat State

```typescript
import { useState, useCallback } from "react";
import type { ChatMessage } from "../types";

export function useChat() {
  const [messages, setMessages] = useState<ChatMessage[]>([]);

  const addMessage = useCallback((message: Omit<ChatMessage, "timestamp">) => {
    setMessages((prev) => [
      ...prev,
      {
        ...message,
        timestamp: Date.now()
      }
    ]);
  }, []);

  const updateLastMessage = useCallback((content: string) => {
    setMessages((prev) => {
      const last = prev[prev.length - 1];
      if (!last) return prev;
      
      return [
        ...prev.slice(0, -1),
        {
          ...last,
          content: last.content + content
        }
      ];
    });
  }, []);

  const clearMessages = useCallback(() => {
    setMessages([]);
  }, []);

  return {
    messages,
    addMessage,
    updateLastMessage,
    clearMessages
  };
}
```

**Features:**
- Message array management
- Streaming content updates
- Clear history

## TypeScript Types

### types/index.ts

```typescript
export interface User {
  email: string;
  sub: string;
}

export interface ChatMessage {
  role: "user" | "assistant" | "tool";
  content: string;
  timestamp: number;
  toolCall?: ToolCallData;
}

export interface ToolCallData {
  tool: string;
  arguments: Record<string, unknown>;
  result?: string;
}

export interface WebSocketChunk {
  type: "content" | "tool_call" | "tool_result" | "done" | "error";
  text?: string;
  tool?: string;
  arguments?: Record<string, unknown>;
  result?: unknown;
  message?: string;
}
```

## Styling

### index.css - Global Styles

```css
:root {
  --bg-primary: #0a0e27;
  --bg-secondary: #1a1f3a;
  --text-primary: #e0e0e0;
  --text-secondary: #a0a0a0;
  --accent: #00d9ff;
  --user-msg: #1e3a8a;
  --assistant-msg: #2a2a3a;
}

* {
  margin: 0;
  padding: 0;
  box-sizing: border-box;
}

body {
  font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif;
  background: var(--bg-primary);
  color: var(--text-primary);
}

.app {
  height: 100vh;
  display: flex;
  flex-direction: column;
}

.chat-container {
  flex: 1;
  display: flex;
  flex-direction: column;
  max-width: 1200px;
  margin: 0 auto;
  width: 100%;
}

.chat-header {
  padding: 1rem;
  background: var(--bg-secondary);
  display: flex;
  align-items: center;
  gap: 1rem;
  border-bottom: 1px solid rgba(255, 255, 255, 0.1);
}

.message-list {
  flex: 1;
  overflow-y: auto;
  padding: 1rem;
  display: flex;
  flex-direction: column;
  gap: 1rem;
}

.message {
  display: flex;
  gap: 0.5rem;
  max-width: 80%;
}

.message.user {
  align-self: flex-end;
  flex-direction: row-reverse;
}

.message-avatar {
  width: 40px;
  height: 40px;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 1.5rem;
  flex-shrink: 0;
}

.message-content {
  flex: 1;
  padding: 0.75rem 1rem;
  border-radius: 8px;
}

.message.user .message-content {
  background: var(--user-msg);
}

.message.assistant .message-content {
  background: var(--assistant-msg);
}

.message-text {
  line-height: 1.5;
  white-space: pre-wrap;
}

.message-timestamp {
  font-size: 0.75rem;
  color: var(--text-secondary);
  margin-top: 0.25rem;
}

.tool-call {
  border: 1px solid var(--accent);
  border-radius: 4px;
  padding: 0.5rem;
  background: rgba(0, 217, 255, 0.05);
}

.tool-call-header {
  font-weight: bold;
  margin-bottom: 0.5rem;
}

.tool-call-args code {
  display: block;
  background: rgba(0, 0, 0, 0.3);
  padding: 0.5rem;
  border-radius: 4px;
  font-size: 0.875rem;
  overflow-x: auto;
}

.tool-call-result pre {
  background: rgba(0, 0, 0, 0.3);
  padding: 0.5rem;
  border-radius: 4px;
  margin-top: 0.5rem;
  overflow-x: auto;
}

.message-input-container {
  padding: 1rem;
  background: var(--bg-secondary);
  border-top: 1px solid rgba(255, 255, 255, 0.1);
  display: flex;
  gap: 0.5rem;
}

textarea {
  flex: 1;
  padding: 0.75rem;
  background: var(--bg-primary);
  color: var(--text-primary);
  border: 1px solid rgba(255, 255, 255, 0.2);
  border-radius: 4px;
  resize: none;
  font-family: inherit;
  font-size: 1rem;
}

button {
  padding: 0.75rem 1.5rem;
  background: var(--accent);
  color: var(--bg-primary);
  border: none;
  border-radius: 4px;
  font-weight: bold;
  cursor: pointer;
  transition: opacity 0.2s;
}

button:hover:not(:disabled) {
  opacity: 0.8;
}

button:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

.model-selector {
  padding: 0.5rem;
  background: var(--bg-primary);
  color: var(--text-primary);
  border: 1px solid rgba(255, 255, 255, 0.2);
  border-radius: 4px;
}

.connection-status {
  margin-left: auto;
  font-size: 1.5rem;
}
```

**Design:**
- Dark theme matching Shifter cyberpunk aesthetic
- Responsive layout
- Clean, minimal UI

## Build Configuration

### vite.config.ts

```typescript
import { defineConfig } from "vite";
import react from "@vitejs/plugin-react";

export default defineConfig({
  plugins: [react()],
  build: {
    outDir: "dist",
    sourcemap: true
  },
  server: {
    proxy: {
      "/ws": {
        target: "ws://localhost:8000",
        ws: true
      }
    }
  }
});
```

### tsconfig.json

```json
{
  "compilerOptions": {
    "target": "ES2020",
    "useDefineForClassFields": true,
    "lib": ["ES2020", "DOM", "DOM.Iterable"],
    "module": "ESNext",
    "skipLibCheck": true,
    "moduleResolution": "bundler",
    "allowImportingTsExtensions": true,
    "resolveJsonModule": true,
    "isolatedModules": true,
    "noEmit": true,
    "jsx": "react-jsx",
    "strict": true,
    "noUnusedLocals": true,
    "noUnusedParameters": true,
    "noFallthroughCasesInSwitch": true
  },
  "include": ["src"],
  "references": [{ "path": "./tsconfig.node.json" }]
}
```

### eslint.config.js

```javascript
import js from "@eslint/js";
import globals from "globals";
import reactHooks from "eslint-plugin-react-hooks";
import reactRefresh from "eslint-plugin-react-refresh";
import tseslint from "typescript-eslint";

export default tseslint.config(
  { ignores: ["dist"] },
  {
    extends: [js.configs.recommended, ...tseslint.configs.recommended],
    files: ["**/*.{ts,tsx}"],
    languageOptions: {
      ecmaVersion: 2020,
      globals: globals.browser,
    },
    plugins: {
      "react-hooks": reactHooks,
      "react-refresh": reactRefresh,
    },
    rules: {
      ...reactHooks.configs.recommended.rules,
      "react-refresh/only-export-components": [
        "warn",
        { allowConstantExport: true },
      ],
    },
  }
);
```

## Dependencies

### package.json

```json
{
  "name": "faceplate-frontend",
  "version": "0.1.0",
  "type": "module",
  "scripts": {
    "dev": "vite",
    "build": "tsc && vite build",
    "preview": "vite preview",
    "lint": "eslint . --ext ts,tsx",
    "lint:fix": "eslint . --ext ts,tsx --fix",
    "format": "prettier --write src/**/*.{ts,tsx}",
    "format:check": "prettier --check src/**/*.{ts,tsx}"
  },
  "dependencies": {
    "react": "^18.3.1",
    "react-dom": "^18.3.1"
  },
  "devDependencies": {
    "@eslint/js": "^9.15.0",
    "@types/react": "^18.3.12",
    "@types/react-dom": "^18.3.1",
    "@vitejs/plugin-react": "^4.3.4",
    "eslint": "^9.15.0",
    "eslint-plugin-react-hooks": "^5.0.0",
    "eslint-plugin-react-refresh": "^0.4.14",
    "globals": "^15.12.0",
    "prettier": "^3.4.2",
    "typescript": "^5.6.3",
    "typescript-eslint": "^8.15.0",
    "vite": "^6.0.1"
  }
}
```

## Development

### Local Development

```bash
# Install dependencies
npm install

# Start dev server with hot reload
npm run dev

# Open http://localhost:5173
```

### Building for Production

```bash
# Build static files
npm run build

# Output: dist/
# - index.html
# - assets/index-[hash].js
# - assets/index-[hash].css
```

### Linting and Formatting

```bash
# Check linting
npm run lint

# Fix linting issues
npm run lint:fix

# Check formatting
npm run format:check

# Format code
npm run format
```

## Testing (Future)

### Vitest Setup

```typescript
// vite.config.ts
import { defineConfig } from "vitest/config";
import react from "@vitejs/plugin-react";

export default defineConfig({
  plugins: [react()],
  test: {
    globals: true,
    environment: "jsdom",
    setupFiles: "./src/test/setup.ts"
  }
});
```

### Example Tests

```typescript
// src/components/Message.test.tsx
import { render, screen } from "@testing-library/react";
import Message from "./Message";

describe("Message", () => {
  it("renders user message", () => {
    render(
      <Message
        message={{
          role: "user",
          content: "Hello",
          timestamp: Date.now()
        }}
      />
    );
    
    expect(screen.getByText("Hello")).toBeInTheDocument();
  });
});
```

## Performance Optimization

### Code Splitting

```typescript
// Lazy load components
const ModelSelector = lazy(() => import("./components/ModelSelector"));

// Use Suspense
<Suspense fallback={<div>Loading...</div>}>
  <ModelSelector />
</Suspense>
```

### Memoization

```typescript
// Memoize expensive renders
const Message = memo(({ message }: MessageProps) => {
  // Component implementation
});

// Memoize callbacks
const handleSend = useCallback(() => {
  // Implementation
}, [dependencies]);
```

### Virtual Scrolling (Future)

For long conversations (>1000 messages), implement virtual scrolling with `react-window`:

```typescript
import { FixedSizeList } from "react-window";

<FixedSizeList
  height={600}
  itemCount={messages.length}
  itemSize={100}
>
  {({ index, style }) => (
    <div style={style}>
      <Message message={messages[index]} />
    </div>
  )}
</FixedSizeList>
```

## Browser Compatibility

- Chrome/Edge: 90+
- Firefox: 88+
- Safari: 14+

**Required Features:**
- WebSocket API
- ES2020 syntax
- CSS Grid/Flexbox


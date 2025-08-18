import React, { useState } from 'react';

interface Message {
  id: string;
  type: 'user' | 'agent' | 'system';
  content: string;
  timestamp: string;
}

interface ChatInterfaceProps {
  onViewChange: (view: string) => void;
}

const ChatInterface: React.FC<ChatInterfaceProps> = ({ onViewChange }) => {
  const [messages, setMessages] = useState<Message[]>([
    {
      id: '1',
      type: 'system',
      content: 'Agent ready. Ask me to help with customer tasks!',
      timestamp: new Date().toISOString()
    }
  ]);
  const [input, setInput] = useState('');
  const [isLoading, setIsLoading] = useState(false);

  const handleSend = async () => {
    if (!input.trim() || isLoading) return;

    const userMessage: Message = {
      id: Date.now().toString(),
      type: 'user',
      content: input.trim(),
      timestamp: new Date().toISOString()
    };

    setMessages(prev => [...prev, userMessage]);
    setInput('');
    setIsLoading(true);

    try {
      const response = await fetch('http://localhost:8000/api/chat', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ message: input.trim() }),
      });

      if (!response.ok) throw new Error('Failed to send message');
      
      const data = await response.json();

      const agentMessage: Message = {
        id: (Date.now() + 1).toString(),
        type: 'agent',
        content: data.response,
        timestamp: new Date().toISOString()
      };

      setMessages(prev => [...prev, agentMessage]);

      // Handle view changes based on agent response
      if (data.view_change) {
        onViewChange(data.view_change);
      }

    } catch (error) {
      const errorMessage: Message = {
        id: (Date.now() + 1).toString(),
        type: 'system',
        content: `Error: ${error instanceof Error ? error.message : 'Unknown error'}`,
        timestamp: new Date().toISOString()
      };
      setMessages(prev => [...prev, errorMessage]);
    } finally {
      setIsLoading(false);
    }
  };

  const handleKeyPress = (e: React.KeyboardEvent) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      handleSend();
    }
  };

  return (
    <div className="bg-white rounded-lg shadow-lg flex flex-col h-96">
      <div className="p-3 border-b bg-gray-50 rounded-t-lg">
        <h3 className="font-semibold text-gray-800">Agent Chat</h3>
        <p className="text-xs text-gray-600">Ask me to help with customer tasks!</p>
      </div>
      
      <div className="flex-1 overflow-y-auto p-3 space-y-3">
        {messages.map(message => (
          <div
            key={message.id}
            className={`flex ${message.type === 'user' ? 'justify-end' : 'justify-start'}`}
          >
            <div
              className={`max-w-xs lg:max-w-md px-3 py-2 rounded-lg text-sm ${
                message.type === 'user'
                  ? 'bg-blue-500 text-white'
                  : message.type === 'agent'
                  ? 'bg-gray-200 text-gray-800'
                  : 'bg-yellow-100 text-yellow-800 border border-yellow-300'
              }`}
            >
              <div>{message.content}</div>
              <div className={`text-xs mt-1 ${
                message.type === 'user' ? 'text-blue-100' : 'text-gray-500'
              }`}>
                {new Date(message.timestamp).toLocaleTimeString()}
              </div>
            </div>
          </div>
        ))}
        {isLoading && (
          <div className="flex justify-start">
            <div className="bg-gray-200 text-gray-800 px-3 py-2 rounded-lg text-sm">
              <div className="flex items-center space-x-1">
                <div className="w-2 h-2 bg-gray-500 rounded-full animate-bounce"></div>
                <div className="w-2 h-2 bg-gray-500 rounded-full animate-bounce" style={{animationDelay: '0.1s'}}></div>
                <div className="w-2 h-2 bg-gray-500 rounded-full animate-bounce" style={{animationDelay: '0.2s'}}></div>
              </div>
            </div>
          </div>
        )}
      </div>
      
      <div className="p-3 border-t">
        <div className="flex space-x-2">
          <input
            type="text"
            value={input}
            onChange={(e) => setInput(e.target.value)}
            onKeyPress={handleKeyPress}
            placeholder="Ask me to help with customers..."
            className="flex-1 px-3 py-2 border rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500 text-sm"
            disabled={isLoading}
          />
          <button
            onClick={handleSend}
            disabled={isLoading || !input.trim()}
            className="px-4 py-2 bg-blue-500 text-white rounded-md hover:bg-blue-600 disabled:opacity-50 disabled:cursor-not-allowed text-sm font-medium"
          >
            Send
          </button>
        </div>
        <div className="mt-2 flex flex-wrap gap-2">
          <button
            onClick={() => setInput("Show me Acme's open tickets")}
            className="px-2 py-1 bg-gray-100 text-gray-700 rounded text-xs hover:bg-gray-200"
          >
            Show Acme tickets
          </button>
          <button
            onClick={() => setInput("Generate a daily summary report")}
            className="px-2 py-1 bg-gray-100 text-gray-700 rounded text-xs hover:bg-gray-200"
          >
            Daily report
          </button>
          <button
            onClick={() => setInput("Show customer analytics")}
            className="px-2 py-1 bg-gray-100 text-gray-700 rounded text-xs hover:bg-gray-200"
          >
            Analytics
          </button>
          <button
            onClick={() => setInput("Find high activity customers")}
            className="px-2 py-1 bg-gray-100 text-gray-700 rounded text-xs hover:bg-gray-200"
          >
            High activity
          </button>
          <button
            onClick={() => setInput("Show customer health report")}
            className="px-2 py-1 bg-gray-100 text-gray-700 rounded text-xs hover:bg-gray-200"
          >
            Health report
          </button>
          <button
            onClick={() => setInput("Close resolved tickets")}
            className="px-2 py-1 bg-gray-100 text-gray-700 rounded text-xs hover:bg-gray-200"
          >
            Close tickets
          </button>
          <button
            onClick={() => setInput("Onboard TechCorp as a new customer")}
            className="px-2 py-1 bg-purple-100 text-purple-700 rounded text-xs hover:bg-purple-200"
          >
            🚀 Onboard Customer
          </button>
          <button
            onClick={() => setInput("Run ticket escalation workflow")}
            className="px-2 py-1 bg-red-100 text-red-700 rounded text-xs hover:bg-red-200"
          >
            🚨 Escalate Tickets
          </button>
          <button
            onClick={() => setInput("Generate weekly business report")}
            className="px-2 py-1 bg-blue-100 text-blue-700 rounded text-xs hover:bg-blue-200"
          >
            📊 Weekly Report
          </button>
          <button
            onClick={() => setInput("Run customer health check workflow")}
            className="px-2 py-1 bg-green-100 text-green-700 rounded text-xs hover:bg-green-200"
          >
            💚 Health Check
          </button>
        </div>
      </div>
    </div>
  );
};

export default ChatInterface;
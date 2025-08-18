import React, { useState, useRef, useEffect } from 'react';
import { motion, AnimatePresence } from 'framer-motion';

interface Message {
  id: string;
  type: 'user' | 'agent' | 'system' | 'tool';
  content: string;
  timestamp: string;
  toolCall?: string;
  isTyping?: boolean;
}

interface ChatInterfaceProps {
  onViewChange: (view: string) => void;
}

const TypingAnimation = ({ text, onComplete }: { text: string; onComplete: () => void }) => {
  const [displayedText, setDisplayedText] = useState('');
  const [isComplete, setIsComplete] = useState(false);

  useEffect(() => {
    if (!text) return;
    
    let i = 0;
    const timer = setInterval(() => {
      if (i < text.length) {
        setDisplayedText(text.slice(0, i + 1));
        i++;
      } else {
        setIsComplete(true);
        clearInterval(timer);
        setTimeout(onComplete, 500);
      }
    }, 30);

    return () => clearInterval(timer);
  }, [text, onComplete]);

  return (
    <span>
      {displayedText}
      {!isComplete && <span className="animate-pulse">|</span>}
    </span>
  );
};

const ChatInterface: React.FC<ChatInterfaceProps> = ({ onViewChange }) => {
  const [messages, setMessages] = useState<Message[]>([
    {
      id: '1',
      type: 'system',
      content: '🤖 Agent ready. Ask me to help with customer tasks!',
      timestamp: new Date().toISOString()
    }
  ]);
  const [input, setInput] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const [toolExecutions, setToolExecutions] = useState<string[]>([]);
  const messagesEndRef = useRef<HTMLDivElement>(null);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages, toolExecutions]);

  const simulateToolExecution = async (tools: string[]) => {
    for (const tool of tools) {
      setToolExecutions(prev => [...prev, tool]);
      await new Promise(resolve => setTimeout(resolve, 800));
    }
  };

  const handleSend = async () => {
    if (!input.trim() || isLoading) return;

    const userMessage: Message = {
      id: Date.now().toString(),
      type: 'user',
      content: input.trim(),
      timestamp: new Date().toISOString()
    };

    setMessages(prev => [...prev, userMessage]);
    const userInput = input.trim();
    setInput('');
    setIsLoading(true);
    setToolExecutions([]);

    // Simulate tool execution visualization
    const mockTools = [
      '🔍 Searching customers...',
      '📊 Analyzing data...',
      '🎯 Switching view...'
    ];
    
    setTimeout(() => simulateToolExecution(mockTools), 500);

    try {
      const response = await fetch('http://localhost:8000/api/chat', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ message: userInput }),
      });

      if (!response.ok) throw new Error('Failed to send message');
      
      const data = await response.json();

      // Clear tool executions
      setToolExecutions([]);

      // Add typing message first
      const typingMessage: Message = {
        id: (Date.now() + 1).toString(),
        type: 'agent',
        content: data.response,
        timestamp: new Date().toISOString(),
        isTyping: true
      };

      setMessages(prev => [...prev, typingMessage]);

      // Handle view changes based on agent response
      if (data.view_change) {
        setTimeout(() => onViewChange(data.view_change), 1000);
      }

    } catch (error) {
      setToolExecutions([]);
      const errorMessage: Message = {
        id: (Date.now() + 1).toString(),
        type: 'system',
        content: `❌ Error: ${error instanceof Error ? error.message : 'Unknown error'}`,
        timestamp: new Date().toISOString()
      };
      setMessages(prev => [...prev, errorMessage]);
    } finally {
      setIsLoading(false);
    }
  };

  const handleTypingComplete = (messageId: string) => {
    setMessages(prev => 
      prev.map(msg => 
        msg.id === messageId ? { ...msg, isTyping: false } : msg
      )
    );
  };

  const handleKeyPress = (e: React.KeyboardEvent) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      handleSend();
    }
  };

  const quickActions = [
    { text: "Show me Acme's open tickets", color: 'blue', icon: '🎫' },
    { text: "Generate a daily summary report", color: 'green', icon: '📊' },
    { text: "Show customer analytics", color: 'purple', icon: '📈' },
    { text: "Find high activity customers", color: 'orange', icon: '🔥' },
    { text: "Show customer health report", color: 'teal', icon: '💚' },
    { text: "Close resolved tickets", color: 'gray', icon: '✅' },
    { text: "Onboard TechCorp as a new customer", color: 'purple', icon: '🚀', special: true },
    { text: "Run ticket escalation workflow", color: 'red', icon: '🚨', special: true },
    { text: "Generate weekly business report", color: 'blue', icon: '📊', special: true },
    { text: "Run customer health check workflow", color: 'green', icon: '💚', special: true }
  ];

  return (
    <motion.div 
      initial={{ opacity: 0, scale: 0.95 }}
      animate={{ opacity: 1, scale: 1 }}
      className="glass-strong flex flex-col h-[600px] glow"
    >
      {/* Header */}
      <div className="p-4 border-b border-white/10">
        <div className="flex items-center space-x-3">
          <div className="w-8 h-8 rounded-full bg-gradient-to-r from-indigo-500 to-purple-600 flex items-center justify-center">
            <span className="text-white text-sm font-bold">AI</span>
          </div>
          <div>
            <h3 className="font-semibold text-white">Agent Assistant</h3>
            <p className="text-xs text-gray-300">Powered by AI • Ready to help</p>
          </div>
          <div className="ml-auto">
            <div className="w-2 h-2 bg-green-400 rounded-full animate-pulse"></div>
          </div>
        </div>
      </div>
      
      {/* Messages */}
      <div className="flex-1 overflow-y-auto p-4 space-y-4">
        <AnimatePresence>
          {messages.map((message, index) => (
            <motion.div
              key={message.id}
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              exit={{ opacity: 0, y: -20 }}
              transition={{ delay: index * 0.1 }}
              className={`flex ${message.type === 'user' ? 'justify-end' : 'justify-start'}`}
            >
              <div
                className={`max-w-[80%] px-4 py-3 rounded-2xl text-sm backdrop-blur-sm ${
                  message.type === 'user'
                    ? 'bg-gradient-to-r from-indigo-500 to-purple-600 text-white'
                    : message.type === 'agent'
                    ? 'bg-white/10 border border-white/20 text-gray-100'
                    : 'bg-amber-500/20 border border-amber-400/30 text-amber-200'
                }`}
              >
                <div className="font-medium">
                  {message.isTyping ? (
                    <TypingAnimation 
                      text={message.content} 
                      onComplete={() => handleTypingComplete(message.id)}
                    />
                  ) : (
                    message.content
                  )}
                </div>
                <div className={`text-xs mt-2 opacity-70 ${
                  message.type === 'user' ? 'text-white' : 'text-gray-300'
                }`}>
                  {new Date(message.timestamp).toLocaleTimeString()}
                </div>
              </div>
            </motion.div>
          ))}
        </AnimatePresence>

        {/* Tool Execution Visualization */}
        <AnimatePresence>
          {toolExecutions.map((tool, index) => (
            <motion.div
              key={`tool-${index}`}
              initial={{ opacity: 0, x: -20 }}
              animate={{ opacity: 1, x: 0 }}
              exit={{ opacity: 0, x: 20 }}
              className="flex justify-start"
            >
              <div className="bg-blue-500/20 border border-blue-400/30 px-4 py-2 rounded-xl text-sm text-blue-300 flex items-center space-x-2">
                <div className="w-2 h-2 bg-blue-400 rounded-full animate-pulse"></div>
                <span>{tool}</span>
              </div>
            </motion.div>
          ))}
        </AnimatePresence>

        {/* Loading indicator */}
        {isLoading && toolExecutions.length === 0 && (
          <motion.div
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            className="flex justify-start"
          >
            <div className="bg-white/10 border border-white/20 px-4 py-3 rounded-2xl text-sm">
              <div className="flex items-center space-x-2">
                <div className="flex space-x-1">
                  <div className="w-2 h-2 bg-gray-400 rounded-full animate-bounce"></div>
                  <div className="w-2 h-2 bg-gray-400 rounded-full animate-bounce" style={{animationDelay: '0.1s'}}></div>
                  <div className="w-2 h-2 bg-gray-400 rounded-full animate-bounce" style={{animationDelay: '0.2s'}}></div>
                </div>
                <span className="text-gray-300">Agent thinking...</span>
              </div>
            </div>
          </motion.div>
        )}
        <div ref={messagesEndRef} />
      </div>
      
      {/* Input Area */}
      <div className="p-4 border-t border-white/10">
        <div className="flex space-x-3 mb-3">
          <input
            type="text"
            value={input}
            onChange={(e) => setInput(e.target.value)}
            onKeyPress={handleKeyPress}
            placeholder="Ask me to help with customers..."
            className="flex-1 px-4 py-3 bg-white/5 border border-white/20 rounded-xl focus:outline-none focus:ring-2 focus:ring-indigo-500 focus:border-transparent text-sm text-white placeholder-gray-400 backdrop-blur-sm"
            disabled={isLoading}
          />
          <motion.button
            whileHover={{ scale: 1.05 }}
            whileTap={{ scale: 0.95 }}
            onClick={handleSend}
            disabled={isLoading || !input.trim()}
            className="px-6 py-3 bg-gradient-to-r from-indigo-500 to-purple-600 text-white rounded-xl hover:from-indigo-600 hover:to-purple-700 disabled:opacity-50 disabled:cursor-not-allowed text-sm font-medium btn-glow transition-all duration-200"
          >
            {isLoading ? '⚡' : '→'}
          </motion.button>
        </div>
        
        {/* Quick Actions */}
        <div className="flex flex-wrap gap-2 max-h-24 overflow-y-auto">
          {quickActions.map((action, index) => (
            <motion.button
              key={index}
              initial={{ opacity: 0, scale: 0.9 }}
              animate={{ opacity: 1, scale: 1 }}
              transition={{ delay: index * 0.05 }}
              whileHover={{ scale: 1.05 }}
              whileTap={{ scale: 0.95 }}
              onClick={() => setInput(action.text)}
              className={`px-3 py-1.5 rounded-lg text-xs transition-all duration-200 ${
                action.special 
                  ? 'bg-gradient-to-r from-purple-500/20 to-pink-500/20 border border-purple-400/30 text-purple-300 hover:from-purple-500/30 hover:to-pink-500/30'
                  : 'bg-white/5 border border-white/20 text-gray-300 hover:bg-white/10'
              } backdrop-blur-sm`}
            >
              <span className="mr-1">{action.icon}</span>
              {action.text.length > 20 ? action.text.substring(0, 20) + '...' : action.text}
            </motion.button>
          ))}
        </div>
      </div>
    </motion.div>
  );
};

export default ChatInterface;
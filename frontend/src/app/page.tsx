"use client";
import React, { useState, useEffect, useRef } from 'react';
import { Send, Bot, User, AlertCircle, CheckCircle2, Loader2 } from 'lucide-react';
import Link from 'next/link';

interface Message {
  role: 'user' | 'assistant';
  content: string;
  timestamp: Date;
}

interface ChatResponse {
  session_id: string;
  response: string;
  is_escalated: boolean;
  status: 'active' | 'escalated';
  summary: string | null;
}

const API_BASE_URL = 'http://localhost:8000';

// Component to render markdown-style text
const MarkdownText = ({ text }: { text: string }) => {
  const renderText = (input: string) => {
    const parts: React.ReactNode[] = [];
    let lastIndex = 0;
    
    // Regex to match **text** or *text* for bold
    const boldRegex = /\*\*([^*]+)\*\*|\*([^*]+)\*/g; // This is tightly coupled with Gemini 1.5's markdown style
    let match;
    
    while ((match = boldRegex.exec(input)) !== null) {
      // Add text before the match
      if (match.index > lastIndex) {
        parts.push(input.substring(lastIndex, match.index));
      }
      
      // Add bold text (either **text** or *text*)
      const boldText = match[1] || match[2];
      parts.push(
        <strong key={match.index} className="font-bold">
          {boldText}
        </strong>
      );
      
      lastIndex = match.index + match[0].length;
    }
    
    // Add remaining text
    if (lastIndex < input.length) {
      parts.push(input.substring(lastIndex));
    }
    
    return parts.length > 0 ? parts : input;
  };

  const lines = text.split('\n');
  
  return (
    <div className="space-y-2">
      {lines.map((line, idx) => {
        // Check if line is a bullet point
        if (line.trim().startsWith('*') || line.trim().startsWith('-')) {
          const bulletText = line.replace(/^[\s]*[*-][\s]*/, '');
          return (
            <div key={idx} className="flex gap-2 items-start">
              <span className="text-indigo-600 font-bold mt-0.5">•</span>
              <span className="flex-1">{renderText(bulletText)}</span>
            </div>
          );
        }
        
        // Check if line is numbered list
        const numberedMatch = line.match(/^[\s]*(\d+)\.[\s]*(.*)/);
        if (numberedMatch) {
          return (
            <div key={idx} className="flex gap-2 items-start">
              <span className="text-indigo-600 font-bold">{numberedMatch[1]}.</span>
              <span className="flex-1">{renderText(numberedMatch[2])}</span>
            </div>
          );
        }
        
        // Regular line
        if (line.trim()) {
          return <div key={idx}>{renderText(line)}</div>;
        }
        
        // Empty line for spacing
        return <div key={idx} className="h-2" />;
      })}
    </div>
  );
};

export default function ChatInterface() {
  const [messages, setMessages] = useState<Message[]>([]);
  const [inputMessage, setInputMessage] = useState('');
  const [sessionId, setSessionId] = useState<string | null>(null);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [isEscalated, setIsEscalated] = useState(false);
  const messagesEndRef = useRef<HTMLDivElement>(null);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  const sendMessage = async () => {
    if (!inputMessage.trim() || isLoading) return;

    const userMessage = inputMessage.trim();
    setInputMessage('');
    setError(null);

    const newUserMessage: Message = {
      role: 'user',
      content: userMessage,
      timestamp: new Date()
    };
    setMessages(prev => [...prev, newUserMessage]);
    setIsLoading(true);

    try {
      const requestBody: any = {
        user_message: userMessage
      };

      if (sessionId) {
        requestBody.session_id = sessionId;
      }

      const response = await fetch(`${API_BASE_URL}/api/chat`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(requestBody)
      });

      if (!response.ok) {
        if (response.status === 404) {
          throw new Error('Session not found. Starting a new conversation.');
        } else if (response.status === 500) {
          const errorData = await response.json();
          throw new Error(errorData.detail || 'Server error occurred');
        } else {
          throw new Error(`Request failed with status ${response.status}`);
        }
      }

      const data: ChatResponse = await response.json();

      if (!sessionId && data.session_id) {
        setSessionId(data.session_id);
      }

      if (data.is_escalated) {
        setIsEscalated(true);
      }

      const botMessage: Message = {
        role: 'assistant',
        content: data.response,
        timestamp: new Date()
      };
      setMessages(prev => [...prev, botMessage]);

    } catch (err) {
      const errorMessage = err instanceof Error ? err.message : 'Failed to send message';
      setError(errorMessage);
      
      const errorBotMessage: Message = {
        role: 'assistant',
        content: `Sorry, I encountered an error: ${errorMessage}. Please try again.`,
        timestamp: new Date()
      };
      setMessages(prev => [...prev, errorBotMessage]);
    } finally {
      setIsLoading(false);
    }
  };

  const handleKeyPress = (e: React.KeyboardEvent<HTMLInputElement>) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      sendMessage();
    }
  };

  const resetChat = () => {
    setMessages([]);
    setSessionId(null);
    setIsEscalated(false);
    setError(null);
    setInputMessage('');
  };

  return (
    <div className="flex flex-col h-screen bg-gradient-to-br from-blue-50 to-indigo-100">
      <div className="bg-white shadow-md border-b border-gray-200">
        <div className="max-w-4xl mx-auto px-4 py-4 flex items-center justify-between">
          <div className="flex items-center gap-3">
            <div className="bg-indigo-600 p-2 rounded-lg">
              <Bot className="w-6 h-6 text-white" />
            </div>
            <div>
              <h1 className="text-xl font-bold text-gray-900">AI Customer Support</h1>
              <p className="text-sm text-gray-600">
                {isEscalated ? (
                  <span className="flex items-center gap-1 text-orange-600">
                    <AlertCircle className="w-4 h-4" />
                    Escalated to agent
                  </span>
                ) : (
                  <span className="flex items-center gap-1 text-green-600">
                    <CheckCircle2 className="w-4 h-4" />
                    Online
                  </span>
                )}
              </p>
            </div>
          </div>
          <div className='flex gap-4'>

          <button
            onClick={resetChat}
            className=" py-2 text-sm font-medium text-indigo-600 hover:bg-indigo-50 rounded-lg transition-colors"
            >
            New Chat
          </button>
          <Link
            href="/manage"
            // onClick={resetChat}
            className="py-2 text-sm font-medium text-indigo-600 hover:bg-indigo-50 rounded-lg transition-colors"
            >
            Manage
          </Link>
            </div>
        </div>
      </div>

      <div className="flex-1 overflow-y-auto">
        <div className="max-w-4xl mx-auto px-4 py-6">
          {messages.length === 0 && (
            <div className="text-center py-12">
              <div className="bg-white rounded-full p-4 w-16 h-16 mx-auto mb-4 shadow-lg">
                <Bot className="w-8 h-8 text-indigo-600" />
              </div>
              <h2 className="text-2xl font-semibold text-gray-900 mb-2">
                Welcome to AI Support
              </h2>
              <p className="text-gray-600 mb-8">
                Ask me anything about our products, services, or policies.
              </p>
              <div className="grid grid-cols-1 md:grid-cols-2 gap-3 max-w-2xl mx-auto">
                {[
                  'What are your business hours?',
                  'How can I track my order?',
                  'What is your return policy?',
                  'How do I contact support?'
                ].map((suggestion, idx) => (
                  <button
                    key={idx}
                    onClick={() => setInputMessage(suggestion)}
                    className="px-4 py-3 bg-white hover:bg-indigo-50 border border-gray-200 hover:border-indigo-300 rounded-lg text-left text-sm text-gray-700 hover:text-indigo-600 transition-all shadow-sm"
                  >
                    {suggestion}
                  </button>
                ))}
              </div>
            </div>
          )}

          {messages.map((message, idx) => (
            <div
              key={idx}
              className={`flex gap-3 mb-4 ${
                message.role === 'user' ? 'justify-end' : 'justify-start'
              }`}
            >
              {message.role === 'assistant' && (
                <div className="flex-shrink-0 w-8 h-8 bg-indigo-600 rounded-full flex items-center justify-center">
                  <Bot className="w-5 h-5 text-white" />
                </div>
              )}
              
              <div
                className={`max-w-xl px-4 py-3 rounded-2xl shadow-sm ${
                  message.role === 'user'
                    ? 'bg-indigo-600 text-white'
                    : 'bg-white text-gray-900 border border-gray-200'
                }`}
              >
                <div className="text-sm leading-relaxed">
                  {message.role === 'assistant' ? (
                    <MarkdownText text={message.content} />
                  ) : (
                    <p className="whitespace-pre-wrap">{message.content}</p>
                  )}
                </div>
                <span className={`text-xs mt-2 block ${
                  message.role === 'user' ? 'text-indigo-200' : 'text-gray-500'
                }`}>'
                  {message.timestamp.toLocaleTimeString([], { 
                    hour: '2-digit', 
                    minute: '2-digit' 
                  })}
                </span>
              </div>

              {message.role === 'user' && (
                <div className="flex-shrink-0 w-8 h-8 bg-gray-700 rounded-full flex items-center justify-center">
                  <User className="w-5 h-5 text-white" />
                </div>
              )}
            </div>
          ))}

          {isLoading && (
            <div className="flex gap-3 mb-4">
              <div className="flex-shrink-0 w-8 h-8 bg-indigo-600 rounded-full flex items-center justify-center">
                <Bot className="w-5 h-5 text-white" />
              </div>
              <div className="bg-white px-4 py-3 rounded-2xl shadow-sm border border-gray-200">
                <div className="flex items-center gap-2">
                  <Loader2 className="w-4 h-4 text-indigo-600 animate-spin" />
                  <span className="text-sm text-gray-600">Typing...</span>
                </div>
              </div>
            </div>
          )}

          {error && (
            <div className="bg-red-50 border border-red-200 rounded-lg p-4 mb-4">
              <div className="flex items-start gap-2">
                <AlertCircle className="w-5 h-5 text-red-600 flex-shrink-0 mt-0.5" />
                <div>
                  <p className="text-sm font-medium text-red-800">Error</p>
                  <p className="text-sm text-red-700">{error}</p>
                </div>
              </div>
            </div>
          )}

          <div ref={messagesEndRef} />
        </div>
      </div>

      <div className="bg-white border-t border-gray-200 shadow-lg">
        <div className="max-w-4xl mx-auto px-4 py-4">
          {isEscalated && (
            <div className="mb-3 bg-orange-50 border border-orange-200 rounded-lg p-3">
              <div className="flex items-center gap-2">
                <AlertCircle className="w-4 h-4 text-orange-600" />
                <p className="text-sm text-orange-800">
                  Your query has been escalated to a human agent. They will assist you shortly.
                </p>
              </div>
            </div>
          )}
          
          <div className="flex gap-2">
            <input
              type="text"
              value={inputMessage}
              onChange={(e) => setInputMessage(e.target.value)}
              onKeyPress={handleKeyPress}
              placeholder="Type your message..."
              disabled={isLoading}
              className="flex-1 px-4 py-3 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-indigo-500 focus:border-transparent disabled:bg-gray-100 disabled:cursor-not-allowed text-gray-900 placeholder-gray-500"
            />
            <button
              onClick={sendMessage}
              disabled={isLoading || !inputMessage.trim()}
              className="px-6 py-3 bg-indigo-600 text-white rounded-lg hover:bg-indigo-700 disabled:bg-gray-400 disabled:cursor-not-allowed transition-colors flex items-center gap-2 font-medium"
            >
              <Send className="w-5 h-5" />
              Send
            </button>
          </div>
          
          {sessionId && (
            <p className="text-xs text-gray-500 mt-2">
              Session: {sessionId.substring(0, 8)}...
            </p>
          )}
        </div>
      </div>
    </div>
  );
}
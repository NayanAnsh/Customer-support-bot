"use client";
import React, { useState, useEffect } from 'react';
import { 
  Search, 
  MessageSquare, 
  Clock, 
  AlertTriangle, 
  CheckCircle, 
  RefreshCw, 
  Eye,
  X,
  Filter,
  TrendingUp,
  Users,
  Activity
} from 'lucide-react';

interface Message {
  role: 'user' | 'assistant';
  content: string;
  timestamp?: string;
}

interface Conversation {
  session_id: string;
  status: 'active' | 'escalated';
  created_at: string;
  updated_at: string;
  message_count: number;
  is_escalated: boolean;
  summary?: string | null;
}

interface ConversationDetail {
  session_id: string;
  status: string;
  created_at: string;
  updated_at: string;
  history: Message[];
}

const API_BASE_URL = 'http://localhost:8000';

const MarkdownText = ({ text }: { text: string }) => {
  const renderText = (input: string) => {
    const parts: React.ReactNode[] = [];
    let lastIndex = 0;
    const boldRegex = /\*\*([^*]+)\*\*|\*([^*]+)\*/g;
    let match;
    
    while ((match = boldRegex.exec(input)) !== null) {
      if (match.index > lastIndex) {
        parts.push(input.substring(lastIndex, match.index));
      }
      const boldText = match[1] || match[2];
      parts.push(
        <strong key={match.index} className="font-bold">
          {boldText}
        </strong>
      );
      lastIndex = match.index + match[0].length;
    }
    
    if (lastIndex < input.length) {
      parts.push(input.substring(lastIndex));
    }
    
    return parts.length > 0 ? parts : input;
  };

  const lines = text.split('\n');
  
  return (
    <div className="space-y-1">
      {lines.map((line, idx) => {
        if (line.trim().startsWith('*') || line.trim().startsWith('-')) {
          const bulletText = line.replace(/^[\s]*[*-][\s]*/, '');
          return (
            <div key={idx} className="flex gap-2 items-start">
              <span className="text-indigo-600 font-bold mt-0.5">•</span>
              <span className="flex-1">{renderText(bulletText)}</span>
            </div>
          );
        }
        
        const numberedMatch = line.match(/^[\s]*(\d+)\.[\s]*(.*)/);
        if (numberedMatch) {
          return (
            <div key={idx} className="flex gap-2 items-start">
              <span className="text-indigo-600 font-bold">{numberedMatch[1]}.</span>
              <span className="flex-1">{renderText(numberedMatch[2])}</span>
            </div>
          );
        }
        
        if (line.trim()) {
          return <div key={idx}>{renderText(line)}</div>;
        }
        
        return <div key={idx} className="h-1" />;
      })}
    </div>
  );
};

export default function AdminDashboard() {
  const [conversations, setConversations] = useState<Conversation[]>([]);
  const [filteredConversations, setFilteredConversations] = useState<Conversation[]>([]);
  const [selectedConversation, setSelectedConversation] = useState<ConversationDetail | null>(null);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [searchTerm, setSearchTerm] = useState('');
  const [statusFilter, setStatusFilter] = useState<'all' | 'active' | 'escalated'>('all');
  const [showModal, setShowModal] = useState(false);

  const fetchConversations = async () => {
    setIsLoading(true);
    setError(null);
    
    try {
      const response = await fetch(`${API_BASE_URL}/api/conversations`);
      
      if (!response.ok) {
        throw new Error(`Failed to fetch conversations: ${response.status}`);
      }
      
      const data = await response.json();
      setConversations(data);
      setFilteredConversations(data);
    } catch (err) {
      const errorMessage = err instanceof Error ? err.message : 'Failed to load conversations';
      setError(errorMessage);
    } finally {
      setIsLoading(false);
    }
  };

  const fetchConversationDetail = async (sessionId: string) => {
    setIsLoading(true);
    setError(null);
    
    try {
      const response = await fetch(`${API_BASE_URL}/api/conversations/${sessionId}`);
      
      if (!response.ok) {
        throw new Error(`Failed to fetch conversation details: ${response.status}`);
      }
      
      const data = await response.json();
      setSelectedConversation(data);
      setShowModal(true);
    } catch (err) {
      const errorMessage = err instanceof Error ? err.message : 'Failed to load conversation';
      setError(errorMessage);
    } finally {
      setIsLoading(false);
    }
  };

  useEffect(() => {
    fetchConversations();
  }, []);

  useEffect(() => {
    let filtered = conversations;
    
    if (statusFilter !== 'all') {
      filtered = filtered.filter(conv => conv.status === statusFilter);
    }
    
    if (searchTerm) {
      filtered = filtered.filter(conv => 
        conv.session_id.toLowerCase().includes(searchTerm.toLowerCase()) ||
        (conv.summary && conv.summary.toLowerCase().includes(searchTerm.toLowerCase()))
      );
    }
    
    setFilteredConversations(filtered);
  }, [searchTerm, statusFilter, conversations]);

  const formatDate = (dateString: string) => {
    const date = new Date(dateString);
    // console.log(dateString);
    return date.toLocaleString([], {
      timeZone: 'Asia/Kolkata', 
      month: 'short',
      day: 'numeric',
      year: 'numeric',
      hour: '2-digit',
      minute: '2-digit',
     

    });
  };

  const stats = {
    total: conversations.length,
    active: conversations.filter(c => c.status === 'active').length,
    escalated: conversations.filter(c => c.status === 'escalated').length,
    avgMessages: conversations.length > 0 
      ? Math.round(conversations.reduce((sum, c) => sum + c.message_count, 0) / conversations.length)
      : 0
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-50 to-slate-100">
      {/* Header */}
      <div className="bg-white shadow-md border-b border-gray-200">
        <div className="max-w-7xl mx-auto px-6 py-4">
          <div className="flex items-center justify-between">
            <div>
              <h1 className="text-2xl font-bold text-gray-900">Admin Dashboard</h1>
              <p className="text-sm text-gray-600 mt-1">Manage and monitor customer conversations</p>
            </div>
            <button
              onClick={fetchConversations}
              disabled={isLoading}
              className="flex items-center gap-2 px-4 py-2 bg-indigo-600 text-white rounded-lg hover:bg-indigo-700 disabled:bg-gray-400 transition-colors"
            >
              <RefreshCw className={`w-4 h-4 ${isLoading ? 'animate-spin' : ''}`} />
              Refresh
            </button>
          </div>
        </div>
      </div>

      <div className="max-w-7xl mx-auto px-6 py-6">
        {/* Stats Cards */}
        <div className="grid grid-cols-1 md:grid-cols-4 gap-4 mb-6">
          <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-4">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm text-gray-600">Total Conversations</p>
                <p className="text-2xl font-bold text-gray-900 mt-1">{stats.total}</p>
              </div>
              <div className="bg-indigo-100 p-3 rounded-lg">
                <MessageSquare className="w-6 h-6 text-indigo-600" />
              </div>
            </div>
          </div>

          <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-4">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm text-gray-600">Active Chats</p>
                <p className="text-2xl font-bold text-green-600 mt-1">{stats.active}</p>
              </div>
              <div className="bg-green-100 p-3 rounded-lg">
                <Activity className="w-6 h-6 text-green-600" />
              </div>
            </div>
          </div>

          <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-4">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm text-gray-600">Escalated</p>
                <p className="text-2xl font-bold text-orange-600 mt-1">{stats.escalated}</p>
              </div>
              <div className="bg-orange-100 p-3 rounded-lg">
                <AlertTriangle className="w-6 h-6 text-orange-600" />
              </div>
            </div>
          </div>

          <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-4">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm text-gray-600">Avg Messages</p>
                <p className="text-2xl font-bold text-blue-600 mt-1">{stats.avgMessages}</p>
              </div>
              <div className="bg-blue-100 p-3 rounded-lg">
                <TrendingUp className="w-6 h-6 text-blue-600" />
              </div>
            </div>
          </div>
        </div>

        {/* Filters and Search */}
        <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-4 mb-6">
          <div className="flex flex-col md:flex-row gap-4">
            <div className="flex-1 relative">
              <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 w-5 h-5 text-gray-400" />
              <input
                type="text"
                placeholder="Search by session ID or summary..."
                value={searchTerm}
                onChange={(e) => setSearchTerm(e.target.value)}
                className="w-full pl-10 pr-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-indigo-500 text-gray-900"
              />
            </div>
            
            <div className="flex items-center gap-2">
              <Filter className="w-5 h-5 text-gray-600" />
              <select
                value={statusFilter}
                onChange={(e) => setStatusFilter(e.target.value as any)}
                className="px-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-indigo-500 text-gray-900 bg-white"
              >
                <option value="all">All Status</option>
                <option value="active">Active</option>
                <option value="escalated">Escalated</option>
              </select>
            </div>
          </div>
        </div>

        {/* Error Message */}
        {error && (
          <div className="bg-red-50 border border-red-200 rounded-lg p-4 mb-6">
            <div className="flex items-start gap-2">
              <AlertTriangle className="w-5 h-5 text-red-600 flex-shrink-0 mt-0.5" />
              <div>
                <p className="text-sm font-medium text-red-800">Error</p>
                <p className="text-sm text-red-700">{error}</p>
              </div>
            </div>
          </div>
        )}

        {/* Conversations List */}
        <div className="bg-white rounded-lg shadow-sm border border-gray-200">
          <div className="px-6 py-4 border-b border-gray-200">
            <h2 className="text-lg font-semibold text-gray-900">
              Conversations ({filteredConversations.length})
            </h2>
          </div>

          {isLoading && conversations.length === 0 ? (
            <div className="p-12 text-center">
              <RefreshCw className="w-8 h-8 text-indigo-600 animate-spin mx-auto mb-4" />
              <p className="text-gray-600">Loading conversations...</p>
            </div>
          ) : filteredConversations.length === 0 ? (
            <div className="p-12 text-center">
              <MessageSquare className="w-12 h-12 text-gray-400 mx-auto mb-4" />
              <p className="text-gray-600">No conversations found</p>
            </div>
          ) : (
            <div className="divide-y divide-gray-200">
              {filteredConversations.map((conv) => (
                <div
                  key={conv.session_id}
                  className="p-4 hover:bg-gray-50 transition-colors"
                >
                  <div className="flex items-start justify-between gap-4">
                    <div className="flex-1 min-w-0">
                      <div className="flex items-center gap-2 mb-2">
                        <span className="font-mono text-sm font-medium text-gray-900">
                          {conv.session_id.substring(0, 8)}...
                        </span>
                        <span className={`px-2 py-1 text-xs font-medium rounded-full ${
                          conv.status === 'escalated'
                            ? 'bg-orange-100 text-orange-700'
                            : 'bg-green-100 text-green-700'
                        }`}>
                          {conv.status === 'escalated' ? (
                            <span className="flex items-center gap-1">
                              <AlertTriangle className="w-3 h-3" />
                              Escalated
                            </span>
                          ) : (
                            <span className="flex items-center gap-1">
                              <CheckCircle className="w-3 h-3" />
                              Active
                            </span>
                          )}
                        </span>
                      </div>
                      
                      {conv.summary && (
                        <p className="text-sm text-gray-600 mb-2 line-clamp-2">
                          {conv.summary}
                        </p>
                      )}
                      
                      <div className="flex items-center gap-4 text-xs text-gray-500">
                        <span className="flex items-center gap-1">
                          <MessageSquare className="w-3 h-3" />
                          {conv.message_count} messages
                        </span>
                        <span className="flex items-center gap-1">
                          <Clock className="w-3 h-3" />
                          {formatDate(conv.created_at)}
                        </span>
                      </div>
                    </div>
                    
                    <button
                      onClick={() => fetchConversationDetail(conv.session_id)}
                      className="flex items-center gap-2 px-3 py-2 text-sm text-indigo-600 hover:bg-indigo-50 rounded-lg transition-colors"
                    >
                      <Eye className="w-4 h-4" />
                      View
                    </button>
                  </div>
                </div>
              ))}
            </div>
          )}
        </div>
      </div>

      {/* Conversation Detail Modal */}
      {showModal && selectedConversation && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center p-4 z-50">
          <div className="bg-white rounded-lg shadow-xl max-w-4xl w-full max-h-[90vh] overflow-hidden flex flex-col">
            <div className="px-6 py-4 border-b border-gray-200 flex items-center justify-between">
              <div>
                <h3 className="text-lg font-semibold text-gray-900">Conversation Details</h3>
                <p className="text-sm text-gray-600 font-mono mt-1">
                  {selectedConversation.session_id}
                </p>
              </div>
              <button
                onClick={() => {
                  setShowModal(false);
                  setSelectedConversation(null);
                }}
                className="p-2 hover:bg-gray-100 rounded-lg transition-colors"
              >
                <X className="w-5 h-5 text-gray-600" />
              </button>
            </div>

            <div className="flex-1 overflow-y-auto p-6">
              <div className="mb-6 grid grid-cols-2 gap-4">
                <div className="bg-gray-50 rounded-lg p-3">
                  <p className="text-xs text-gray-600 mb-1">Status</p>
                  <span className={`inline-flex items-center gap-1 px-2 py-1 text-xs font-medium rounded-full ${
                    selectedConversation.status === 'escalated'
                      ? 'bg-orange-100 text-orange-700'
                      : 'bg-green-100 text-green-700'
                  }`}>
                    {selectedConversation.status === 'escalated' ? (
                      <>
                        <AlertTriangle className="w-3 h-3" />
                        Escalated
                      </>
                    ) : (
                      <>
                        <CheckCircle className="w-3 h-3" />
                        Active
                      </>
                    )}
                  </span>
                </div>
                <div className="bg-gray-50 rounded-lg p-3">
                  <p className="text-xs text-gray-600 mb-1">Created</p>
                  <p className="text-sm font-medium text-gray-900">
                    {formatDate(selectedConversation.created_at)}
                  </p>
                </div>
              </div>

              <div className="space-y-4">
                <h4 className="text-sm font-semibold text-gray-900 mb-3">Message History</h4>
                {selectedConversation.history.map((message, idx) => (
                  <div
                    key={idx}
                    className={`flex gap-3 ${
                      message.role === 'user' ? 'justify-end' : 'justify-start'
                    }`}
                  >
                    <div
                      className={`max-w-xl px-4 py-3 rounded-lg ${
                        message.role === 'user'
                          ? 'bg-indigo-600 text-white'
                          : 'bg-gray-100 text-gray-900'
                      }`}
                    >
                      <div className="flex items-center gap-2 mb-1">
                        <span className="text-xs font-medium">
                          {message.role === 'user' ? 'User' : 'Assistant'}
                        </span>
                      </div>
                      <div className="text-sm">
                        {message.role === 'assistant' ? (
                          <MarkdownText text={message.content} />
                        ) : (
                          <p>{message.content}</p>
                        )}
                      </div>
                    </div>
                  </div>
                ))}
              </div>
            </div>

            <div className="px-6 py-4 border-t border-gray-200 flex justify-end">
              <button
                onClick={() => {
                  setShowModal(false);
                  setSelectedConversation(null);
                }}
                className="px-4 py-2 bg-gray-100 text-gray-700 rounded-lg hover:bg-gray-200 transition-colors"
              >
                Close
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
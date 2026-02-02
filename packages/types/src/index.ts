// Core type definitions for ReformaTax platform

export interface User {
  id: string;
  email: string;
  name: string;
  tier: 'free' | 'pro' | 'team';
  createdAt: Date;
  lastActiveAt: Date;
}

export interface Question {
  id: string;
  userId: string;
  content: string;
  mode: 'technical' | 'simplified';
  createdAt: Date;
}

export interface Response {
  id: string;
  questionId: string;
  content: string;
  citations: Citation[];
  mode: 'technical' | 'simplified';
  createdAt: Date;
  tokens: number;
}

export interface Citation {
  article: string;
  section?: string;
  law: string;
  text: string;
  url?: string;
}

export interface Conversation {
  id: string;
  userId: string;
  questions: Question[];
  responses: Response[];
  createdAt: Date;
  updatedAt: Date;
}

export interface LegalDocument {
  id: string;
  title: string;
  type: 'law' | 'ordinance' | 'instruction' | 'circular';
  number: string;
  year: number;
  publishedAt: Date;
  url: string;
  hash: string;
}

export interface DocumentChunk {
  id: string;
  documentId: string;
  content: string;
  metadata: Record<string, any>;
  embedding?: number[];
  createdAt: Date;
}

// API Request/Response types
export interface QueryRequest {
  question: string;
  mode: 'technical' | 'simplified';
  userId?: string;
}

export interface QueryResponse {
  id: string;
  answer: string;
  citations: Citation[];
  mode: 'technical' | 'simplified';
  sources: SourceDocument[];
  tokens: number;
  timestamp: Date;
}

export interface SourceDocument {
  id: string;
  title: string;
  type: string;
  url: string;
  relevantChunks: string[];
}

// Error types
export interface APIError {
  code: string;
  message: string;
  details?: Record<string, any>;
}

// Rate limiting types
export interface RateLimit {
  userId: string;
  tier: User['tier'];
  requestsToday: number;
  requestsPerMinute: number;
  lastRequest: Date;
  resetAt: Date;
}

// Search types
export interface SearchResult {
  chunkId: string;
  documentId: string;
  content: string;
  score: number;
  metadata: Record<string, any>;
}

export interface SearchRequest {
  query: string;
  limit?: number;
  threshold?: number;
  mode?: 'vector' | 'keyword' | 'hybrid';
}

// Monitoring and analytics
export interface UsageMetrics {
  userId: string;
  date: Date;
  questionsAsked: number;
  tokensUsed: number;
  cacheHits: number;
  cacheMisses: number;
  averageResponseTime: number;
}
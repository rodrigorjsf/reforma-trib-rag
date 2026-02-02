import { useState } from 'react';

// Common business logic and validation functions

export function validateEmail(email: string): boolean {
  const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
  return emailRegex.test(email);
}

export function validateQuestion(question: string): {
  isValid: boolean;
  error?: string;
} {
  if (!question.trim()) {
    return { isValid: false, error: 'Question cannot be empty' };
  }
  
  if (question.length < 10) {
    return { isValid: false, error: 'Question must be at least 10 characters' };
  }
  
  if (question.length > 1000) {
    return { isValid: false, error: 'Question must be less than 1000 characters' };
  }
  
  return { isValid: true };
}

export function formatDate(date: Date): string {
  return new Intl.DateTimeFormat('pt-BR', {
    day: '2-digit',
    month: '2-digit',
    year: 'numeric',
    hour: '2-digit',
    minute: '2-digit',
  }).format(date);
}

export function formatTokens(tokens: number): string {
  if (tokens < 1000) {
    return `${tokens}`;
  }
  return `${(tokens / 1000).toFixed(1)}K`;
}

export function truncateText(text: string, maxLength: number): string {
  if (text.length <= maxLength) return text;
  return text.substring(0, maxLength).trim() + '...';
}

export function debounce<T extends (...args: any[]) => void>(
  func: T,
  wait: number
): (...args: Parameters<T>) => void {
  let timeout: NodeJS.Timeout;
  
  return (...args: Parameters<T>) => {
    clearTimeout(timeout);
    timeout = setTimeout(() => func(...args), wait);
  };
}
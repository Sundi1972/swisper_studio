/**
 * Tests for auth storage utilities
 * Minimal tests for confidence before UAT
 */

import { describe, it, expect, beforeEach } from 'vitest';
import { storeApiKey, getApiKey, clearApiKey, isAuthenticated } from '../auth-storage';

describe('auth-storage', () => {
  beforeEach(() => {
    // Clear real localStorage (jsdom provides this)
    window.localStorage.clear();
  });

  it('stores and retrieves API key', () => {
    const testKey = 'test-api-key-123';
    
    storeApiKey(testKey);
    const retrieved = getApiKey();
    
    expect(retrieved).toBe(testKey);
  });

  it('returns null when no API key stored', () => {
    const retrieved = getApiKey();
    expect(retrieved).toBeNull();
  });

  it('clears API key', () => {
    storeApiKey('test-key');
    clearApiKey();
    
    expect(getApiKey()).toBeNull();
  });

  it('isAuthenticated returns true when API key exists', () => {
    storeApiKey('test-key');
    expect(isAuthenticated()).toBe(true);
  });

  it('isAuthenticated returns false when no API key', () => {
    expect(isAuthenticated()).toBe(false);
  });
});


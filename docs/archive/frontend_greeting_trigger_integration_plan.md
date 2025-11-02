# Frontend Surgical Integration Plan

**Date:** October 8, 2025  
**Strategy:** Take main's refactored frontend, add our empty message trigger  
**Status:** Ready for Implementation

---

## Key Finding

✅ **GOOD NEWS:** Main's `use-stream-message` hook DOES support empty `prompt` parameter!

**Evidence:**
```typescript
// main/use-stream-message.tsx (line 17)
interface UseStreamMessageProps {
  prompt: string;  // ← Can be empty string ''
  model: string;
  // ...
}
```

**This means:** We CAN integrate our empty message feature into main's architecture!

---

## Integration Strategy

### Phase 1: Use Main's Files as Base

**Accept from main:**
- ✅ `use-stream-message.tsx` (replaces our useLLMStream.tsx)
- ✅ `use-create-chat.tsx` (replaces our useCreateNewChat.tsx)
- ✅ All other frontend files

**Keep from ours:**
- ✅ `chat-speech-mode-container/` (voice modal - no conflicts)

---

### Phase 2: Add Empty Message Trigger to Main's useNewChat

**File:** `frontend/src/domain/chat/hooks/index.ts`

**Main's Version (Simple):**
```typescript
export function useNewChat() {
  const resetLayout = useResetLayout();
  const [_, setSelectedChatId] = useCurrentChatId();

  return useCallback(() => {
    setSelectedChatId(NEW_CHAT_ID);
    resetLayout();
  }, [setSelectedChatId, resetLayout]);
}
```

**Enhanced with Our Feature:**
```typescript
import { useStreamMessage } from '@/features/chat/hooks/use-stream-message';
import { useChatActions } from '@/domain/chat/hooks/useChatActions';  // Or equivalent in main
import { useSetAtom } from 'jotai';
import { streamingMessageIdAtom, streamingNodeNameAtom } from '@/domain/chat/atoms/streaming';

export function useNewChat() {
  const resetLayout = useResetLayout();
  const [_, setSelectedChatId] = useCurrentChatId();
  const { streamMessage } = useStreamMessage();
  const navigate = useNavigate();
  
  // Chat actions (check what main uses)
  const { addUserMessage, appendAssistantMessage, clearAssistantMessage, replaceMessageIds } = useChatActions();
  const setStreamingMessageId = useSetAtom(streamingMessageIdAtom);
  const setStreamingNodeName = useSetAtom(streamingNodeNameAtom);

  return useCallback(() => {
    resetLayout();
    setSelectedChatId(NEW_CHAT_ID);
    
    // OUR ADDITION: Trigger greeting with empty message
    const model = 'Llama-4-Maverick-17B-128E-Instruct-FP8';
    
    // Add empty user message (will be hidden in UI)
    addUserMessage('');
    
    // Stream empty message to trigger backend greeting/intro
    let messageIdsReplaced = false;
    
    streamMessage({
      prompt: '',  // ← Empty message triggers greeting
      model,
      onToken: (chunk) => {
        // Handle message ID replacement
        if (!messageIdsReplaced && chunk.previousMessageId) {
          replaceMessageIds({
            userId: chunk.previousMessageId,
            assistantId: chunk.messageId,
          });
          messageIdsReplaced = true;
        }
        
        // Track streaming state
        setStreamingMessageId(chunk.messageId);
        setStreamingNodeName(chunk.nodeName);
        
        // Handle node switching
        if (chunk.clearPrevious) {
          clearAssistantMessage(chunk.messageId, chunk.response);
          return;
        }
        
        // Append streaming content
        appendAssistantMessage(chunk.messageId, chunk.response);
      },
      onSuccess: (chatId) => {
        setStreamingMessageId(null);
        setStreamingNodeName(undefined);
        if (chatId) {
          setSelectedChatId(chatId);
          navigate(`/${chatId}`);
        }
      },
      onError: (error) => {
        setStreamingMessageId(null);
        setStreamingNodeName(undefined);
        console.warn('[NewChat] Failed:', error);
        navigate('/');
      }
    });
  }, [setSelectedChatId, resetLayout, streamMessage, navigate, /* ...other deps */]);
}
```

---

### Phase 3: Create useAutoGreeting with Main's Architecture

**File:** `frontend/src/features/chat/hooks/useAutoGreeting.ts` (NEW in main)

**Same logic as ours, but use main's hooks:**
```typescript
import { useEffect, useRef } from 'react';
import { useNavigate } from 'react-router-dom';
import { useSessionInit } from '@/features/security/endpoint-hooks/useSessionInit';
import { useStreamMessage } from '@/features/chat/hooks/use-stream-message';  // Main's hook
import { useChatActions } from '@/domain/chat/hooks/useChatActions';  // Check what main uses

export function useAutoGreeting() {
  const { data: sessionData } = useSessionInit();
  const { streamMessage } = useStreamMessage();  // Use main's hook
  const navigate = useNavigate();
  const { addUserMessage, appendAssistantMessage, replaceMessageIds, clearAssistantMessage } = useChatActions();
  
  const hasTriggered = useRef(false);

  useEffect(() => {
    if (!sessionData) return;
    if (hasTriggered.current) return;
    if (!sessionData.shouldAutoGreet) return;

    hasTriggered.current = true;

    setTimeout(() => {
      const model = 'Llama-4-Maverick-17B-128E-Instruct-FP8';
      
      addUserMessage('');  // Empty message
      
      let messageIdsReplaced = false;
      
      streamMessage({
        prompt: '',  // Trigger greeting
        model,
        onToken: (chunk) => {
          if (!messageIdsReplaced && chunk.previousMessageId) {
            replaceMessageIds({
              userId: chunk.previousMessageId,
              assistantId: chunk.messageId,
            });
            messageIdsReplaced = true;
          }
          
          appendAssistantMessage(chunk.messageId, chunk.response);
        },
        onSuccess: (chatId) => {
          if (chatId) navigate(`/${chatId}`);
        },
        onError: (error) => {
          console.warn('[AutoGreeting] Failed:', error);
        }
      });
    }, 500);
  }, [sessionData, streamMessage, navigate]);
}
```

---

## Dependencies to Verify in Main

### Check if These Exist:

**1. useChatActions (or equivalent)**
```bash
git ls-tree -r --name-only origin/main frontend/src | grep -i "chataction\|chat.*action"
```

**2. Streaming atoms**
```bash
git show origin/main:frontend/src/domain/chat/atoms/streaming.ts
```

**3. Message management**
```bash
# Check how main handles:
# - addUserMessage
# - appendAssistantMessage
# - replaceMessageIds
```

**If missing:** We need to find main's equivalent or keep our implementations

---

## Detailed File-by-File Integration

### File 1: domain/chat/hooks/index.ts

**Resolution:**
```
1. Start with main's version
2. Add imports:
   - useStreamMessage from main
   - Message management hooks (from main or ours)
   - Streaming atoms (from main or ours)
3. Enhance useNewChat() with empty message logic
4. Keep all other hooks from main unchanged
```

**Result:** Main's architecture + our greeting trigger

---

### File 2: features/chat/useLLMStream.tsx (DELETED in main)

**Resolution:**
```
DELETE (main deleted it)
Our code should use main's use-stream-message.tsx instead
```

**Migration:**
```typescript
// OLD (ours):
import { useChatStream } from '@/features/chat/useLLMStream';
const { streamChat } = useChatStream();
streamChat('', model, { ... });

// NEW (main):
import { useStreamMessage } from '@/features/chat/hooks/use-stream-message';
const { streamMessage } = useStreamMessage();
streamMessage({ prompt: '', model, ... });
```

---

### File 3: features/chat/useChatStore.ts (DELETED in main)

**Need to check:** What replaced this?

**Likely candidates in main:**
- React Query for server state
- Jotai/Zustand for client state
- Message context (check chat-message-history)

**Action:** Investigate main's state management approach

---

### File 4: features/chat/hooks/useAutoGreeting.ts (NOT in main)

**Resolution:**
```
CREATE in main
Use main's hooks (use-stream-message)
Same logic as ours
```

---

## Investigation Checklist

**Before we can integrate, verify:**

- [ ] Does main have message management hooks (addUserMessage, appendAssistantMessage)?
- [ ] Do streaming atoms exist in main?
- [ ] What replaced useChatStore?
- [ ] Does use-stream-message accept empty prompt without errors?
- [ ] How does main handle message ID replacement?

---

## Recommended Approach

### Option A: Pure Integration (Cleanest)

**Steps:**
1. Accept ALL frontend from main
2. Modify ONLY `domain/chat/hooks/index.ts`:
   - Import main's `use-stream-message`
   - Add empty message trigger to `useNewChat()`
3. Create `useAutoGreeting.ts` using main's hooks
4. Test

**Pros:**
- ✅ Minimal changes to main's architecture
- ✅ Clean integration
- ✅ No old code kept

**Cons:**
- ⚠️ Need to verify all dependencies exist in main
- ⚠️ Might need to create missing helper functions

---

### Option B: Hybrid (Safer)

**Steps:**
1. Accept most frontend from main
2. Keep our `useLLMStream.tsx` (renamed to avoid conflicts)
3. Keep our `useChatStore.ts` if needed
4. Use our hooks but import main's where possible

**Pros:**
- ✅ Lower risk (our code still works)
- ✅ Faster integration

**Cons:**
- ⚠️ Mixed architecture (main + ours)
- ⚠️ Technical debt
- ⚠️ Harder to maintain

---

## Next Steps

**1. Investigate Main's Dependencies:**
```bash
# Check for chat actions
git ls-tree -r --name-only origin/main frontend/src | grep -i "action\|message.*hook"

# Check streaming atoms
git show origin/main:frontend/src/domain/chat/atoms/streaming.ts

# Check message context
git show origin/main:frontend/src/features/messages/
```

**2. Create Migration Map:**
```
Our Hook                 → Main's Equivalent
─────────────────────────────────────────────
useChatStream            → useStreamMessage
addUserMessage           → ??? (need to find)
appendAssistantMessage   → ??? (need to find)
replaceMessageIds        → ??? (useUpdateTemporaryChatData?)
```

**3. Implement Integration:**
- Modify main's files with our features
- Test locally
- Commit

---

**Shall I proceed with the investigation to find all dependencies?**


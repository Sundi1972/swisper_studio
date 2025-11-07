# Architecture Documentation

This directory contains architecture diagrams and documentation for SwisperStudio.

## 📁 Files

### **1. ARCHITECTURE_OVERVIEW.md**
Comprehensive text-based architecture documentation with:
- High-level architecture diagram (ASCII)
- Component breakdown
- Data flow diagrams
- Database schema
- Technology stack
- Performance metrics

**View:** Just open the file in Cursor/VS Code with Markdown preview (`Ctrl+Shift+V`)

---

### **2. swisper_studio_architecture.excalidraw**
Interactive architecture diagram created with Excalidraw.

**How to view:**

#### **Option A: Excalidraw Web (Recommended)**
1. Go to https://excalidraw.com
2. Click **"Open"** in the menu
3. Upload `swisper_studio_architecture.excalidraw`
4. Explore the interactive diagram!

#### **Option B: VS Code Extension**
1. Install **Excalidraw** extension in VS Code/Cursor
2. Open `swisper_studio_architecture.excalidraw`
3. Diagram renders directly in the editor

#### **Option C: Export to PNG/SVG**
1. Open in Excalidraw web
2. Click **"Export"** → Save as PNG or SVG
3. Use image in presentations/documentation

---

## 🏗️ Architecture Highlights

### **SwisperStudio Platform**
- **Frontend:** React + MUI (Port 3000)
- **Backend:** FastAPI + SQLModel (Port 8001)
- **Database:** PostgreSQL (Port 5433)
- **Cache/Stream:** Redis (Port 6379)

### **Swisper Integration**
- **Backend:** FastAPI + LangGraph (Port 8000)
- **SDK:** SwisperStudio SDK v0.5.0 (in-process)
- **Agents:** 4 LangGraph agents (Research, Productivity, Wealth, Document)

### **Key Data Flows**
1. **Tracing:** SDK → Redis Streams → SwisperStudio Backend → PostgreSQL
2. **Viewing:** Frontend → Backend REST API → Display traces
3. **Toggle:** Admin UI → Backend → Redis Cache → SDK checks

---

## 🔄 Keeping Diagrams Updated

When making architecture changes:

1. Update `ARCHITECTURE_OVERVIEW.md` (text version)
2. Update `swisper_studio_architecture.excalidraw` (visual version)
3. Export new PNG/SVG if needed
4. Commit both files together

---

## 📊 Current Status

**Last Updated:** 2025-11-07  
**Version:** 1.0  
**MVP Progress:** 85% Complete  
**Status:** Production-ready architecture, pending auth implementation

---

**Questions?** See `CURRENT_STATUS_AND_NEXT_STEPS.md` in project root.


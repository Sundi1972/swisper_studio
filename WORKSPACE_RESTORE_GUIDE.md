# 🔄 Swisper Dual-Workspace Restore Guide

**Last Updated:** November 1, 2025

---

## 🎯 Goal

Restore your perfect dual-workspace setup:
- **Window 1:** Helvetiq (Swisper App) via WSL
- **Window 2:** SwisperStudio (Observability Platform) via WSL

---

## ✅ What Was Created

### 1. **Workspace Files**
```
/root/projects/helvetiq/helvetiq.code-workspace
/root/projects/swisper_studio/swisper_studio.code-workspace
```

### 2. **Desktop Launcher**
```
C:\Users\heiko\Desktop\Open-Swisper-Workspaces.bat
```

---

## 🚀 Three Ways to Restore Your Setup

### **Option 1: Desktop Shortcut (EASIEST)** ⭐

**Double-click:**
```
C:\Users\heiko\Desktop\Open-Swisper-Workspaces.bat
```

**What happens:**
1. Opens Helvetiq workspace in WSL
2. Waits 3 seconds
3. Opens SwisperStudio workspace in WSL
4. Both windows appear automatically

**To pin to taskbar:**
1. Right-click `Open-Swisper-Workspaces.bat`
2. Create shortcut
3. Drag shortcut to taskbar

---

### **Option 2: Cursor Recent Projects (AUTOMATIC)**

Cursor remembers your recent projects!

**Steps:**
1. Open Cursor
2. Click `File` → `Open Recent`
3. You'll see:
   - `helvetiq.code-workspace`
   - `swisper_studio.code-workspace`
4. Click each one (opens in separate windows)

**Pro tip:** Cursor may auto-restore on startup if you have the right settings (see Option 4).

---

### **Option 3: Manual Open (FLEXIBLE)**

**From any Cursor window:**

**For Helvetiq:**
```
File → Open Workspace from File...
→ \\wsl.localhost\Ubuntu\root\projects\helvetiq\helvetiq.code-workspace
```

**For SwisperStudio:**
```
File → Open Workspace from File...
→ \\wsl.localhost\Ubuntu\root\projects\swisper_studio\swisper_studio.code-workspace
```

---

### **Option 4: Enable Automatic Session Restore**

**Make Cursor restore everything on startup:**

**In EACH Cursor window:**

1. Press `Ctrl+,` (Settings)
2. Search: `window.restoreWindows`
3. Set to: **`all`**
4. Restart Cursor

**Next time you open Cursor:**
- All your previous windows will reopen automatically
- Both workspaces will restore
- You're back to work instantly! 🎉

---

## 🔧 Advanced: PowerShell Version (Alternative)

If you prefer PowerShell, create this file:

**File:** `C:\Users\heiko\Desktop\Open-Swisper-Workspaces.ps1`

```powershell
Write-Host "Opening Swisper Development Environment..." -ForegroundColor Cyan
Write-Host ""

# Open Helvetiq
Start-Process "C:\Users\heiko\AppData\Local\Programs\cursor\Cursor.exe" `
    -ArgumentList "--remote", "wsl+Ubuntu", "/root/projects/helvetiq/helvetiq.code-workspace"

# Wait 3 seconds
Start-Sleep -Seconds 3

# Open SwisperStudio
Start-Process "C:\Users\heiko\AppData\Local\Programs\cursor\Cursor.exe" `
    -ArgumentList "--remote", "wsl+Ubuntu", "/root/projects/swisper_studio/swisper_studio.code-workspace"

Write-Host ""
Write-Host "✅ Both workspaces opening..." -ForegroundColor Green
Write-Host "✅ Helvetiq + SwisperStudio" -ForegroundColor Green
Write-Host ""
Start-Sleep -Seconds 2
```

**Run with:**
```powershell
powershell -ExecutionPolicy Bypass -File "C:\Users\heiko\Desktop\Open-Swisper-Workspaces.ps1"
```

---

## 📊 What's in the Workspace Files?

Both workspace files configure:
- ✅ File exclusions (`.git`, `node_modules`, `__pycache__`)
- ✅ Search exclusions (faster searches)
- ✅ Recommended extensions (Python, ESLint, Prettier, WSL)
- ✅ WSL integration settings

---

## 🎨 Customization

### **Change Window Order:**

Edit the batch script order:
```bat
REM Open SwisperStudio first
start "" "..." swisper_studio.code-workspace

REM Wait
timeout /t 3 /nobreak >nul

REM Then Helvetiq
start "" "..." helvetiq.code-workspace
```

### **Change Wait Time:**

In the batch script:
```bat
REM Wait 5 seconds instead of 3
timeout /t 5 /nobreak >nul
```

### **Add Third Workspace:**

Add another `start` command:
```bat
start "" "C:\Users\heiko\AppData\Local\Programs\cursor\Cursor.exe" --remote wsl+Ubuntu /path/to/workspace.code-workspace
```

---

## 🐛 Troubleshooting

### **Issue 1: Batch file doesn't work**

**Check Cursor installation path:**
```powershell
# In PowerShell
Test-Path "C:\Users\heiko\AppData\Local\Programs\cursor\Cursor.exe"
```

If False, update the path in the batch script.

---

### **Issue 2: Windows opens but shows wrong folder**

**Solution:** Open the `.code-workspace` file directly:
1. Navigate to `\\wsl.localhost\Ubuntu\root\projects\helvetiq\`
2. Double-click `helvetiq.code-workspace`

---

### **Issue 3: WSL connection fails**

**Solution:**
1. Make sure WSL is running: `wsl --list --running`
2. Restart WSL: `wsl --shutdown` then reopen Cursor
3. Reinstall Remote-WSL extension in Cursor

---

## ✅ Verification Checklist

After opening both workspaces, verify:

- [ ] **Window 1:**
  - Bottom-left: `WSL: Ubuntu`
  - Status bar: `helvetiq`
  - Folder: `/root/projects/helvetiq`

- [ ] **Window 2:**
  - Bottom-left: `WSL: Ubuntu`
  - Status bar: `swisper_studio`
  - Folder: `/root/projects/swisper_studio`

---

## 🎯 Recommended Setup

**For daily development:**

1. ✅ Use **Option 4** (Auto-restore) for automatic session restore
2. ✅ Keep **Desktop shortcut** for manual/fresh starts
3. ✅ Pin workspaces to Recent Projects for quick access

**Result:** You never lose your workspace setup! 🚀

---

## 📚 Related Documentation

- **SwisperStudio Setup:** `/root/projects/swisper_studio/PARALLEL_DEV_SETUP.md`
- **Helvetiq Structure:** `/root/projects/helvetiq/AGENTS.md`
- **Cursor WSL Docs:** https://code.visualstudio.com/docs/remote/wsl

---

**Remember:** Your dual-workspace setup is now saved and reproducible! 🎉


# Quick UAT Reference Card

## 🔑 Login

**API Key:** `dev-api-key-change-in-production`

(Click 👁️ to verify you typed it correctly)

---

## 📋 Create Your First Project

**Use these test values:**

```
Project Name:          My First Swisper
Swisper URL:           https://swisper.example.com
Swisper API Key:       test-key-123
Description:           Test project for UAT
```

**What these mean:**

| Field | What To Enter | Why |
|-------|---------------|-----|
| **Project Name** | Any name you want | This is YOUR label for this Swisper deployment |
| **Swisper URL** | Any valid URL | Where your Swisper instance runs (not validated yet in Phase 1) |
| **Swisper API Key** | Any string | Will be used to connect to Swisper (not validated yet in Phase 1) |
| **Description** | Any text or leave blank | Optional notes |

---

## 🎯 What You Can Test

✅ **Login** - Use SwisperStudio API key  
✅ **Create Project** - Add a test project  
✅ **View Projects** - See list of projects  
✅ **View Traces** - Empty for now (until Swisper SDK integration)  
✅ **Dark Mode** - Swisper branding active  
✅ **Hot Reload** - Edit files, see instant updates  

---

## 💡 Quick Tips

- **Two Types of API Keys:** Don't confuse them!
  - Login = SwisperStudio API key
  - Project = Swisper Instance API key
  
- **URLs Must Be Valid:** Start with http:// or https://

- **Can't Login?** 
  - Check you're using: `dev-api-key-change-in-production`
  - Check backend is running: `docker compose ps`

---

## 🌐 URLs

- **Frontend:** http://localhost:3000
- **Backend API:** http://localhost:8001
- **API Docs:** http://localhost:8001/api/v1/docs

---

**Happy Testing!** 🎉


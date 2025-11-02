# Creating Your First Project

## 🎯 What is a "Project"?

A **Project** in SwisperStudio represents a connection to ONE Swisper deployment.

Think of it like:
- One SwisperStudio instance can monitor multiple Swisper deployments
- Each deployment = one project
- Example: Production Swisper, Staging Swisper, Dev Swisper

---

## 📝 What to Enter in the Form

### **1. Project Name** (Required)

**What it is:** A friendly name YOU choose to identify this Swisper deployment.

**Examples:**
- "Production Swisper"
- "Staging Environment"
- "Local Development"
- "Customer Demo Instance"

**Can be anything!** This is just for YOUR reference in SwisperStudio.

---

### **2. Swisper Instance URL** (Required)

**What it is:** The URL where your Swisper backend is running.

**Format:** Must be a valid URL starting with `http://` or `https://`

**Examples:**

**For Testing/Development (No Real Swisper Yet):**
```
https://swisper.example.com
http://localhost:8000
https://swisper-dev.mycompany.com
```

**For Production (When You Have Real Swisper):**
```
https://swisper.mycompany.com
https://api.swisper.acme.corp
```

**Current Situation (MVP Phase 1):**
Since we haven't integrated with a real Swisper instance yet, you can enter:
- ✅ **ANY valid URL** (it won't be validated yet)
- Example: `https://swisper.example.com`
- Later (Phase 2): We'll actually connect and validate

---

### **3. Swisper Instance API Key** (Required)

**What it is:** The API key that SwisperStudio will use to authenticate when calling your Swisper instance.

**IMPORTANT - Two Types of API Keys:**

| Type | Purpose | Where Used |
|------|---------|------------|
| **SwisperStudio API Key** | Authenticate YOU to SwisperStudio | Login page |
| **Swisper Instance API Key** | SwisperStudio connects to Swisper | Project creation |

This field is asking for the **Swisper Instance API Key** (the second type).

**Current Situation (MVP Phase 1):**
Since we haven't integrated with a real Swisper instance yet:
- ✅ **Enter ANY string** (won't be validated yet)
- Example: `my-test-swisper-key-123`
- Example: `swisper-production-key`
- Later (Phase 2): This will be the actual API key from your Swisper deployment

**For Real Swisper Instance (Phase 2+):**
- This would be an API key generated in your Swisper backend
- Swisper would expose an endpoint like `POST /api/admin/keys`
- You'd copy that key and paste it here

---

### **4. Description** (Optional)

**What it is:** Any notes about this deployment.

**Examples:**
- "Main production instance for customer support"
- "Staging environment for testing new features"
- "Local dev instance"
- Leave blank if you want!

---

## ✅ Example: Creating Your First Test Project

**Here's what to enter for testing:**

```
Project Name:        My First Swisper
Swisper URL:         https://swisper.example.com
Swisper API Key:     test-key-123
Description:         Test project for Phase 1 UAT
```

**Click "Create Project"** and you should see it appear in the list!

---

## 🔐 Security Note

**For MVP/Testing:**
- The "Swisper API Key" is stored (hashed) in SwisperStudio's database
- It's not validated against a real Swisper instance yet
- You can enter any string for now

**For Production (Phase 2+):**
- This will be a real API key from your Swisper deployment
- SwisperStudio will use it to call Swisper APIs
- It will be validated when you create the project

---

## 🎯 Quick Test Values

**Copy-paste ready:**

```
Project Name:        UAT Test Project
Swisper URL:         https://swisper-uat.example.com
Swisper API Key:     uat-test-key-12345
Description:         Created during Phase 1 UAT testing
```

---

## 💡 Tips

1. ✅ **Click the 👁️ icon** to see what you're typing in the API key field
2. ✅ **Use descriptive names** - You'll have multiple projects eventually
3. ✅ **URL format matters** - Must start with http:// or https://
4. ✅ **Don't worry about API key** - Can be anything for now (Phase 1 MVP)

---

**Ready to create your first project!** 🚀


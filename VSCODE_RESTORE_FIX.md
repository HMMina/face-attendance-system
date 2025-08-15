# Hướng dẫn khắc phục vấn đề VS Code restore files

## 🛠️ **Nguyên nhân files bị restore sau khi close VS Code:**

### 1. **VS Code Workspace Cache**
- VS Code cache lại file structure 
- Khi restart, nó restore về trạng thái cache

### 2. **Git Tracking** (Đã khắc phục)
- Files đang được Git track sẽ restore về commit state
- ✅ **Giải pháp**: Đã tạo `.gitignore` và commit changes

### 3. **VS Code Settings Sync**
- VS Code sync settings có thể restore files
- Settings: `workbench.settings.enableNaturalLanguageSearch`

## 🔧 **Các bước khắc phục đã thực hiện:**

### ✅ **Bước 1: Tạo .gitignore mạnh**
```gitignore
# Files to prevent restore
__init__.py
run_server.py
enhanced_requirements.txt
scripts/
package-lock.json
data/
backups/
```

### ✅ **Bước 2: Git commit changes**
```bash
git rm -r --cached data/
git add .
git commit -m "Fix: Remove PostgreSQL data and improve .gitignore"
```

### ✅ **Bước 3: Xóa PostgreSQL data files**
- Removed 2000+ PostgreSQL data files khỏi Git
- Data directory không nên commit vào Git

## 🚫 **Ngăn chặn restore trong tương lai:**

### **1. Workspace Settings**
Tạo `.vscode/settings.json`:
```json
{
  "files.exclude": {
    "**/__init__.py": true,
    "**/run_server.py": true,
    "**/package-lock.json": true,
    "data/": true,
    "scripts/": true
  },
  "search.exclude": {
    "data/": true,
    "**/__pycache__": true
  }
}
```

### **2. PowerShell Commands để xóa persistent**
```powershell
# Force remove với -Force -Recurse
Remove-Item "file.py" -Force -ErrorAction SilentlyContinue

# Clear VS Code workspace cache
Remove-Item "$env:APPDATA\Code\User\workspaceStorage" -Recurse -Force
```

### **3. Git hooks để prevent**
Tạo `.git/hooks/pre-commit` để block commit các files không mong muốn.

## ⚡ **Lệnh nhanh để cleanup:**

```powershell
# Xóa files thường restore
cd "c:\Users\ADMIN\.vscode\face-attendace-system\backend"
Remove-Item "__init__.py", "run_server.py", "package-lock.json" -Force -ErrorAction SilentlyContinue

# Commit ngay để Git track việc xóa
git add . ; git commit -m "Cleanup: Remove restored files"
```

## 📋 **Checklist để tránh restore:**

- [x] Tạo `.gitignore` comprehensive
- [x] Git commit changes ngay lập tức  
- [x] Xóa PostgreSQL data files
- [ ] Tạo VS Code workspace settings
- [ ] Clear VS Code cache nếu cần
- [x] Đổi tên files thay vì xóa (như `run_server.py` → `start_server.py`)

## 🎯 **Kết quả cuối cùng:**
Backend structure đã được optimize và clean, files không cần thiết đã được remove hoặc rename properly.

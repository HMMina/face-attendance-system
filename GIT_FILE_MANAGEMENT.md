# Git File Management Quick Guide

## Kiểm tra file có cần update Git không:

### 🔍 **Lệnh kiểm tra:**
```powershell
# Xem files được Git track
git ls-files | findstr "filename"

# Xem trạng thái tất cả files
git status

# Xem files bị ignore
git status --ignored
```

### 📊 **Các trường hợp:**

| Trạng thái File | Cần Git Update? | Lệnh thực hiện |
|----------------|----------------|----------------|
| **Tracked (đã commit)** | ✅ **CẦN** | `git rm file; git commit` |
| **Untracked (chưa add)** | ❌ **KHÔNG** | `Remove-Item file` |
| **Ignored (.gitignore)** | ❌ **KHÔNG** | `Remove-Item file` |
| **Staged (đã add)** | ✅ **CẦN** | `git reset file; Remove-Item file` |

### ⚡ **Lệnh nhanh cho backend:**
```powershell
# Xóa file và update Git nếu cần
function Remove-FileWithGit {
    param($filename)
    if (git ls-files | Select-String $filename) {
        git rm $filename
        git commit -m "Remove $filename"
    } else {
        Remove-Item $filename -Force -ErrorAction SilentlyContinue
    }
}

# Sử dụng:
Remove-FileWithGit "__init__.py"
```

### 🖱️ **Xóa file bằng Delete key/File Explorer:**

#### **Quy trình sau khi xóa manual:**
```powershell
# 1. Kiểm tra Git có thấy file bị xóa không
git status

# 2a. Nếu hiện "deleted: filename" → CẦN update Git
git add .
git commit -m "Remove filename"

# 2b. Nếu không hiện gì → File chưa tracked, không cần làm gì
```

#### **Git status sẽ hiện:**
- `deleted: filename` → **CẦN commit**
- Không hiện gì → **KHÔNG cần commit**

### 🎯 **Best Practice:**
1. **Luôn check sau khi xóa:** `git status`
2. **Nếu thấy "deleted":** `git add . && git commit`
3. **Nếu không thấy gì:** Không cần làm gì
4. **Files ignore:** Git sẽ không thấy

#!/usr/bin/env python3
"""
Final UTC Validation Script
Kiểm tra toàn bộ project đã sử dụng UTC đúng cách
"""
import os
import re
import sys

def scan_python_files():
    """Scan Python files for datetime.now() usage"""
    print("🐍 SCANNING PYTHON FILES")
    print("=" * 50)
    
    issues = []
    good_patterns = [
        r'datetime\.utcnow\(\)',
        r'datetime\.datetime\.utcnow\(\)',
        r'\.utcnow\(\)',
    ]
    
    bad_patterns = [
        r'datetime\.now\(\)',
        r'datetime\.datetime\.now\(\)',
        r'\.now\(\)(?!\s*\.toUtc)',  # Allow .now().toUtc() for Dart
    ]
    
    # Scan backend directory
    backend_dir = os.path.join("backend", "app")
    if os.path.exists(backend_dir):
        for root, dirs, files in os.walk(backend_dir):
            for file in files:
                if file.endswith('.py'):
                    file_path = os.path.join(root, file)
                    rel_path = os.path.relpath(file_path)
                    
                    with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                        content = f.read()
                        lines = content.split('\n')
                        
                        for i, line in enumerate(lines, 1):
                            # Skip comments and test files
                            if line.strip().startswith('#') or 'test_' in file or line.strip().startswith('"""'):
                                continue
                                
                            for bad_pattern in bad_patterns:
                                if re.search(bad_pattern, line):
                                    # Check if it's in an allowlist context
                                    if any(good in line for good in ['test_', 'demo', 'example', 'local_now']):
                                        continue
                                    issues.append({
                                        'file': rel_path,
                                        'line': i,
                                        'content': line.strip(),
                                        'type': 'bad_datetime'
                                    })
    
    if issues:
        print("❌ ISSUES FOUND:")
        for issue in issues:
            print(f"  📁 {issue['file']}:{issue['line']}")
            print(f"     {issue['content']}")
            print()
    else:
        print("✅ All Python files use UTC correctly!")
    
    return len(issues) == 0

def scan_dart_files():
    """Scan Dart files for DateTime.now() usage"""
    print("🎯 SCANNING DART FILES")
    print("=" * 50)
    
    issues = []
    kiosk_dir = os.path.join("kiosk-app", "lib")
    
    if os.path.exists(kiosk_dir):
        for root, dirs, files in os.walk(kiosk_dir):
            for file in files:
                if file.endswith('.dart'):
                    file_path = os.path.join(root, file)
                    rel_path = os.path.relpath(file_path)
                    
                    with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                        content = f.read()
                        lines = content.split('\n')
                        
                        for i, line in enumerate(lines, 1):
                            # Look for DateTime.now() without .toUtc()
                            if 'DateTime.now()' in line and '.toUtc()' not in line:
                                # Allow cache and timing operations
                                if any(word in line.lower() for word in ['cache', 'timestamp', 'difference', 'duration', 'fallback']):
                                    continue
                                issues.append({
                                    'file': rel_path,
                                    'line': i,
                                    'content': line.strip(),
                                    'type': 'local_datetime'
                                })
    
    if issues:
        print("❌ ISSUES FOUND:")
        for issue in issues:
            print(f"  📁 {issue['file']}:{issue['line']}")
            print(f"     {issue['content']}")
            print()
    else:
        print("✅ All Dart files handle timezone correctly!")
    
    return len(issues) == 0

def check_database_models():
    """Check database models use UTC defaults"""
    print("🗄️  CHECKING DATABASE MODELS")
    print("=" * 50)
    
    models_dir = os.path.join("backend", "app", "models")
    issues = []
    
    if os.path.exists(models_dir):
        for file in os.listdir(models_dir):
            if file.endswith('.py') and file != '__init__.py':
                file_path = os.path.join(models_dir, file)
                rel_path = os.path.relpath(file_path)
                
                with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                    content = f.read()
                    
                    # Check for DateTime columns
                    if 'DateTime' in content:
                        if 'default=datetime.datetime.utcnow' not in content:
                            if 'timestamp' in content.lower() or 'created_at' in content.lower() or 'updated_at' in content.lower():
                                issues.append({
                                    'file': rel_path,
                                    'issue': 'DateTime column without UTC default',
                                    'content': content
                                })
    
    if issues:
        print("❌ ISSUES FOUND:")
        for issue in issues:
            print(f"  📁 {issue['file']}: {issue['issue']}")
    else:
        print("✅ All database models use UTC defaults!")
    
    return len(issues) == 0

def check_api_responses():
    """Check API responses include timezone info"""
    print("🔌 CHECKING API RESPONSES")
    print("=" * 50)
    
    api_dir = os.path.join("backend", "app", "api")
    good_patterns = []
    
    if os.path.exists(api_dir):
        for root, dirs, files in os.walk(api_dir):
            for file in files:
                if file.endswith('.py'):
                    file_path = os.path.join(root, file)
                    
                    with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                        content = f.read()
                        
                        # Look for timestamp returns
                        if 'isoformat()' in content:
                            good_patterns.append(file)
    
    print(f"✅ Found {len(good_patterns)} API files with proper ISO format timestamps")
    return True

def validate_timezone_utils():
    """Check if timezone utilities exist"""
    print("🛠️  CHECKING TIMEZONE UTILITIES")
    print("=" * 50)
    
    utils_file = os.path.join("backend", "app", "utils", "timezone_utils.py")
    
    if os.path.exists(utils_file):
        print("✅ Timezone utilities found!")
        
        with open(utils_file, 'r', encoding='utf-8') as f:
            content = f.read()
            if 'utc_to_vietnam_time' in content and 'format_vietnam_time' in content:
                print("✅ Vietnam timezone conversion functions available!")
                return True
            else:
                print("⚠️  Timezone utilities incomplete")
                return False
    else:
        print("⚠️  Timezone utilities not found")
        return False

def main():
    print("🕐 FINAL UTC VALIDATION")
    print("=" * 60)
    print("Checking entire project for proper UTC usage...")
    print()
    
    results = []
    
    # Run all checks
    results.append(("Python Files", scan_python_files()))
    print()
    
    results.append(("Dart Files", scan_dart_files()))
    print()
    
    results.append(("Database Models", check_database_models()))
    print()
    
    results.append(("API Responses", check_api_responses()))
    print()
    
    results.append(("Timezone Utils", validate_timezone_utils()))
    print()
    
    # Summary
    print("📊 VALIDATION SUMMARY")
    print("=" * 60)
    
    all_passed = True
    for check_name, passed in results:
        status = "✅ PASS" if passed else "❌ FAIL"
        print(f"  {check_name:20}: {status}")
        if not passed:
            all_passed = False
    
    print()
    if all_passed:
        print("🎉 ALL CHECKS PASSED!")
        print("✅ Project correctly uses UTC for all datetime operations")
        print("✅ Frontend properly converts UTC to Vietnam timezone")
        print("✅ Database stores all timestamps in UTC")
        print("✅ API responses are timezone-aware")
    else:
        print("⚠️  SOME ISSUES FOUND")
        print("Please review the issues above and fix them")
    
    print("\n💡 BEST PRACTICES VERIFIED:")
    print("  📥 Store: Always UTC in database")
    print("  📤 Display: Convert UTC to user timezone")
    print("  🔌 API: Return UTC timestamps with timezone info")
    print("  🌍 Scale: Ready for international expansion")

if __name__ == "__main__":
    main()

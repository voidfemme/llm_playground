#!/usr/bin/env python3
"""
Script to replace logkontrol usage with new logging system.
"""

import re
from pathlib import Path


def fix_logging_in_file(file_path: Path) -> bool:
    """Fix logging imports and calls in a single file."""
    try:
        content = file_path.read_text()
        original_content = content
        
        # Replace import statements
        content = re.sub(
            r'from logkontrol import.*?\n',
            '''from ..utils.logging import (
    get_logger,
    log_function_call,
    log_json_content,
    log_message,
    log_variable,
    log_api_call,
    log_error
)
''',
            content,
            flags=re.DOTALL
        )
        
        # Add logger initialization to classes (basic pattern)
        content = re.sub(
            r'(class \w+.*?:\s+def __init__\(self.*?\).*?\n.*?super\(\).__init__\(.*?\))',
            r'\1\n        self.logger = get_logger(self.__class__.__name__.lower())',
            content,
            flags=re.DOTALL
        )
        
        # Replace log_funktion_kall patterns
        content = re.sub(
            r'log_funktion_kall\(\s*"[^"]*",\s*"([^"]*)"([^)]*)\)',
            r'log_function_call(self.logger, "\1"\2)',
            content
        )
        
        # Replace log_json_kontent patterns
        content = re.sub(
            r'log_json_kontent\(\s*"[^"]*",\s*([^)]*)\)',
            r'log_json_content(self.logger, \1)',
            content
        )
        
        # Replace log_message patterns
        content = re.sub(
            r'log_message\(\s*"[^"]*",\s*([^)]*)\)',
            r'log_message(self.logger, \1)',
            content
        )
        
        # Replace log_variable patterns
        content = re.sub(
            r'log_variable\(\s*"[^"]*",\s*([^)]*)\)',
            r'log_variable(self.logger, \1)',
            content
        )
        
        if content != original_content:
            file_path.write_text(content)
            print(f"✅ Fixed logging in {file_path}")
            return True
        else:
            print(f"ℹ️  No changes needed in {file_path}")
            return False
            
    except Exception as e:
        print(f"❌ Error processing {file_path}: {e}")
        return False


def main():
    """Fix logging in all source files."""
    src_dir = Path("src/chatbot_library")
    files_with_logkontrol = []
    
    # Find files that use logkontrol
    for py_file in src_dir.rglob("*.py"):
        try:
            content = py_file.read_text()
            if "logkontrol" in content:
                files_with_logkontrol.append(py_file)
        except Exception:
            continue
    
    print(f"Found {len(files_with_logkontrol)} files using logkontrol:")
    for file_path in files_with_logkontrol:
        print(f"  - {file_path}")
    
    print("\nFixing files...")
    fixed_count = 0
    for file_path in files_with_logkontrol:
        if fix_logging_in_file(file_path):
            fixed_count += 1
    
    print(f"\n✅ Fixed {fixed_count} files")


if __name__ == "__main__":
    main()
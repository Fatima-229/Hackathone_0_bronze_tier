#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Bronze Tier Verification Script

Tests that all Bronze Tier components are working correctly.

Usage:
    py scripts\verify.py [vault_path]
"""

import sys
import json
from pathlib import Path
from datetime import datetime


def check_folder_structure(vault_path: Path) -> bool:
    """Check that all required folders exist."""
    required_folders = [
        'Inbox',
        'Needs_Action',
        'Done',
        'Plans',
        'Logs',
        'Approved',
        'Rejected',
        'Briefings',
        'Invoices',
        'Accounting',
        'scripts'
    ]
    
    all_exist = True
    for folder in required_folders:
        folder_path = vault_path / folder
        if folder_path.exists() and folder_path.is_dir():
            print(f'  [OK] {folder}/')
        else:
            print(f'  [MISSING] {folder}/')
            all_exist = False
    
    return all_exist


def check_required_files(vault_path: Path) -> bool:
    """Check that all required files exist."""
    required_files = [
        'Dashboard.md',
        'Company_Handbook.md',
        'Business_Goals.md',
        'README.md',
        '.gitignore',
        '.env.example'
    ]
    
    all_exist = True
    for file in required_files:
        file_path = vault_path / file
        if file_path.exists() and file_path.is_file():
            print(f'  [OK] {file}')
        else:
            print(f'  [MISSING] {file}')
            all_exist = False
    
    return all_exist


def check_scripts(vault_path: Path) -> bool:
    """Check that all required scripts exist and are valid Python."""
    required_scripts = [
        'base_watcher.py',
        'filesystem_watcher.py',
        'orchestrator.py',
        'SKILL.md',
        'requirements.txt',
        'verify.py'
    ]
    
    all_exist = True
    for script in required_scripts:
        script_path = vault_path / 'scripts' / script
        if script_path.exists() and script_path.is_file():
            print(f'  [OK] scripts/{script}')
        else:
            print(f'  [MISSING] scripts/{script}')
            all_exist = False
    
    return all_exist


def check_python_syntax(vault_path: Path) -> bool:
    """Check Python syntax of all scripts."""
    import py_compile
    
    scripts = [
        'base_watcher.py',
        'filesystem_watcher.py',
        'orchestrator.py',
        'verify.py'
    ]
    
    all_valid = True
    for script in scripts:
        script_path = vault_path / 'scripts' / script
        try:
            py_compile.compile(script_path, doraise=True)
            print(f'  [OK] {script} - syntax OK')
        except py_compile.PyCompileError as e:
            print(f'  [ERROR] {script} - syntax error: {e}')
            all_valid = False
    
    return all_valid


def check_dashboard_template(vault_path: Path) -> bool:
    """Check that Dashboard.md has required placeholders."""
    dashboard_path = vault_path / 'Dashboard.md'
    if not dashboard_path.exists():
        return False
    
    content = dashboard_path.read_text(encoding='utf-8')
    
    required_placeholders = [
        '{{pending_count}}',
        '{{needs_action_count}}',
        '{{completed_today}}',
        '{{completed_this_week}}',
        '{{watcher_status}}',
        '{{orchestrator_status}}',
        '{{last_sync}}'
    ]
    
    all_present = True
    for placeholder in required_placeholders:
        if placeholder in content:
            print(f'  [OK] Placeholder: {placeholder}')
        else:
            print(f'  [MISSING] Placeholder: {placeholder}')
            all_present = False
    
    return all_present


def check_company_handbook(vault_path: Path) -> bool:
    """Check that Company_Handbook.md has required sections."""
    handbook_path = vault_path / 'Company_Handbook.md'
    if not handbook_path.exists():
        return False
    
    content = handbook_path.read_text(encoding='utf-8')
    
    required_sections = [
        'Rules of Engagement',
        'Decision Matrix',
        'Priority Levels',
        'Security Rules',
        'Human-in-the-Loop'
    ]
    
    all_present = True
    for section in required_sections:
        if section in content:
            print(f'  [OK] Section: {section}')
        else:
            print(f'  [MISSING] Section: {section}')
            all_present = False
    
    return all_present


def check_sample_content(vault_path: Path) -> bool:
    """Check that folders have sample content for demonstration."""
    print('\n--- Sample Content ---')
    
    checks = {
        'Inbox/*.md': 'Sample inbox item',
        'Needs_Action/*.md': 'Sample action file',
        'Plans/*.md': 'Sample plan',
        'Done/*.md': 'Sample completed task',
        'Logs/*.json': 'Sample log entry',
        'Briefings/*.md': 'Sample briefing',
        'Invoices/*.md': 'Invoice template',
        'Accounting/*.md': 'Accounting record'
    }
    
    all_present = True
    for pattern, description in checks.items():
        folder = pattern.split('/')[0]
        ext = '*' + pattern.split('.')[1] if '.' in pattern else '*'
        files = list((vault_path / folder).glob(ext))
        md_files = [f for f in files if f.suffix == '.md' or f.suffix == '.json']
        
        if md_files:
            print(f'  [OK] {description}: {md_files[0].name}')
        else:
            print(f'  [EMPTY] {description} in {folder}/')
            all_present = False
    
    return all_present


def run_test_workflow(vault_path: Path) -> bool:
    """Run a simple test workflow."""
    print('\n--- Test Workflow ---')
    
    # Create test file in Drop_Folder
    drop_folder = vault_path / 'Drop_Folder'
    drop_folder.mkdir(parents=True, exist_ok=True)
    
    test_file = drop_folder / 'test_verify.txt'
    test_content = f'Test file created at {datetime.now().isoformat()}'
    test_file.write_text(test_content)
    print(f'  [OK] Created test file: {test_file}')
    
    # Verify file watcher can detect it (manual verification)
    print(f'  [INFO] Run: py scripts/filesystem_watcher.py .')
    print(f'         To detect this file')
    
    return True


def check_bronze_tier_requirements(vault_path: Path) -> bool:
    """Check official Bronze Tier requirements from hackathon document."""
    print('\n--- Bronze Tier Requirements ---')
    
    requirements = [
        ('Dashboard.md exists', (vault_path / 'Dashboard.md').exists()),
        ('Company_Handbook.md exists', (vault_path / 'Company_Handbook.md').exists()),
        ('File System Watcher script', (vault_path / 'scripts' / 'filesystem_watcher.py').exists()),
        ('Claude Code integration (orchestrator)', (vault_path / 'scripts' / 'orchestrator.py').exists()),
        ('Folder: /Inbox', (vault_path / 'Inbox').exists()),
        ('Folder: /Needs_Action', (vault_path / 'Needs_Action').exists()),
        ('Folder: /Done', (vault_path / 'Done').exists()),
        ('Agent Skill (SKILL.md)', (vault_path / 'scripts' / 'SKILL.md').exists()),
    ]
    
    all_met = True
    for requirement, met in requirements:
        if met:
            print(f'  [OK] {requirement}')
        else:
            print(f'  [MISSING] {requirement}')
            all_met = False
    
    return all_met


def main():
    """Main verification function."""
    print('=' * 60)
    print('AI Employee Bronze Tier - Verification')
    print('=' * 60)
    
    # Get vault path
    if len(sys.argv) > 1:
        vault_path = Path(sys.argv[1])
    else:
        vault_path = Path(__file__).parent
    
    print(f'\nVault path: {vault_path.absolute()}')
    
    if not vault_path.exists():
        print(f'ERROR: Vault path does not exist: {vault_path}')
        sys.exit(1)
    
    all_passed = True
    
    # Check folder structure
    print('\n--- Folder Structure ---')
    if not check_folder_structure(vault_path):
        all_passed = False
    
    # Check required files
    print('\n--- Required Files ---')
    if not check_required_files(vault_path):
        all_passed = False
    
    # Check scripts
    print('\n--- Scripts ---')
    if not check_scripts(vault_path):
        all_passed = False
    
    # Check Python syntax
    print('\n--- Python Syntax ---')
    if not check_python_syntax(vault_path):
        all_passed = False
    
    # Check dashboard template
    print('\n--- Dashboard Template ---')
    if not check_dashboard_template(vault_path):
        all_passed = False
    
    # Check company handbook
    print('\n--- Company Handbook ---')
    if not check_company_handbook(vault_path):
        all_passed = False
    
    # Check sample content
    if not check_sample_content(vault_path):
        all_passed = False
    
    # Check Bronze Tier requirements
    if not check_bronze_tier_requirements(vault_path):
        all_passed = False
    
    # Run test workflow
    if not run_test_workflow(vault_path):
        all_passed = False
    
    # Summary
    print('\n' + '=' * 60)
    if all_passed:
        print('[SUCCESS] All checks passed! Bronze Tier is ready.')
        print('\nNext steps:')
        print('  1. Open vault in Obsidian to view Dashboard.md')
        print('  2. Copy .env.example to .env (optional)')
        print('  3. Run: py scripts/filesystem_watcher.py .')
        print('  4. Run: py scripts/orchestrator.py .')
        print('  5. Drop a file in Drop_Folder/ to test')
        print('  6. Use "claude" command to process files with Claude Code')
        sys.exit(0)
    else:
        print('[FAILED] Some checks failed. Please review above.')
        sys.exit(1)


if __name__ == '__main__':
    main()

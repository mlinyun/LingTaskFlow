#!/usr/bin/env python3
"""
LingTaskFlow 测试运行器

统一的测试执行入口，支持运行不同类型的测试

使用方法：
    python run_tests.py --all                # 运行所有测试
    python run_tests.py --auth               # 只运行认证测试
    python run_tests.py --permissions        # 只运行权限测试
    python run_tests.py --models             # 只运行模型测试
    python run_tests.py --unit               # 运行Django单元测试
    python run_tests.py --integration        # 运行集成测试
"""
import os
import sys
import argparse
import subprocess
import django

# 设置Django环境
project_root = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, project_root)
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'ling_task_flow_backend.settings')
django.setup()


def run_django_tests(test_path=None):
    """运行Django单元测试"""
    cmd = [sys.executable, 'manage.py', 'test']
    if test_path:
        cmd.append(test_path)
    
    print(f"运行Django测试: {' '.join(cmd)}")
    return subprocess.run(cmd, cwd=project_root)


def run_integration_tests(test_module=None):
    """运行集成测试（直接执行Python脚本）"""
    test_scripts = []
    
    if test_module == 'auth' or test_module is None:
        test_scripts.extend([
            'tests/auth/test_register_api.py',
            'tests/auth/test_login_api.py',
            'tests/auth/test_token_refresh.py',
        ])
    
    if test_module == 'permissions' or test_module is None:
        test_scripts.extend([
            'tests/permissions/test_all_permissions.py',
            'tests/permissions/test_permissions_fixed.py',
        ])
    
    if test_module == 'models' or test_module is None:
        test_scripts.extend([
            'tests/models/test_userprofile.py',
        ])
    
    success_count = 0
    total_count = len(test_scripts)
    
    for script in test_scripts:
        script_path = os.path.join(project_root, script)
        if os.path.exists(script_path):
            print(f"\n{'='*60}")
            print(f"运行集成测试: {script}")
            print(f"{'='*60}")
            
            result = subprocess.run([sys.executable, script_path], cwd=project_root)
            if result.returncode == 0:
                print(f"✅ {script} - 测试通过")
                success_count += 1
            else:
                print(f"❌ {script} - 测试失败")
        else:
            print(f"⚠️  测试文件不存在: {script}")
    
    print(f"\n{'='*60}")
    print(f"集成测试结果: {success_count}/{total_count} 通过")
    print(f"{'='*60}")
    
    return success_count == total_count


def main():
    parser = argparse.ArgumentParser(description='LingTaskFlow 测试运行器')
    parser.add_argument('--all', action='store_true', help='运行所有测试')
    parser.add_argument('--auth', action='store_true', help='运行认证相关测试')
    parser.add_argument('--permissions', action='store_true', help='运行权限相关测试')
    parser.add_argument('--models', action='store_true', help='运行模型相关测试')
    parser.add_argument('--unit', action='store_true', help='只运行Django单元测试')
    parser.add_argument('--integration', action='store_true', help='只运行集成测试')
    
    args = parser.parse_args()
    
    if not any(vars(args).values()):
        print("请指定测试类型，使用 --help 查看可用选项")
        return 1
    
    print("LingTaskFlow 测试运行器")
    print("=" * 60)
    
    if args.all:
        print("运行所有测试...")
        # 运行Django单元测试
        django_result = run_django_tests('tests')
        # 运行集成测试
        integration_result = run_integration_tests()
        return 0 if django_result.returncode == 0 and integration_result else 1
    
    elif args.unit:
        print("运行Django单元测试...")
        result = run_django_tests('tests')
        return result.returncode
    
    elif args.integration:
        print("运行集成测试...")
        result = run_integration_tests()
        return 0 if result else 1
    
    elif args.auth:
        print("运行认证相关测试...")
        # Django单元测试
        django_result = run_django_tests('tests.auth')
        # 集成测试
        integration_result = run_integration_tests('auth')
        return 0 if django_result.returncode == 0 and integration_result else 1
    
    elif args.permissions:
        print("运行权限相关测试...")
        # Django单元测试
        django_result = run_django_tests('tests.permissions')
        # 集成测试
        integration_result = run_integration_tests('permissions')
        return 0 if django_result.returncode == 0 and integration_result else 1
    
    elif args.models:
        print("运行模型相关测试...")
        # Django单元测试
        django_result = run_django_tests('tests.models')
        # 集成测试
        integration_result = run_integration_tests('models')
        return 0 if django_result.returncode == 0 and integration_result else 1


if __name__ == '__main__':
    sys.exit(main())

#!/usr/bin/env python3
"""
LingTaskFlow 依赖验证脚本
验证所有必需的包是否正确安装
"""
import importlib
import subprocess
import sys


def check_package(package_name, min_version=None):
    """检查包是否安装并满足版本要求"""
    try:
        module = importlib.import_module(package_name)

        # 获取版本信息
        pkg_version = None
        if hasattr(module, '__version__'):
            pkg_version = module.__version__
        elif hasattr(module, 'VERSION'):
            if isinstance(module.VERSION, tuple):
                pkg_version = '.'.join(map(str, module.VERSION))
            else:
                pkg_version = str(module.VERSION)
        elif hasattr(module, 'get_version'):
            pkg_version = module.get_version()

        status = "✅"
        version_info = ""

        if pkg_version:
            version_info = f" (v{pkg_version})"
            if min_version:
                try:
                    # 简单版本比较
                    current = tuple(map(int, pkg_version.split('.')[:3]))
                    required = tuple(map(int, min_version.split('.')[:3]))
                    if current < required:
                        status = "⚠️ "
                        version_info += f" - 需要 >= {min_version}"
                except ValueError:
                    # 版本解析失败，跳过比较
                    pass

        print(f"{status} {package_name}{version_info}")
        return True

    except ImportError:
        print(f"❌ {package_name} - 未安装")
        return False
    except Exception as e:
        print(f"⚠️  {package_name} - 检查失败: {e}")
        return False


def check_django_setup():
    """检查Django项目配置"""
    try:
        import django
        from django.conf import settings
        from django.core.management import execute_from_command_line

        # 设置Django环境
        import os
        os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'ling_task_flow_backend.settings')
        django.setup()

        print("\n🔧 Django配置检查:")
        print(f"✅ Django版本: {django.get_version()}")
        print(f"✅ 设置模块: {settings.SETTINGS_MODULE}")
        print(f"✅ 数据库引擎: {settings.DATABASES['default']['ENGINE']}")
        print(f"✅ 已安装应用: {len(settings.INSTALLED_APPS)} 个")

        return True
    except Exception as e:
        print(f"❌ Django配置检查失败: {e}")
        return False


def run_system_check():
    """运行Django系统检查"""
    try:
        print("\n🔍 Django系统检查:")
        result = subprocess.run([
            sys.executable, 'manage.py', 'check'
        ], capture_output=True, text=True)

        if result.returncode == 0:
            print("✅ 系统检查通过")
            if result.stdout.strip():
                print(f"   输出: {result.stdout.strip()}")
        else:
            print("❌ 系统检查失败")
            if result.stderr:
                print(f"   错误: {result.stderr.strip()}")

        return result.returncode == 0
    except Exception as e:
        print(f"❌ 系统检查失败: {e}")
        return False


def main():
    """主函数"""
    print("🔍 LingTaskFlow 依赖验证")
    print("=" * 50)

    # 核心Django包
    print("\n📦 核心Django包:")
    core_packages = [
        ("django", "5.2.0"),
        ("rest_framework", "3.14.0"),
        ("rest_framework_simplejwt", "5.0.0"),
    ]

    core_ok = all(check_package(pkg, ver) for pkg, ver in core_packages)

    # 第三方依赖
    print("\n📦 第三方依赖:")
    third_party_packages = [
        "corsheaders",
        "django_filters",
        "jwt",
        "cryptography",
    ]

    third_party_ok = all(check_package(pkg) for pkg in third_party_packages)

    # 可选依赖
    print("\n📦 可选依赖:")
    optional_packages = [
        "PIL",  # Pillow
        "redis",
        "celery",
        "gunicorn",
    ]

    for pkg in optional_packages:
        check_package(pkg)

    # Django配置检查
    django_ok = check_django_setup()

    # 系统检查
    system_ok = run_system_check()

    # 总结
    print("\n" + "=" * 50)
    print("📊 验证结果:")

    if core_ok and third_party_ok and django_ok and system_ok:
        print("✅ 所有关键依赖已正确安装，项目可以正常运行！")
        return 0
    else:
        print("❌ 发现问题，请检查上述错误信息")
        if not core_ok:
            print("   - 核心Django包存在问题")
        if not third_party_ok:
            print("   - 第三方依赖存在问题")
        if not django_ok:
            print("   - Django配置存在问题")
        if not system_ok:
            print("   - Django系统检查失败")
        return 1


if __name__ == "__main__":
    sys.exit(main())

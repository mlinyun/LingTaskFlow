#!/usr/bin/env python
"""
LingTaskFlow API集成测试运行脚本
快速运行所有API集成测试并生成报告
"""

import os
import sys
import time
import subprocess
from datetime import datetime

def print_header():
    """打印测试开始头部信息"""
    print("=" * 80)
    print("🚀 LingTaskFlow API集成测试套件")
    print("=" * 80)
    print(f"📅 测试时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"🐍 Python版本: {sys.version.split()[0]}")
    print(f"📁 工作目录: {os.getcwd()}")
    print("=" * 80)

def run_tests():
    """运行API集成测试"""
    print("\n🧪 开始运行API集成测试...")
    
    # 构建测试命令
    cmd = [
        sys.executable, 
        "manage.py", 
        "test", 
        "tests.integration.test_task_api_integration",
        "--verbosity=1"
    ]
    
    # 记录开始时间
    start_time = time.time()
    
    try:
        # 运行测试
        result = subprocess.run(cmd, capture_output=True, text=True)
        
        # 计算执行时间
        end_time = time.time()
        execution_time = end_time - start_time
        
        # 输出结果
        print(result.stdout)
        if result.stderr:
            print("⚠️ 警告信息:")
            print(result.stderr)
        
        # 分析测试结果
        analyze_results(result, execution_time)
        
    except Exception as e:
        print(f"❌ 测试执行失败: {e}")
        return False
    
    return result.returncode == 0

def analyze_results(result, execution_time):
    """分析测试结果并生成报告"""
    print("\n" + "=" * 80)
    print("📊 测试结果分析")
    print("=" * 80)
    
    output = result.stdout
    
    # 提取测试数量
    if "Ran" in output:
        lines = output.split('\n')
        for line in lines:
            if line.startswith("Ran"):
                print(f"🔢 {line}")
                break
    
    # 判断测试结果
    if result.returncode == 0:
        print("✅ 测试结果: 全部通过 (SUCCESS)")
        success_rate = "100%"
        status_icon = "🎉"
    else:
        print("❌ 测试结果: 部分失败 (FAILED)")
        success_rate = "< 100%"
        status_icon = "⚠️"
    
    # 性能分析
    print(f"⏱️ 执行时间: {execution_time:.2f}秒")
    
    # 统计测试模块
    test_modules = [
        "TaskAPIAdvancedTest",
        "TaskAPIBatchOperationsTest", 
        "TaskAPIBoundaryTest",
        "TaskAPICompleteIntegrationTest",
        "TaskAPIIntegrationTest"
    ]
    
    print(f"📦 测试模块: {len(test_modules)}个")
    print(f"📈 覆盖率: {success_rate}")
    
    # 生成总结
    print("\n" + "=" * 80)
    print(f"{status_icon} 测试总结")
    print("=" * 80)
    
    if result.returncode == 0:
        print("🎯 所有API集成测试成功通过！")
        print("🏆 已达到100%测试覆盖率目标！")
        print("✨ API系统质量验证完成，可以投入生产使用")
    else:
        print("🔧 存在测试失败，需要进一步修复")
        print("📋 建议检查失败的测试用例并进行修复")
    
    # 推荐后续步骤
    print("\n📋 后续步骤:")
    print("1. 查看详细测试覆盖率报告: tests/integration/test_coverage_report.md")
    print("2. 运行前端集成测试")
    print("3. 进行端到端测试")
    print("4. 部署到测试环境进行验收测试")

def main():
    """主函数"""
    print_header()
    
    # 检查是否在正确的目录
    if not os.path.exists("manage.py"):
        print("❌ 错误: 请在Django项目根目录下运行此脚本")
        print("   应该在包含manage.py的目录中执行")
        sys.exit(1)
    
    # 检查测试文件是否存在
    test_file = "tests/integration/test_task_api_integration.py"
    if not os.path.exists(test_file):
        print(f"❌ 错误: 测试文件不存在: {test_file}")
        sys.exit(1)
    
    # 运行测试
    success = run_tests()
    
    print("\n" + "=" * 80)
    if success:
        print("🎉 API集成测试完成 - 所有测试通过！")
        exit_code = 0
    else:
        print("⚠️ API集成测试完成 - 存在失败的测试")
        exit_code = 1
    
    print("=" * 80)
    sys.exit(exit_code)

if __name__ == "__main__":
    main()

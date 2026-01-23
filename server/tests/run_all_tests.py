import asyncio
import subprocess
import sys
from pathlib import Path


def run_test(test_file):
    print(f"\n{'='*60}")
    print(f"运行测试: {test_file.name}")
    print('='*60)
    
    result = subprocess.run(
        [sys.executable, str(test_file)],
        cwd=test_file.parent,
        capture_output=False
    )
    
    return result.returncode == 0


def main():
    tests_dir = Path(__file__).parent
    
    tests = [
        tests_dir / "test_checkpointer.py",
        tests_dir / "test_conversation.py",
        tests_dir / "test_persistence.py",
    ]
    
    print("=" * 60)
    print("开始运行测试套件")
    print("=" * 60)
    
    results = {}
    for test_file in tests:
        if test_file.exists():
            results[test_file.name] = run_test(test_file)
        else:
            print(f"⚠️ 测试文件不存在: {test_file}")
            results[test_file.name] = False
    
    print("\n" + "=" * 60)
    print("测试结果汇总")
    print("=" * 60)
    
    for test_name, passed in results.items():
        status = "✅ 通过" if passed else "❌ 失败"
        print(f"{status} - {test_name}")
    
    print("\n" + "=" * 60)
    print("API 测试 (需要服务器运行)")
    print("=" * 60)
    print("手动运行: python test_api.py")
    print("前提条件: 在另一个终端运行 'cd server/chatbox && python main.py'")
    
    all_passed = all(results.values())
    
    if all_passed:
        print("\n✅ 所有测试通过！")
        return 0
    else:
        print("\n❌ 部分测试失败")
        return 1


if __name__ == "__main__":
    sys.exit(main())

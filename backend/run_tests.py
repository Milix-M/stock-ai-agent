"""
テスト実行スクリプト
"""
import subprocess
import sys


def run_tests():
    """すべてのテストを実行"""
    test_modules = [
        "tests.test_security",
        "tests.test_stock_service",
        "tests.test_pattern_service",
        "tests.test_watchlist_service",
        "tests.test_recommendation_service",
        "tests.test_notification_service",
        "tests.test_market_service",
    ]
    
    print("=" * 60)
    print("Stock AI Agent - テスト実行")
    print("=" * 60)
    
    failed = []
    passed = []
    
    for module in test_modules:
        print(f"\n📦 {module} を実行中...")
        print("-" * 40)
        
        result = subprocess.run(
            [sys.executable, "-m", "pytest", module, "-v"],
            capture_output=True,
            text=True
        )
        
        if result.returncode == 0:
            print(f"✅ {module} - 成功")
            passed.append(module)
        else:
            print(f"❌ {module} - 失敗")
            print(result.stdout)
            print(result.stderr)
            failed.append(module)
    
    print("\n" + "=" * 60)
    print("テスト結果サマリー")
    print("=" * 60)
    print(f"成功: {len(passed)} / {len(passed) + len(failed)}")
    
    if failed:
        print(f"失敗: {len(failed)}")
        print("\n失敗したモジュール:")
        for f in failed:
            print(f"  - {f}")
        return 1
    else:
        print("\n🎉 すべてのテストが成功しました！")
        return 0


if __name__ == "__main__":
    sys.exit(run_tests())
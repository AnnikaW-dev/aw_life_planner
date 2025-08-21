# tests/run_tests.py

import subprocess
import sys
import os

def run_command(command):
    """Run a command using the current Python executable"""
    try:
        # Use the same Python executable that's running this script
        cmd = [sys.executable] + command.split()[1:]  # Skip 'python' and use sys.executable
        result = subprocess.run(cmd, cwd=os.getcwd())
        return result.returncode == 0
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

def smoke_test():
    """Quick system check"""
    print("💨 Smoke Test...")
    print("-" * 40)

    success = run_command("python manage.py check")
    if success:
        print("✅ Django setup is working!")
    else:
        print("❌ Django setup has issues!")
    return success

def webhook_tests():
    """Run webhook tests"""
    print("🧪 Running Webhook Tests...")
    print("-" * 40)

    success = run_command("python manage.py test tests.test_webhooks checkout.tests -v 2")
    if success:
        print("✅ Webhook tests passed!")
    else:
        print("❌ Webhook tests failed!")
    return success

def all_tests():
    """Run all tests"""
    print("🧪 Running All Tests...")
    print("-" * 40)

    success = run_command("python manage.py test -v 2")
    if success:
        print("✅ All tests passed!")
    else:
        print("❌ Some tests failed!")
    return success

def main():
    if len(sys.argv) > 1:
        command = sys.argv[1]

        if command == 'smoke':
            success = smoke_test()
        elif command == 'webhooks':
            success = webhook_tests()
        elif command == 'all':
            success = all_tests()
        else:
            print(f"Unknown command: {command}")
            print("Available: smoke, webhooks, all")
            sys.exit(1)
    else:
        print("Usage: python tests/run_tests.py [smoke|webhooks|all]")
        print("Or just use Django directly:")
        print("  python manage.py check")
        print("  python manage.py test")
        sys.exit(1)

    sys.exit(0 if success else 1)

if __name__ == "__main__":
    main()

#!/usr/bin/env python3
"""
Script untuk menguji instalasi tools security scanner.
Jalankan script ini untuk memverifikasi bahwa semua tools sudah terinstal dengan benar.
"""

import subprocess
import sys
import os
from typing import Dict, Tuple

def test_python() -> Tuple[bool, str]:
    """Test Python installation."""
    try:
        version = sys.version
        major, minor = sys.version_info[:2]
        if major >= 3 and minor >= 7:
            return True, f"Python {major}.{minor} - OK"
        else:
            return False, f"Python {major}.{minor} - Versi terlalu lama (minimal 3.7)"
    except Exception as e:
        return False, f"Python error: {str(e)}"

def test_pip() -> Tuple[bool, str]:
    """Test pip installation."""
    try:
        result = subprocess.run(
            [sys.executable, "-m", "pip", "--version"],
            capture_output=True,
            text=True,
            timeout=10
        )
        if result.returncode == 0:
            return True, f"pip - OK ({result.stdout.strip()})"
        else:
            return False, f"pip error: {result.stderr}"
    except Exception as e:
        return False, f"pip error: {str(e)}"

def test_semgrep() -> Tuple[bool, str]:
    """Test Semgrep installation."""
    try:
        # Test command line access
        result = subprocess.run(
            ["semgrep", "--version"],
            capture_output=True,
            text=True,
            timeout=30
        )
        if result.returncode == 0:
            version = result.stdout.strip()
            return True, f"Semgrep - OK ({version})"
        else:
            return False, f"Semgrep tidak dapat diakses: {result.stderr}"
    except FileNotFoundError:
        return False, "Semgrep tidak ditemukan di PATH"
    except Exception as e:
        return False, f"Semgrep error: {str(e)}"

def test_grype() -> Tuple[bool, str]:
    """Test Grype installation."""
    try:
        # Test command line access
        result = subprocess.run(
            ["grype", "version"],
            capture_output=True,
            text=True,
            timeout=30
        )
        if result.returncode == 0:
            version = result.stdout.strip()
            return True, f"Grype - OK ({version})"
        else:
            return False, f"Grype tidak dapat diakses: {result.stderr}"
    except FileNotFoundError:
        return False, "Grype tidak ditemukan di PATH"
    except Exception as e:
        return False, f"Grype error: {str(e)}"

def test_trufflehog() -> Tuple[bool, str]:
    """Test TruffleHog installation."""
    try:
        # Test Python import
        import truffleHog
        return True, "TruffleHog - OK (Python module)"
    except ImportError:
        return False, "TruffleHog tidak terinstal (pip install truffleHog)"
    except Exception as e:
        return False, f"TruffleHog error: {str(e)}"

def test_scanner_modules() -> Dict[str, Tuple[bool, str]]:
    """Test scanner modules."""
    modules = {
        "downloader": "scanner.downloader",
        "semgrep_scan": "scanner.semgrep_scan",
        "grype_scan": "scanner.grype_scan",
        "trufflehog_scan": "scanner.trufflehog_scan",
        "report_generator": "scanner.report_generator"
    }
    
    results = {}
    for name, module in modules.items():
        try:
            __import__(module)
            results[name] = (True, f"{name} module - OK")
        except ImportError as e:
            results[name] = (False, f"{name} module error: {str(e)}")
        except Exception as e:
            results[name] = (False, f"{name} module error: {str(e)}")
    
    return results

def test_dependencies() -> Dict[str, Tuple[bool, str]]:
    """Test Python dependencies."""
    dependencies = {
        "requests": "requests",
        "beautifulsoup4": "bs4",
        "reportlab": "reportlab",
        "python-telegram-bot": "telegram",
        "python-dotenv": "dotenv",
        "truffleHog": "truffleHog"
    }
    
    results = {}
    for package_name, import_name in dependencies.items():
        try:
            __import__(import_name)
            results[package_name] = (True, f"{package_name} - OK")
        except ImportError:
            results[package_name] = (False, f"{package_name} - MISSING (pip install {package_name})")
        except Exception as e:
            results[package_name] = (False, f"{package_name} - ERROR: {str(e)}")
    
    return results

def check_directories() -> Dict[str, Tuple[bool, str]]:
    """Check required directories."""
    dirs = ["output", "temp", "scanner"]
    results = {}
    
    for dir_name in dirs:
        if os.path.exists(dir_name):
            if os.path.isdir(dir_name):
                results[dir_name] = (True, f"Directory {dir_name} - OK")
            else:
                results[dir_name] = (False, f"{dir_name} exists but not a directory")
        else:
            results[dir_name] = (False, f"Directory {dir_name} - MISSING")
    
    return results

def print_results(title: str, results: Dict[str, Tuple[bool, str]]):
    """Print test results."""
    print(f"\n{'='*50}")
    print(f"{title}")
    print(f"{'='*50}")
    
    for name, (success, message) in results.items():
        status = "✅" if success else "❌"
        print(f"{status} {message}")

def main():
    """Main test function."""
    print("🔍 JavaScript Security Scanner - Tool Installation Test")
    print("=" * 60)
    
    # Test basic requirements
    print("\n📋 Testing Basic Requirements...")
    basic_tests = {
        "Python": test_python(),
        "pip": test_pip()
    }
    
    for name, (success, message) in basic_tests.items():
        status = "✅" if success else "❌"
        print(f"{status} {message}")
    
    # Test security tools
    print("\n🔒 Testing Security Tools...")
    security_tests = {
        "Semgrep": test_semgrep(),
        "Grype": test_grype(),
        "TruffleHog": test_trufflehog()
    }
    
    for name, (success, message) in security_tests.items():
        status = "✅" if success else "❌"
        print(f"{status} {message}")
    
    # Test Python dependencies
    print("\n📦 Testing Python Dependencies...")
    dep_results = test_dependencies()
    for name, (success, message) in dep_results.items():
        status = "✅" if success else "❌"
        print(f"{status} {message}")
    
    # Test scanner modules
    print("\n🔧 Testing Scanner Modules...")
    module_results = test_scanner_modules()
    for name, (success, message) in module_results.items():
        status = "✅" if success else "❌"
        print(f"{status} {message}")
    
    # Test directories
    print("\n📁 Testing Directories...")
    dir_results = check_directories()
    for name, (success, message) in dir_results.items():
        status = "✅" if success else "❌"
        print(f"{status} {message}")
    
    # Summary
    print("\n" + "="*60)
    print("📊 SUMMARY")
    print("="*60)
    
    all_results = {**basic_tests, **security_tests, **dep_results, **module_results, **dir_results}
    total_tests = len(all_results)
    passed_tests = sum(1 for success, _ in all_results.values() if success)
    failed_tests = total_tests - passed_tests
    
    print(f"Total Tests: {total_tests}")
    print(f"✅ Passed: {passed_tests}")
    print(f"❌ Failed: {failed_tests}")
    
    if failed_tests == 0:
        print("\n🎉 Semua tests berhasil! Scanner siap digunakan.")
        print("\n🚀 Jalankan scanner dengan: python run.py -u https://example.com")
    else:
        print(f"\n⚠️  {failed_tests} tests gagal. Silakan perbaiki masalah di atas.")
        print("\n📚 Untuk bantuan instalasi:")
        print("   - Lihat INSTALLATION.md")
        print("   - Jalankan install_tools.bat (Windows)")
        print("   - Lihat TROUBLESHOOTING.md untuk masalah umum")
    
    print("\n" + "="*60)
    return failed_tests == 0

if __name__ == "__main__":
    try:
        success = main()
        sys.exit(0 if success else 1)
    except KeyboardInterrupt:
        print("\n\n⏹️  Test dibatalkan oleh user.")
        sys.exit(1)
    except Exception as e:
        print(f"\n\n💥 Error tidak terduga: {str(e)}")
        sys.exit(1)
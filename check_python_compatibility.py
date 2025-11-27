#!/usr/bin/env python3
"""
Python Package Compatibility Checker
=====================================

Checks if your installed Python packages support a specific Python version
by querying PyPI metadata.

Usage:
    python check_python_compatibility.py [--version 3.14] [--full] [--save results.json]

Examples:
    # Check for Python 3.14 support (sample of 50 packages)
    python check_python_compatibility.py --version 3.14

    # Full check of all packages (takes longer)
    python check_python_compatibility.py --version 3.13 --full

    # Save results to JSON file
    python check_python_compatibility.py --version 3.14 --save results.json

Author: Generated via Warp AI
License: MIT
"""

import json
import subprocess
import sys
import urllib.request
import urllib.error
import argparse
from datetime import datetime
from typing import Dict, List, Tuple


class CompatibilityChecker:
    """Check Python package compatibility with specified Python version."""
    
    def __init__(self, target_version: str = "3.14"):
        self.target_version = target_version
        self.target_major_minor = '.'.join(target_version.split('.')[:2])
        
    def get_installed_packages(self) -> List[Dict[str, str]]:
        """Get list of all installed packages."""
        result = subprocess.run(
            [sys.executable, '-m', 'pip', 'list', '--format=json'],
            capture_output=True,
            text=True,
            check=False
        )
        
        if result.returncode != 0:
            print("Error: Could not get package list from pip")
            return []
        
        return json.loads(result.stdout)
    
    def check_package_compatibility(self, package_name: str) -> Tuple[str, List[str]]:
        """
        Check if a package supports the target Python version.
        
        Returns:
            Tuple of (status, python_versions)
            status: "compatible", "likely", "incompatible", "unknown"
        """
        try:
            url = f'https://pypi.org/pypi/{package_name}/json'
            req = urllib.request.Request(
                url, 
                headers={'User-Agent': 'Python-Compatibility-Checker/1.0'}
            )
            
            with urllib.request.urlopen(req, timeout=5) as response:
                data = json.loads(response.read())
                
                # Get Python version classifiers
                classifiers = data.get('info', {}).get('classifiers', [])
                py_versions = [
                    c.split('::')[-1].strip() 
                    for c in classifiers 
                    if 'Programming Language :: Python ::' in c 
                    and not 'Implementation' in c
                ]
                
                # Check for target version support
                has_target = any(self.target_major_minor in v for v in py_versions)
                
                # Check for previous version
                prev_minor = int(self.target_major_minor.split('.')[1]) - 1
                prev_version = f"3.{prev_minor}"
                has_previous = any(prev_version in v for v in py_versions)
                
                if has_target:
                    return "compatible", py_versions
                elif has_previous or not py_versions:
                    # If it supports previous version or no info, it might work
                    return "likely", py_versions
                else:
                    return "incompatible", py_versions
                    
        except urllib.error.HTTPError as e:
            if e.code == 404:
                return "unknown", ["Package not found on PyPI"]
            return "unknown", [f"HTTP Error: {e.code}"]
        except Exception as e:
            return "unknown", [f"Error: {str(e)}"]
    
    def analyze_packages(self, packages: List[Dict[str, str]], full_check: bool = False) -> Dict:
        """
        Analyze package compatibility.
        
        Args:
            packages: List of package dictionaries
            full_check: If True, check all packages. If False, sample.
        """
        total = len(packages)
        check_count = total if full_check else min(50, total)
        
        print(f"\n{'='*70}")
        print(f"Python {self.target_version} Compatibility Check")
        print(f"{'='*70}")
        print(f"Total packages installed: {total}")
        print(f"Checking: {check_count} packages")
        print(f"Mode: {'FULL SCAN' if full_check else 'SAMPLE'}")
        print(f"Started: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print(f"{'='*70}\n")
        
        results = {
            'compatible': [],
            'likely': [],
            'incompatible': [],
            'unknown': []
        }
        
        packages_to_check = packages if full_check else packages[:check_count]
        
        for idx, pkg in enumerate(packages_to_check, 1):
            name = pkg['name']
            version = pkg['version']
            
            if idx % 10 == 0 or idx == 1:
                print(f"Progress: {idx}/{check_count} packages checked...")
            
            status, py_versions = self.check_package_compatibility(name)
            
            pkg_info = {
                'name': name,
                'version': version,
                'python_versions': py_versions
            }
            
            results[status].append(pkg_info)
        
        print(f"\nCompleted: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
        
        return results
    
    def print_results(self, results: Dict):
        """Print formatted results."""
        total = sum(len(results[k]) for k in results)
        
        print(f"\n{'='*70}")
        print(f"RESULTS SUMMARY")
        print(f"{'='*70}\n")
        
        # Compatible packages
        compatible = results['compatible']
        print(f"✅ COMPATIBLE with Python {self.target_version}: {len(compatible)} packages")
        if compatible:
            print(f"   ({len(compatible)/total*100:.1f}% of checked packages)")
            for pkg in compatible[:10]:
                print(f"   • {pkg['name']:30} (v{pkg['version']})")
            if len(compatible) > 10:
                print(f"   ... and {len(compatible)-10} more")
        
        print()
        
        # Likely compatible
        likely = results['likely']
        print(f"🟡 LIKELY COMPATIBLE: {len(likely)} packages")
        if likely:
            print(f"   ({len(likely)/total*100:.1f}% of checked packages)")
            print(f"   (No explicit {self.target_version} support, but may work)")
            for pkg in likely[:10]:
                max_py = max(pkg['python_versions']) if pkg['python_versions'] else 'Unknown'
                print(f"   • {pkg['name']:30} (max confirmed: {max_py})")
            if len(likely) > 10:
                print(f"   ... and {len(likely)-10} more")
        
        print()
        
        # Incompatible
        incompatible = results['incompatible']
        print(f"🔴 POTENTIALLY INCOMPATIBLE: {len(incompatible)} packages")
        if incompatible:
            print(f"   ({len(incompatible)/total*100:.1f}% of checked packages)")
            print(f"   (May need updates before upgrading Python)")
            for pkg in incompatible[:15]:
                max_py = max(pkg['python_versions']) if pkg['python_versions'] else 'Unknown'
                print(f"   • {pkg['name']:30} (max: {max_py})")
            if len(incompatible) > 15:
                print(f"   ... and {len(incompatible)-15} more")
        
        print()
        
        # Unknown
        unknown = results['unknown']
        if unknown:
            print(f"❓ COULD NOT VERIFY: {len(unknown)} packages")
            print(f"   ({len(unknown)/total*100:.1f}% of checked packages)")
            for pkg in unknown[:5]:
                print(f"   • {pkg['name']:30}")
            if len(unknown) > 5:
                print(f"   ... and {len(unknown)-5} more")
            print()
        
        print(f"{'='*70}")
        
        # Risk assessment
        compat_percent = len(compatible) / total * 100
        incompat_percent = len(incompatible) / total * 100
        
        print(f"\n📊 RISK ASSESSMENT for Python {self.target_version} upgrade:\n")
        
        if compat_percent >= 80:
            print("   ✅ LOW RISK - Most packages support this Python version")
        elif compat_percent >= 50:
            print("   🟡 MEDIUM RISK - Partial support, test thoroughly")
        elif incompat_percent >= 30:
            print("   🔴 HIGH RISK - Many packages may not work")
        else:
            print("   ⚠️  UNCERTAIN - Limited compatibility data available")
        
        print(f"\n   Compatible:     {compat_percent:.1f}%")
        print(f"   Incompatible:   {incompat_percent:.1f}%")
        print(f"   Likely/Unknown: {(len(likely) + len(unknown))/total*100:.1f}%")
        
        print(f"\n{'='*70}\n")
        
        # Recommendations
        print("💡 RECOMMENDATIONS:\n")
        
        if incompat_percent > 20:
            print("   1. DO NOT upgrade Python yet")
            print("   2. Wait for package updates")
            print("   3. Check incompatible packages for updates")
        elif incompat_percent > 10:
            print("   1. Test in isolated environment first")
            print("   2. Check critical packages manually")
            print("   3. Have rollback plan ready")
        else:
            print("   1. Create test environment to verify")
            print("   2. Check for known issues with critical packages")
            print("   3. Upgrade non-critical environments first")
        
        print(f"\n{'='*70}\n")
    
    def save_results(self, results: Dict, filename: str):
        """Save results to JSON file."""
        output = {
            'timestamp': datetime.now().isoformat(),
            'target_python_version': self.target_version,
            'current_python_version': f"{sys.version_info.major}.{sys.version_info.minor}.{sys.version_info.micro}",
            'total_checked': sum(len(results[k]) for k in results),
            'results': results,
            'summary': {
                'compatible': len(results['compatible']),
                'likely': len(results['likely']),
                'incompatible': len(results['incompatible']),
                'unknown': len(results['unknown'])
            }
        }
        
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(output, f, indent=2)
        
        print(f"✅ Results saved to: {filename}\n")


def main():
    parser = argparse.ArgumentParser(
        description='Check Python package compatibility with target Python version'
    )
    parser.add_argument(
        '--version',
        default='3.14',
        help='Target Python version to check (e.g., 3.14, 3.13)'
    )
    parser.add_argument(
        '--full',
        action='store_true',
        help='Check all installed packages (slower)'
    )
    parser.add_argument(
        '--save',
        metavar='FILE',
        help='Save results to JSON file'
    )
    
    args = parser.parse_args()
    
    # Initialize checker
    checker = CompatibilityChecker(target_version=args.version)
    
    # Get packages
    packages = checker.get_installed_packages()
    
    if not packages:
        print("Error: No packages found")
        sys.exit(1)
    
    # Analyze
    results = checker.analyze_packages(packages, full_check=args.full)
    
    # Print results
    checker.print_results(results)
    
    # Save if requested
    if args.save:
        checker.save_results(results, args.save)


if __name__ == '__main__':
    main()

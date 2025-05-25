#!/usr/bin/env python3
"""
scripts/env_audit.py: CLI to audit Ethical AI Framework environment.

This tool performs structured checks against the environment to identify
potential conflicts with ethical AI framework requirements.
"""

import os
import sys
import json
import shutil
import platform
import subprocess
import argparse
from pathlib import Path
from typing import Dict, List, Any, Optional


class EnvironmentAuditor:
    """Audits the current environment for ethical AI framework compliance."""
    
    def __init__(self, config: Optional[Dict] = None):
        self.config = config or {
            "model": "gpt-4o-mini",
            "temperature": 0.2,
            "max_tokens": 1200,
            "timeout": 30
        }
        
    def gather_environment(self) -> Dict[str, Any]:
        """Collect comprehensive environment information."""
        data = {
            "python_version": platform.python_version(),
            "platform": platform.platform(),
            "cwd": os.getcwd()
        }
        
        # Package information with error handling
        try:
            reqs = subprocess.check_output(
                [sys.executable, "-m", "pip", "freeze"], 
                text=True, 
                timeout=self.config["timeout"]
            )
            data["pip_freeze"] = reqs.splitlines()
        except subprocess.TimeoutExpired:
            data["pip_freeze_error"] = "Timeout expired"
            data["pip_freeze"] = []
        except Exception as e:
            data["pip_freeze_error"] = str(e)
            data["pip_freeze"] = []
        
        # Tool availability
        data["docker_installed"] = bool(shutil.which("docker"))
        data["kubectl_installed"] = bool(shutil.which("kubectl"))
        data["git_installed"] = bool(shutil.which("git"))
        
        # CI/CD configuration files
        data["ci_configs"] = self._scan_ci_configs()
        
        # Project structure
        data["project_structure"] = self._scan_project_structure()
        
        # Configuration files
        data["config_files"] = self._scan_config_files()
        
        # Python package files
        data["package_files"] = self._scan_package_files()
        
        return data
    
    def _scan_ci_configs(self) -> List[str]:
        """Scan for CI/CD configuration files."""
        ci_files = []
        
        # GitHub Actions
        github_dir = Path(".github")
        if github_dir.is_dir():
            workflows_dir = github_dir / "workflows"
            if workflows_dir.is_dir():
                for file_path in workflows_dir.glob("*.yml"):
                    ci_files.append(str(file_path))
                for file_path in workflows_dir.glob("*.yaml"):
                    ci_files.append(str(file_path))
        
        # Other CI systems
        ci_patterns = [".travis.yml", ".circleci/config.yml", "azure-pipelines.yml"]
        for pattern in ci_patterns:
            if Path(pattern).exists():
                ci_files.append(pattern)
                
        return ci_files
    
    def _scan_project_structure(self) -> Dict[str, Any]:
        """Analyze project directory structure."""
        structure = {}
        
        # Check for key directories
        key_dirs = ["core", "ethical_engine", "scripts", "tests", "docs"]
        for dir_name in key_dirs:
            dir_path = Path(dir_name)
            structure[f"{dir_name}_exists"] = dir_path.is_dir()
            
            # Check for __init__.py in Python packages
            if dir_name in ["core", "ethical_engine"] and dir_path.is_dir():
                init_file = dir_path / "__init__.py"
                structure[f"{dir_name}_has_init"] = init_file.exists()
        
        # Top-level directories (excluding hidden)
        structure["top_level_dirs"] = [
            d.name for d in Path(".").iterdir() 
            if d.is_dir() and not d.name.startswith(".")
        ]
        
        return structure
    
    def _scan_config_files(self) -> Dict[str, bool]:
        """Check for important configuration files."""
        config_files = {
            "pytest.ini": Path("pytest.ini").exists(),
            "pyproject.toml": Path("pyproject.toml").exists(),
            "setup.py": Path("setup.py").exists(),
            "requirements.txt": Path("requirements.txt").exists(),
            ".gitignore": Path(".gitignore").exists(),
            "README.md": Path("README.md").exists(),
            "LICENSE": Path("LICENSE").exists() or Path("LICENSE.txt").exists()
        }
        return config_files
    
    def _scan_package_files(self) -> Dict[str, Any]:
        """Analyze Python package configuration."""
        package_info = {}
        
        # Check setup.py content
        setup_py = Path("setup.py")
        if setup_py.exists():
            try:
                with open(setup_py, 'r') as f:
                    content = f.read()
                    package_info["setup_py_has_install_requires"] = "install_requires" in content
                    package_info["setup_py_has_python_requires"] = "python_requires" in content
            except Exception as e:
                package_info["setup_py_error"] = str(e)
        
        # Check pyproject.toml
        pyproject = Path("pyproject.toml")
        if pyproject.exists():
            try:
                # Basic existence check - could be enhanced with TOML parsing
                package_info["pyproject_toml_exists"] = True
            except Exception as e:
                package_info["pyproject_error"] = str(e)
        
        # Check requirements.txt
        req_txt = Path("requirements.txt")
        if req_txt.exists():
            try:
                with open(req_txt, 'r') as f:
                    requirements = f.read().strip()
                    package_info["requirements_txt_empty"] = len(requirements) == 0
                    package_info["requirements_count"] = len([
                        line for line in requirements.split('\n') 
                        if line.strip() and not line.startswith('#')
                    ])
            except Exception as e:
                package_info["requirements_error"] = str(e)
        
        return package_info
    
    def build_audit_prompt(self, env_data: Dict[str, Any]) -> str:
        """Build structured audit prompt for LLM analysis."""
        summary = json.dumps(env_data, indent=2)
        
        checklist = """
We need to verify these environment requirements for the Ethical AI Framework:

1. **Dependencies**: setup.py or requirements.txt defines install_requires with key packages (openai, pytest, etc.)
2. **CI/CD**: .github/workflows/*.yml exists and runs pytest for automated testing
3. **Package Structure**: core/ and ethical_engine/ directories exist with proper __init__.py files
4. **Configuration**: pytest.ini exists for test configuration; .gitignore includes sensitive files
5. **Credentials**: Environment variables used for API keys (no hardcoded secrets)
6. **Persistence**: ledger/ directory exists and is writable; scripts/ directory exists
7. **Python Version**: Current Python version is compatible with project requirements

For each requirement, evaluate:
- PASS: Requirement is met
- FAIL: Requirement is not met
- WARN: Requirement is partially met or needs attention
- UNKNOWN: Cannot determine status

Please analyze the environment data and respond with a JSON array of objects, each containing:
- "check": Brief description of what was checked
- "status": One of "PASS", "FAIL", "WARN", "UNKNOWN"  
- "issue": Description of any problems found (empty string if none)
- "recommendation": Specific action to take (empty string if none needed)
"""
        
        return (
            f"You are an expert in ethical AI environment validation.\n\n"
            f"Environment snapshot:\n```json\n{summary}\n```\n\n"
            f"{checklist}\n\n"
            "Respond with valid JSON only - no additional text or formatting."
        )
    
    def call_model(self, prompt: str) -> str:
        """Call OpenAI API with the audit prompt."""
        try:
            import openai
            
            # Check for API key
            api_key = os.getenv("OPENAI_API_KEY")
            if not api_key:
                raise ValueError("OPENAI_API_KEY environment variable not set")
            
            client = openai.OpenAI(api_key=api_key)
            
            resp = client.chat.completions.create(
                model=self.config["model"],
                messages=[{"role": "user", "content": prompt}],
                temperature=self.config["temperature"],
                max_tokens=self.config["max_tokens"],
            )
            
            return resp.choices[0].message.content
            
        except ImportError:
            raise ImportError("OpenAI package not installed. Run: pip install openai")
        except Exception as e:
            raise Exception(f"Failed to call OpenAI API: {str(e)}")
    
    def parse_audit_results(self, response: str) -> List[Dict[str, str]]:
        """Parse and validate the LLM response."""
        try:
            # Try to extract JSON from the response
            response = response.strip()
            if response.startswith("```json"):
                response = response[7:]
            if response.endswith("```"):
                response = response[:-3]
            
            results = json.loads(response)
            
            # Validate structure
            if not isinstance(results, list):
                raise ValueError("Response must be a JSON array")
            
            for item in results:
                required_keys = ["check", "status", "issue", "recommendation"]
                if not all(key in item for key in required_keys):
                    raise ValueError(f"Missing required keys in result: {item}")
                
                if item["status"] not in ["PASS", "FAIL", "WARN", "UNKNOWN"]:
                    raise ValueError(f"Invalid status: {item['status']}")
            
            return results
            
        except json.JSONDecodeError as e:
            raise ValueError(f"Invalid JSON response: {str(e)}")
        except Exception as e:
            raise ValueError(f"Failed to parse audit results: {str(e)}")
    
    def run_audit(self, use_llm: bool = True) -> Dict[str, Any]:
        """Run the complete environment audit."""
        print("🔍 Gathering environment information...")
        env_data = self.gather_environment()
        
        audit_results = {
            "timestamp": platform.node(),
            "environment": env_data,
            "audit_results": []
        }
        
        if use_llm:
            try:
                print("🤖 Analyzing environment with AI...")
                prompt = self.build_audit_prompt(env_data)
                response = self.call_model(prompt)
                audit_results["audit_results"] = self.parse_audit_results(response)
                print("✅ AI analysis complete")
                
            except Exception as e:
                print(f"❌ AI analysis failed: {str(e)}")
                print("📋 Falling back to basic checks...")
                audit_results["audit_results"] = self._basic_audit_checks(env_data)
        else:
            print("📋 Running basic environment checks...")
            audit_results["audit_results"] = self._basic_audit_checks(env_data)
        
        return audit_results
    
    def _basic_audit_checks(self, env_data: Dict[str, Any]) -> List[Dict[str, str]]:
        """Perform basic audit checks without LLM."""
        checks = []
        
        # Check 1: Dependencies
        has_setup = env_data["config_files"].get("setup.py", False)
        has_requirements = env_data["config_files"].get("requirements.txt", False)
        
        if has_setup or has_requirements:
            checks.append({
                "check": "Dependency Configuration",
                "status": "PASS",
                "issue": "",
                "recommendation": ""
            })
        else:
            checks.append({
                "check": "Dependency Configuration", 
                "status": "FAIL",
                "issue": "No setup.py or requirements.txt found",
                "recommendation": "Create requirements.txt or setup.py with project dependencies"
            })
        
        # Check 2: CI/CD
        if env_data["ci_configs"]:
            checks.append({
                "check": "CI/CD Configuration",
                "status": "PASS", 
                "issue": "",
                "recommendation": ""
            })
        else:
            checks.append({
                "check": "CI/CD Configuration",
                "status": "FAIL",
                "issue": "No CI/CD configuration files found",
                "recommendation": "Create .github/workflows/test.yml for automated testing"
            })
        
        # Check 3: Project Structure
        structure = env_data["project_structure"]
        core_exists = structure.get("core_exists", False)
        engine_exists = structure.get("ethical_engine_exists", False)
        
        if core_exists and engine_exists:
            checks.append({
                "check": "Project Structure",
                "status": "PASS",
                "issue": "",
                "recommendation": ""
            })
        else:
            missing = []
            if not core_exists:
                missing.append("core/")
            if not engine_exists:
                missing.append("ethical_engine/")
            
            checks.append({
                "check": "Project Structure",
                "status": "FAIL", 
                "issue": f"Missing directories: {', '.join(missing)}",
                "recommendation": f"Create missing directories: {', '.join(missing)}"
            })
        
        return checks
    
    def print_results(self, audit_results: Dict[str, Any]) -> None:
        """Print formatted audit results."""
        print("\n" + "="*60)
        print("🛡️  ETHICAL AI FRAMEWORK ENVIRONMENT AUDIT")
        print("="*60)
        
        # Summary
        results = audit_results["audit_results"]
        pass_count = sum(1 for r in results if r["status"] == "PASS")
        fail_count = sum(1 for r in results if r["status"] == "FAIL") 
        warn_count = sum(1 for r in results if r["status"] == "WARN")
        
        print(f"\n📊 SUMMARY: {pass_count} PASS, {fail_count} FAIL, {warn_count} WARN")
        
        # Detailed results
        for result in results:
            status_emoji = {
                "PASS": "✅",
                "FAIL": "❌", 
                "WARN": "⚠️",
                "UNKNOWN": "❓"
            }
            
            print(f"\n{status_emoji[result['status']]} {result['check']}")
            if result["issue"]:
                print(f"   Issue: {result['issue']}")
            if result["recommendation"]:
                print(f"   Action: {result['recommendation']}")
        
        print("\n" + "="*60)


def main():
    """Main CLI entry point."""
    parser = argparse.ArgumentParser(
        description="Audit environment for Ethical AI Framework compliance"
    )
    parser.add_argument(
        "--no-llm", 
        action="store_true",
        help="Skip LLM analysis and use basic checks only"
    )
    parser.add_argument(
        "--output", "-o",
        help="Save results to JSON file"
    )
    parser.add_argument(
        "--config",
        help="Path to configuration file (JSON)"
    )
    
    args = parser.parse_args()
    
    # Load configuration
    config = None
    if args.config:
        try:
            with open(args.config, 'r') as f:
                config = json.load(f)
        except Exception as e:
            print(f"Warning: Could not load config file: {e}")
    
    # Run audit
    try:
        auditor = EnvironmentAuditor(config)
        results = auditor.run_audit(use_llm=not args.no_llm)
        
        # Print results
        auditor.print_results(results)
        
        # Save to file if requested
        if args.output:
            with open(args.output, 'w') as f:
                json.dump(results, f, indent=2)
            print(f"\n💾 Results saved to {args.output}")
            
    except KeyboardInterrupt:
        print("\n\n⏹️  Audit cancelled by user")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ Audit failed: {str(e)}")
        sys.exit(1)


if __name__ == "__main__":
    main()

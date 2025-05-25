#!/usr/bin/env python3
"""
scripts/env_audit.py: Multimodal Environment Auditor for Ethical AI Framework.

This tool can work with any LLM provider (OpenAI, Anthropic, Ollama, etc.)
and automatically adapts to whatever models are available in the environment.
"""

import os
import sys
import json
import shutil
import platform
import subprocess
import argparse
import asyncio
from pathlib import Path
from typing import Dict, List, Any, Optional

# Import our multimodal LLM system
from llm_adapters import (
    LLMProvider, LLMConfig, MultiLLMManager,
    load_llm_configs_from_env, load_llm_configs_from_file
)


class MultimodalEnvironmentAuditor:
    """Environment auditor that works with any available LLM provider."""
    
    def __init__(self, llm_configs: Optional[List[LLMConfig]] = None):
        self.llm_manager = None
        self.basic_config = {
            "timeout": 30,
            "max_retries": 3
        }
        
        if llm_configs:
            try:
                self.llm_manager = MultiLLMManager(llm_configs)
                print(f"✅ LLM Manager initialized with {len(self.llm_manager.adapters)} working providers")
            except Exception as e:
                print(f"⚠️  LLM initialization failed: {e}")
                print("   Falling back to basic checks only")
        
    @classmethod
    def auto_configure(cls, config_file: Optional[str] = None):
        """Auto-configure auditor by detecting available LLM providers."""
        print("🔍 Auto-detecting available LLM providers...")
        
        if config_file and Path(config_file).exists():
            print(f"📄 Loading configuration from {config_file}")
            configs = load_llm_configs_from_file(config_file)
        else:
            print("🌍 Scanning environment variables for LLM configurations")
            configs = load_llm_configs_from_env()
        
        if not configs:
            print("❌ No LLM configurations found")
            print("   Set environment variables like OPENAI_API_KEY, ANTHROPIC_API_KEY, etc.")
            print("   Or use --no-llm flag for basic checks only")
            return cls()
        
        print(f"🎯 Found {len(configs)} potential LLM configurations")
        for config in configs:
            print(f"   - {config.provider.value}: {config.model}")
        
        return cls(configs)
    
    def gather_environment(self) -> Dict[str, Any]:
        """Collect comprehensive environment information."""
        print("📊 Gathering environment data...")
        
        data = {
            "python_version": platform.python_version(),
            "platform": platform.platform(),
            "cwd": Path.cwd().name,  # Only directory name for privacy
            "audit_tool_version": "2.0.0-multimodal"
        }
        
        # Package information with robust error handling
        data["packages"] = self._scan_packages()
        
        # Tool availability
        data["tools"] = {
            "docker": bool(shutil.which("docker")),
            "kubectl": bool(shutil.which("kubectl")),
            "git": bool(shutil.which("git")),
            "pip": bool(shutil.which("pip")),
            "python": bool(shutil.which("python")),
            "pytest": bool(shutil.which("pytest"))
        }
        
        # Project analysis
        data["project"] = self._analyze_project_structure()
        data["configuration"] = self._scan_configuration_files()
        data["ci_cd"] = self._scan_ci_cd_setup()
        
        # LLM availability
        if self.llm_manager:
            data["llm_status"] = self.llm_manager.get_status()
        else:
            data["llm_status"] = {"working_providers": [], "message": "No LLM providers configured"}
        
        return data
    
    def _scan_packages(self) -> Dict[str, Any]:
        """Scan installed packages with comprehensive error handling."""
        package_info = {"error": None, "packages": [], "analysis": {}}
        
        try:
            result = subprocess.run(
                [sys.executable, "-m", "pip", "freeze"],
                capture_output=True,
                text=True,
                timeout=self.basic_config["timeout"]
            )
            
            if result.returncode == 0:
                packages = result.stdout.strip().split('\n')
                package_info["packages"] = [p for p in packages if p.strip()]
                
                # Analyze key packages
                package_names = [p.split('==')[0].lower() for p in packages]
                package_info["analysis"] = {
                    "has_openai": any("openai" in name for name in package_names),
                    "has_anthropic": any("anthropic" in name for name in package_names),
                    "has_pytest": any("pytest" in name for name in package_names),
                    "has_requests": any("requests" in name for name in package_names),
                    "total_packages": len(packages)
                }
            else:
                package_info["error"] = f"pip freeze failed: {result.stderr}"
                
        except subprocess.TimeoutExpired:
            package_info["error"] = "pip freeze timed out"
        except FileNotFoundError:
            package_info["error"] = "pip command not found"
        except Exception as e:
            package_info["error"] = f"Unexpected error: {str(e)}"
        
        return package_info
    
    def _analyze_project_structure(self) -> Dict[str, Any]:
        """Analyze project directory structure."""
        structure = {
            "directories": {},
            "python_packages": {},
            "top_level": []
        }
        
        try:
            # Key directories to check
            key_dirs = ["core", "ethical_engine", "scripts", "tests", "docs", "src"]
            for dir_name in key_dirs:
                dir_path = Path(dir_name)
                structure["directories"][dir_name] = {
                    "exists": dir_path.is_dir(),
                    "has_init": (dir_path / "__init__.py").exists() if dir_path.is_dir() else False
                }
            
            # Python package analysis
            python_dirs = [d for d in key_dirs if structure["directories"][d]["exists"]]
            for py_dir in python_dirs:
                if structure["directories"][py_dir]["has_init"]:
                    structure["python_packages"][py_dir] = self._analyze_python_package(Path(py_dir))
            
            # Top-level structure
            structure["top_level"] = [
                d.name for d in Path(".").iterdir()
                if d.is_dir() and not d.name.startswith(".") and d.name != "__pycache__"
            ]
            
        except Exception as e:
            structure["error"] = f"Error analyzing project structure: {str(e)}"
        
        return structure
    
    def _analyze_python_package(self, package_path: Path) -> Dict[str, Any]:
        """Analyze a Python package directory."""
        analysis = {
            "submodules": [],
            "has_main": False,
            "py_files_count": 0
        }
        
        try:
            for item in package_path.iterdir():
                if item.is_file() and item.suffix == ".py":
                    analysis["py_files_count"] += 1
                    if item.name == "__main__.py":
                        analysis["has_main"] = True
                elif item.is_dir() and (item / "__init__.py").exists():
                    analysis["submodules"].append(item.name)
        except Exception:
            pass  # Silently handle permission errors, etc.
        
        return analysis
    
    def _scan_configuration_files(self) -> Dict[str, Any]:
        """Scan for important configuration files."""
        config_analysis = {"files": {}, "content_analysis": {}}
        
        # File existence checks
        config_files = {
            "setup.py": "setup.py",
            "pyproject.toml": "pyproject.toml",
            "requirements.txt": "requirements.txt",
            "pytest.ini": "pytest.ini",
            "tox.ini": "tox.ini",
            ".gitignore": ".gitignore",
            "README.md": "README.md",
            "LICENSE": ["LICENSE", "LICENSE.txt", "LICENSE.md"],
            "Dockerfile": "Dockerfile",
            "docker-compose.yml": ["docker-compose.yml", "docker-compose.yaml"]
        }
        
        for key, paths in config_files.items():
            if isinstance(paths, str):
                paths = [paths]
            config_analysis["files"][key] = any(Path(path).exists() for path in paths)
        
        # Content analysis for key files
        config_analysis["content_analysis"] = self._analyze_config_contents()
        
        return config_analysis
    
    def _analyze_config_contents(self) -> Dict[str, Any]:
        """Analyze contents of key configuration files."""
        analysis = {}
        
        # Analyze setup.py
        if Path("setup.py").exists():
            try:
                with open("setup.py", 'r', encoding='utf-8') as f:
                    content = f.read().lower()
                    analysis["setup_py"] = {
                        "has_install_requires": "install_requires" in content,
                        "has_python_requires": "python_requires" in content,
                        "mentions_openai": "openai" in content,
                        "mentions_anthropic": "anthropic" in content
                    }
            except Exception:
                analysis["setup_py"] = {"error": "Could not read setup.py"}
        
        # Analyze requirements.txt
        if Path("requirements.txt").exists():
            try:
                with open("requirements.txt", 'r', encoding='utf-8') as f:
                    lines = [line.strip() for line in f.readlines() if line.strip() and not line.startswith('#')]
                    analysis["requirements_txt"] = {
                        "line_count": len(lines),
                        "has_openai": any("openai" in line.lower() for line in lines),
                        "has_anthropic": any("anthropic" in line.lower() for line in lines),
                        "has_pytest": any("pytest" in line.lower() for line in lines)
                    }
            except Exception:
                analysis["requirements_txt"] = {"error": "Could not read requirements.txt"}
        
        # Analyze .gitignore
        if Path(".gitignore").exists():
            try:
                with open(".gitignore", 'r', encoding='utf-8') as f:
                    content = f.read().lower()
                    analysis["gitignore"] = {
                        "ignores_logs": ".log" in content or "*.log" in content,
                        "ignores_json": ".json" in content or "*.json" in content,
                        "ignores_env": ".env" in content or "*.env" in content,
                        "ignores_pycache": "__pycache__" in content
                    }
            except Exception:
                analysis["gitignore"] = {"error": "Could not read .gitignore"}
        
        return analysis
    
    def _scan_ci_cd_setup(self) -> Dict[str, Any]:
        """Scan for CI/CD configuration."""
        ci_cd = {"github_actions": [], "other_ci": [], "analysis": {}}
        
        # GitHub Actions
        github_workflows = Path(".github/workflows")
        if github_workflows.exists():
            for workflow_file in github_workflows.glob("*.yml"):
                ci_cd["github_actions"].append(str(workflow_file))
            for workflow_file in github_workflows.glob("*.yaml"):
                ci_cd["github_actions"].append(str(workflow_file))
        
        # Other CI systems
        ci_files = [".travis.yml", ".circleci/config.yml", "azure-pipelines.yml", "Jenkinsfile"]
        for ci_file in ci_files:
            if Path(ci_file).exists():
                ci_cd["other_ci"].append(ci_file)
        
        # Analysis
        ci_cd["analysis"] = {
            "has_github_actions": len(ci_cd["github_actions"]) > 0,
            "has_other_ci": len(ci_cd["other_ci"]) > 0,
            "total_ci_files": len(ci_cd["github_actions"]) + len(ci_cd["other_ci"])
        }
        
        return ci_cd
    
    def build_audit_prompt(self, env_data: Dict[str, Any]) -> str:
        """Build a comprehensive audit prompt for any LLM provider."""
        # Filter and summarize data for LLM consumption
        filtered_data = self._prepare_data_for_llm(env_data)
        
        prompt = f"""You are an expert in ethical AI framework environment validation.

ENVIRONMENT ANALYSIS REQUEST:
Analyze the following environment data and provide structured feedback on compliance with ethical AI framework requirements.

ENVIRONMENT DATA:
```json
{json.dumps(filtered_data, indent=2)}
```

VALIDATION REQUIREMENTS:
1. **Dependencies**: Project should have proper dependency management (setup.py, requirements.txt, pyproject.toml) with key packages like openai, anthropic, pytest
2. **CI/CD**: Automated testing should be configured (GitHub Actions, etc.) with pytest integration  
3. **Project Structure**: Should have proper Python package structure with __init__.py files in core directories
4. **Configuration**: Should have test configuration (pytest.ini), proper .gitignore for sensitive files
5. **Security**: No hardcoded secrets, proper environment variable usage for API keys
6. **LLM Integration**: Should support multiple LLM providers for flexibility and resilience
7. **Documentation**: Should have README, LICENSE, and other documentation files

RESPONSE FORMAT:
Respond with a JSON array of validation results. Each result should have:
- "check": Description of what was validated
- "status": One of "PASS", "FAIL", "WARN", "UNKNOWN"
- "issue": Description of any problems (empty if none)
- "recommendation": Specific action to take (empty if none needed)
- "priority": One of "HIGH", "MEDIUM", "LOW"

Focus on actionable recommendations and be specific about what needs to be fixed or improved."""
        
        return prompt
    
    def _prepare_data_for_llm(self, env_data: Dict[str, Any]) -> Dict[str, Any]:
        """Prepare environment data for LLM analysis by filtering sensitive info."""
        filtered = {
            "python_version": env_data["python_version"],
            "platform_type": env_data["platform"].split('-')[0] if env_data["platform"] else "unknown",
            "audit_version": env_data["audit_tool_version"]
        }
        
        # Package analysis (summarized)
        if "packages" in env_data and env_data["packages"].get("analysis"):
            filtered["package_analysis"] = env_data["packages"]["analysis"]
        
        # Tool availability
        if "tools" in env_data:
            filtered["available_tools"] = env_data["tools"]
        
        # Project structure (summarized)
        if "project" in env_data:
            project = env_data["project"]
            filtered["project_structure"] = {
                "has_core": project["directories"].get("core", {}).get("exists", False),
                "has_ethical_engine": project["directories"].get("ethical_engine", {}).get("exists", False),
                "has_scripts": project["directories"].get("scripts", {}).get("exists", False),
                "has_tests": project["directories"].get("tests", {}).get("exists", False),
                "python_packages": list(project.get("python_packages", {}).keys())
            }
        
        # Configuration files
        if "configuration" in env_data:
            config = env_data["configuration"]
            filtered["configuration"] = {
                "files": config["files"],
                "content_analysis": config["content_analysis"]
            }
        
        # CI/CD
        if "ci_cd" in env_data:
            filtered["ci_cd"] = env_data["ci_cd"]["analysis"]
        
        # LLM status
        if "llm_status" in env_data:
            filtered["llm_integration"] = {
                "providers_available": len(env_data["llm_status"].get("working_providers", [])),
                "provider_types": env_data["llm_status"].get("working_providers", [])
            }
        
        return filtered
    
    async def call_llm_async(self, prompt: str) -> str:
        """Make an async call to any available LLM."""
        if not self.llm_manager:
            raise Exception("No LLM providers available")
        
        response = await self.llm_manager.call_with_fallback(prompt)
        return response.content
    
    def call_llm_sync(self, prompt: str) -> str:
        """Make a synchronous call to any available LLM."""
        return asyncio.run(self.call_llm_async(prompt))
    
    def parse_llm_response(self, response: str) -> List[Dict[str, str]]:
        """Parse LLM response with enhanced error handling."""
        try:
            # Clean up response
            response = response.strip()
            
            # Extract JSON from markdown if present
            if "```json" in response:
                start = response.find("```json") + 7
                end = response.find("```", start)
                if end != -1:
                    response = response[start:end].strip()
            
            # Find JSON array in response
            if not response.startswith('['):
                start_idx = response.find('[')
                end_idx = response.rfind(']')
                if start_idx != -1 and end_idx != -1:
                    response = response[start_idx:end_idx + 1]
            
            results = json.loads(response)
            
            # Validate structure
            if not isinstance(results, list):
                raise ValueError("Response must be a JSON array")
            
            # Validate and clean each result
            validated_results = []
            for item in results:
                if not isinstance(item, dict):
                    continue
                
                # Required fields with defaults
                validated_item = {
                    "check": item.get("check", "Unknown Check"),
                    "status": item.get("status", "UNKNOWN"),
                    "issue": item.get("issue", ""),
                    "recommendation": item.get("recommendation", ""),
                    "priority": item.get("priority", "MEDIUM")
                }
                
                # Validate status
                if validated_item["status"] not in ["PASS", "FAIL", "WARN", "UNKNOWN"]:
                    validated_item["status"] = "UNKNOWN"
                
                # Validate priority
                if validated_item["priority"] not in ["HIGH", "MEDIUM", "LOW"]:
                    validated_item["priority"] = "MEDIUM"
                
                validated_results.append(validated_item)
            
            return validated_results
            
        except json.JSONDecodeError as e:
            raise ValueError(f"Invalid JSON in LLM response: {str(e)}")
        except Exception as e:
            raise ValueError(f"Failed to parse LLM response: {str(e)}")
    
    def generate_basic_audit(self, env_data: Dict[str, Any]) -> List[Dict[str, str]]:
        """Generate basic audit results without LLM."""
        results = []
        
        # Check 1: Dependency Management
        config = env_data.get("configuration", {})
        files = config.get("files", {})
        
        has_deps = files.get("setup.py") or files.get("requirements.txt") or files.get("pyproject.toml")
        results.append({
            "check": "Dependency Management",
            "status": "PASS" if has_deps else "FAIL", 
            "issue": "" if has_deps else "No dependency management files found",
            "recommendation": "" if has_deps else "Create setup.py, requirements.txt, or pyproject.toml",
            "priority": "HIGH" if not has_deps else "LOW"
        })
        
        # Check 2: Testing Setup
        has_pytest_config = files.get("pytest.ini") or files.get("pyproject.toml")
        has_tests_dir = env_data.get("project", {}).get("directories", {}).get("tests", {}).get("exists", False)
        
        testing_ok = has_pytest_config and has_tests_dir
        results.append({
            "check": "Testing Configuration",
            "status": "PASS" if testing_ok else "WARN",
            "issue": "Missing test configuration or tests directory" if not testing_ok else "",
            "recommendation": "Create pytest.ini and tests/ directory" if not testing_ok else "",
            "priority": "MEDIUM"
        })
        
        # Check 3: Project Structure
        project = env_data.get("project", {})
        dirs = project.get("directories", {})
        
        has_core = dirs.get("core", {}).get("exists", False)
        has_engine = dirs.get("ethical_engine", {}).get("exists", False)
        
        structure_ok = has_core or has_engine  # At least one main package
        results.append({
            "check": "Project Structure",
            "status": "PASS" if structure_ok else "FAIL",
            "issue": "Missing core project directories" if not structure_ok else "",
            "recommendation": "Create core/ or ethical_engine/ directories with __init__.py" if not structure_ok else "",
            "priority": "HIGH" if not structure_ok else "LOW"
        })
        
        # Check 4: CI/CD
        ci_analysis = env_data.get("ci_cd", {}).get("analysis", {})
        has_ci = ci_analysis.get("has_github_actions", False) or ci_analysis.get("has_other_ci", False)
        
        results.append({
            "check": "Continuous Integration",
            "status": "PASS" if has_ci else "WARN",
            "issue": "No CI/CD configuration found" if not has_ci else "",
            "recommendation": "Add GitHub Actions workflow for automated testing" if not has_ci else "",
            "priority": "MEDIUM"
        })
        
        # Check 5: LLM Integration
        llm_status = env_data.get("llm_integration", {})
        provider_count = llm_status.get("providers_available", 0)
        
        results.append({
            "check": "LLM Provider Integration",
            "status": "PASS" if provider_count > 0 else "WARN",
            "issue": f"Only {provider_count} LLM providers configured" if provider_count < 2 else "",
            "recommendation": "Configure multiple LLM providers for redundancy" if provider_count < 2 else "",
            "priority": "MEDIUM"
        })
        
        # Check 6: Security
        content_analysis = config.get("content_analysis", {})
        gitignore = content_analysis.get("gitignore", {})
        
        ignores_sensitive = (
            gitignore.get("ignores_env", False) and 
            gitignore.get("ignores_logs", False)
        )
        
        results.append({
            "check": "Security Configuration",
            "status": "PASS" if ignores_sensitive else "WARN",
            "issue": "gitignore may not exclude sensitive files" if not ignores_sensitive else "",
            "recommendation": "Update .gitignore to exclude .env, *.log, and other sensitive files" if not ignores_sensitive else "",
            "priority": "HIGH"
        })
        
        return results
    
    async def run_audit_async(self, use_llm: bool = True) -> Dict[str, Any]:
        """Run the complete audit asynchronously."""
        print("🚀 Starting multimodal environment audit...")
        
        # Gather environment data
        env_data = self.gather_environment()
        
        audit_results = {
            "timestamp": platform.node(),
            "audit_version": "2.0.0-multimodal",
            "environment": env_data,
            "audit_results": [],
            "llm_used": False
        }
        
        if use_llm and self.llm_manager:
            try:
                print("🤖 Running AI-powered analysis...")
                prompt = self.build_audit_prompt(env_data)
                
                llm_response = await self.call_llm_async(prompt)
                audit_results["audit_results"] = self.parse_llm_response(llm_response)
                audit_results["llm_used"] = True
                audit_results["llm_provider"] = self.llm_manager.adapters[0].config.provider.value
                
                print("✅ AI analysis completed successfully")
                
            except Exception as e:
                print(f"❌ AI analysis failed: {str(e)}")
                print("📋 Falling back to basic audit...")
                audit_results["audit_results"] = self.generate_basic_audit(env_data)
                audit_results["llm_error"] = str(e)
        else:
            print("📋 Running basic audit (no LLM)...")
            audit_results["audit_results"] = self.generate_basic_audit(env_data)
        
        return audit_results
    
    def run_audit_sync(self, use_llm: bool = True) -> Dict[str, Any]:
        """Run the complete audit synchronously."""
        return asyncio.run(self.run_audit_async(use_llm))
    
    def print_results(self, audit_results: Dict[str, Any]) -> None:
        """Print formatted audit results with enhanced output."""
        print("\n" + "="*70)
        print("🛡️  MULTIMODAL ETHICAL AI FRAMEWORK ENVIRONMENT AUDIT")
        print("="*70)
        
        # Header info
        print(f"📊 Audit Version: {audit_results.get('audit_version', 'unknown')}")
        if audit_results.get("llm_used"):
            print(f"🤖 AI Analysis: {audit_results.get('llm_provider', 'unknown')} LLM")
        else:
            print("🔧 Analysis: Basic checks only")
        
        # Summary with priority breakdown 
        results = audit_results["audit_results"]
        
        status_counts = {"PASS": 0, "FAIL": 0, "WARN": 0, "UNKNOWN": 0}
        priority_counts = {"HIGH": 0, "MEDIUM": 0, "LOW": 0}
        
        for result in results:
            status_counts[result["status"]] += 1
            priority_counts[result.get("priority", "MEDIUM")] += 1
        
        print(f"\n📈 SUMMARY:")
        print(f"   Status: {status_counts['PASS']} PASS, {status_counts['FAIL']} FAIL, {status_counts['WARN']} WARN")
        print(f"   Priority: {priority_counts['HIGH']} HIGH, {priority_counts['MEDIUM']} MEDIUM, {priority_counts['LOW']} LOW")
        
        # Detailed results grouped by priority
        for priority in ["HIGH", "MEDIUM", "LOW"]:
            priority_results = [r for r in results if r.get("priority") == priority]
            if not priority_results:
                continue
                
            print(f"\n🔥 {priority} PRIORITY ITEMS:")
            print("-" * 50)
            
            for result in priority_results:
                status_emoji = {
                    "PASS": "✅", "FAIL": "❌", "WARN": "⚠️", "UNKNOWN": "❓"
                }
                
                print(f"{status_emoji[result['status']]} {result['check']}")
                if result["issue"]:
                    print(f"   Issue: {result['issue']}")
                if result["recommendation"]:
                    print(f"   Action: {result['recommendation']}")
                print()
        
        # Environment summary
        env = audit_results.get("environment", {})
        llm_status = env.get("llm_status", {})
        working_providers = llm_status.get("working_providers", [])
        
        if working_providers:
            print(f"🔗 Available LLM Providers: {', '.join(working_providers)}")
        else:
            print("⚠️  No LLM providers configured")
        
        print("="*70)


def main():
    """Enhanced main CLI with multimodal support."""
    parser = argparse.ArgumentParser(
        description="Multimodal Environment Auditor for Ethical AI Framework",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  %(prog)s                          # Auto-detect LLMs and run full audit
  %(prog)s --no-llm                 # Run basic checks only
  %(prog)s --config llm_config.json # Use specific LLM configuration
  %(prog)s --list-providers         # Show available LLM providers
  %(prog)s --test-llms              # Test all configured LLM connections
        """
    )
    
    parser.add_argument("--no-llm", action="store_true", 
                       help="Skip LLM analysis, use basic checks only")
    parser.add_argument("--config", help="Path to LLM configuration file (JSON)")
    parser.add_argument("--output", "-o", help="Save results to JSON file")
    parser.add_argument("--list-providers", action="store_true",
                       help="List all available LLM providers and exit")
    parser.add_argument("--test-llms", action="store_true",
                       help="Test LLM connections and exit")
    parser.add_argument("--verbose", "-v", action="store_true",
                       help="Enable verbose output")
    
    args = parser.parse_args()
    
    if args.list_providers:
        from llm_adapters import LLMAdapterFactory
        providers = LLMAdapterFactory.get_available_providers()
        print("Available LLM Providers:")
        for provider in providers:
            print(f"  - {provider.value}")
        return
    
    try:
        # Initialize auditor
        if args.config:
            print(f"📄 Using configuration file: {args.config}")
            auditor = MultimodalEnvironmentAuditor.auto_configure(args.config)
        else:
            auditor = MultimodalEnvironmentAuditor.auto_configure()
        
        if args.test_llms:
            if auditor.llm_manager:
                status = auditor.llm_manager.get_status()
                print("\n🔧 LLM Connection Test Results:")
                print(f"✅ Working: {status['working_providers']}")
                if status['failed_providers']:
                    print(f"❌ Failed: {status['failed_providers']}")
            else:
                print("❌ No LLM providers configured")
            return
        
        # Run audit
        print("\n🎯 Starting environment audit...")
        results = auditor.run_audit_sync(use_llm=not args.no_llm)
        
        # Print results
        auditor.print_results(results)
        
        # Save to file if requested
        if args.output:
            with open(args.output, 'w') as f:
                json.dump(results, f, indent=2)
            print(f"\n💾 Results saved to {args.output}")
        
        # Exit code based on results
        audit_results = results["audit_results"]
        has_failures = any(r["status"] == "FAIL" for r in audit_results)
        has_high_priority_issues = any(
            r.get("priority") == "HIGH" and r["status"] in ["FAIL", "WARN"] 
            for r in audit_results
        )
        
        if has_failures or has_high_priority_issues:
            print("\n⚠️  Audit completed with issues that need attention")
            sys.exit(1)
        else:
            print("\n✅ Audit completed successfully")
            sys.exit(0)
            
    except KeyboardInterrupt:
        print("\n\n⏹️  Audit cancelled by user")
        sys.exit(130)
    except Exception as e:
        print(f"\n❌ Audit failed: {str(e)}")
        if args.verbose:
            import traceback
            traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()

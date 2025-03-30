#!/bin/bash

echo "🚀 Onboarding — Ethical AI Framework"
echo ""
echo "Welcome aboard."
echo "The world doesn’t need another AI tool."
echo "It needs AI with a spine."
echo "You’re here because you know that."
echo ""
echo "----------------------------------------"
echo ""

# Step 1: Confirm location
echo "You are in: $(pwd)"
echo "✅ Repo directory confirmed."

# Step 2: Set up virtual environment
echo ""
echo "2. Setting up Python virtual environment..."
python3 -m venv venv
source venv/bin/activate
pip install -e .
echo "✅ Virtual environment ready and dependencies installed."

# Step 3: Explore the codebase
echo ""
echo "3. Key folders in this project:"
echo "   /ethical_engine → Core ethical logic"
echo "   /tests          → Automated test coverage"
echo "   /examples       → Usage examples"
echo ""
echo "Take a moment to explore."

# Step 4: Start contributing
echo "----------------------------------------"
echo ""
echo "4. Ready to contribute? Follow these steps:"
echo ""
echo "Create a new branch:"
echo "   git checkout -b your-feature-name"
echo ""
echo "Make your changes, then:"
echo "   git add ."
echo "   git commit -m \"Describe your changes\""
echo "   git push origin your-feature-name"
echo ""
echo "Finally, open a Pull Request on GitHub."
echo ""
echo "----------------------------------------"
echo ""
echo "Ethics First. Always."
echo "If your code violates consent, autonomy, or transparency, it will not be merged. No exceptions."
echo ""

# Optional: Open repo in VSCode if available
if command -v code &> /dev/null
then
    echo "Opening project in VSCode..."
    code .
fi

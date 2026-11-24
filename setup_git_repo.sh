#!/bin/bash
# ComfyUI Platform - Git Repository Setup
# Run all git commands to push to GitHub

echo "=============================================="
echo "ComfyUI + Kaggle - GitHub Push Setup"
echo "=============================================="
echo ""

# -------------------------------------------------------------------------
# UPDATE THESE VALUES OR SET THEM AS ENVIRONMENT VARIABLES
# -------------------------------------------------------------------------

GITHUB_USERNAME="${COMFYUI_GITHUB_USERNAME:-your-username}"
GITHUB_EMAIL="${COMFYUI_GITHUB_EMAIL:-your-email@example.com}"
REPO_NAME="${COMFYUI_REPO_NAME:-comfyui-project}"
REPO_URL="${COMFYUI_REPO_URL:-git@github.com:${GITHUB_USERNAME}/${REPO_NAME}.git}"

# -------------------------------------------------------------------------
# USER INPUT
# -------------------------------------------------------------------------

echo "Repository URL: $REPO_URL"
echo ""

read -p "Do you have a GitHub Personal Access Token (PAT)? This is recommended for pushing to GitHub. (y/n): " -n 1 -r
echo ""

PUSH_WITH_TOKEN=false
if [[ $REPLY =~ ^[Yy]$ ]]; then
    read -p "Enter your GitHub Personal Access Token: " GITHUB_TOKEN
    if [ -n "$GITHUB_TOKEN" ]; then
        PUSH_WITH_TOKEN=true
        # Add safe directory for token in git config
        git config --global --add safe.directory "/tmp/comfyui-project"
    fi
else
    echo "Note: If your SSH keys are set up correctly, you can push without a token."
fi

echo ""
read -p "GitHub Username (again for confirmation): " CONFIRM_USERNAME
if [ "$CONFIRM_USERNAME" != "$GITHUB_USERNAME" ]; then
    echo "Username mismatch! Please update the script with your correct username."
    exit 1
fi

# -------------------------------------------------------------------------
# GIT SETUP
# -------------------------------------------------------------------------

echo ""
echo "Setting up Git repository..."

# Create script location (adjust if you saved this in a different folder)
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"

# Create a working copy of the project structure
if [ -z "$COMFYUI_SKIP_CLONE" ]; then
    TEMP_DIR="/tmp/comfyui-project"
    echo ""
    echo "Creating working copy in: $TEMP_DIR"
    rm -rf "$TEMP_DIR"
    mkdir -p "$TEMP_DIR"
    cp -r "$SCRIPT_DIR"/* "$TEMP_DIR/" 2>/dev/null || {
        # Fallback: copy files individually
        cp "$SCRIPT_DIR"/README.md "$TEMP_DIR/" 2>/dev/null || true
        cp "$SCRIPT_DIR"/comfyui_kaggle_setup_roadmap.md "$TEMP_DIR/" 2>/dev/null || true
        cp "$SCRIPT_DIR"/essentials.txt "$TEMP_DIR/" 2>/dev/null || true
        mkdir -p "$TEMP_DIR/workflows"
        cp "$SCRIPT_DIR/workflows"/*.json "$TEMP_DIR/workflows/" 2>/dev/null || true
        cp "$SCRIPT_DIR/essentials.txt" "$TEMP_DIR/" 2>/dev/null || true
        mkdir -p "$TEMP_DIR/documentation"
        cp "$TEMP_DIR"/documentation/*.md "$TEMP_DIR/documentation/" 2>/dev/null || true
        cp "$TEMP_DIR"/.gitignore "$TEMP_DIR/" 2>/dev/null || true
    }
    cd "$TEMP_DIR"
else
    cd "$SCRIPT_DIR"
fi

# Initialize git
git init

# Configure git
git config user.name "$GITHUB_USERNAME"
git config user.email "$GITHUB_EMAIL"

echo "Git initialized in $(pwd)"

# -------------------------------------------------------------------------
# CONFIGURATION FILES ONLY (MODELS ARE NOT PUSHED)
# -------------------------------------------------------------------------

echo ""
echo "Adding configuration files to Git..."

# Create .gitignore if it doesn't exist
if [ ! -f ".gitignore" ]; then
    cat > .gitignore << 'EOF'
# Python
__pycache__/
*.py[cod]
*$py.class
*.so
.Python
env/
venv/
*.egg-info/
dist/
build/

# Models (large files to exclude)
*.safetensors
*.ckpt
*.pth
*.bin
models/stable_diffusion/
models/control_nets/
models/custom/
*.model

# Outputs (generated images)
outputs/generated/
outputs/temporary/
*.jpg
*.jpeg
*.png

# IDE and IDEAs
.vscode/
.idea/
*.swp
*.swo
*.sublime-*

# OS
.DS_Store
Thumbs.db

# Logs
*.log
logs/

# Temporary
*.tmp
*.temp
cache/
temp/

# Environment
.env
.env.local
EOF
fi

# Add .gitignore
git add .gitignore

# Add all source files except models and outputs
find . -type f -not -path "./models/*" -not -path "./outputs/*" -not -path "./__pycache__/*" -not -path "./.git/*" ! -path "./.*" ! -path "./*~" ! -path "./comfyui_env/*" | grep -v "__pycache__" | grep -v ".pyc" | head -50

git add -A

# Commit
git commit -m "Initial commit: ComfyUI + Kaggle setup project"

echo "✓ Configuration files committed"

# -------------------------------------------------------------------------
# PUSH TO GITHUB
# -------------------------------------------------------------------------

echo ""
echo "Pushing to GitHub: $REPO_URL"

if [ "$PUSH_WITH_TOKEN" = true ] && [ -n "$GITHUB_TOKEN" ]; then
    # Push with token
    git remote add origin "$REPO_URL"
    git remote -v
    git push https://"$GITHUB_TOKEN"@github.com/"$GITHUB_USERNAME"/"$REPO_NAME".git main --force || git push https://"$GITHUB_TOKEN"@github.com/"$GITHUB_USERNAME"/"$REPO_NAME".git master --force
    URL="https://github.com/$GITHUB_USERNAME/$REPO_NAME"
else
    # Push with SSH (if keys are set up)
    git remote add origin "$REPO_URL" 2>/dev/null || git remote set-url origin "$REPO_URL"
    git remote -v
    git push origin main --force 2>/dev/null || git push origin master --force
    URL="$REPO_URL"
fi

if [ $? -eq 0 ]; then
    echo ""
    echo "=============================================="
    echo "✅ SUCCESS! Repository pushed to GitHub"
    echo "=============================================="
    echo ""
    echo "Repository URL:"
    echo "  $URL"
    echo ""
    echo "Next steps:"
    echo "1. Go to https://github.com/$GITHUB_USERNAME/$REPO_NAME"
    echo "2. Add your models manually or use GitHub Releases"
    echo "3. Clone this repo elsewhere to start working"
    echo ""
    echo "To add models to GitHub:"
    echo "  git clone https://github.com/$GITHUB_USERNAME/$REPO_NAME.git"
    echo "  cd $REPO_NAME"
    echo "  # Download your models (.safetensors) and place in models/ folder"
    echo "  git add models/"
    echo "  git commit -m 'Add models'"
    echo "  git push"
    echo ""
else
    echo ""
    echo "=============================================="
    echo "❌ Push failed"
    echo "=============================================="
    echo "Make sure either:"
    echo "  1. Your SSH keys are set up (if using SSH), OR"
    echo "  2. Your GitHub token is valid and has write permissions"
    echo ""
fi

echo "=============================================="
# Automated Release Workflow

This document describes the automated release process for `tidy-viewer` and how to use the local testing capabilities.

## 🚀 **Overview**

The release process has been fully automated with GitHub Actions. When you push a tag, the workflow automatically:

1. **Validates** the release (version format, CHANGELOG, code quality)
2. **Publishes** to crates.io
3. **Builds** Debian and RPM packages
4. **Updates** Homebrew formulas
5. **Creates** GitHub release with assets

## 📋 **Release Process**

### **Manual Release (Current Method)**
```bash
# 1. Update version in Cargo.toml
# 2. Add entry to CHANGELOG.md
# 3. Commit changes
git add .
git commit -m "Prepare for release v1.6.6"
git push origin main

# 4. Create and push tag
git tag v1.6.6
git push origin v1.6.6
```

### **Automated Release (New Method)**
```bash
# 1. Update version in Cargo.toml
# 2. Add entry to CHANGELOG.md
# 3. Commit changes
git add .
git commit -m "Prepare for release v1.6.6"
git push origin main

# 4. Create and push tag (triggers automation)
git tag v1.6.6
git push origin v1.6.6
```

**That's it!** The GitHub Actions workflow will handle everything else automatically.

## 🧪 **Local Testing**

### **PowerShell Testing (Windows)**
```powershell
# Test current version
.\scripts\test-release.ps1

# Test specific version
.\scripts\test-release.ps1 1.6.6

# Test with strict mode (fail on warnings)
.\scripts\test-release.ps1 1.6.6 false
```

### **Bash Testing (Linux/macOS)**
```bash
# Test current version
bash scripts/test-release.sh

# Test specific version
bash scripts/test-release.sh 1.6.6

# Test with strict mode (fail on warnings)
bash scripts/test-release.sh 1.6.6 false
```

## 🔧 **Workflow Details**

### **Trigger Conditions**
- **Tag Push**: `v*` or `[0-9]+.[0-9]+.[0-9]+`
- **Examples**: `v1.6.6`, `1.6.6`, `v2.0.0`

### **Validation Steps**
1. **Version Format**: Ensures semantic versioning (X.Y.Z)
2. **CHANGELOG**: Checks for version entry
3. **Git Status**: Verifies no uncommitted changes
4. **Code Quality**: Runs tests, formatting, clippy
5. **Documentation**: Validates README and docs
6. **Build**: Creates release build

### **Publishing Steps**
1. **Cargo Publish**: Uploads to crates.io
2. **Package Building**: Creates Debian and RPM packages
3. **Homebrew Updates**: Updates personal tap and core formulas
4. **GitHub Release**: Creates release with assets

## 📦 **Package Distribution**

### **Debian Package**
- **Build**: `cargo deb`
- **Location**: `./target/debian/`
- **Install**: `sudo dpkg -i tidy-viewer_<VERSION>_amd64.deb`

### **RPM Package**
- **Build**: `alien --verbose --to-rpm ./target/debian/tidy-viewer_<VERSION>_amd64.deb`
- **Location**: `./target/`
- **Install**: `sudo rpm -i tidy-viewer_<VERSION>_amd64.rpm`

### **Homebrew**
- **Personal Tap**: `https://github.com/alexhallam/homebrew-tidy-viewer`
- **Core Formula**: `https://github.com/Homebrew/homebrew-core`
- **Install**: `brew install tidy-viewer`

## 🔍 **Local Testing Features**

### **What It Tests**
- ✅ Version format validation
- ✅ CHANGELOG entry verification
- ✅ Uncommitted changes detection
- ✅ All cargo tests
- ✅ Code formatting (rustfmt)
- ✅ Clippy warnings
- ✅ Release build
- ✅ Documentation validation
- ✅ Package building simulation
- ✅ Homebrew formula simulation

### **Benefits**
- **Fast Feedback**: Test locally before pushing
- **No Risk**: Doesn't actually publish anything
- **Comprehensive**: Covers all release steps
- **Cross-Platform**: Works on Windows, Linux, macOS

## ⚙️ **Configuration**

### **Required Secrets**
- `CARGO_REGISTRY_TOKEN`: For crates.io publishing
- `GITHUB_TOKEN`: For GitHub API access

### **Environment Variables**
- `CARGO_REGISTRY_TOKEN`: Cargo registry authentication
- `GITHUB_TOKEN`: GitHub API authentication

## 🚨 **Troubleshooting**

### **Common Issues**

#### **Workflow Fails on Validation**
```bash
# Check version format
grep '^version = ' Cargo.toml

# Check CHANGELOG entry
grep "^1.6.6 (" CHANGELOG.md

# Check for uncommitted changes
git status
```

#### **Package Building Fails**
```bash
# Install cargo-deb
cargo install cargo-deb

# Install alien (Ubuntu/Debian)
sudo apt-get install alien

# Test locally
.\scripts\test-release.ps1
```

#### **Homebrew Updates Fail**
- Check repository permissions
- Verify GitHub token has write access
- Ensure personal forks are up to date

### **Manual Override**
If automation fails, you can still release manually:
```bash
# Publish to crates.io
cargo publish

# Build packages manually
cargo deb
alien --verbose --to-rpm ./target/debian/tidy-viewer_<VERSION>_amd64.deb

# Update Homebrew manually
brew bump-formula-pr --version=<VERSION> tidy-viewer
```

## 📊 **Monitoring**

### **GitHub Actions**
- **URL**: https://github.com/alexhallam/tv/actions
- **Workflow**: `Release Process`
- **Status**: Check for green checkmarks

### **Crates.io**
- **URL**: https://crates.io/crates/tidy-viewer
- **Verification**: Check version appears in list

### **Homebrew**
- **Personal Tap**: https://github.com/alexhallam/homebrew-tidy-viewer
- **Core**: https://github.com/Homebrew/homebrew-core

## 🎯 **Best Practices**

### **Before Releasing**
1. **Test Locally**: Always run local tests first
2. **Update CHANGELOG**: Document all changes
3. **Check Dependencies**: Ensure all deps are up to date
4. **Review Code**: Run clippy and fix warnings

### **During Release**
1. **Monitor Workflow**: Watch GitHub Actions progress
2. **Verify Publications**: Check crates.io and Homebrew
3. **Test Installation**: Verify packages work correctly

### **After Release**
1. **Update Documentation**: Ensure README reflects new version
2. **Monitor Issues**: Watch for user feedback
3. **Plan Next Release**: Start working on next version

## 🔗 **Related Documentation**

- [Release Checklist](RELEASE.md): Manual release process
- [Testing Guide](TESTING.md): Comprehensive testing instructions
- [GitHub Actions](https://docs.github.com/en/actions): Workflow documentation

## 📝 **Changelog**

### **v1.6.5** (2025-01-27)
- ✅ Added automated release workflow
- ✅ Created local testing scripts
- ✅ Added package distribution automation
- ✅ Added Homebrew formula updates
- ✅ Added comprehensive validation steps

---

**Note**: This automation significantly reduces manual work and ensures consistent releases. The local testing scripts provide immediate feedback without affecting production systems.

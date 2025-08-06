# Release Checklist for Tidy-Viewer

This document outlines the complete process for releasing new versions of `tidy-viewer`. As the project matures, releases will become less frequent, so this checklist ensures no steps are missed during the release process.

## 📋 Pre-Release Checklist

### 1. Documentation Updates
- [ ] **README.md**: Update version number in the help section
- [ ] **CHANGELOG.md**: Document all changes for the new version
- [ ] **Version Bump**: Update version in `Cargo.toml`

### 2. Code Quality
- [ ] **Tests**: Ensure all tests pass (`cargo test`)
- [ ] **Build**: Verify clean build (`cargo build --release`)
- [ ] **Format**: Check code formatting (`cargo fmt --all -- --check`)

## 🚀 Release Process

### Step 1: Prepare Release Commit
```bash
# Create and push a "prep" commit
git add .
git commit -m "Prepare for release v<version>"
git push origin main
```

### Step 2: Create and Push Git Tag
```bash
# Ensure you're on main branch and up to date
git checkout main
git pull origin main

# Create local tag matching version number
git tag <version>

# Push tag to trigger GitHub Actions
git push origin <version>
```

### Step 3: Publish to Cargo
```bash
# Publish to crates.io
cargo publish
```

## 📦 Package Distribution

### Debian Package
```bash
# Install cargo-deb if not already installed
cargo install cargo-deb

# Build Debian package
cargo deb

# The .deb file will be in ./target/debian/
# Upload to GitHub releases page
```

### RPM Package
```bash
# Convert Debian package to RPM using alien
alien --verbose --to-rpm ./target/debian/tidy-viewer_<VERSION_NUMBER>_amd64.deb

# The .rpm file will be in ./tv/*.rpm
# Upload to GitHub releases page
```

## 🍺 Homebrew Distribution

### Personal Homebrew Tap
```bash
# Update personal homebrew tap
brew bump-formula-pr --version=<version_number> tidy-viewer

# Get SHA256 of the release tarball
wget https://github.com/alexhallam/tv/archive/refs/tags/<version>.tar.gz
sha256sum <version>.tar.gz

# Update the formula at: https://github.com/alexhallam/homebrew-tidy-viewer/blob/main/tidy-viewer.rb
# - Update version number
# - Update SHA256 hash
```

### Homebrew Core
```bash
# Update personal homebrew-core fork
# 1. Go to https://github.com/alexhallam/homebrew-core
# 2. Click "Fetch upstream"

# Try the bump command
brew bump-formula-pr --version=<version> tidy-viewer

# If manual update needed:
# 1. Get SHA256 of release tarball
wget https://github.com/alexhallam/tv/archive/refs/tags/<version>.tar.gz
sha256sum <version>.tar.gz

# 2. Update the formula:
#    - Update version number in URL
#    - Update SHA256 hash
#    - Create branch named: tidy-viewer-<version> (e.g., tidy-viewer-1.4.6)

# 3. Push to personal fork and create PR to main homebrew
```

## 📝 Version Numbering

Follow semantic versioning: `<major>.<minor>.<patch>`

- **Major**: Breaking changes
- **Minor**: New features (backward compatible)
- **Patch**: Bug fixes (backward compatible)

## 🔍 Post-Release Verification

### 1. Cargo Installation
```bash
# Test installation from crates.io
cargo install tidy-viewer
tv --version
```

### 2. Homebrew Installation
```bash
# Test homebrew installation
brew install tidy-viewer
tv --version
```

### 3. GitHub Actions
- [ ] Verify all CI/CD workflows pass
- [ ] Check that releases are properly tagged
- [ ] Confirm packages are uploaded to releases

## 📚 Additional Notes

### Release Frequency
As `tidy-viewer` approaches completion, releases will become less frequent. This checklist ensures consistency when releases do occur.

### Automation Opportunities
Consider automating these steps in the future:
- Debian package building in GitHub Actions
- Automatic homebrew formula updates
- Release note generation

### Troubleshooting
- If `cargo publish` fails, check that you're logged in: `cargo login`
- For homebrew issues, ensure you have write access to the repositories
- Always test packages locally before distribution

## 🎯 Quick Reference

**Essential Commands:**
```bash
# Version bump
# Update Cargo.toml version

# Tag and push
git tag <version>
git push origin <version>

# Publish
cargo publish

# Package
cargo deb
alien --verbose --to-rpm ./target/debian/tidy-viewer_<VERSION>_amd64.deb

# Homebrew
brew bump-formula-pr --version=<version> tidy-viewer
```

**Key URLs:**
- [Personal Homebrew Tap](https://github.com/alexhallam/homebrew-tidy-viewer)
- [Personal Homebrew Core Fork](https://github.com/alexhallam/homebrew-core)
- [Main Homebrew Core](https://github.com/Homebrew/homebrew-core)

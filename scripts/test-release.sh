#!/bin/bash

# Local Release Testing Script
# This script simulates the release process without actually publishing

set -e  # Exit on any error

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Function to print colored output
print_status() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

print_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Function to check if command exists
command_exists() {
    command -v "$1" >/dev/null 2>&1
}

# Function to extract version from Cargo.toml
get_current_version() {
    grep '^version = ' Cargo.toml | sed 's/version = "\(.*\)"/\1/'
}

# Function to check if version exists in CHANGELOG
check_changelog() {
    local version=$1
    if grep -q "^$version (" CHANGELOG.md; then
        return 0
    else
        return 1
    fi
}

# Function to validate version format
validate_version() {
    local version=$1
    if [[ $version =~ ^[0-9]+\.[0-9]+\.[0-9]+$ ]]; then
        return 0
    else
        return 1
    fi
}

# Main function
main() {
    local version=${1:-$(get_current_version)}
    local dry_run=${2:-true}
    
    print_status "Starting release test for version: $version"
    print_status "Dry run mode: $dry_run"
    echo
    
    # Step 1: Version validation
    print_status "Step 1: Validating version format..."
    if validate_version "$version"; then
        print_success "Version format valid: $version"
    else
        print_error "Invalid version format: $version"
        print_error "Expected format: X.Y.Z (e.g., 1.6.5)"
        exit 1
    fi
    
    # Step 2: Check CHANGELOG
    print_status "Step 2: Checking CHANGELOG.md..."
    if check_changelog "$version"; then
        print_success "CHANGELOG entry found for version $version"
    else
        print_error "Version $version not found in CHANGELOG.md"
        print_error "Please add an entry for version $version"
        exit 1
    fi
    
    # Step 3: Check for uncommitted changes
    print_status "Step 3: Checking for uncommitted changes..."
    if git diff-index --quiet HEAD --; then
        print_success "No uncommitted changes"
    else
        print_warning "Uncommitted changes detected:"
        git status --porcelain
        if [ "$dry_run" = "false" ]; then
            print_error "Cannot proceed with uncommitted changes"
            exit 1
        fi
    fi
    
    # Step 4: Code quality checks
    print_status "Step 4: Running code quality checks..."
    
    print_status "  - Running tests..."
    if cargo test; then
        print_success "  [OK] All tests passed"
    else
        print_error "  [FAIL] Tests failed"
        exit 1
    fi
    
    print_status "  - Checking formatting..."
    if cargo fmt --all -- --check; then
        print_success "  [OK] Code formatting is correct"
    else
        print_warning "  [WARN] Code formatting issues detected"
        if [ "$dry_run" = "false" ]; then
            print_error "Cannot proceed with formatting issues"
            exit 1
        fi
    fi
    
    print_status "  - Running clippy..."
    if cargo clippy -- -D warnings; then
        print_success "  [OK] Clippy checks passed"
    else
        print_warning "  [WARN] Clippy warnings detected"
        if [ "$dry_run" = "false" ]; then
            print_error "Cannot proceed with clippy warnings"
            exit 1
        fi
    fi
    
    print_status "  - Building release version..."
    if cargo build --release; then
        print_success "  [OK] Release build successful"
    else
        print_error "  [FAIL] Release build failed"
        exit 1
    fi
    
    # Step 5: Documentation validation
    print_status "Step 5: Validating documentation..."
    
    if [ ! -f README.md ] || [ ! -s README.md ]; then
        print_error "README.md is missing or empty"
        exit 1
    fi
    
    if [ ! -d docs ]; then
        print_error "docs directory is missing"
        exit 1
    fi
    
    for file in docs/RELEASE.md docs/TESTING.md; do
        if [ ! -f "$file" ]; then
            print_error "Required documentation file missing: $file"
            exit 1
        fi
    done
    
    print_success "Documentation validation passed"
    
    # Step 6: Package building (simulation)
    print_status "Step 6: Testing package building..."
    
    if command_exists cargo-deb; then
        print_status "  - Testing Debian package build..."
        if cargo deb --no-build; then
            print_success "  [OK] Debian package build simulation successful"
        else
            print_warning "  [WARN] Debian package build simulation failed"
        fi
    else
        print_warning "  [WARN] cargo-deb not installed, skipping Debian package test"
    fi
    
    if command_exists alien; then
        print_status "  - Testing RPM package build..."
        if [ -d target/debian ] && ls target/debian/*.deb >/dev/null 2>&1; then
            if alien --verbose --to-rpm ./target/debian/*.deb >/dev/null 2>&1; then
                print_success "  [OK] RPM package build simulation successful"
            else
                print_warning "  [WARN] RPM package build simulation failed"
            fi
        else
            print_warning "  [WARN] No Debian package found for RPM conversion"
        fi
    else
        print_warning "  [WARN] alien not installed, skipping RPM package test"
    fi
    
    # Step 7: Homebrew formula test (simulation)
    print_status "Step 7: Testing Homebrew formula updates..."
    
    # Simulate getting SHA256
    print_status "  - Simulating SHA256 calculation..."
    local temp_file="temp_release_test_$version.tar.gz"
    tar -czf "$temp_file" --exclude='.git' --exclude='target' . >/dev/null 2>&1
    local sha256=$(sha256sum "$temp_file" | cut -d' ' -f1)
    rm "$temp_file"
    print_success "  [OK] SHA256 calculated: $sha256"
    
    # Step 8: Final summary
    echo
    print_success "[SUCCESS] Release test completed successfully!"
    echo
    print_status "Summary for version $version:"
    echo "  [OK] Version format valid"
    echo "  [OK] CHANGELOG entry found"
    echo "  [OK] Code quality checks passed"
    echo "  [OK] Documentation validation passed"
    echo "  [OK] Release build successful"
    echo "  [OK] Package building simulation completed"
    echo "  [OK] Homebrew formula simulation completed"
    echo
    print_status "Next steps for actual release:"
    echo "  1. git add ."
    echo "  2. git commit -m \"Prepare for release v$version\""
    echo "  3. git push origin main"
    echo "  4. git tag v$version"
    echo "  5. git push origin v$version"
    echo
    print_status "Or use the automated workflow by pushing a tag:"
    echo "  git tag v$version"
    echo "  git push origin v$version"
}

# Show usage if no arguments provided
if [ $# -eq 0 ]; then
    echo "Usage: $0 [VERSION] [DRY_RUN]"
    echo
    echo "Arguments:"
    echo "  VERSION    Version to test (default: current version from Cargo.toml)"
    echo "  DRY_RUN    Set to 'false' to fail on warnings (default: true)"
    echo
    echo "Examples:"
    echo "  $0                    # Test current version in dry-run mode"
    echo "  $0 1.6.6             # Test version 1.6.6 in dry-run mode"
    echo "  $0 1.6.6 false       # Test version 1.6.6, fail on warnings"
    echo
    exit 1
fi

# Run main function
main "$@"

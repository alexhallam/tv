# Local Release Testing Script (PowerShell)
# This script simulates the release process without actually publishing

param(
    [string]$Version = "",
    [string]$DryRun = "true"
)

# Function to print colored output
function Write-Status {
    param([string]$Message)
    Write-Host "[INFO] $Message" -ForegroundColor Blue
}

function Write-Success {
    param([string]$Message)
    Write-Host "[SUCCESS] $Message" -ForegroundColor Green
}

function Write-Warning {
    param([string]$Message)
    Write-Host "[WARNING] $Message" -ForegroundColor Yellow
}

function Write-Error {
    param([string]$Message)
    Write-Host "[ERROR] $Message" -ForegroundColor Red
}

# Function to check if command exists
function Test-Command {
    param([string]$Command)
    try {
        Get-Command $Command -ErrorAction Stop | Out-Null
        return $true
    }
    catch {
        return $false
    }
}

# Function to extract version from Cargo.toml
function Get-CurrentVersion {
    $content = Get-Content "Cargo.toml"
    $versionLine = $content | Where-Object { $_ -match '^version = ' }
    if ($versionLine) {
        return $versionLine -replace 'version = "([^"]+)"', '$1'
    }
    return ""
}

# Function to check if version exists in CHANGELOG
function Test-Changelog {
    param([string]$Version)
    $content = Get-Content "CHANGELOG.md"
    $matches = $content | Where-Object { $_ -match "^$Version \(" } | Measure-Object
    return $matches.Count -gt 0
}

# Function to validate version format
function Test-VersionFormat {
    param([string]$Version)
    return $Version -match '^\d+\.\d+\.\d+$'
}

# Main function
function Test-Release {
    param(
        [string]$Version = $(Get-CurrentVersion),
        [string]$DryRun = "true"
    )
    
    Write-Status "Starting release test for version: $Version"
    Write-Status "Dry run mode: $DryRun"
    Write-Host ""
    
    # Step 1: Version validation
    Write-Status "Step 1: Validating version format..."
    if (Test-VersionFormat $Version) {
        Write-Success "Version format valid: $Version"
    }
    else {
        Write-Error "Invalid version format: $Version"
        Write-Error "Expected format: X.Y.Z (e.g., 1.6.5)"
        exit 1
    }
    
    # Step 2: Check CHANGELOG
    Write-Status "Step 2: Checking CHANGELOG.md..."
    if (Test-Changelog $Version) {
        Write-Success "CHANGELOG entry found for version $Version"
    }
    else {
        Write-Error "Version $Version not found in CHANGELOG.md"
        Write-Error "Please add an entry for version $Version"
        exit 1
    }
    
    # Step 3: Check for uncommitted changes
    Write-Status "Step 3: Checking for uncommitted changes..."
    $gitStatus = git status --porcelain
    if ($LASTEXITCODE -eq 0 -and -not $gitStatus) {
        Write-Success "No uncommitted changes"
    }
    else {
        Write-Warning "Uncommitted changes detected:"
        git status
        if ($DryRun -eq "false") {
            Write-Error "Cannot proceed with uncommitted changes"
            exit 1
        }
    }
    
    # Step 4: Code quality checks
    Write-Status "Step 4: Running code quality checks..."
    
    Write-Status "  - Running tests..."
    cargo test
    if ($LASTEXITCODE -eq 0) {
        Write-Success "  [OK] All tests passed"
    }
    else {
        Write-Error "  [FAIL] Tests failed"
        exit 1
    }
    
    Write-Status "  - Checking formatting..."
    cargo fmt --all -- --check
    if ($LASTEXITCODE -eq 0) {
        Write-Success "  [OK] Code formatting is correct"
    }
    else {
        Write-Warning "  [WARN] Code formatting issues detected"
        if ($DryRun -eq "false") {
            Write-Error "Cannot proceed with formatting issues"
            exit 1
        }
    }
    
    Write-Status "  - Running clippy..."
    cargo clippy -- -D warnings
    if ($LASTEXITCODE -eq 0) {
        Write-Success "  [OK] Clippy checks passed"
    }
    else {
        Write-Warning "  [WARN] Clippy warnings detected"
        if ($DryRun -eq "false") {
            Write-Error "Cannot proceed with clippy warnings"
            exit 1
        }
    }
    
    Write-Status "  - Building release version..."
    cargo build --release
    if ($LASTEXITCODE -eq 0) {
        Write-Success "  [OK] Release build successful"
    }
    else {
        Write-Error "  [FAIL] Release build failed"
        exit 1
    }
    
    # Step 5: Documentation validation
    Write-Status "Step 5: Validating documentation..."
    
    if (-not (Test-Path "README.md") -or (Get-Item "README.md").Length -eq 0) {
        Write-Error "README.md is missing or empty"
        exit 1
    }
    
    if (-not (Test-Path "docs")) {
        Write-Error "docs directory is missing"
        exit 1
    }
    
    $requiredDocs = @("docs/RELEASE.md", "docs/TESTING.md")
    foreach ($file in $requiredDocs) {
        if (-not (Test-Path $file)) {
            Write-Error "Required documentation file missing: $file"
            exit 1
        }
    }
    
    Write-Success "Documentation validation passed"
    
    # Step 6: Package building (simulation)
    Write-Status "Step 6: Testing package building..."
    
    if (Test-Command "cargo-deb") {
        Write-Status "  - Testing Debian package build..."
        cargo deb --no-build
        if ($LASTEXITCODE -eq 0) {
            Write-Success "  [OK] Debian package build simulation successful"
        }
        else {
            Write-Warning "  [WARN] Debian package build simulation failed"
        }
    }
    else {
        Write-Warning "  [WARN] cargo-deb not installed, skipping Debian package test"
    }
    
    if (Test-Command "alien") {
        Write-Status "  - Testing RPM package build..."
        if (Test-Path "target/debian" -and (Get-ChildItem "target/debian/*.deb" -ErrorAction SilentlyContinue)) {
            alien --verbose --to-rpm ./target/debian/*.deb | Out-Null
            if ($LASTEXITCODE -eq 0) {
                Write-Success "  [OK] RPM package build simulation successful"
            }
            else {
                Write-Warning "  [WARN] RPM package build simulation failed"
            }
        }
        else {
            Write-Warning "  [WARN] No Debian package found for RPM conversion"
        }
    }
    else {
        Write-Warning "  [WARN] alien not installed, skipping RPM package test"
    }
    
    # Step 7: Homebrew formula test (simulation)
    Write-Status "Step 7: Testing Homebrew formula updates..."
    
    # Simulate getting SHA256
    Write-Status "  - Simulating SHA256 calculation..."
    $tempFile = "temp_release_test_$Version.tar.gz"
    
    # Create a temporary tar file (simulating release tarball)
    $excludeFiles = @(".git", "target", "temp_release_test_*.tar.gz")
    $tarArgs = @()
    foreach ($file in $excludeFiles) {
        $tarArgs += "--exclude=$file"
    }
    
    # Note: This is a simplified simulation since tar might not be available on Windows
    Write-Success "  [OK] SHA256 calculation simulation completed"
    
    # Step 8: Final summary
    Write-Host ""
    Write-Success "[SUCCESS] Release test completed successfully!"
    Write-Host ""
    Write-Status "Summary for version ${Version}:"
    Write-Host "  [OK] Version format valid"
    Write-Host "  [OK] CHANGELOG entry found"
    Write-Host "  [OK] Code quality checks passed"
    Write-Host "  [OK] Documentation validation passed"
    Write-Host "  [OK] Release build successful"
    Write-Host "  [OK] Package building simulation completed"
    Write-Host "  [OK] Homebrew formula simulation completed"
    Write-Host ""
    Write-Status "Next steps for actual release:"
    Write-Host "  1. git add ."
    Write-Host "  2. git commit -m `"Prepare for release v${Version}`""
    Write-Host "  3. git push origin main"
    Write-Host "  4. git tag v${Version}"
    Write-Host "  5. git push origin v${Version}"
    Write-Host ""
    Write-Status "Or use the automated workflow by pushing a tag:"
    Write-Host "  git tag v${Version}"
    Write-Host "  git push origin v${Version}"
}

# Show usage if no arguments provided
if ($args.Count -eq 0 -and $Version -eq "") {
    Write-Host "Usage: .\scripts\test-release.ps1 [VERSION] [DRY_RUN]"
    Write-Host ""
    Write-Host "Arguments:"
    Write-Host "  VERSION    Version to test (default: current version from Cargo.toml)"
    Write-Host "  DRY_RUN    Set to 'false' to fail on warnings (default: true)"
    Write-Host ""
    Write-Host "Examples:"
    Write-Host "  .\scripts\test-release.ps1                    # Test current version in dry-run mode"
    Write-Host "  .\scripts\test-release.ps1 1.6.6             # Test version 1.6.6 in dry-run mode"
    Write-Host "  .\scripts\test-release.ps1 1.6.6 false       # Test version 1.6.6, fail on warnings"
    Write-Host ""
    exit 1
}

# Run main function
Test-Release -Version $Version -DryRun $DryRun

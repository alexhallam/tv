# Generate and copy documentation script for Windows
# This script generates Rust documentation and copies it to the docs directory

Write-Host "🔧 Generating Rust documentation..." -ForegroundColor Green

# Generate documentation for all crates
cargo doc --workspace --no-deps

# Copy documentation to docs directory
Write-Host "📁 Copying documentation to docs/..." -ForegroundColor Green
Copy-Item -Path "target/doc/*" -Destination "docs/" -Recurse -Force

Write-Host "✅ Documentation generated successfully!" -ForegroundColor Green
Write-Host "📖 View documentation at: docs/index.html" -ForegroundColor Cyan
Write-Host "🔗 Rust API docs at: docs/tidy_viewer_core/index.html" -ForegroundColor Cyan

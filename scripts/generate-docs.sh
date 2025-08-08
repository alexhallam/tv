#!/bin/bash

# Generate and copy documentation script
# This script generates Rust documentation and copies it to the docs directory

set -e

echo "🔧 Generating Rust documentation..."

# Generate documentation for all crates
cargo doc --workspace --no-deps

# Copy documentation to docs directory
echo "📁 Copying documentation to docs/..."
cp -r target/doc/* docs/

echo "✅ Documentation generated successfully!"
echo "📖 View documentation at: docs/index.html"
echo "🔗 Rust API docs at: docs/tidy_viewer_core/index.html"

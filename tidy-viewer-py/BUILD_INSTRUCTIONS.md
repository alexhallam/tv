# Building tidy-viewer-py for PyPI

This package has a dependency on `tidy-viewer-core`, which is a local Rust crate. To build and publish this package to PyPI, follow these steps:

## Prerequisites

- Python 3.8+
- Rust toolchain
- maturin (`pip install maturin`)

## Building for Distribution

1. **Prepare the build** - Copy tidy-viewer-core into the package:
   ```bash
   cd tidy-viewer-py
   python prepare_build.py
   ```

2. **Build the source distribution and wheels**:
   ```bash
   maturin build --release
   ```

3. **For development/testing**:
   ```bash
   maturin develop
   ```

## Publishing to PyPI

1. Prepare the build as described above
2. Build the wheels:
   ```bash
   maturin build --release
   ```
3. Upload to PyPI:
   ```bash
   maturin publish
   ```

## Important Notes

- The `prepare_build.py` script copies `tidy-viewer-core` into the package directory and updates all workspace dependencies to concrete versions
- The copied `tidy-viewer-core` directory is git-ignored and should not be committed
- Always run `prepare_build.py` before building or publishing
- The `MANIFEST.in` file ensures that all necessary files are included in the source distribution

## Testing the Package

After building, you can test the package installation:

```bash
pip install dist/tidy_viewer_py-*.whl
python -c "import tidy_viewer_py; print('Import successful!')"
```
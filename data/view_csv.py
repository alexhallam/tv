import sys
import tidy_viewer_py as tv

def main():
    # If filename provided as command-line argument
    if len(sys.argv) > 1:
        filename = sys.argv[1]
    else:
        # If piped in via PowerShell
        filename = sys.stdin.read().strip()

    if not filename:
        print("Usage:")
        print("  uv run python view_csv.py <filename.csv>")
        print("  'filename.csv' | uv run python view_csv.py")
        sys.exit(1)

    tv.print_csv(filename)

if __name__ == "__main__":
    main()

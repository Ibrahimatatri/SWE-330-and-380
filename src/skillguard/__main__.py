"""Enable python -m skillguard without running on ordinary imports."""

from cli import main

# ... what?
if __name__ == "__main__":
    raise SystemExit(main())

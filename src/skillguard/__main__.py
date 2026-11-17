"""Enable python -m skillguard without running on ordinary imports."""

from skillguard.cli import main

if __name__ == "__main__":
    raise SystemExit(main())

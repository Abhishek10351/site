#!/usr/bin/env python
import os
import sys


# Separate definition to ease calling this in other scripts.
def main():
    """Entry point for Django management script."""

    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'pydis_site.settings')
    try:
        from django.core.management import execute_from_command_line
    except ImportError as exc:
        raise ImportError(
            "Couldn't import Django. Are you sure it's installed and "
            "available on your PYTHONPATH environment variable? Did you "
            "forget to activate a virtual environment?"
        ) from exc
    execute_from_command_line(sys.argv)


if __name__ == '__main__':
    main()

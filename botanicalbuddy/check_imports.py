import sys
import django

print(f"Django version: {django.get_version()}")
print(f"Django installed at: {django.__file__}")
print("sys.path:")
for path in sys.path:
    print(f"  - {path}")
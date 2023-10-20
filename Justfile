export DJANGO_SETTINGS_MODULE := "docserv.settings"

# Show this help
help:
  @just --list

# Run manage.py
manage *ARGS:
  pipenv run ./manage.py {{ARGS}}

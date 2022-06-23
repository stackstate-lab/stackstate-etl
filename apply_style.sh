 #/bin/bash
set -e
PACKAGE=stackstate_etl
echo "Formatting code..."
poetry run black $PACKAGE tests
echo "Sorting imports..."
poetry run isort $PACKAGE
echo "Checking code style..."
poetry run flakehell lint
echo "Checking typing..."
poetry run mypy $PACKAGE
echo "All done!"
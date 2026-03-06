#!/usr/bin/env bash
# =============================================================================
# Setup Supabase database for Boutique Management
# =============================================================================
# Prerequisites:
#   1. Create a Supabase project at https://supabase.com
#   2. Copy .env.example to .env and fill in your DATABASE_URL
#   3. Run this script: bash setup_supabase.sh
# =============================================================================
set -o errexit

echo "=== Boutique Management - Supabase Setup ==="
echo ""

# Check .env file exists
if [ ! -f .env ]; then
    echo "ERROR: .env file not found."
    echo "Run: cp .env.example .env"
    echo "Then fill in your Supabase DATABASE_URL and SECRET_KEY."
    exit 1
fi

# Check DATABASE_URL is set and not the placeholder
source <(grep -v '^#' .env | grep DATABASE_URL | head -1)
if [ -z "$DATABASE_URL" ] || [[ "$DATABASE_URL" == *"[PROJECT-REF]"* ]]; then
    echo "ERROR: DATABASE_URL is not set or still contains placeholder values."
    echo "Update your .env file with the connection string from Supabase Dashboard."
    echo "  Supabase Dashboard > Settings > Database > Connection string > URI"
    exit 1
fi

echo "[1/4] Installing dependencies..."
pip install -r requirements.txt --quiet

echo "[2/4] Running database migrations..."
python manage.py migrate --noinput

echo "[3/4] Setting up user roles (Manager, Sales, Seamstress)..."
python manage.py setup_roles

echo "[4/4] Collecting static files..."
python manage.py collectstatic --noinput --clear --quiet

echo ""
echo "=== Setup complete! ==="
echo ""
echo "To create an admin user, run:"
echo "  python manage.py createsuperuser"
echo ""
echo "To start the development server, run:"
echo "  DEBUG=true python manage.py runserver"
echo ""

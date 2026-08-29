#!/usr/bin/env bash
# Repo root से चलाएं (जहां backend/ और frontend/ दिखते हैं)
set -e

echo "1) Removing fabricated/orphaned files..."
rm -f backend/app/services/rotary_screw.py backend/app/api/v1/rotary_screw.py
rm -f backend/app/services/demand.py backend/app/api/v1/demand.py
rm -f backend/app/services/multi_compressor.py backend/app/api/v1/multi_compressor.py
rm -f backend/app/services/air_dryer.py backend/app/api/v1/air_dryer.py
rm -f backend/app/services/receiver_piping.py backend/app/api/v1/receiver_piping.py
rm -f backend/app/services/system_orchestrator.py backend/app/api/v1/system_orchestrator.py
rm -f backend/app/services/technology_selection.py backend/app/api/v1/technology_selection.py

echo "2) Clearing api/v1/__init__.py (dead/duplicate router aggregator)..."
: > backend/app/api/v1/__init__.py

echo "3) Cleaning dangling imports and registrations from main.py..."
python3 - << 'PYEOF'
path = "backend/app/main.py"
with open(path) as f:
    content = f.read()

dead_imports = [
    'from app.api.v1.air_dryer import router as air_dryer_router\n',
    'from app.api.v1.demand import router as demand_router\n',
    'from app.api.v1.multi_compressor import router as multi_compressor_router\n',
    'from app.api.v1.receiver_piping import router as receiver_piping_router\n',
    'from app.api.v1.rotary_screw import router as rotary_screw_router\n',
    'from app.api.v1.system_orchestrator import router as system_orchestrator_router\n',
]
for line in dead_imports:
    content = content.replace(line, '')

marker = "# --- Compressed Air Engine Routers Registration ---"
idx = content.find(marker)
if idx != -1:
    content = content[:idx].rstrip() + "\n"

with open(path, "w") as f:
    f.write(content)
print("main.py cleaned")
PYEOF

echo "4) pyproject.toml: rename + add reportlab, remove httpx2..."
python3 - << 'PYEOF'
path = "backend/pyproject.toml"
with open(path) as f:
    content = f.read()

content = content.replace(
    'name = "kes-compressor-suite"',
    'name = "kamra-compressor-os"',
)
content = content.replace(
    'description = "KES Compressor Engineering Suite - Compressor sizing, performance, utilities, compliance, and reporting SaaS."',
    'description = "Kamra Compressor OS - Vendor-neutral factory compressed-air and compressor engineering, audit, optimization, and decision-support platform."',
)
content = content.replace(
    '    "pyjwt>=2.10,<3.0",\n]',
    '    "pyjwt>=2.10,<3.0",\n    "reportlab>=4.2,<5.0",\n]',
)
content = content.replace(
    '    "httpx>=0.28,<1.0",\n    "httpx2>=2.10,<3.0",\n',
    '    "httpx>=0.28,<1.0",\n',
)

with open(path, "w") as f:
    f.write(content)
print("pyproject.toml updated")
PYEOF

echo "5) Rebranding app_name (backend config)..."
sed -i 's/app_name: str = "KES Compressor Engineering Suite"/app_name: str = "Kamra Compressor OS"/' backend/app/core/config.py

echo "6) Updating hardcoded name in test_health.py..."
sed -i 's/"service": "KES Compressor Engineering Suite",/"service": "Kamra Compressor OS",/' backend/tests/api/test_health.py
sed -i 's/assert data\["name"\] == "KES Compressor Engineering Suite"/assert data["name"] == "Kamra Compressor OS"/' backend/tests/api/test_health.py

echo "7) Rebranding frontend..."
sed -i 's/KES Compressor Engineering Suite/Kamra Compressor OS/g' \
  frontend/src/layouts/AppLayout.tsx \
  frontend/src/pages/LoginPage.tsx \
  frontend/src/pages/CompressorEngineeringPage.tsx \
  frontend/src/pages/DashboardPage.tsx
sed -i 's/kes_compressor_access_token/kamra_compressor_access_token/g' frontend/src/features/auth/authStorage.ts
sed -i 's/"name": "frontend",/"name": "kamra-compressor-os-frontend",/' frontend/package.json
sed -i 's|<title>frontend</title>|<title>Kamra Compressor OS</title>|' frontend/index.html

echo "8) Adding frontend .env.example..."
cat > frontend/.env.example << 'ENVEOF'
# Backend API base URL (required -- the app fails fast without it).
# Local development against the backend at http://localhost:8000:
VITE_API_BASE_URL=http://localhost:8000
ENVEOF

echo ""
echo "Done. Now verify:"
echo "  cd backend && pytest -q"
echo "  cd ../frontend && npm install && npx tsc -b && npx vitest run"

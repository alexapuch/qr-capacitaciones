# Sistema QR de capacitaciones (Backend + páginas HTML)

Incluye:
- Página pública `/p?token=...` (registro + PRE / CURP + POST)
- Dashboard simple `/dashboard` (login, tablas, export CSV)
- Admin Django `/admin` (gestión avanzada)
- API en `/api/*` (QR, tests, reportes)
- Seeds con 4 cursos + preguntas PRE/POST

## 1) Probar en Windows (local)
1. Abre una terminal en esta carpeta
2. Ejecuta:
   ```bash
   docker compose up -d --build
   ```
3. Abre:
- Público: http://localhost:8000/p?token=...
- Dashboard: http://localhost:8000/dashboard
- Admin: http://localhost:8000/admin

Credenciales iniciales (se crean automáticamente):
- Email: admin@example.com
- Password: admin12345

## 2) Generar un QR (desde dashboard o API)
En el Dashboard inicia sesión y carga reportes.
Para generar QR usa el endpoint (requiere login JWT), o desde el Admin Django puedes usar una herramienta simple (por ahora es endpoint).

Ejemplo (PowerShell):
1) Login:
```powershell
$body = @{ email="admin@example.com"; password="admin12345" } | ConvertTo-Json
$resp = Invoke-RestMethod -Method Post -Uri http://localhost:8000/api/auth/login -ContentType "application/json" -Body $body
$token = $resp.token
```

2) Ver cursos:
```powershell
Invoke-RestMethod -Method Get -Uri http://localhost:8000/api/admin/catalog/courses -Headers @{ Authorization = "Bearer $token" }
```

3) Generar QR PRE para course_id=1:
```powershell
$body = @{ qr_type="PRE"; expires_in_days=30 } | ConvertTo-Json
Invoke-RestMethod -Method Post -Uri http://localhost:8000/api/admin/courses/1/qr -Headers @{ Authorization = "Bearer $token" } -ContentType "application/json" -Body $body
```
La respuesta incluye `qr_url`. Ese link lo conviertes a QR con cualquier generador.

## 3) Deploy en Render (sin programar)
### Opción recomendada: Render Blueprint (con `render.yaml`)
1. Crea un repositorio en GitHub y sube esta carpeta.
2. En Render: **New + > Blueprint**
3. Conecta tu repo y elige el `render.yaml`
4. Click en **Apply** / **Deploy**
5. Cuando termine, tendrás una URL pública:
   - Público: https://TU-SERVICIO.onrender.com/p?token=...
   - Dashboard: https://TU-SERVICIO.onrender.com/dashboard
   - Admin: https://TU-SERVICIO.onrender.com/admin

Cambia las credenciales ADMIN_EMAIL y ADMIN_PASSWORD en Render (Environment) después del primer deploy.

## Notas
- El seed se ejecuta al iniciar si `SEED_ON_START=1`. Cuando ya tengas datos reales, cambia a `0` para que no vuelva a re-seedear.
- El reporte está limitado a 5000 filas por consulta para no saturar.

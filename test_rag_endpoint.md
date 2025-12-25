# Test RAG Endpoint

## Quick Test Script

Save this as `test_rag.ps1` and run it:

```powershell
$body = @{
    query = "newspaper 1964"
    n_results = 1
} | ConvertTo-Json

$headers = @{
    "Content-Type" = "application/json"
    "X-Session-ID" = "test-session"
}

Invoke-WebRequest -Uri "http://localhost:8000/api/rag/generate_layout" `
    -Method POST `
    -Headers $headers `
    -Body $body
```

Or use this simpler curl command:
```bash
curl -X POST http://localhost:8000/api/rag/generate_layout \
  -H "Content-Type: application/json" \
  -H "X-Session-ID: test" \
  -d '{"query":"newspaper"}'
```

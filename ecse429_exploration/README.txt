ECSE 429 Part A exploratory scripts (PowerShell + curl.exe)

Run from PowerShell while the Java Todo Manager server is running:
  powershell -ExecutionPolicy Bypass -File .\todos.ps1
  powershell -ExecutionPolicy Bypass -File .\categories.ps1

Run scripts one at a time. Both create temporary records and attempt cleanup.
Each run writes logs/<area>-<unique-id>/summary.csv, results.json, and individual request/response files.
The 'expected' column comes from Swagger, not from verified behavior. Review differences manually.
HTTP responses are observations, not JUnit assertions. Convert findings to independent JUnit tests.
Do not run on a server containing important data without backing it up first.
The OpenAPI document does not define body schemas. Relationship payloads use {"id":"..."} as an exploratory hypothesis.
If a create response lacks a JSON id, dependent probes are skipped. Inspect the raw response.

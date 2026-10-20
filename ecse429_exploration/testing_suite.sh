# Set base URL
BASE_URL="http://localhost:4567"

# 1. Projects - GET and POST
curl -v -X GET "$BASE_URL/projects"
curl -v -X POST "$BASE_URL/projects" -H "Content-Type: application/json" -d '{"title": "Test Project", "completed": false}'
curl -v -X PUT "$BASE_URL/projects" # Expect 405 Method Not Allowed

# 2. Specific Project - Update and Fetch
# Replace 1 with actual ID returned from POST
curl -v -X GET "$BASE_URL/projects/1"
curl -v -X POST "$BASE_URL/projects/1" -H "Content-Type: application/json" -d '{"title": "Amended Project"}'
curl -v -X DELETE "$BASE_URL/projects/1"

# 3. Relationships - Tasks and Categories
curl -v -X POST "$BASE_URL/projects/1/tasks" -H "Content-Type: application/json" -d '{"id": "1"}'
curl -v -X DELETE "$BASE_URL/projects/1/tasks/1"

# 4. Undocumented API Discovery
curl -v -X GET "$BASE_URL/docs"

# 5. Shutdown Server (Run Last)[cite: 1]
curl -v -X GET "$BASE_URL/shutdown"
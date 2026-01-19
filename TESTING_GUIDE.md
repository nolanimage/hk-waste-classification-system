# Testing Guide

## Quick Status Check

### 1. Check if System is Running
```bash
# Check Docker containers
docker-compose ps

# Test API health
curl http://localhost:8000/health
```

Expected output: `{"status":"healthy"}`

## Testing Content Filtering

### Test 1: Valid Waste Item (Should Pass)
```bash
curl -X POST http://localhost:8000/api/classify \
  -H "Content-Type: application/json" \
  -d '{"text": "a crumpled aluminum can"}'
```

### Test 2: Inappropriate Content (Should Be Blocked)
```bash
curl -X POST http://localhost:8000/api/classify \
  -H "Content-Type: application/json" \
  -d '{"text": "a human body"}'
```

Expected: `400 Bad Request` with error message about inappropriate content

### Test 3: Non-Waste Content (Should Be Blocked)
```bash
curl -X POST http://localhost:8000/api/classify \
  -H "Content-Type: application/json" \
  -d '{"text": "I love programming"}'
```

Expected: `400 Bad Request` with message about waste items only

## Testing Material Recognition

### Test Material Identification
```bash
# Test aluminum can (should identify as metal)
curl -X POST http://localhost:8000/api/classify \
  -H "Content-Type: application/json" \
  -d '{"text": "empty aluminum soda can"}' | python3 -m json.tool
```

Look for:
- `"category": "metal"`
- `"binColor": "yellow"`
- Explanation should mention material

### Test Plastic Bottle
```bash
curl -X POST http://localhost:8000/api/classify \
  -H "Content-Type: application/json" \
  -d '{"text": "empty plastic water bottle"}' | python3 -m json.tool
```

Look for:
- `"category": "plastic"`
- `"binColor": "brown"`
- Material identification in explanation

## Testing Multi-Item Classification

```bash
curl -X POST http://localhost:8000/api/classify \
  -H "Content-Type: application/json" \
  -d '{"text": "an aluminum can and a plastic bottle"}' | python3 -m json.tool
```

Expected: `total_items: 2` with both items classified

## Using Python Test Script

```bash
# Run comprehensive tests
python3 test_improvements.py
```

This will test:
1. ✅ API health
2. ✅ Content filtering (appropriate/inappropriate)
3. ✅ Material recognition
4. ✅ Multi-item classification

## Using Web Interface

1. Open browser: http://localhost:3000
2. Select "Text Description"
3. Enter: "a crumpled aluminum can"
4. Click "Classify"
5. Check results for material identification

## What to Look For

### ✅ Content Filtering Working:
- Inappropriate content returns 400 error
- Valid waste items are processed normally
- Clear error messages

### ✅ Material Recognition Working:
- LLM identifies materials (metal, plastic, paper, glass)
- Explanations mention material composition
- Correct bin selection based on material

### ✅ System Working:
- Fast responses (< 5 seconds)
- Accurate classifications
- Clear explanations

## Troubleshooting

### If API is not responding:
```bash
# Restart containers
docker-compose restart backend

# Check logs
docker-compose logs backend
```

### If content filter is too strict:
- Check `backend/app/services/content_filter.py`
- Adjust `INAPPROPRIATE_KEYWORDS` if needed

### If material recognition is poor:
- Check LLM prompt in `backend/app/services/openrouter.py`
- Verify RAG examples are being retrieved
- Check OpenRouter API key and credits

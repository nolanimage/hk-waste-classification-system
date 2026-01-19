#!/bin/bash
set -e

echo "Starting waste classification backend..."

# Check if RAG database needs seeding
python3 -c "
import sys
try:
    from app.services.rag_service import rag_service
    examples = rag_service.get_all_examples()
    if len(examples) == 0:
        print('RAG database is empty, seeding...')
        from app.services.seed_data import seed_rag_database
        seed_rag_database()
        print('Seeding completed!')
    else:
        print(f'RAG database already has {len(examples)} examples')
except Exception as e:
    print(f'Warning: Could not check/seed database: {e}')
    print('Continuing anyway...')
    sys.exit(0)
" || echo "Warning: Database seeding check failed, continuing..."

# Start the application
echo "Starting uvicorn server..."
exec uvicorn app.main:app --host 0.0.0.0 --port 8000

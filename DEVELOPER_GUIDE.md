# Developer Guide

## Code Structure & Architecture

### Backend Architecture

```
FastAPI Server (server.py)
    ├── API Routes (/api/*)
    ├── Agent Orchestration
    └── MongoDB Integration

7 Agent Pipeline:
    [1] Validation → [2] Alignment → [3] Mutation Detection →
    [4] Annotation → [5] Classification → [6] Retrieval →
    [7] AI Explanation
```

### Agent Communication

Agents are **loosely coupled** - each outputs a dictionary that becomes input for the next:

```python
validation_output = validation_agent.validate(sequence)
↓
alignment_output = alignment_agent.align(validation_output['cleaned_sequence'])
↓
mutation_output = mutation_agent.detect(alignment_output['aligned_reference'], ...)
↓
... and so on
```

### Adding a New Agent

1. Create `agents/new_agent.py`
2. Implement class with clear input/output
3. Add to pipeline in `server.py`
4. Update frontend to display new data

Example skeleton:
```python
class NewAgent:
    def __init__(self):
        # Initialize resources
        pass
    
    def process(self, input_data: Dict) -> Dict:
        # Process and return results
        return {"success": True, "data": ...}
```

## Frontend Architecture

### Component Hierarchy

```
App.js
└── Dashboard.js
    ├── SequenceInput.js
    └── ResultsView.js
        ├── MutationMap.js
        ├── AlignmentViewer.js
        ├── EvidenceList.js
        └── AIExplanation.js
```

### Data Flow

```
User Input → Dashboard state → API call → Results → ResultsView
```

State management uses React hooks (useState):
- `sequence`: Current DNA input
- `results`: API response
- `isAnalyzing`: Loading state

### Adding New Visualization

1. Create component in `components/`
2. Import in `ResultsView.js`
3. Add new tab in Tabs component
4. Pass relevant data from results prop

## API Integration

### Adding New Endpoint

In `server.py`:

```python
@api_router.post("/new-endpoint")
async def new_endpoint(request: RequestModel):
    # Your logic
    return {"result": data}
```

In frontend:

```javascript
const response = await axios.post(
    `${API}/new-endpoint`,
    { data: input }
);
```

## Database Schema

MongoDB collections:

```javascript
analyses: {
    _id: ObjectId,
    analysis_id: String,
    timestamp: String,
    gene: String,
    validation: {},
    alignment: {},
    mutations: {},
    annotations: {},
    classification: {},
    evidence: {},
    explanation: {}
}
```

## Testing Strategy

### Backend Testing

```bash
# Test individual agent
python -c "
from agents.validation_agent import ValidationAgent
agent = ValidationAgent()
result = agent.validate('ATCG')
print(result)
"

# Test API endpoint
curl -X POST http://localhost:8001/api/analyze \
  -H "Content-Type: application/json" \
  -d '{"sequence": "ATCG", "gene": "TP53"}'
```

### Frontend Testing

```bash
# Manual testing in browser
yarn start
# Visit http://localhost:3000

# Component testing (if added)
yarn test
```

## Performance Optimization

### Current Bottlenecks

1. **Alignment**: O(n*m) complexity
   - For 5000bp sequences: ~2 seconds
   - Solution: Consider using BLAST for initial filtering

2. **AI Explanation**: Network latency
   - Gemini API: 2-5 seconds
   - Solution: Cache common mutation patterns

3. **Database Search**: Linear scan
   - Solution: Add indexes on position and mutation_type

### Optimization Tips

```python
# Cache expensive computations
@lru_cache(maxsize=128)
def expensive_function(input):
    ...

# Use async for I/O operations
async def fetch_data():
    async with aiohttp.ClientSession() as session:
        ...

# Batch database operations
await db.collection.insert_many(documents)
```

## Common Development Tasks

### Adding a New Gene

1. Add FASTA file to `backend/data/`:
```
>BRCA1 Reference Sequence
ATGCGA...
```

2. Update `load_reference_sequence()` in `server.py`

3. Update frontend gene selector

### Expanding ClinVar Database

1. Download from https://ftp.ncbi.nlm.nih.gov/pub/clinvar/
2. Parse VCF/CSV format
3. Convert to our schema
4. Replace `clinvar_sample.csv`

### Changing AI Model

In `explanation_agent.py`:

```python
# Current: Gemini 3 Flash
chat.with_model("gemini", "gemini-3-flash-preview")

# Change to: GPT-4
chat.with_model("openai", "gpt-4-turbo")
```

## Security Considerations

### Current State
- No authentication
- Public API endpoints
- No rate limiting
- Demo API key

### Production Requirements
1. Add JWT authentication
2. Implement rate limiting
3. Use environment-specific API keys
4. Add HTTPS
5. Sanitize user inputs
6. Add CORS restrictions

## Debugging Tips

### Backend Issues

```bash
# View detailed logs
tail -f /var/log/supervisor/backend.err.log

# Test agent in isolation
python
>>> from agents.validation_agent import ValidationAgent
>>> agent = ValidationAgent()
>>> agent.validate("INVALID123")
```

### Frontend Issues

```javascript
// Add console.log in Dashboard.js
console.log("API Response:", response.data);

// Check network tab in browser DevTools
// Look for failed requests
```

### Common Errors

**"ModuleNotFoundError: No module named 'biopython'"**
- Solution: `pip install -r requirements.txt`

**"CORS policy error"**
- Solution: Check CORS_ORIGINS in backend/.env

**"MongoDB connection failed"**
- Solution: Ensure MongoDB is running: `brew services start mongodb-community`

## Contributing Guidelines

### Code Style

**Python:**
- Follow PEP 8
- Use type hints
- Add docstrings
- Keep functions < 50 lines

**JavaScript:**
- Use functional components
- Prefer const/let over var
- Use async/await over promises
- Add PropTypes

### Commit Messages

```
feat: Add BRCA1 gene support
fix: Correct frameshift detection logic
docs: Update README with installation steps
refactor: Simplify alignment algorithm
```

### Pull Request Process

1. Fork repository
2. Create feature branch: `git checkout -b feature/new-gene`
3. Make changes with tests
4. Update documentation
5. Submit PR with description

## Deployment

### Local Development
```bash
# Backend
cd backend && uvicorn server:app --reload

# Frontend
cd frontend && yarn start
```

### Production Deployment

**Docker:**
```dockerfile
# Dockerfile for backend
FROM python:3.11
COPY backend /app
RUN pip install -r requirements.txt
CMD ["uvicorn", "server:app", "--host", "0.0.0.0"]
```

**Environment Variables:**
```env
# Production .env
MONGO_URL=mongodb://production-host:27017
DB_NAME=gene_mutations_prod
CORS_ORIGINS=https://yourdomain.com
GEMINI_API_KEY=your-production-key
```

## Resources

- [Biopython Tutorial](https://biopython.org/wiki/Documentation)
- [FastAPI Docs](https://fastapi.tiangolo.com/)
- [React Hooks Guide](https://react.dev/reference/react)
- [MongoDB Manual](https://www.mongodb.com/docs/)

## Contact

For questions about the codebase, see code comments or README.

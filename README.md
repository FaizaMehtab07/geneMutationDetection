# Gene Mutation Detection System - Local Edition

A complete bioinformatics pipeline for detecting and analyzing DNA mutations **without any external API dependencies**. This system runs entirely on your local machine using only open-source libraries.

## What This System Does

Analyzes DNA sequences to:
1. **Validate** sequences (ensure only A, T, C, G nucleotides)
2. **Align** with reference genes using Biopython
3. **Detect** mutations (substitutions, insertions, deletions)
4. **Annotate** protein-level effects (missense, nonsense, frameshift)
5. **Classify** pathogenicity risk (Pathogenic/Benign)

**All processing is LOCAL** - no internet connection or API keys required.

## Real-World Application

When a patient gets DNA sequenced, doctors need to know:
- Are there mutations in cancer-related genes?
- Are these mutations dangerous or harmless?
- What's the predicted clinical impact?

This system automates that analysis using a 5-stage pipeline.

## Technologies Used

- **Python 3.11+** - Core language
- **FastAPI** - Web framework
- **Biopython** - Sequence alignment (PairwiseAligner)
- **Pandas/NumPy** - Data processing
- **React** - Frontend UI
- **No AI APIs** - Pure computational biology

## Quick Start

### Prerequisites

```bash
# Check you have required tools
python --version  # Should be 3.11+
node --version    # Should be 18+
yarn --version    # Should be 1.22+
```

### Backend Setup

```bash
# Navigate to backend
cd backend

# Create virtual environment
python -m venv venv

# Activate virtual environment
source venv/bin/activate  # macOS/Linux
# OR
venv\Scripts\activate     # Windows

# Install dependencies (all local, no API keys)
pip install -r requirements.txt

# Start server
uvicorn server:app --host 0.0.0.0 --port 8001 --reload
```

Backend runs at: `http://localhost:8001`

Test it: `curl http://localhost:8001/api/`

### Frontend Setup

```bash
# Open new terminal
cd frontend

# Install dependencies
yarn install

# Start development server
yarn start
```

Frontend opens at: `http://localhost:3000`

## Project Structure

```
/app
├── backend/
│   ├── agents/                      # Analysis modules
│   │   ├── validation_agent.py      # Validates DNA input
│   │   ├── alignment_agent.py       # Aligns sequences (Biopython)
│   │   ├── mutation_detection_agent.py  # Detects mutations
│   │   ├── annotation_agent.py      # DNA→Protein translation
│   │   └── classification_agent.py  # Risk assessment
│   ├── data/
│   │   └── tp53_reference.fasta     # TP53 reference sequence
│   ├── server.py                    # FastAPI app
│   ├── requirements.txt             # Python dependencies
│   └── .env                         # Configuration
│
├── frontend/
│   ├── src/components/              # React components
│   ├── package.json                 # Node dependencies
│   └── .env                         # Frontend config
│
└── README.md                        # This file
```

## The 5-Stage Pipeline

### Stage 1: Validation
**Purpose:** Ensure input quality

**Checks:**
- Only A, T, C, G characters
- Length between 10-10,000 nucleotides
- No invalid characters

**Example:**
```python
# Valid
ATCGATCGATCG

# Invalid (contains numbers)
ATCG123ATCG
```

### Stage 2: Alignment
**Purpose:** Match query sequence with reference

**Algorithm:** Biopython PairwiseAligner (Needleman-Wunsch global alignment)

**Scoring:**
- Match: +2 points
- Mismatch: -1 point
- Gap open: -0.5 points
- Gap extend: -0.1 points

**Why needed:** Insertions/deletions shift positions. Alignment finds best match despite length differences.

**Example:**
```
Reference: ATCG-ATCG
           |||| ||||
Query:     ATCGTATCG
           (T inserted)
```

### Stage 3: Mutation Detection
**Purpose:** Identify exact differences

**Detects:**
1. **Substitutions** - One base changes (A→T)
2. **Insertions** - Bases added
3. **Deletions** - Bases removed

**Output:** List of mutations with positions and types

### Stage 4: Annotation
**Purpose:** Translate DNA changes to protein effects

**Uses genetic code:**
- DNA triplets (codons) → Amino acids
- ATG = Methionine (M)
- TAG = Stop codon

**Effect types:**
- **Missense:** Amino acid changes (may affect function)
- **Nonsense:** Stop codon created (truncates protein)
- **Synonymous:** Silent change (no protein effect)
- **Frameshift:** Reading frame shifted (usually severe)

**Example:**
```
DNA:     CGT → CAT
Protein: Arg → His
Effect:  Missense (R175H)
```

### Stage 5: Classification
**Purpose:** Assess pathogenicity risk

**Rules:**
- Frameshift → **Pathogenic** (HIGH risk)
- Nonsense → **Pathogenic** (HIGH risk)
- Missense → **Potentially Pathogenic** (MODERATE risk)
- Synonymous → **Benign** (LOW risk)

**Output:** Clinical classification + recommendation

## Testing the System

### Test 1: Load Sample Sequence

1. Open `http://localhost:3000`
2. Click "Load Sample Sequence"
3. Click "Run Analysis"
4. View results in tabs

**Expected output:**
- Classification: Pathogenic
- Risk: HIGH
- Mutations: 4-6 detected
- Identity: ~41% match

### Test 2: Perfect Match (No Mutations)

Use first 100 bases of reference:
```
ATGGAGGAGCCGCAGTCAGATCCTAGCGTCGAGCCCCCTCTGAGTCAGGAA
ACATTTTCAGACCTATGGAAACTACTTCCTGAAAACAACGTTCTGTCCCCC
```

**Expected output:**
- Classification: Benign
- Mutations: 0
- Identity: 100%

### Test 3: Invalid Input

Try invalid sequence:
```
ATCG123XYZ
```

**Expected output:**
- Validation Error: "Invalid nucleotides found: 1, 2, 3, X, Y, Z"

## API Endpoints

### Health Check
```bash
GET /api/
```
Returns API status and version

### Get Available Genes
```bash
GET /api/reference-genes
```
Lists reference genes (currently TP53)

### Analyze Sequence
```bash
POST /api/analyze
Content-Type: application/json

{
  "sequence": "ATCGATCG...",
  "gene": "TP53"
}
```

Returns complete analysis results

### Upload FASTA File
```bash
POST /api/upload-sequence
Content-Type: multipart/form-data

file: sequence.fasta
```

Extracts sequence from file

## Understanding the Results

### Validation Tab
Shows if sequence passed quality checks:
- ✅ Valid: Green checkmark, proceed to analysis
- ❌ Invalid: Red X with error messages

### Alignment Tab
Visual comparison of sequences:
- **Score:** Higher = better match
- **Matches:** Identical positions
- **Mismatches:** Different bases
- **Gaps:** Insertions/deletions
- **Identity %:** Percentage similarity

Color coding:
- Green: Adenine (A)
- Red: Thymine (T)  
- Yellow: Cytosine (C)
- Gray: Guanine (G)

### Mutations Tab
Details of each mutation:
- Position in sequence
- Type (substitution/insertion/deletion)
- DNA change (e.g., C→T)
- Protein change (e.g., R175H)
- Effect classification

### Classification Tab
Overall risk assessment:
- **Pathogenic (HIGH):** Likely causes disease
- **Potentially Pathogenic (MODERATE):** May cause disease
- **Uncertain (MODERATE):** Unclear significance
- **Benign (LOW):** Likely harmless

## Code Comments

Every file contains extensive line-by-line comments explaining:
- **What** each line does
- **Why** it's necessary
- **How** it works
- **What** output it produces

Perfect for learning bioinformatics programming!

## Limitations

### Current Limitations:
1. **Single gene:** Only TP53 (can add more easily)
2. **Rule-based classification:** No machine learning yet
3. **No population data:** Doesn't check variant frequencies
4. **No conservation scores:** Doesn't use evolutionary data

### What This System Does NOT Have:
- ❌ External API dependencies
- ❌ AI/ML models (intentionally kept simple)
- ❌ Clinical database integration
- ❌ Authentication/user accounts
- ❌ Advanced visualizations

### What This System DOES Have:
- ✅ Complete local execution
- ✅ Accurate sequence alignment
- ✅ Real mutation detection
- ✅ Protein effect prediction
- ✅ Rule-based classification
- ✅ Clean, commented code

## Adding More Genes

To add new reference genes:

1. Create FASTA file:
```bash
# backend/data/brca1_reference.fasta
>BRCA1 Reference Sequence
ATGCGA...
```

2. Update `server.py`:
```python
REFERENCE_SEQUENCES = {
    'TP53': load_reference_sequence('TP53'),
    'BRCA1': load_reference_sequence('BRCA1')  # Add this
}
```

3. Restart backend

## Troubleshooting

### Backend won't start

**Error:** `ModuleNotFoundError: No module named 'Bio'`

**Solution:**
```bash
cd backend
source venv/bin/activate
pip install -r requirements.txt
```

### Port already in use

**Error:** `Address already in use`

**Solution:**
```bash
# Find and kill process on port 8001
lsof -ti:8001 | xargs kill -9

# Or use different port
uvicorn server:app --port 8002
```

### Frontend can't connect

**Error:** `Network Error` in browser console

**Solution:**
1. Check backend is running: `curl http://localhost:8001/api/`
2. Verify `frontend/.env` has:
   ```
   REACT_APP_BACKEND_URL=http://localhost:8001
   ```
3. Restart frontend: `yarn start`

### Alignment fails

**Error:** `No valid alignment found`

**Possible causes:**
1. Sequences too different (from wrong gene)
2. Very short sequence (<20 bp)
3. Contains many non-ATCG characters

**Solution:** Ensure sequence is from TP53 gene

## Performance

| Metric | Value |
|--------|-------|
| Validation | <0.1 seconds |
| Alignment (1000bp) | ~1-2 seconds |
| Mutation detection | <0.5 seconds |
| Total analysis | 2-5 seconds |
| Max sequence length | 10,000 nucleotides |

## Educational Value

Perfect for learning:
- Bioinformatics algorithms
- Sequence alignment (Needleman-Wunsch)
- Genetic code and translation
- Mutation classification
- Full-stack development
- API design

## Contributing

This is a clean, educational codebase. To contribute:

1. Read the code comments
2. Understand the pipeline flow
3. Make improvements
4. Add tests
5. Submit changes

Suggested improvements:
- Add more reference genes
- Implement batch processing
- Add visualization of protein structures
- Integrate population databases
- Machine learning classification

## License

Educational and research use. Not for clinical diagnosis.

**Medical Disclaimer:** This tool is for educational purposes only. NOT approved for clinical use. Always consult qualified healthcare professionals for medical decisions.

## Version History

**v2.0.0** (Current) - Local Edition
- Removed all external API dependencies
- Refactored to use modern Biopython
- Added comprehensive code comments
- Pure computational biology approach

**v1.0.0** - Original
- Had external AI API dependencies
- Less detailed documentation

---

**Runs 100% locally • No API keys needed • Open source libraries only**

# Multi-Agent AI System for Gene Mutation Detection and Clinical Interpretation

## 🧬 What is This Project?

A **production-ready bioinformatics application** that analyzes DNA sequences to detect genetic mutations and assess their clinical significance using 7 specialized AI agents working together.

## 🎯 Real-World Use Case

When a patient gets DNA sequenced, doctors need to know:
- Does this person have mutations in cancer genes?
- Are these mutations dangerous?
- What diseases might they be at risk for?

This system automates that analysis, providing answers in seconds.

## 🏗️ System Architecture - 7 Agent Pipeline

```
User DNA Input
    ↓
[1] VALIDATION AGENT     → Checks sequence validity (only A,T,C,G)
    ↓
[2] ALIGNMENT AGENT      → Compares with reference DNA using Biopython
    ↓
[3] MUTATION DETECTION   → Finds substitutions, insertions, deletions
    ↓
[4] ANNOTATION AGENT     → Translates DNA changes to protein changes
    ↓
[5] CLASSIFICATION       → Determines if mutations are dangerous
    ↓
[6] RETRIEVAL (RAG)      → Searches ClinVar medical database
    ↓
[7] AI EXPLANATION       → Generates clinical report via Gemini
    ↓
Results Dashboard
```

## 🔬 Key Concepts Explained Simply

**What is a Gene Mutation?**
- DNA is made of 4 letters: A, T, C, G
- Mutation = difference from normal reference
- Types: Substitution (A→T), Deletion (remove), Insertion (add)

**Why TP53 Gene?**
- "Guardian of the genome" - prevents cancer
- Mutations found in 50% of cancers
- Linked to Li-Fraumeni Syndrome

**Pathogenic vs Benign:**
- Pathogenic = Dangerous, likely causes disease
- Benign = Harmless variation
- Uncertain = Not enough evidence

## 🛠️ Technologies Used

**Backend:** Python, FastAPI, Biopython, MongoDB, Gemini AI  
**Frontend:** React, Tailwind CSS, Shadcn/UI  
**AI/ML:** Google Gemini 3 Flash, RAG (Retrieval-Augmented Generation)

## 📁 Project Structure

```
/app
├── backend/
│   ├── agents/                         # 7 AI Agents
│   │   ├── validation_agent.py         # Validates DNA
│   │   ├── alignment_agent.py          # Aligns sequences
│   │   ├── mutation_detection_agent.py # Detects mutations
│   │   ├── annotation_agent.py         # DNA→Protein
│   │   ├── classification_agent.py     # Risk assessment
│   │   ├── retrieval_agent.py          # ClinVar RAG
│   │   └── explanation_agent.py        # AI reports
│   ├── data/
│   │   ├── tp53_reference.fasta        # Reference gene
│   │   └── clinvar_sample.csv          # Medical database
│   ├── server.py                       # FastAPI app
│   ├── requirements.txt                # Dependencies
│   └── .env                            # Config
│
├── frontend/
│   ├── src/components/
│   │   ├── Dashboard.js                # Main page
│   │   ├── SequenceInput.js            # DNA input
│   │   ├── ResultsView.js              # Results display
│   │   ├── MutationMap.js              # Visual map
│   │   ├── AlignmentViewer.js          # Sequence alignment
│   │   ├── EvidenceList.js             # ClinVar evidence
│   │   └── AIExplanation.js            # AI report
│   └── package.json
│
└── README.md (this file)
```

## 🚀 Setup for Local Execution

### Prerequisites

1. **Python 3.11+**
```bash
python --version  # Should show 3.11+
```

2. **Node.js 18+ and Yarn**
```bash
node --version   # Should show 18+
yarn --version   # Should show 1.22+
```

3. **MongoDB**
```bash
# macOS
brew services start mongodb-community

# Linux
sudo systemctl start mongod

# Docker
docker run -d -p 27017:27017 mongo:latest
```

### Step 1: Backend Setup

```bash
# Navigate to backend
cd backend

# Create virtual environment
python -m venv venv

# Activate it
source venv/bin/activate  # macOS/Linux
# OR
venv\Scripts\activate     # Windows

# Install dependencies
pip install -r requirements.txt
```

### Step 2: Configure Backend

Ensure `backend/.env` contains:
```env
MONGO_URL=mongodb://localhost:27017
DB_NAME=gene_mutation_db
CORS_ORIGINS=http://localhost:3000
EMERGENT_LLM_KEY=sk-emergent-37d77Fc09E5CeE143C
```

### Step 3: Start Backend

```bash
# From backend/ directory
uvicorn server:app --host 0.0.0.0 --port 8001 --reload

# Should see:
# INFO: Uvicorn running on http://0.0.0.0:8001
```

Test: Visit http://localhost:8001/api/ (should show welcome message)

### Step 4: Frontend Setup

**Open new terminal** (keep backend running):

```bash
cd frontend
yarn install  # Takes 2-3 minutes
```

### Step 5: Configure Frontend

Ensure `frontend/.env` contains:
```env
REACT_APP_BACKEND_URL=http://localhost:8001
```

### Step 6: Start Frontend

```bash
# From frontend/ directory
yarn start

# Browser opens automatically at http://localhost:3000
```

## 🧪 Testing the System

### Quick Test

1. Open http://localhost:3000
2. Click **"Load Sample Sequence"** button
3. Click **"Run Analysis"** button (takes ~5-10 seconds)
4. View results in 5 tabs:
   - Overview: Classification & mutation map
   - Mutations: Detailed mutation list
   - Alignment: Visual sequence comparison
   - Evidence: ClinVar database matches
   - AI Interpretation: Gemini-generated report

### Expected Output
```
Classification: Pathogenic
Risk Level: HIGH
Mutations: 5-6 detected
Identity: ~41% match with reference
Evidence: 3 ClinVar records
AI Report: Comprehensive clinical interpretation
```

## 📸 UI Components Explained

### 1. Input Panel (Left)
- **Gene Selector**: Choose TP53 (currently only option)
- **File Upload**: Drag/drop FASTA files
- **Sequence Box**: Paste DNA manually (A,T,C,G only)
- **Load Sample**: Loads test sequence with mutations
- **Run Analysis**: Starts 7-agent pipeline
- **Reset**: Clears everything

### 2. Results Panel (Right)

**Overview Tab:**
- Classification card (Pathogenic/Benign/Uncertain)
- Risk badge (HIGH/MODERATE/LOW)
- Quick stats (Gene, Mutations, Identity, Evidence)
- Mutation map visualization (colored position markers)
- Classification summary (4 boxes: Pathogenic/Potential/Uncertain/Benign)
- Clinical recommendation

**Mutations Tab:**
- Individual mutation cards
- Position, type, DNA change
- Protein change (e.g., R175H)
- Effect (missense/nonsense/frameshift)
- Impact description

**Alignment Tab:**
- Alignment statistics (Score, Matches, Mismatches, Gaps)
- Color-coded nucleotides:
  - Green: Adenine (A)
  - Red: Thymine (T)
  - Yellow: Cytosine (C)
  - Gray: Guanine (G)
- Match indicators (|, *, space)

**Evidence Tab:**
- ClinVar database records
- Mutation IDs, clinical significance
- Associated conditions (cancers, syndromes)
- Evidence summaries
- Match quality scores

**AI Interpretation Tab:**
- Gemini-generated clinical report
- Clinical interpretation section
- Molecular impact explanation
- Recommendations
- Disclaimer

## 🧠 How Each Agent Works

### Agent 1: Validation (Quality Control)
**Purpose:** Ensure input is valid before processing

**Checks:**
- Only A, T, C, G characters
- Minimum 10 nucleotides
- Maximum 10,000 nucleotides
- Warns if not divisible by 3

**Why:** Invalid data would crash system or give meaningless results

### Agent 2: Alignment (DNA Comparison)
**Purpose:** Line up query DNA with reference DNA

**Method:**
- Biopython pairwise global alignment
- Needleman-Wunsch algorithm
- Scoring: Match +2, Mismatch -1, Gap -0.5

**Output:** Aligned sequences with gaps inserted for best match

**Why:** Sequences may differ in length due to insertions/deletions

### Agent 3: Mutation Detection (Find Differences)
**Purpose:** Identify exact changes between sequences

**Detects:**
- Substitutions: One base changed (C→T)
- Deletions: Bases removed
- Insertions: Bases added

**Output:** List of mutations with exact positions

**Why:** Different mutation types have different health impacts

### Agent 4: Annotation (DNA to Protein)
**Purpose:** Translate DNA changes to protein changes

**Process:**
- Uses genetic code (codon table)
- Groups DNA into triplets (codons)
- Each codon = 1 amino acid

**Effects Classified:**
- Missense: Changes amino acid
- Nonsense: Creates stop codon (truncates protein)
- Synonymous: No amino acid change (silent)
- Frameshift: Shifts reading frame (severe)

**Why:** Proteins do cell work. Knowing protein impact predicts disease.

### Agent 5: Classification (Risk Assessment)
**Purpose:** Determine if mutations are dangerous

**Rules:**
- Frameshift → Pathogenic (HIGH)
- Nonsense → Pathogenic (HIGH)
- Missense → Potentially Pathogenic (MODERATE)
- Synonymous → Benign (LOW)

**Output:** Overall classification + risk level + recommendation

**Why:** Key medical decision - should patient be concerned?

### Agent 6: Retrieval (RAG - Database Search)
**Purpose:** Find scientific evidence from ClinVar

**Method:**
- Searches by exact position match
- Searches by position proximity (±5 nucleotides)
- Searches by mutation type
- Calculates match quality score

**Output:** Top matching evidence records

**Why:** Provides scientific backing. If others with same mutation developed cancer, that's strong evidence.

### Agent 7: AI Explanation (Report Generation)
**Purpose:** Generate human-readable medical report

**Process:**
- Collects all previous agent outputs
- Constructs detailed prompt for Gemini
- AI generates structured report with:
  - Clinical interpretation
  - Molecular impact
  - Recommendations
  - Patient counseling

**Fallback:** Rule-based template if AI unavailable

**Why:** Translates complex data into actionable medical advice

## ⚙️ API Endpoints

### GET /api/
Health check
```bash
curl http://localhost:8001/api/
```

### GET /api/reference-genes
List available genes
```bash
curl http://localhost:8001/api/reference-genes
```

### POST /api/analyze
Main analysis endpoint
```bash
curl -X POST http://localhost:8001/api/analyze \
  -H "Content-Type: application/json" \
  -d '{"sequence": "ATCGATCG...", "gene": "TP53"}'
```

### POST /api/upload-sequence
Upload FASTA file
```bash
curl -X POST http://localhost:8001/api/upload-sequence \
  -F "file=@sequence.fasta"
```

## ⚠️ Troubleshooting

### Backend won't start
```bash
# Ensure venv activated
source venv/bin/activate
pip install -r requirements.txt
```

### Port already in use
```bash
# Kill process on port 8001
kill -9 $(lsof -ti:8001)
# Or use different port
uvicorn server:app --port 8002
```

### MongoDB connection failed
```bash
# Start MongoDB
brew services start mongodb-community  # macOS
sudo systemctl start mongod            # Linux
```

### Frontend can't connect
1. Check backend running: http://localhost:8001/api/
2. Verify frontend/.env has: `REACT_APP_BACKEND_URL=http://localhost:8001`
3. Restart: `yarn start`

### AI explanation not working
- Check EMERGENT_LLM_KEY in backend/.env
- Demo key has daily limits
- Check internet connection
- Fallback template will be used if AI fails

## 🚧 Current Limitations

1. **Single Gene:** Only TP53 (others need reference sequences)
2. **Small Database:** 13 ClinVar records (full has millions)
3. **Rule-Based:** Simple heuristics, not ML
4. **Internet Required:** For AI explanations
5. **No Auth:** Anyone can access
6. **No Batch:** One sequence at a time

## 🚀 Future Enhancements

**Easy Wins:**
- Add BRCA1, BRCA2, EGFR genes
- Expand ClinVar database
- Export PDF reports
- Batch processing

**Medium Effort:**
- Machine learning classification
- 3D protein structure visualization
- Population frequency data (gnomAD)
- User authentication

**Research Projects:**
- Multi-gene panel analysis
- Real-time sequencing integration
- Clinical decision support
- Treatment recommendations

## 📚 Resources

- [ClinVar Database](https://www.ncbi.nlm.nih.gov/clinvar/)
- [Biopython Documentation](https://biopython.org/)
- [FastAPI Guide](https://fastapi.tiangolo.com/)
- [ACMG Guidelines](https://www.acmg.net/) - Variant interpretation standards

## 📄 License & Disclaimer

**Educational and research purposes only.**

⚠️ **Medical Disclaimer:** NOT approved for clinical diagnosis. Always consult qualified healthcare professionals and certified genetic counselors for medical decisions.

## 🎓 Educational Value

Ideal for learning:
- DNA sequence analysis
- Multi-agent AI systems
- Bioinformatics pipelines
- Full-stack AI applications
- RAG (Retrieval-Augmented Generation)

---

**Version:** 1.0.0  
**Last Updated:** March 2026  
**Status:** Production-Ready MVP

"""
FastAPI Backend for Multi-Agent Gene Mutation Detection System
Orchestrates all agents and provides RESTful API endpoints
"""

from fastapi import FastAPI, APIRouter, HTTPException, UploadFile, File
from fastapi.responses import JSONResponse
from dotenv import load_dotenv
from starlette.middleware.cors import CORSMiddleware
from motor.motor_asyncio import AsyncIOMotorClient
import os
import logging
from pathlib import Path
from pydantic import BaseModel, Field, ConfigDict
from typing import List, Optional
import uuid
from datetime import datetime, timezone

# Import all agents
from agents.validation_agent import ValidationAgent
from agents.alignment_agent import AlignmentAgent
from agents.mutation_detection_agent import MutationDetectionAgent
from agents.annotation_agent import AnnotationAgent
from agents.classification_agent import ClassificationAgent
from agents.retrieval_agent import RetrievalAgent
from agents.explanation_agent import ExplanationAgent

# Load environment variables
ROOT_DIR = Path(__file__).parent
load_dotenv(ROOT_DIR / '.env')

# MongoDB connection
mongo_url = os.environ['MONGO_URL']
client = AsyncIOMotorClient(mongo_url)
db = client[os.environ['DB_NAME']]

# Create the main app
app = FastAPI(title="Gene Mutation Detection System")

# Create API router with /api prefix
api_router = APIRouter(prefix="/api")

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Load reference sequences
def load_reference_sequence(gene_name: str) -> str:
    """Load reference gene sequence from FASTA file"""
    try:
        fasta_path = ROOT_DIR / 'data' / f'{gene_name.lower()}_reference.fasta'
        with open(fasta_path, 'r') as f:
            lines = f.readlines()
            # Skip header line and join sequence lines
            sequence = ''.join(line.strip() for line in lines if not line.startswith('>'))
        return sequence
    except Exception as e:
        logger.error(f"Error loading reference sequence for {gene_name}: {e}")
        raise HTTPException(status_code=404, detail=f"Reference sequence for {gene_name} not found")

# Initialize reference sequences
REFERENCE_SEQUENCES = {
    'TP53': load_reference_sequence('TP53')
}

# Pydantic Models
class AnalysisRequest(BaseModel):
    """Request model for gene sequence analysis"""
    sequence: str = Field(..., description="Gene sequence to analyze (ATCG nucleotides)")
    gene: str = Field(default="TP53", description="Reference gene name")

class AnalysisResponse(BaseModel):
    """Response model for analysis results"""
    model_config = ConfigDict(extra="ignore")
    
    analysis_id: str
    timestamp: str
    gene: str
    validation: dict
    alignment: dict
    mutations: dict
    annotations: dict
    classification: dict
    evidence: dict
    explanation: dict
    status: str

# API Endpoints

@api_router.get("/")
async def root():
    """Health check endpoint"""
    return {
        "message": "Multi-Agent Gene Mutation Detection System",
        "version": "1.0.0",
        "status": "operational"
    }

@api_router.get("/reference-genes")
async def get_reference_genes():
    """Get list of available reference genes"""
    return {
        "available_genes": list(REFERENCE_SEQUENCES.keys()),
        "genes": [
            {
                "name": "TP53",
                "full_name": "Tumor Protein P53",
                "description": "Tumor suppressor gene, critical for cell cycle regulation",
                "length": len(REFERENCE_SEQUENCES['TP53'])
            }
        ]
    }

@api_router.post("/analyze", response_model=AnalysisResponse)
async def analyze_sequence(request: AnalysisRequest):
    """
    Main endpoint for gene mutation analysis
    Orchestrates all agents in the pipeline:
    1. Validation → 2. Alignment → 3. Mutation Detection → 
    4. Annotation → 5. Classification → 6. RAG Retrieval → 7. AI Explanation
    """
    
    analysis_id = str(uuid.uuid4())
    timestamp = datetime.now(timezone.utc).isoformat()
    
    logger.info(f"Starting analysis {analysis_id} for gene {request.gene}")
    
    try:
        # Get reference sequence
        if request.gene not in REFERENCE_SEQUENCES:
            raise HTTPException(
                status_code=400, 
                detail=f"Reference gene {request.gene} not available"
            )
        
        reference_sequence = REFERENCE_SEQUENCES[request.gene]
        
        # AGENT 1: Validation
        logger.info("Step 1/7: Validation")
        validation_agent = ValidationAgent()
        validation_result = validation_agent.validate(request.sequence)
        
        if not validation_result['is_valid']:
            return AnalysisResponse(
                analysis_id=analysis_id,
                timestamp=timestamp,
                gene=request.gene,
                validation=validation_result,
                alignment={},
                mutations={},
                annotations={},
                classification={},
                evidence={},
                explanation={},
                status="validation_failed"
            )
        
        # AGENT 2: Alignment
        logger.info("Step 2/7: Alignment")
        alignment_agent = AlignmentAgent(reference_sequence)
        alignment_result = alignment_agent.align(validation_result['cleaned_sequence'])
        
        if not alignment_result['success']:
            raise HTTPException(status_code=500, detail="Alignment failed")
        
        # AGENT 3: Mutation Detection
        logger.info("Step 3/7: Mutation Detection")
        mutation_agent = MutationDetectionAgent()
        mutation_result = mutation_agent.detect(
            alignment_result['aligned_reference'],
            alignment_result['aligned_query']
        )
        
        # AGENT 4: Annotation
        logger.info("Step 4/7: Annotation")
        annotation_agent = AnnotationAgent()
        
        # Remove gaps for annotation
        ref_clean = alignment_result['aligned_reference'].replace('-', '')
        query_clean = alignment_result['aligned_query'].replace('-', '')
        
        annotation_result = annotation_agent.annotate(
            mutation_result['mutations'],
            ref_clean,
            query_clean
        )
        
        # AGENT 5: Classification
        logger.info("Step 5/7: Classification")
        classification_agent = ClassificationAgent()
        classification_result = classification_agent.classify(
            annotation_result['annotated_mutations'],
            mutation_result
        )
        
        # AGENT 6: RAG Retrieval
        logger.info("Step 6/7: Evidence Retrieval (RAG)")
        retrieval_agent = RetrievalAgent()
        evidence_result = retrieval_agent.retrieve(
            annotation_result['annotated_mutations'],
            request.gene
        )
        
        # AGENT 7: AI Explanation
        logger.info("Step 7/7: AI Explanation Generation")
        explanation_agent = ExplanationAgent()
        explanation_result = await explanation_agent.generate_explanation(
            classification_result['classified_mutations'],
            classification_result,
            evidence_result,
            request.gene
        )
        
        # Prepare response
        response = AnalysisResponse(
            analysis_id=analysis_id,
            timestamp=timestamp,
            gene=request.gene,
            validation=validation_result,
            alignment=alignment_result,
            mutations=mutation_result,
            annotations=annotation_result,
            classification=classification_result,
            evidence=evidence_result,
            explanation=explanation_result,
            status="completed"
        )
        
        # Store in database (optional - for history)
        try:
            doc = response.model_dump()
            await db.analyses.insert_one(doc)
        except Exception as e:
            logger.warning(f"Failed to store analysis in database: {e}")
        
        logger.info(f"Analysis {analysis_id} completed successfully")
        
        return response
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Analysis failed: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Analysis failed: {str(e)}")

@api_router.post("/upload-sequence")
async def upload_sequence(file: UploadFile = File(...)):
    """
    Upload a sequence file (FASTA or plain text)
    Returns the extracted sequence
    """
    try:
        content = await file.read()
        text = content.decode('utf-8')
        
        # Parse FASTA format or plain text
        if text.startswith('>'):
            # FASTA format - skip header lines
            lines = text.split('\n')
            sequence = ''.join(line.strip() for line in lines if not line.startswith('>'))
        else:
            # Plain text - remove whitespace
            sequence = text.replace(' ', '').replace('\n', '').replace('\r', '').strip()
        
        return {
            "success": True,
            "sequence": sequence,
            "length": len(sequence),
            "filename": file.filename
        }
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"File upload failed: {str(e)}")

# Include router in app
app.include_router(api_router)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_credentials=True,
    allow_origins=os.environ.get('CORS_ORIGINS', '*').split(','),
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.on_event("shutdown")
async def shutdown_db_client():
    """Close database connection on shutdown"""
    client.close()

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8001)

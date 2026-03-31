"""
Gene Mutation Detection System - Backend Server
================================================

This FastAPI server orchestrates the mutation detection pipeline:
1. Validates DNA sequences
2. Aligns with reference gene
3. Detects mutations (substitutions, insertions, deletions)
4. Annotates protein-level effects
5. Classifies pathogenicity risk

All processing is done locally without external API dependencies.
"""

# Web framework imports
from fastapi import FastAPI, APIRouter, HTTPException, UploadFile, File
from fastapi.responses import JSONResponse
from starlette.middleware.cors import CORSMiddleware

# Configuration and utilities
from dotenv import load_dotenv
import os
import logging
from pathlib import Path
from datetime import datetime, timezone
import uuid

# Data validation
from pydantic import BaseModel, Field, ConfigDict
from typing import Optional

# Import our custom agents
from agents.validation_agent import ValidationAgent
from agents.alignment_agent import AlignmentAgent
from agents.mutation_detection_agent import MutationDetectionAgent
from agents.annotation_agent import AnnotationAgent
from agents.classification_agent import ClassificationAgent

# Load environment variables from .env file
# This reads configuration like database URL, CORS settings, etc.
ROOT_DIR = Path(__file__).parent
load_dotenv(ROOT_DIR / '.env')

# Create main FastAPI application
# title parameter sets the API documentation title
app = FastAPI(title="Gene Mutation Detection System - Local")

# Create API router with /api prefix
# All endpoints will be accessed as /api/endpoint_name
api_router = APIRouter(prefix="/api")

# Configure logging for debugging and monitoring
logging.basicConfig(
    level=logging.INFO,  # Log INFO level and above
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# ============================================================================
# REFERENCE SEQUENCE LOADING
# ============================================================================

def load_reference_sequence(gene_name: str) -> str:
    """
    Load reference gene sequence from FASTA file
    
    FASTA format:
    >Header line (starts with >)
    ATCGATCG...
    ATCGATCG...
    
    Args:
        gene_name: Name of gene (e.g., 'TP53')
        
    Returns:
        DNA sequence as string (without header)
        
    Raises:
        HTTPException: If file not found or invalid
    """
    try:
        # Construct file path: data/tp53_reference.fasta
        # gene_name converted to lowercase for filename
        fasta_path = ROOT_DIR / 'data' / f'{gene_name.lower()}_reference.fasta'
        
        # Open and read FASTA file
        with open(fasta_path, 'r') as f:
            lines = f.readlines()
        
        # Parse FASTA format:
        # - Skip lines starting with '>' (header lines)
        # - Join all sequence lines
        # - Remove whitespace
        sequence = ''.join(
            line.strip() 
            for line in lines 
            if not line.startswith('>')  # Skip header
        )
        
        logger.info(f"Loaded {gene_name} reference: {len(sequence)} bp")
        return sequence
        
    except FileNotFoundError:
        # File doesn't exist
        logger.error(f"Reference file not found: {fasta_path}")
        raise HTTPException(
            status_code=404,
            detail=f"Reference sequence for {gene_name} not found"
        )
    except Exception as e:
        # Other errors (permissions, corrupt file, etc.)
        logger.error(f"Error loading reference for {gene_name}: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to load reference: {str(e)}"
        )

# Load available reference sequences at startup
# Dictionary: gene_name -> sequence
REFERENCE_SEQUENCES = {
    'TP53': load_reference_sequence('TP53')
}

# ============================================================================
# DATA MODELS (Request/Response schemas)
# ============================================================================

class AnalysisRequest(BaseModel):
    """
    Request model for gene sequence analysis
    
    This defines what data the client must send to analyze a sequence.
    """
    # DNA sequence to analyze (required)
    sequence: str = Field(
        ...,  # ... means required
        description="DNA sequence containing only A, T, C, G nucleotides",
        min_length=10,
        max_length=10000
    )
    
    # Reference gene to compare against (optional, defaults to TP53)
    gene: str = Field(
        default="TP53",
        description="Reference gene name (currently only TP53 supported)"
    )

class AnalysisResponse(BaseModel):
    """
    Response model for analysis results
    
    This defines the structure of data returned to the client.
    """
    model_config = ConfigDict(extra="ignore")  # Ignore extra fields
    
    # Unique identifier for this analysis
    analysis_id: str
    
    # Timestamp when analysis was performed
    timestamp: str
    
    # Gene analyzed
    gene: str
    
    # Results from each pipeline stage
    validation: dict      # Validation results (is_valid, errors, etc.)
    alignment: dict       # Alignment results (score, matches, gaps, etc.)
    mutations: dict       # Detected mutations (substitutions, indels, etc.)
    annotations: dict     # Protein-level effects (missense, nonsense, etc.)
    classification: dict  # Risk classification (pathogenic, benign, etc.)
    
    # Overall status
    status: str  # 'completed' or 'validation_failed'

# ============================================================================
# API ENDPOINTS
# ============================================================================

@api_router.get("/")
async def root():
    """
    Health check endpoint
    
    Returns basic API information to verify server is running.
    """
    return {
        "message": "Gene Mutation Detection System - Local Version",
        "version": "2.0.0",
        "status": "operational",
        "features": [
            "DNA sequence validation",
            "Sequence alignment (Biopython)",
            "Mutation detection (substitutions, indels)",
            "Protein annotation",
            "Pathogenicity classification"
        ],
        "note": "Runs completely locally without external APIs"
    }

@api_router.get("/reference-genes")
async def get_reference_genes():
    """
    Get list of available reference genes
    
    Returns information about genes that can be analyzed.
    """
    return {
        "available_genes": list(REFERENCE_SEQUENCES.keys()),
        "genes": [
            {
                "name": "TP53",
                "full_name": "Tumor Protein P53",
                "description": "Tumor suppressor gene, critical for cell cycle regulation",
                "length": len(REFERENCE_SEQUENCES['TP53']),
                "chromosome": "17",
                "function": "Prevents cancer by regulating cell division"
            }
        ]
    }

@api_router.post("/analyze", response_model=AnalysisResponse)
async def analyze_sequence(request: AnalysisRequest):
    """
    Main analysis endpoint - runs complete mutation detection pipeline
    
    Pipeline stages:
    1. VALIDATION: Check sequence validity (A,T,C,G only, proper length)
    2. ALIGNMENT: Align with reference using Biopython
    3. MUTATION DETECTION: Find substitutions, insertions, deletions
    4. ANNOTATION: Translate to protein-level effects
    5. CLASSIFICATION: Assess pathogenicity risk
    
    Args:
        request: AnalysisRequest containing sequence and gene name
        
    Returns:
        AnalysisResponse with complete results from all pipeline stages
        
    Raises:
        HTTPException: If gene not found or processing fails
    """
    # Generate unique ID for this analysis
    analysis_id = str(uuid.uuid4())
    
    # Get current timestamp in ISO format
    timestamp = datetime.now(timezone.utc).isoformat()
    
    logger.info(f"Starting analysis {analysis_id} for gene {request.gene}")
    
    try:
        # ====================================================================
        # STEP 0: Verify reference gene exists
        # ====================================================================
        
        if request.gene not in REFERENCE_SEQUENCES:
            raise HTTPException(
                status_code=400,
                detail=f"Reference gene '{request.gene}' not available. "
                       f"Available genes: {list(REFERENCE_SEQUENCES.keys())}"
            )
        
        # Get reference sequence for this gene
        reference_sequence = REFERENCE_SEQUENCES[request.gene]
        
        # ====================================================================
        # STAGE 1: VALIDATION AGENT
        # ====================================================================
        
        logger.info("Stage 1/5: Validating sequence")
        
        # Create validation agent instance
        validation_agent = ValidationAgent()
        
        # Validate the input sequence
        # Returns: {is_valid, cleaned_sequence, length, errors, warnings}
        validation_result = validation_agent.validate(request.sequence)
        
        # Check if validation passed
        if not validation_result['is_valid']:
            # Validation failed - return error response
            logger.warning(f"Validation failed: {validation_result['errors']}")
            return AnalysisResponse(
                analysis_id=analysis_id,
                timestamp=timestamp,
                gene=request.gene,
                validation=validation_result,
                alignment={},      # Empty - didn't reach this stage
                mutations={},      # Empty
                annotations={},    # Empty
                classification={}, # Empty
                status="validation_failed"
            )
        
        # ====================================================================
        # STAGE 2: ALIGNMENT AGENT
        # ====================================================================
        
        logger.info("Stage 2/5: Aligning sequences")
        
        # Create alignment agent with reference sequence
        alignment_agent = AlignmentAgent(reference_sequence)
        
        # Align cleaned sequence with reference
        # Returns: {success, aligned_reference, aligned_query, score, matches, ...}
        alignment_result = alignment_agent.align(
            validation_result['cleaned_sequence']
        )
        
        # Check if alignment succeeded
        if not alignment_result['success']:
            raise HTTPException(
                status_code=500,
                detail=f"Alignment failed: {alignment_result.get('error', 'Unknown error')}"
            )
        
        # ====================================================================
        # STAGE 3: MUTATION DETECTION AGENT
        # ====================================================================
        
        logger.info("Stage 3/5: Detecting mutations")
        
        # Create mutation detection agent
        mutation_agent = MutationDetectionAgent()
        
        # Detect mutations by comparing aligned sequences
        # Returns: {total_mutations, mutations, mutation_counts, has_mutations}
        mutation_result = mutation_agent.detect(
            alignment_result['aligned_reference'],
            alignment_result['aligned_query']
        )
        
        # ====================================================================
        # STAGE 4: ANNOTATION AGENT
        # ====================================================================
        
        logger.info("Stage 4/5: Annotating protein effects")
        
        # Create annotation agent
        annotation_agent = AnnotationAgent()
        
        # Remove gaps from sequences for annotation
        # Gaps ('-') are alignment artifacts, not real nucleotides
        ref_clean = alignment_result['aligned_reference'].replace('-', '')
        query_clean = alignment_result['aligned_query'].replace('-', '')
        
        # Annotate mutations with protein-level effects
        # Returns: {annotated_mutations, impact_summary}
        annotation_result = annotation_agent.annotate(
            mutation_result['mutations'],
            ref_clean,
            query_clean
        )
        
        # ====================================================================
        # STAGE 5: CLASSIFICATION AGENT
        # ====================================================================
        
        logger.info("Stage 5/5: Classifying pathogenicity")
        
        # Create classification agent
        classification_agent = ClassificationAgent()
        
        # Classify mutations and assess overall risk
        # Returns: {overall_classification, risk_level, confidence, ...}
        classification_result = classification_agent.classify(
            annotation_result['annotated_mutations'],
            mutation_result
        )
        
        # ====================================================================
        # PREPARE RESPONSE
        # ====================================================================
        
        # Create final response with all results
        response = AnalysisResponse(
            analysis_id=analysis_id,
            timestamp=timestamp,
            gene=request.gene,
            validation=validation_result,
            alignment=alignment_result,
            mutations=mutation_result,
            annotations=annotation_result,
            classification=classification_result,
            status="completed"
        )
        
        logger.info(f"Analysis {analysis_id} completed successfully")
        logger.info(f"Result: {classification_result['overall_classification']} "
                   f"({mutation_result['total_mutations']} mutations)")
        
        return response
        
    except HTTPException:
        # Re-raise HTTP exceptions (already have proper status codes)
        raise
        
    except Exception as e:
        # Catch any unexpected errors
        logger.error(f"Analysis failed: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail=f"Analysis failed: {str(e)}"
        )

@api_router.post("/upload-sequence")
async def upload_sequence(file: UploadFile = File(...)):
    """
    Upload a sequence file (FASTA or plain text format)
    
    Accepts:
    - FASTA files (.fasta, .fa, .txt)
    - Plain text files with DNA sequence
    
    Returns:
        Extracted sequence ready for analysis
    """
    try:
        # Read uploaded file content
        content = await file.read()
        
        # Decode bytes to string (assuming UTF-8 encoding)
        text = content.decode('utf-8')
        
        # Parse different formats
        if text.startswith('>'):
            # FASTA format - skip header lines (start with >)
            lines = text.split('\n')
            sequence = ''.join(
                line.strip() 
                for line in lines 
                if not line.startswith('>')
            )
        else:
            # Plain text format - just remove whitespace
            sequence = text.replace(' ', '').replace('\n', '').replace('\r', '').strip()
        
        logger.info(f"File uploaded: {file.filename}, extracted {len(sequence)} bp")
        
        return {
            "success": True,
            "sequence": sequence,
            "length": len(sequence),
            "filename": file.filename
        }
        
    except Exception as e:
        logger.error(f"File upload failed: {e}")
        raise HTTPException(
            status_code=400,
            detail=f"File upload failed: {str(e)}"
        )

# ============================================================================
# REGISTER ROUTER AND CONFIGURE MIDDLEWARE
# ============================================================================

# Include all API routes
app.include_router(api_router)

# Add CORS middleware to allow frontend requests
# CORS = Cross-Origin Resource Sharing
# Allows frontend (React) on different port to call this API
app.add_middleware(
    CORSMiddleware,
    allow_credentials=True,
    # Get allowed origins from environment or default to all
    allow_origins=os.environ.get('CORS_ORIGINS', '*').split(','),
    allow_methods=["*"],  # Allow all HTTP methods (GET, POST, etc.)
    allow_headers=["*"],  # Allow all headers
)

# ============================================================================
# MAIN ENTRY POINT
# ============================================================================

if __name__ == "__main__":
    # Run server directly for testing
    # In production, use: uvicorn server:app --host 0.0.0.0 --port 8001
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8001)

"""
Retrieval Agent - Local ClinVar Evidence Database
==================================================

This agent searches a local ClinVar database (CSV file) for evidence
about detected mutations. This provides scientific backing for our
classification by showing what is known about similar mutations.

WHAT IS CLINVAR?
- Public database maintained by NIH (National Institutes of Health)
- Contains genetic variants and their clinical significance
- Links mutations to diseases
- Includes expert reviews and evidence

HOW THIS WORKS (LOCAL, NO API):
1. Load ClinVar CSV file using pandas
2. Search for mutations matching:
   - Same gene
   - Same or nearby position
   - Same mutation type
3. Return matching records with clinical significance

This is RAG (Retrieval-Augmented Generation) without the AI generation part.
We retrieve relevant evidence to support our computational predictions.
"""

import pandas as pd
from typing import Dict, List
from pathlib import Path

class RetrievalAgent:
    """
    Agent for retrieving clinical evidence from local ClinVar database
    """
    
    def __init__(self, clinvar_csv_path: str = None):
        """
        Initialize retrieval agent with ClinVar database
        
        Args:
            clinvar_csv_path: Path to ClinVar CSV file
                             If None, uses default path in data/ folder
        """
        # Set default path if not provided
        if clinvar_csv_path is None:
            backend_dir = Path(__file__).parent.parent
            clinvar_csv_path = backend_dir / 'data' / 'clinvar_database.csv'
        
        # Try to load ClinVar database
        try:
            # Read CSV file using pandas
            # This loads the entire database into memory for fast searching
            self.clinvar_data = pd.read_csv(clinvar_csv_path)
            print(f"[Retrieval Agent] Loaded ClinVar database: {len(self.clinvar_data)} records")
            
            # Verify required columns exist
            required_columns = ['gene', 'position', 'mutation_type', 'clinical_significance']
            missing = [col for col in required_columns if col not in self.clinvar_data.columns]
            if missing:
                print(f"Warning: Missing columns in ClinVar CSV: {missing}")
                
        except FileNotFoundError:
            # Database file doesn't exist - log warning but don't crash
            print(f"Warning: ClinVar database not found at {clinvar_csv_path}")
            print("Evidence retrieval will not be available")
            # Create empty dataframe so rest of code doesn't break
            self.clinvar_data = pd.DataFrame()
            
        except Exception as e:
            # Other errors (corrupted file, wrong format, etc.)
            print(f"Error loading ClinVar database: {e}")
            self.clinvar_data = pd.DataFrame()
    
    def retrieve(self, mutations: List[Dict], gene: str) -> Dict:
        """
        Retrieve clinical evidence for detected mutations
        
        Process:
        1. Check if database is available
        2. For each mutation, search ClinVar for:
           - Exact position match
           - Nearby position match (within ±5 nucleotides)
           - Same mutation type
        3. Calculate match quality score
        4. Return top matches
        
        Args:
            mutations: List of detected mutations from mutation detection agent
            gene: Gene name (e.g., 'TP53', 'BRCA1')
            
        Returns:
            Dictionary containing:
            - success: Whether retrieval succeeded
            - total_evidence: Number of evidence records found
            - evidence: List of matching ClinVar records
            - database: Database name ('ClinVar')
            - gene: Gene analyzed
        """
        # Check if database is available
        if self.clinvar_data.empty:
            return {
                'success': False,
                'error': 'ClinVar database not available',
                'evidence': [],
                'total_evidence': 0,
                'database': 'ClinVar',
                'gene': gene
            }
        
        # Check if we have mutations to search for
        if not mutations:
            return {
                'success': True,
                'evidence': [],
                'total_evidence': 0,
                'message': 'No mutations to search for - sequence matches reference perfectly',
                'database': 'ClinVar',
                'gene': gene
            }
        
        # Search for evidence for each mutation
        evidence_records = []
        
        for mutation in mutations:
            # Search ClinVar for this mutation
            matches = self._search_clinvar(mutation, gene)
            
            # Add each match to evidence list
            for match in matches:
                evidence_records.append({
                    'mutation_id': match.get('mutation_id', 'Unknown'),
                    'position': mutation.get('position'),
                    'mutation_type': mutation.get('type'),
                    'clinical_significance': match.get('clinical_significance', 'Unknown'),
                    'review_status': match.get('review_status', 'Not specified'),
                    'condition': match.get('condition', 'Not specified'),
                    'evidence_summary': match.get('evidence_summary', 'No summary available'),
                    'protein_change': match.get('protein_change', 'N/A'),
                    'match_quality': self._calculate_match_quality(mutation, match)
                })
        
        # Sort by match quality (best matches first)
        evidence_records = sorted(
            evidence_records,
            key=lambda x: x['match_quality'],
            reverse=True  # Highest quality first
        )
        
        # Remove duplicate mutation IDs
        seen_ids = set()
        unique_evidence = []
        for record in evidence_records:
            mut_id = record['mutation_id']
            if mut_id not in seen_ids:
                seen_ids.add(mut_id)
                unique_evidence.append(record)
        
        return {
            'success': True,
            'total_evidence': len(unique_evidence),
            'evidence': unique_evidence,
            'database': 'ClinVar',
            'gene': gene
        }
    
    def _search_clinvar(self, mutation: Dict, gene: str) -> List[Dict]:
        """
        Search ClinVar database for matching mutations
        
        Search strategies (in order of priority):
        1. Exact match: Same gene, same position, same type
        2. Proximity match: Same gene, nearby position (±5), same type
        3. Type match: Same gene, same type (any position)
        
        Args:
            mutation: Mutation to search for
            gene: Gene name
            
        Returns:
            List of matching ClinVar records
        """
        matches = []
        
        # Filter database to only this gene
        # This narrows down search space significantly
        gene_data = self.clinvar_data[self.clinvar_data['gene'] == gene]
        
        # If no data for this gene, return empty
        if gene_data.empty:
            return matches
        
        # Get mutation details
        mutation_type = mutation.get('type')
        position = mutation.get('position')
        
        # STRATEGY 1: Exact position and type match
        if position and mutation_type:
            # Convert position to numeric for comparison
            # ClinVar CSV might have positions as strings
            gene_data_copy = gene_data.copy()
            gene_data_copy['position'] = pd.to_numeric(
                gene_data_copy['position'], 
                errors='coerce'  # Convert invalid values to NaN
            )
            
            # Find exact matches
            exact_matches = gene_data_copy[
                (gene_data_copy['mutation_type'] == mutation_type) &
                (gene_data_copy['position'] == position)
            ]
            
            # Add to matches list
            if not exact_matches.empty:
                matches.extend(exact_matches.to_dict('records'))
        
        # STRATEGY 2: Proximity match (if no exact matches found)
        if not matches and position and mutation_type:
            # Search within ±5 nucleotides
            # Mutations near each other often affect same protein region
            proximity_window = 5
            
            for _, row in gene_data.iterrows():
                # Check if mutation types match
                if row['mutation_type'] != mutation_type:
                    continue
                
                # Check if positions are close
                try:
                    row_position = int(row['position'])
                    distance = abs(row_position - position)
                    
                    # Within proximity window?
                    if distance <= proximity_window:
                        matches.append(row.to_dict())
                        
                except (ValueError, TypeError):
                    # Skip if position can't be converted to int
                    continue
        
        # STRATEGY 3: Type match only (if still no matches)
        if not matches and mutation_type:
            # Find any mutations of same type in this gene
            # Less specific but still relevant
            type_matches = gene_data[gene_data['mutation_type'] == mutation_type]
            
            # Take up to 3 examples
            if not type_matches.empty:
                matches.extend(type_matches.head(3).to_dict('records'))
        
        return matches
    
    def _calculate_match_quality(self, mutation: Dict, clinvar_record: Dict) -> float:
        """
        Calculate quality score for mutation-evidence match
        
        Scoring system:
        - Exact position match: +0.5
        - Proximity match: +0.1 to +0.3 (closer = higher)
        - Type match: +0.3
        - Protein change match: +0.2
        
        Total possible score: 1.0 (perfect match)
        
        Args:
            mutation: Detected mutation
            clinvar_record: ClinVar database record
            
        Returns:
            Match quality score between 0.0 and 1.0
        """
        score = 0.0
        
        # Check position match
        mut_position = mutation.get('position')
        clinvar_position = clinvar_record.get('position')
        
        if mut_position and clinvar_position:
            try:
                # Convert both to integers for comparison
                mut_pos_int = int(mut_position)
                clinvar_pos_int = int(clinvar_position)
                
                # Exact match?
                if mut_pos_int == clinvar_pos_int:
                    score += 0.5  # Highest position score
                else:
                    # Proximity score (closer = higher)
                    distance = abs(mut_pos_int - clinvar_pos_int)
                    if distance <= 10:
                        # Score decreases with distance
                        # 1 nucleotide away = 0.45
                        # 10 nucleotides away = 0.05
                        proximity_score = 0.3 * (1 - distance / 10)
                        score += proximity_score
                        
            except (ValueError, TypeError):
                # Can't compare positions
                pass
        
        # Check mutation type match
        if mutation.get('type') == clinvar_record.get('mutation_type'):
            score += 0.3
        
        # Check protein change match (if available)
        mut_protein = mutation.get('protein_change')
        clinvar_protein = clinvar_record.get('protein_change')
        
        if mut_protein and clinvar_protein and mut_protein == clinvar_protein:
            score += 0.2  # Exact protein change match
        
        return score

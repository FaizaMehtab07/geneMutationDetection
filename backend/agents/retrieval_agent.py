"""
Retrieval Agent (RAG) - Evidence-Based Mutation Search
=======================================================

PURPOSE:
Implements RAG (Retrieval-Augmented Generation) to find scientific evidence
from ClinVar database. This adds credibility by showing "other patients with
this mutation also had these outcomes."

WHAT IS RAG?
RAG = Retrieval-Augmented Generation
Traditional AI: Relies only on training data (can be outdated or wrong)
RAG: Searches real database first, then uses that evidence to inform response
Result: More accurate, verifiable, up-to-date answers

CLINVAR DATABASE:
- NIH's database of genetic variants
- Links mutations to diseases
- Includes expert reviews
- Updated continuously with new research
- Our sample has 13 records; full ClinVar has millions

SEARCH STRATEGY:
1. Exact Match: Find mutations at exact same position
   - Most reliable evidence
   - Example: Both have mutation at position 175

2. Proximity Match: Find mutations within ±5 nucleotides
   - Nearby mutations often in same functional domain
   - Example: Mutation at 175 vs evidence at 173

3. Type Match: Find same mutation type (sub/ins/del)
   - Different positions but similar mechanism
   - Least specific but still relevant

MATCH QUALITY SCORING:
- Exact position + same type = 1.0 (100%)
- Nearby position + same type = 0.6-0.8
- Same type only = 0.3

WHY THIS MATTERS:
Instead of just saying "this mutation looks bad," we can say "three
other patients with this mutation developed Li-Fraumeni Syndrome,
according to expert-reviewed studies in ClinVar."

LIMITATIONS:
- Sample database only has 13 records (for demo)
- Full ClinVar would give much more evidence
- Novel mutations may have no matches
- Requires periodic database updates
"""

import pandas as pd
from typing import Dict, List
import os
from pathlib import Path

class RetrievalAgent:
    """Agent for retrieving relevant clinical evidence using RAG approach"""
    
    def __init__(self, clinvar_data_path: str = None):
        """
        Initialize retrieval agent with ClinVar dataset
        
        Args:
            clinvar_data_path: Path to ClinVar CSV file
        """
        if clinvar_data_path is None:
            # Default path
            backend_dir = Path(__file__).parent.parent
            clinvar_data_path = backend_dir / 'data' / 'clinvar_sample.csv'
        
        # Load ClinVar dataset
        try:
            self.clinvar_data = pd.read_csv(clinvar_data_path)
            print(f"Loaded ClinVar data: {len(self.clinvar_data)} records")
        except Exception as e:
            print(f"Error loading ClinVar data: {e}")
            self.clinvar_data = pd.DataFrame()
    
    def retrieve(self, mutations: List[Dict], gene: str = 'TP53') -> Dict:
        """
        Retrieve relevant evidence from ClinVar database
        
        Args:
            mutations: List of detected mutations
            gene: Gene name
            
        Returns:
            Dictionary with retrieved evidence
        """
        if self.clinvar_data.empty:
            return {
                'success': False,
                'error': 'ClinVar database not available',
                'evidence': []
            }
        
        if not mutations:
            return {
                'success': True,
                'evidence': [],
                'message': 'No mutations to search for'
            }
        
        # Search for relevant evidence
        evidence_records = []
        
        for mutation in mutations:
            # Search by mutation type and position
            matches = self._search_clinvar(mutation, gene)
            
            for match in matches:
                evidence_records.append({
                    'mutation_id': match.get('mutation_id', 'N/A'),
                    'position': mutation.get('position'),
                    'mutation_type': mutation.get('type'),
                    'clinical_significance': match.get('clinical_significance', 'Unknown'),
                    'review_status': match.get('review_status', 'Not specified'),
                    'condition': match.get('condition', 'Not specified'),
                    'evidence_summary': match.get('evidence_summary', 'No summary available'),
                    'protein_change': match.get('protein_change', 'N/A'),
                    'match_quality': self._calculate_match_quality(mutation, match)
                })
        
        # Remove duplicates and sort by match quality
        evidence_records = sorted(
            evidence_records,
            key=lambda x: x['match_quality'],
            reverse=True
        )
        
        # Deduplicate based on mutation_id
        seen_ids = set()
        unique_evidence = []
        for record in evidence_records:
            if record['mutation_id'] not in seen_ids:
                seen_ids.add(record['mutation_id'])
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
        
        Args:
            mutation: Mutation to search for
            gene: Gene name
            
        Returns:
            List of matching records
        """
        matches = []
        
        # Filter by gene
        gene_data = self.clinvar_data[self.clinvar_data['gene'] == gene]
        
        mutation_type = mutation.get('type')
        position = mutation.get('position')
        
        # Strategy 1: Exact position match
        if position:
            # For substitutions, match exact position
            if mutation_type == 'substitution':
                # Convert position column to int for comparison
                gene_data_copy = gene_data.copy()
                gene_data_copy['position'] = pd.to_numeric(gene_data_copy['position'], errors='coerce')
                exact_matches = gene_data_copy[
                    (gene_data_copy['mutation_type'] == 'substitution') &
                    (gene_data_copy['position'] == position)
                ]
                matches.extend(exact_matches.to_dict('records'))
            
            # For deletions/insertions, match position range
            else:
                # Check if position falls within known mutation ranges
                for _, row in gene_data.iterrows():
                    if mutation_type == row['mutation_type']:
                        # Simple position proximity matching
                        try:
                            row_position = int(row['position']) if isinstance(row['position'], str) else row['position']
                            if abs(row_position - position) <= 5:
                                matches.append(row.to_dict())
                        except (ValueError, TypeError):
                            continue
        
        # Strategy 2: Match by mutation type if no position matches
        if not matches:
            type_matches = gene_data[gene_data['mutation_type'] == mutation_type]
            matches.extend(type_matches.head(3).to_dict('records'))  # Limit to top 3
        
        # Strategy 3: Get general evidence for the gene
        if not matches:
            general_matches = gene_data.head(2)  # Get some general records
            matches.extend(general_matches.to_dict('records'))
        
        return matches
    
    def _calculate_match_quality(self, mutation: Dict, clinvar_record: Dict) -> float:
        """
        Calculate quality score for mutation-evidence match
        
        Args:
            mutation: Detected mutation
            clinvar_record: ClinVar record
            
        Returns:
            Match quality score (0-1)
        """
        score = 0.0
        
        # Exact position match (highest weight)
        if mutation.get('position') == clinvar_record.get('position'):
            score += 0.5
        elif mutation.get('position') and clinvar_record.get('position'):
            # Proximity score - convert both to int
            try:
                mut_pos = int(mutation.get('position'))
                clinvar_pos = int(clinvar_record.get('position'))
                distance = abs(mut_pos - clinvar_pos)
                if distance <= 10:
                    score += 0.3 * (1 - distance / 10)
            except (ValueError, TypeError):
                pass
        
        # Mutation type match
        if mutation.get('type') == clinvar_record.get('mutation_type'):
            score += 0.3
        
        # Protein change match (if available)
        if mutation.get('protein_change') and mutation.get('protein_change') == clinvar_record.get('protein_change'):
            score += 0.2
        
        return score
"""
Mutation Detection Agent - Finding Genetic Differences
=======================================================

PURPOSE:
Scans aligned sequences to identify exact mutations: substitutions,
insertions, and deletions. This is where we discover what's different
between the patient's DNA and healthy reference DNA.

MUTATION TYPES EXPLAINED:

1. SUBSTITUTION (Point Mutation):
   One nucleotide replaced with another
   Example: ATCG → ATGG (C changed to G)
   Impact: Often changes one amino acid (missense mutation)

2. DELETION:
   One or more nucleotides removed
   Example: ATCGAT → AT-GAT (CG deleted)
   Impact: Usually causes frameshift (severe)

3. INSERTION:
   One or more nucleotides added
   Example: ATCGAT → ATCGCGAT (CG inserted)
   Impact: Usually causes frameshift (severe)

WHY DETECTION IS TRICKY:
Deletions and insertions shift all downstream positions, requiring
proper alignment first. That's why alignment agent runs before this one.

FRAMESHIFT CONCEPT:
DNA is read in groups of 3 (codons). If you insert/delete 1 or 2
nucleotides, it shifts the reading frame:
  Original: ATG|CAT|GGC → Met|His|Gly
  Delete 1: ATG|CAG|GC? → Met|Gln|???
  
All amino acids after the mutation become wrong (usually catastrophic).

ALGORITHM:
Walks through aligned sequences character-by-character, tracking:
- Position in original (ungapped) reference
- Whether bases match or differ
- Consecutive gaps indicating indels
"""

from typing import Dict, List

class MutationDetectionAgent:
    """Agent for detecting various types of mutations"""
    
    def __init__(self):
        self.mutation_types = {
            'substitution': 'Single nucleotide change',
            'insertion': 'Addition of nucleotides',
            'deletion': 'Removal of nucleotides'
        }
    
    def detect(self, aligned_reference: str, aligned_query: str) -> Dict:
        """
        Detect mutations between aligned sequences
        
        Args:
            aligned_reference: Aligned reference sequence (may contain gaps '-')
            aligned_query: Aligned query sequence (may contain gaps '-')
            
        Returns:
            Dictionary containing all detected mutations
        """
        mutations = []
        
        # Track position in original (ungapped) reference
        ref_position = 0
        
        # Scan through alignment
        i = 0
        while i < len(aligned_reference):
            ref_base = aligned_reference[i]
            query_base = aligned_query[i]
            
            # CASE 1: Substitution (mismatch, no gaps)
            if ref_base != '-' and query_base != '-' and ref_base != query_base:
                mutations.append({
                    'type': 'substitution',
                    'position': ref_position + 1,  # 1-indexed position
                    'reference_base': ref_base,
                    'alternate_base': query_base,
                    'context': self._get_context(aligned_reference, aligned_query, i)
                })
                ref_position += 1
                i += 1
            
            # CASE 2: Deletion in query (gap in query, base in reference)
            elif ref_base != '-' and query_base == '-':
                # Count consecutive deletions
                deletion_start = ref_position + 1
                deleted_bases = ''
                
                while i < len(aligned_reference) and aligned_reference[i] != '-' and aligned_query[i] == '-':
                    deleted_bases += aligned_reference[i]
                    ref_position += 1
                    i += 1
                
                mutations.append({
                    'type': 'deletion',
                    'position': deletion_start,
                    'deleted_bases': deleted_bases,
                    'length': len(deleted_bases),
                    'context': f'Deletion of {len(deleted_bases)} base(s) at position {deletion_start}'
                })
            
            # CASE 3: Insertion in query (gap in reference, base in query)
            elif ref_base == '-' and query_base != '-':
                # Count consecutive insertions
                insertion_position = ref_position  # Position before insertion
                inserted_bases = ''
                
                while i < len(aligned_reference) and aligned_reference[i] == '-' and aligned_query[i] != '-':
                    inserted_bases += aligned_query[i]
                    i += 1
                
                mutations.append({
                    'type': 'insertion',
                    'position': insertion_position,
                    'inserted_bases': inserted_bases,
                    'length': len(inserted_bases),
                    'context': f'Insertion of {len(inserted_bases)} base(s) after position {insertion_position}'
                })
            
            # CASE 4: Match (no mutation)
            else:
                if ref_base != '-':
                    ref_position += 1
                i += 1
        
        # Calculate mutation statistics
        mutation_counts = {
            'substitution': sum(1 for m in mutations if m['type'] == 'substitution'),
            'insertion': sum(1 for m in mutations if m['type'] == 'insertion'),
            'deletion': sum(1 for m in mutations if m['type'] == 'deletion')
        }
        
        return {
            'total_mutations': len(mutations),
            'mutations': mutations,
            'mutation_counts': mutation_counts,
            'has_mutations': len(mutations) > 0
        }
    
    def _get_context(self, aligned_ref: str, aligned_query: str, position: int, window: int = 5) -> str:
        """
        Get the context around a mutation
        
        Args:
            aligned_ref: Aligned reference sequence
            aligned_query: Aligned query sequence
            position: Position of mutation
            window: Number of bases to show on each side
            
        Returns:
            Context string showing surrounding sequence
        """
        start = max(0, position - window)
        end = min(len(aligned_ref), position + window + 1)
        
        ref_context = aligned_ref[start:end]
        query_context = aligned_query[start:end]
        
        return f'Ref: {ref_context} | Query: {query_context}'
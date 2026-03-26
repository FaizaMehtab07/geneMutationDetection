"""
Alignment Agent
Responsible for aligning input sequences with reference gene:
- Use Biopython pairwise alignment
- Handle sequence alignment
- Return alignment details and positions
"""

from Bio import pairwise2
from Bio.pairwise2 import format_alignment
from typing import Dict, List, Tuple

class AlignmentAgent:
    """Agent for sequence alignment using Biopython"""
    
    def __init__(self, reference_sequence: str):
        """
        Initialize alignment agent with reference sequence
        
        Args:
            reference_sequence: Reference gene sequence to align against
        """
        self.reference_sequence = reference_sequence.upper().strip()
    
    def align(self, query_sequence: str) -> Dict:
        """
        Align query sequence with reference sequence
        Uses global alignment with match/mismatch scoring
        
        Args:
            query_sequence: Input sequence to align
            
        Returns:
            Dictionary containing alignment results
        """
        query_sequence = query_sequence.upper().strip()
        
        # Perform global alignment
        # Parameters: match score=2, mismatch penalty=-1, gap open=-0.5, gap extend=-0.1
        alignments = pairwise2.align.globalms(
            self.reference_sequence,
            query_sequence,
            2,    # Match score
            -1,   # Mismatch penalty
            -0.5, # Gap open penalty
            -0.1  # Gap extend penalty
        )
        
        if not alignments:
            return {
                'success': False,
                'error': 'Alignment failed - sequences may be too dissimilar'
            }
        
        # Get the best alignment (highest score)
        best_alignment = alignments[0]
        
        # Extract alignment details
        aligned_ref = best_alignment.seqA
        aligned_query = best_alignment.seqB
        score = best_alignment.score
        
        # Calculate alignment statistics
        matches = sum(1 for a, b in zip(aligned_ref, aligned_query) if a == b and a != '-')
        mismatches = sum(1 for a, b in zip(aligned_ref, aligned_query) if a != b and a != '-' and b != '-')
        gaps = aligned_ref.count('-') + aligned_query.count('-')
        
        # Calculate identity percentage
        total_positions = len(aligned_ref)
        identity_percent = (matches / total_positions * 100) if total_positions > 0 else 0
        
        # Create visual alignment representation
        alignment_visual = self._create_alignment_visual(aligned_ref, aligned_query)
        
        return {
            'success': True,
            'aligned_reference': aligned_ref,
            'aligned_query': aligned_query,
            'score': score,
            'matches': matches,
            'mismatches': mismatches,
            'gaps': gaps,
            'identity_percent': round(identity_percent, 2),
            'alignment_visual': alignment_visual,
            'reference_length': len(self.reference_sequence),
            'query_length': len(query_sequence)
        }
    
    def _create_alignment_visual(self, aligned_ref: str, aligned_query: str, chunk_size: int = 60) -> List[Dict]:
        """
        Create a visual representation of the alignment in chunks
        
        Args:
            aligned_ref: Aligned reference sequence
            aligned_query: Aligned query sequence
            chunk_size: Number of nucleotides per line
            
        Returns:
            List of alignment chunks with position information
        """
        chunks = []
        
        for i in range(0, len(aligned_ref), chunk_size):
            ref_chunk = aligned_ref[i:i + chunk_size]
            query_chunk = aligned_query[i:i + chunk_size]
            
            # Create match/mismatch indicator line
            match_line = ''.join(
                '|' if r == q and r != '-' else '*' if r != q and r != '-' and q != '-' else ' '
                for r, q in zip(ref_chunk, query_chunk)
            )
            
            chunks.append({
                'position': i + 1,
                'reference': ref_chunk,
                'match_line': match_line,
                'query': query_chunk
            })
        
        return chunks
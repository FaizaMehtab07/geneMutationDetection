"""
Alignment Agent - DNA Sequence Comparison
==========================================

PURPOSE:
Aligns two DNA sequences to find the best way to match them up, even if
they have different lengths due to insertions or deletions.

ANALOGY:
Imagine comparing two similar sentences with typos:
  Reference: "THE QUICK BROWN FOX"
  Query:     "THE QICK BROWN  FOX"  (missing 'U', extra space)

Alignment finds the best way to line them up:
  Ref: THE QUICK BROWN FOX
       ||| |||| ||||| |||
  Qry: THE QI-CK BROWN FOX

ALGORITHM:
Uses Needleman-Wunsch global alignment from Biopython:
- Match score: +2 (reward for matching letters)
- Mismatch penalty: -1 (penalty for differences)
- Gap penalties: -0.5 open, -0.1 extend

WHY THIS MATTERS:
Without alignment, we can't accurately detect mutations. A deletion shifts
all downstream positions, making direct comparison impossible.

EXAMPLE:
  Without alignment:
    Ref: ATCGATCG
    Qry: ATC-ATCG  (G deleted at position 4)
    Position 4: G vs A - FALSE MISMATCH!
    Position 5: A vs T - FALSE MISMATCH!
    ...everything looks wrong

  With alignment:
    Ref: ATCGATCG
         |||*||||
    Qry: ATC-ATCG
    Position 4: G vs gap - TRUE DELETION detected!
    Other positions match correctly.
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
        Align query sequence with reference sequence using global alignment
        
        EDUCATIONAL EXPLANATION:
        This function finds the optimal way to align two DNA sequences.
        Think of it like spell-checking, but for DNA. It finds where
        letters match, where they differ, and where gaps should be inserted.
        
        SCORING SYSTEM:
        - Each matching nucleotide: +2 points (reward similarity)
        - Each mismatch: -1 point (penalize differences)
        - Opening a gap: -0.5 points (penalize insertions/deletions)
        - Extending a gap: -0.1 points (prefer fewer long gaps over many short ones)
        
        The algorithm tries thousands of possible alignments and picks
        the one with the highest score.
        
        ALGORITHM USED:
        Needleman-Wunsch global alignment (Biopython's pairwise2.align.globalms)
        - "Global" means it aligns the entire sequences end-to-end
        - Alternative would be "local" which finds best matching regions
        
        TIME COMPLEXITY:
        O(n*m) where n and m are sequence lengths
        For typical gene sequences (1000-5000 bp), this takes ~1-2 seconds
        
        Args:
            query_sequence: Input DNA sequence from user
            
        Returns:
            Dictionary containing:
            - success: Whether alignment succeeded
            - aligned_reference: Reference with gaps inserted ('-' characters)
            - aligned_query: Query with gaps inserted
            - score: Alignment quality score (higher = better match)
            - matches: Count of matching positions
            - mismatches: Count of different positions (no gaps)
            - gaps: Total gaps in both sequences
            - identity_percent: Percentage of positions that match
            - alignment_visual: Formatted chunks for display
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
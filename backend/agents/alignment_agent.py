"""
Alignment Agent - DNA Sequence Comparison
==========================================

This agent aligns two DNA sequences (query vs reference) to find
the best way to match them up, accounting for mutations like
insertions and deletions.

Why alignment is needed:
- Direct comparison fails when sequences have different lengths
- Insertions/deletions shift all downstream positions
- Alignment finds optimal matching despite these differences

Algorithm used:
- Biopython's PairwiseAligner (modern, recommended API)
- Global alignment (end-to-end comparison)
- Scoring: matches rewarded, mismatches/gaps penalized
"""

from Bio import Align  # Modern Biopython alignment module
from typing import Dict, List

class AlignmentAgent:
    """
    Agent responsible for aligning DNA sequences using Biopython
    """
    
    def __init__(self, reference_sequence: str):
        """
        Initialize the alignment agent with a reference sequence
        
        Args:
            reference_sequence: The reference (normal) DNA sequence to compare against
        """
        # Store reference sequence in uppercase for consistency
        self.reference_sequence = reference_sequence.upper().strip()
        
        # Create aligner object using modern Biopython API
        # PairwiseAligner replaced the old deprecated pairwise2 module
        self.aligner = Align.PairwiseAligner()
        
        # Configure alignment scoring system:
        # - mode: 'global' means we align entire sequences end-to-end
        #   (alternative is 'local' which finds best matching regions)
        self.aligner.mode = 'global'
        
        # - match_score: Points awarded when two bases match (A matches A, etc.)
        #   Higher values favor matches
        self.aligner.match_score = 2.0
        
        # - mismatch_score: Penalty when bases don't match (A vs T, etc.)
        #   Negative values discourage mismatches
        self.aligner.mismatch_score = -1.0
        
        # - gap penalties: Cost of inserting gaps (represented by '-')
        #   open_gap_score: Penalty for starting a new gap
        #   extend_gap_score: Penalty for continuing an existing gap
        #   We prefer fewer long gaps over many short gaps
        self.aligner.open_gap_score = -0.5
        self.aligner.extend_gap_score = -0.1
    
    def align(self, query_sequence: str) -> Dict:
        """
        Perform global alignment between query and reference sequences
        
        This method:
        1. Cleans the input sequence
        2. Runs the alignment algorithm
        3. Calculates alignment statistics
        4. Creates visual representation
        
        Args:
            query_sequence: The DNA sequence to analyze (from user input)
            
        Returns:
            Dictionary containing:
            - success: Boolean indicating if alignment succeeded
            - aligned_reference: Reference sequence with gaps inserted
            - aligned_query: Query sequence with gaps inserted  
            - score: Alignment quality score (higher = better match)
            - matches: Number of matching positions
            - mismatches: Number of differing positions (excluding gaps)
            - gaps: Total number of gap characters in both sequences
            - identity_percent: Percentage of positions that match
            - alignment_visual: List of chunks showing alignment for display
        """
        # Clean query sequence: uppercase and remove whitespace
        query_sequence = query_sequence.upper().strip()
        
        try:
            # Perform the alignment using configured aligner
            # This returns an Alignments object containing all possible alignments
            # (multiple alignments can have the same score)
            alignments = self.aligner.align(self.reference_sequence, query_sequence)
            
            # Check if any alignments were found
            if not alignments or len(alignments) == 0:
                return {
                    'success': False,
                    'error': 'No valid alignment found - sequences may be too different'
                }
            
            # Get the best alignment (first one, as they're sorted by score)
            best_alignment = alignments[0]
            
            # Extract aligned sequences from alignment object
            # The alignment object stores sequences as strings with gaps ('-')
            # Index 0 = reference (target), Index 1 = query
            aligned_ref = str(best_alignment[0])
            aligned_query = str(best_alignment[1])
            
            # Get alignment score (how good the match is)
            score = best_alignment.score
            
            # Calculate alignment statistics
            # Count matches: positions where bases are identical and not gaps
            matches = sum(
                1 for ref_base, query_base in zip(aligned_ref, aligned_query)
                if ref_base == query_base and ref_base != '-'
            )
            
            # Count mismatches: positions where bases differ but neither is a gap
            mismatches = sum(
                1 for ref_base, query_base in zip(aligned_ref, aligned_query)
                if ref_base != query_base and ref_base != '-' and query_base != '-'
            )
            
            # Count gaps: total '-' characters in both sequences
            gaps = aligned_ref.count('-') + aligned_query.count('-')
            
            # Calculate total positions (length of aligned sequences)
            total_positions = len(aligned_ref)
            
            # Calculate identity percentage
            # Identity = (matches / total positions) * 100
            # This tells us what percentage of the sequence is identical
            identity_percent = (matches / total_positions * 100) if total_positions > 0 else 0
            
            # Create visual representation for display
            # Split alignment into chunks for easier viewing
            alignment_visual = self._create_alignment_visual(aligned_ref, aligned_query)
            
            # Return all alignment results
            return {
                'success': True,
                'aligned_reference': aligned_ref,
                'aligned_query': aligned_query,
                'score': float(score),  # Convert to float for JSON serialization
                'matches': matches,
                'mismatches': mismatches,
                'gaps': gaps,
                'identity_percent': round(identity_percent, 2),
                'alignment_visual': alignment_visual,
                'reference_length': len(self.reference_sequence),
                'query_length': len(query_sequence)
            }
            
        except Exception as e:
            # Catch any errors during alignment and return error message
            return {
                'success': False,
                'error': f'Alignment failed: {str(e)}'
            }
    
    def _create_alignment_visual(self, aligned_ref: str, aligned_query: str, 
                                 chunk_size: int = 60) -> List[Dict]:
        """
        Create visual representation of alignment in chunks
        
        This splits the long alignment into manageable chunks for display,
        showing reference, query, and match indicators.
        
        Args:
            aligned_ref: Reference sequence with gaps
            aligned_query: Query sequence with gaps
            chunk_size: Number of bases to show per line (default 60)
            
        Returns:
            List of dictionaries, each containing:
            - position: Starting position of chunk (1-indexed)
            - reference: Reference sequence chunk
            - match_line: String showing matches (|), mismatches (*), gaps (space)
            - query: Query sequence chunk
        """
        chunks = []
        
        # Loop through alignment in chunks
        for i in range(0, len(aligned_ref), chunk_size):
            # Extract chunk of reference sequence
            ref_chunk = aligned_ref[i:i + chunk_size]
            # Extract corresponding chunk of query sequence
            query_chunk = aligned_query[i:i + chunk_size]
            
            # Create match indicator line:
            # '|' = bases match and neither is gap
            # '*' = bases differ and neither is gap (mismatch)
            # ' ' = at least one is a gap
            match_line = ''.join(
                '|' if r == q and r != '-'  # Match
                else '*' if r != q and r != '-' and q != '-'  # Mismatch
                else ' '  # Gap
                for r, q in zip(ref_chunk, query_chunk)
            )
            
            # Store chunk information
            chunks.append({
                'position': i + 1,  # 1-indexed position (not 0-indexed)
                'reference': ref_chunk,
                'match_line': match_line,
                'query': query_chunk
            })
        
        return chunks

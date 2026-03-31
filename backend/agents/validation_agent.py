"""
Validation Agent - DNA Sequence Quality Control
================================================

This agent validates DNA sequences before processing to ensure:
1. Only valid nucleotide characters (A, T, C, G)
2. Reasonable sequence length
3. Proper format

Why validation matters:
- Invalid input would crash downstream processing
- Catches user errors early with clear messages
- Prevents wasted computation on bad data
"""

from typing import Dict

class ValidationAgent:
    """
    Agent responsible for validating DNA sequences before analysis
    """
    
    def __init__(self):
        """
        Initialize the validation agent with validation rules
        """
        # Set of valid DNA nucleotides
        # DNA alphabet consists of only 4 letters:
        # A = Adenine, T = Thymine, C = Cytosine, G = Guanine
        self.valid_nucleotides = set('ATCG')
        
        # Minimum sequence length to analyze
        # Too short sequences aren't meaningful for mutation detection
        self.min_length = 10
        
        # Maximum sequence length to prevent system overload
        # Very long sequences take too much time/memory to process
        self.max_length = 10000
    
    def validate(self, sequence: str) -> Dict:
        """
        Validate a DNA sequence against all quality rules
        
        This method performs multiple checks:
        1. Sequence is not empty
        2. Length is within acceptable range
        3. Contains only valid nucleotides (A, T, C, G)
        4. Length is divisible by 3 (for proper codon translation)
        
        Args:
            sequence: Raw DNA sequence string from user input
            
        Returns:
            Dictionary containing:
            - is_valid: Boolean - True if all checks pass
            - cleaned_sequence: Uppercase sequence with whitespace removed
            - length: Number of nucleotides in sequence
            - errors: List of error messages (empty if valid)
            - warnings: List of warning messages (non-critical issues)
        """
        # Clean the input sequence:
        # - strip(): Remove leading/trailing whitespace
        # - upper(): Convert to uppercase for consistency
        # - replace(): Remove all spaces, newlines, carriage returns
        cleaned_sequence = sequence.strip().upper()
        cleaned_sequence = cleaned_sequence.replace(' ', '')
        cleaned_sequence = cleaned_sequence.replace('\n', '')
        cleaned_sequence = cleaned_sequence.replace('\r', '')
        
        # Initialize result dictionary
        result = {
            'is_valid': False,  # Will be set to True if all checks pass
            'cleaned_sequence': cleaned_sequence,
            'length': len(cleaned_sequence),
            'errors': [],  # Critical issues that prevent processing
            'warnings': []  # Non-critical issues to inform user
        }
        
        # CHECK 1: Ensure sequence is not empty
        if not cleaned_sequence:
            # Add error message to list
            result['errors'].append('Sequence is empty')
            return result  # Return immediately - can't do other checks
        
        # CHECK 2: Validate minimum length
        if len(cleaned_sequence) < self.min_length:
            # Sequence too short to be meaningful
            result['errors'].append(
                f'Sequence too short (minimum {self.min_length} nucleotides required, got {len(cleaned_sequence)})'
            )
        
        # CHECK 3: Validate maximum length
        if len(cleaned_sequence) > self.max_length:
            # Sequence too long for our system to handle efficiently
            result['errors'].append(
                f'Sequence too long (maximum {self.max_length} nucleotides allowed, got {len(cleaned_sequence)})'
            )
        
        # CHECK 4: Verify only valid nucleotides
        # Create set of unique characters in sequence
        sequence_chars = set(cleaned_sequence)
        # Find any characters that aren't A, T, C, or G
        invalid_chars = sequence_chars - self.valid_nucleotides
        
        if invalid_chars:
            # Found invalid characters - DNA should only have A, T, C, G
            # Sort for consistent error message
            invalid_list = ', '.join(sorted(invalid_chars))
            result['errors'].append(
                f'Invalid nucleotides found: {invalid_list}. Only A, T, C, G are allowed'
            )
        
        # CHECK 5: Verify length divisible by 3 (for codon translation)
        # DNA is read in groups of 3 nucleotides (codons)
        # Each codon codes for one amino acid
        # If length isn't divisible by 3, last codon is incomplete
        if len(cleaned_sequence) % 3 != 0:
            # This is a WARNING not ERROR - we can still process
            remainder = len(cleaned_sequence) % 3
            result['warnings'].append(
                f'Sequence length ({len(cleaned_sequence)}) is not divisible by 3. '
                f'Last {remainder} nucleotide(s) will form incomplete codon and may '
                f'affect protein translation accuracy.'
            )
        
        # Set validation status
        # Sequence is valid only if there are NO errors
        # Warnings are OK - they're just informational
        result['is_valid'] = len(result['errors']) == 0
        
        return result
    
    def validate_batch(self, sequences: list) -> list:
        """
        Validate multiple DNA sequences
        
        Useful when processing multiple sequences at once.
        Each sequence is validated independently.
        
        Args:
            sequences: List of DNA sequence strings
            
        Returns:
            List of validation results (one per sequence)
        """
        # Apply validate() method to each sequence in the list
        # This is a simple loop wrapped in list comprehension
        return [self.validate(seq) for seq in sequences]

"""
Validation Agent
Responsible for validating gene sequences:
- Check if sequence contains only valid nucleotides (A, T, C, G)
- Validate sequence length
- Check format integrity
"""

import re
from typing import Dict, Tuple

class ValidationAgent:
    """Agent for validating gene sequences"""
    
    def __init__(self):
        # Valid nucleotides for DNA sequences
        self.valid_nucleotides = set('ATCG')
        self.min_length = 10  # Minimum sequence length
        self.max_length = 10000  # Maximum sequence length for processing
    
    def validate(self, sequence: str) -> Dict:
        """
        Validate a gene sequence
        
        Args:
            sequence: DNA sequence string
            
        Returns:
            Dictionary with validation results
        """
        # Clean the sequence (remove whitespace and convert to uppercase)
        cleaned_sequence = sequence.strip().upper().replace(' ', '').replace('\n', '').replace('\r', '')
        
        # Initialize validation result
        result = {
            'is_valid': False,
            'cleaned_sequence': cleaned_sequence,
            'length': len(cleaned_sequence),
            'errors': [],
            'warnings': []
        }
        
        # Check if sequence is empty
        if not cleaned_sequence:
            result['errors'].append('Sequence is empty')
            return result
        
        # Check sequence length
        if len(cleaned_sequence) < self.min_length:
            result['errors'].append(f'Sequence too short (minimum {self.min_length} nucleotides)')
        
        if len(cleaned_sequence) > self.max_length:
            result['errors'].append(f'Sequence too long (maximum {self.max_length} nucleotides)')
        
        # Check for invalid characters
        invalid_chars = set(cleaned_sequence) - self.valid_nucleotides
        if invalid_chars:
            result['errors'].append(f'Invalid nucleotides found: {", ".join(sorted(invalid_chars))}')
        
        # Check if length is divisible by 3 (for proper codon translation)
        if len(cleaned_sequence) % 3 != 0:
            result['warnings'].append(f'Sequence length ({len(cleaned_sequence)}) is not divisible by 3. May cause incomplete codon translation.')
        
        # Set validation status
        result['is_valid'] = len(result['errors']) == 0
        
        return result
    
    def validate_batch(self, sequences: list) -> list:
        """
        Validate multiple sequences
        
        Args:
            sequences: List of DNA sequence strings
            
        Returns:
            List of validation results
        """
        return [self.validate(seq) for seq in sequences]
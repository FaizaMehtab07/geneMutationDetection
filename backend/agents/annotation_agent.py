"""
Annotation Agent - DNA to Protein Translation
==============================================

PURPOSE:
Translates DNA-level mutations into protein-level effects. This is crucial
because proteins do the actual work in cells, not DNA. DNA is just the
instruction manual.

THE GENETIC CODE:
DNA alphabet: 4 letters (A, T, C, G)
Protein alphabet: 20 amino acids (A, C, D, E, F, G, H, I, K, L, M, N, P, Q, R, S, T, V, W, Y)

DNA is read in triplets called CODONS:
  ATG = Methionine (M)
  TGG = Tryptophan (W)
  TAA = STOP (end of protein)
  
Each codon maps to exactly one amino acid (but multiple codons can
map to same amino acid - this is "degeneracy" of genetic code).

MUTATION EFFECTS:

1. MISSENSE:
   DNA change causes amino acid change
   Example: CGT (Arginine) → CAT (Histidine)
   Notation: R175H (Arginine at position 175 → Histidine)
   Impact: May affect protein function

2. NONSENSE:
   DNA change creates STOP codon
   Example: CAG (Glutamine) → TAG (STOP)
   Notation: Q175* (Glutamine at 175 → Stop)
   Impact: Protein truncated (usually severe)

3. SYNONYMOUS (Silent):
   DNA change but same amino acid
   Example: CGT → CGC (both = Arginine)
   Notation: R175R or R175=
   Impact: Usually none (same protein made)

4. FRAMESHIFT:
   Insertion/deletion not divisible by 3
   Example: Insert 1 nucleotide
   Impact: All downstream codons shift
           → Completely different protein
           → Usually nonsense (catastrophic)

WHY PROTEIN LEVEL MATTERS:
A mutation that doesn't change the protein (synonymous) is usually
harmless. But a mutation that changes the protein can:
- Break enzyme active sites
- Disrupt protein folding
- Remove DNA binding domains
- Create unstable proteins

This agent determines which scenario applies to each mutation.
"""

from typing import Dict, List, Optional

class AnnotationAgent:
    """Agent for annotating mutations with protein-level effects"""
    
    def __init__(self):
        # Standard genetic code (codon to amino acid mapping)
        self.codon_table = {
            'TTT': 'F', 'TTC': 'F', 'TTA': 'L', 'TTG': 'L',
            'TCT': 'S', 'TCC': 'S', 'TCA': 'S', 'TCG': 'S',
            'TAT': 'Y', 'TAC': 'Y', 'TAA': '*', 'TAG': '*',
            'TGT': 'C', 'TGC': 'C', 'TGA': '*', 'TGG': 'W',
            'CTT': 'L', 'CTC': 'L', 'CTA': 'L', 'CTG': 'L',
            'CCT': 'P', 'CCC': 'P', 'CCA': 'P', 'CCG': 'P',
            'CAT': 'H', 'CAC': 'H', 'CAA': 'Q', 'CAG': 'Q',
            'CGT': 'R', 'CGC': 'R', 'CGA': 'R', 'CGG': 'R',
            'ATT': 'I', 'ATC': 'I', 'ATA': 'I', 'ATG': 'M',
            'ACT': 'T', 'ACC': 'T', 'ACA': 'T', 'ACG': 'T',
            'AAT': 'N', 'AAC': 'N', 'AAA': 'K', 'AAG': 'K',
            'AGT': 'S', 'AGC': 'S', 'AGA': 'R', 'AGG': 'R',
            'GTT': 'V', 'GTC': 'V', 'GTA': 'V', 'GTG': 'V',
            'GCT': 'A', 'GCC': 'A', 'GCA': 'A', 'GCG': 'A',
            'GAT': 'D', 'GAC': 'D', 'GAA': 'E', 'GAG': 'E',
            'GGT': 'G', 'GGC': 'G', 'GGA': 'G', 'GGG': 'G'
        }
        
        # Three-letter amino acid codes
        self.aa_three_letter = {
            'A': 'Ala', 'C': 'Cys', 'D': 'Asp', 'E': 'Glu',
            'F': 'Phe', 'G': 'Gly', 'H': 'His', 'I': 'Ile',
            'K': 'Lys', 'L': 'Leu', 'M': 'Met', 'N': 'Asn',
            'P': 'Pro', 'Q': 'Gln', 'R': 'Arg', 'S': 'Ser',
            'T': 'Thr', 'V': 'Val', 'W': 'Trp', 'Y': 'Tyr',
            '*': 'Stop'
        }
    
    def translate_codon(self, codon: str) -> str:
        """
        Translate a DNA codon to amino acid
        
        Args:
            codon: 3-nucleotide DNA sequence
            
        Returns:
            Single letter amino acid code
        """
        codon = codon.upper().replace('U', 'T')  # Handle RNA input
        
        if len(codon) != 3:
            return '?'
        
        return self.codon_table.get(codon, '?')
    
    def translate_sequence(self, sequence: str) -> str:
        """
        Translate DNA sequence to protein
        
        Args:
            sequence: DNA sequence (should be multiple of 3)
            
        Returns:
            Protein sequence (amino acid string)
        """
        sequence = sequence.upper().replace('-', '')
        protein = ''
        
        for i in range(0, len(sequence) - 2, 3):
            codon = sequence[i:i+3]
            protein += self.translate_codon(codon)
        
        return protein
    
    def annotate(self, mutations: List[Dict], reference_sequence: str, query_sequence: str) -> Dict:
        """
        Annotate mutations with protein-level effects
        
        Args:
            mutations: List of mutations from mutation detection agent
            reference_sequence: Reference DNA sequence (no gaps)
            query_sequence: Query DNA sequence (no gaps)
            
        Returns:
            Dictionary with annotated mutations
        """
        annotated_mutations = []
        
        # Remove gaps from sequences
        ref_clean = reference_sequence.replace('-', '')
        query_clean = query_sequence.replace('-', '')
        
        for mutation in mutations:
            annotated = mutation.copy()
            
            if mutation['type'] == 'substitution':
                position = mutation['position'] - 1  # Convert to 0-indexed
                
                # Determine which codon this position is in
                codon_index = position // 3
                codon_position = position % 3  # Position within codon (0, 1, or 2)
                
                # Get the codons
                if codon_index * 3 + 2 < len(ref_clean):
                    ref_codon = ref_clean[codon_index * 3:codon_index * 3 + 3]
                    
                    # Build mutant codon
                    mut_codon = list(ref_codon)
                    if codon_position < len(mut_codon):
                        mut_codon[codon_position] = mutation['alternate_base']
                        mut_codon = ''.join(mut_codon)
                        
                        # Translate both codons
                        ref_aa = self.translate_codon(ref_codon)
                        mut_aa = self.translate_codon(mut_codon)
                        
                        # Create protein annotation
                        if ref_aa != '?' and mut_aa != '?':
                            aa_position = codon_index + 1
                            
                            if ref_aa == mut_aa:
                                effect = 'synonymous'
                                impact = 'Silent mutation - no amino acid change'
                            elif mut_aa == '*':
                                effect = 'nonsense'
                                impact = 'Creates premature stop codon'
                            else:
                                effect = 'missense'
                                impact = f'Amino acid change: {ref_aa} → {mut_aa}'
                            
                            annotated.update({
                                'protein_position': aa_position,
                                'reference_codon': ref_codon,
                                'mutant_codon': mut_codon,
                                'reference_aa': ref_aa,
                                'mutant_aa': mut_aa,
                                'protein_change': f'{ref_aa}{aa_position}{mut_aa}',
                                'effect': effect,
                                'impact': impact
                            })
            
            elif mutation['type'] in ['insertion', 'deletion']:
                # Indels typically cause frameshift
                length = mutation.get('length', 0)
                
                if length % 3 == 0:
                    effect = 'inframe_' + mutation['type']
                    impact = f'In-frame {mutation["type"]} - may preserve reading frame'
                else:
                    effect = 'frameshift'
                    impact = f'Frameshift mutation - likely loss of function'
                
                annotated.update({
                    'effect': effect,
                    'impact': impact
                })
            
            annotated_mutations.append(annotated)
        
        # Calculate overall impact summary
        impact_summary = self._calculate_impact_summary(annotated_mutations)
        
        return {
            'annotated_mutations': annotated_mutations,
            'impact_summary': impact_summary
        }
    
    def _calculate_impact_summary(self, mutations: List[Dict]) -> Dict:
        """
        Calculate summary of mutation impacts
        
        Args:
            mutations: List of annotated mutations
            
        Returns:
            Summary dictionary
        """
        effects = {}
        high_impact = 0
        moderate_impact = 0
        low_impact = 0
        
        for mutation in mutations:
            effect = mutation.get('effect', 'unknown')
            effects[effect] = effects.get(effect, 0) + 1
            
            # Categorize impact level
            if effect in ['frameshift', 'nonsense']:
                high_impact += 1
            elif effect in ['missense', 'inframe_insertion', 'inframe_deletion']:
                moderate_impact += 1
            elif effect == 'synonymous':
                low_impact += 1
        
        return {
            'effect_counts': effects,
            'high_impact': high_impact,
            'moderate_impact': moderate_impact,
            'low_impact': low_impact
        }

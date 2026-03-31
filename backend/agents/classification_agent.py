"""
Classification Agent - Mutation Risk Assessment
================================================

This agent classifies mutations as Pathogenic (dangerous), Benign (harmless),
or Uncertain based on their molecular effects.

Classification is purely rule-based:
- Frameshift mutations → Pathogenic (usually severe)
- Nonsense mutations → Pathogenic (protein truncated)
- Missense mutations → Potentially Pathogenic (protein changed)
- Synonymous mutations → Benign (no protein change)

Note: This is a simplified classification system.
Real clinical classification requires:
- Population frequency data
- Evolutionary conservation
- Functional studies
- Clinical correlation
"""

from typing import Dict, List

class ClassificationAgent:
    """
    Agent responsible for classifying mutation pathogenicity
    """
    
    def __init__(self):
        """
        Initialize classification agent with rule definitions
        """
        # Define classification rules based on mutation effect
        # Key = mutation effect type
        # Value = clinical classification
        self.classification_rules = {
            'frameshift': 'Pathogenic',  # Reading frame shifted - usually catastrophic
            'nonsense': 'Pathogenic',    # Stop codon created - protein truncated
            'missense': 'Potentially Pathogenic',  # Amino acid changed - may affect function
            'inframe_insertion': 'Potentially Pathogenic',  # Bases added but frame preserved
            'inframe_deletion': 'Potentially Pathogenic',   # Bases deleted but frame preserved
            'synonymous': 'Benign'       # No amino acid change - usually harmless
        }
        
        # Define risk levels for each classification
        self.risk_levels = {
            'Pathogenic': {
                'level': 'HIGH',
                'description': 'Mutation likely causes disease'
            },
            'Potentially Pathogenic': {
                'level': 'MODERATE',
                'description': 'Mutation may cause disease - further investigation needed'
            },
            'Uncertain': {
                'level': 'MODERATE',
                'description': 'Clinical significance unknown'
            },
            'Benign': {
                'level': 'LOW',
                'description': 'Mutation likely harmless'
            }
        }
    
    def classify(self, annotated_mutations: List[Dict], mutation_stats: Dict) -> Dict:
        """
        Classify mutations and determine overall risk level
        
        Process:
        1. Classify each individual mutation based on its effect
        2. Count mutations by classification
        3. Determine overall classification (worst mutation determines overall)
        4. Generate clinical recommendation
        
        Args:
            annotated_mutations: List of mutations with protein-level annotations
            mutation_stats: Statistics about mutations detected
            
        Returns:
            Dictionary containing:
            - overall_classification: Overall assessment (Pathogenic/Benign/etc)
            - risk_level: HIGH/MODERATE/LOW
            - confidence: Confidence in classification
            - rationale: Explanation of classification
            - classified_mutations: List of mutations with individual classifications
            - summary: Count of mutations by classification type
            - recommendation: Clinical action recommendation
        """
        
        # CASE 1: No mutations detected
        if not annotated_mutations or len(annotated_mutations) == 0:
            return {
                'overall_classification': 'Benign',
                'risk_level': 'LOW',
                'confidence': 'HIGH',
                'rationale': 'No mutations detected. Sequence matches reference gene perfectly.',
                'classified_mutations': [],
                'summary': {
                    'pathogenic': 0,
                    'potentially_pathogenic': 0,
                    'uncertain': 0,
                    'benign': 0
                },
                'recommendation': 'No clinical concern. Sequence appears normal.'
            }
        
        # CASE 2: Mutations detected - classify each one
        classified_mutations = []
        
        # Initialize counters for each classification type
        classification_counts = {
            'Pathogenic': 0,
            'Potentially Pathogenic': 0,
            'Uncertain': 0,
            'Benign': 0
        }
        
        # Loop through each mutation and classify it
        for mutation in annotated_mutations:
            # Get the effect type (missense, nonsense, etc.)
            effect = mutation.get('effect', 'unknown')
            
            # Apply classification rule based on effect
            # If effect not in our rules, mark as Uncertain
            classification = self.classification_rules.get(effect, 'Uncertain')
            
            # Get corresponding risk level
            risk_info = self.risk_levels.get(classification, {})
            risk_level = risk_info.get('level', 'MODERATE')
            
            # Calculate confidence in this classification
            # High confidence for clear-cut cases (frameshift, nonsense, synonymous)
            # Moderate confidence for missense and uncertain
            confidence = self._calculate_confidence(mutation, effect)
            
            # Create classified mutation entry
            mutation_classification = {
                **mutation,  # Include all original mutation data
                'classification': classification,
                'risk_level': risk_level,
                'confidence': confidence
            }
            
            # Add to results
            classified_mutations.append(mutation_classification)
            
            # Increment counter for this classification type
            classification_counts[classification] += 1
        
        # Determine overall classification based on worst mutation
        # Rationale: One pathogenic mutation is enough to be concerning
        overall_classification, rationale = self._determine_overall_classification(
            classification_counts,
            mutation_stats
        )
        
        # Get overall risk level
        risk_level = self.risk_levels.get(overall_classification, {}).get('level', 'MODERATE')
        
        # Generate clinical recommendation
        recommendation = self._generate_recommendation(
            overall_classification,
            classified_mutations
        )
        
        return {
            'overall_classification': overall_classification,
            'risk_level': risk_level,
            'confidence': 'MODERATE',  # Could be improved with ML model
            'rationale': rationale,
            'classified_mutations': classified_mutations,
            'summary': {
                'pathogenic': classification_counts['Pathogenic'],
                'potentially_pathogenic': classification_counts['Potentially Pathogenic'],
                'uncertain': classification_counts['Uncertain'],
                'benign': classification_counts['Benign']
            },
            'recommendation': recommendation
        }
    
    def _calculate_confidence(self, mutation: Dict, effect: str) -> str:
        """
        Calculate confidence level for mutation classification
        
        Confidence depends on how well-understood the mutation type is:
        - Frameshift/Nonsense: HIGH (almost always pathogenic)
        - Synonymous: HIGH (almost always benign)
        - Missense: MODERATE (depends on specific amino acid change)
        - Unknown: LOW
        
        Args:
            mutation: Mutation data
            effect: Type of mutation effect
            
        Returns:
            Confidence level: HIGH, MODERATE, or LOW
        """
        # High confidence for clear functional impacts
        if effect in ['frameshift', 'nonsense']:
            return 'HIGH'  # These almost always break protein function
        
        # High confidence for synonymous (no change)
        if effect == 'synonymous':
            return 'HIGH'  # No protein change = usually benign
        
        # Moderate confidence for missense and in-frame indels
        if effect in ['missense', 'inframe_insertion', 'inframe_deletion']:
            return 'MODERATE'  # Impact depends on specific change
        
        # Low confidence for unknown types
        return 'LOW'
    
    def _determine_overall_classification(self, counts: Dict, stats: Dict) -> tuple:
        """
        Determine overall classification from individual mutation classifications
        
        Uses "worst-case" approach: if any mutation is pathogenic,
        overall is pathogenic.
        
        Args:
            counts: Dictionary of classification counts
            stats: Mutation statistics
            
        Returns:
            Tuple of (classification string, rationale string)
        """
        # Priority order: Pathogenic > Potentially Pathogenic > Uncertain > Benign
        
        # Check for pathogenic mutations first (highest priority)
        if counts['Pathogenic'] > 0:
            rationale = (
                f"Detected {counts['Pathogenic']} pathogenic mutation(s) with severe "
                f"impact (frameshift or nonsense mutations). These mutations likely "
                f"disrupt normal protein function and may cause disease."
            )
            return 'Pathogenic', rationale
        
        # Check for potentially pathogenic mutations
        if counts['Potentially Pathogenic'] > 0:
            rationale = (
                f"Detected {counts['Potentially Pathogenic']} potentially pathogenic "
                f"mutation(s). These mutations alter the protein and may affect its "
                f"function. Clinical correlation and family history recommended."
            )
            return 'Potentially Pathogenic', rationale
        
        # Check for uncertain significance mutations
        if counts['Uncertain'] > 0:
            rationale = (
                f"Detected {counts['Uncertain']} variant(s) of uncertain significance. "
                f"More information needed to determine clinical impact. Consider "
                f"consulting genetic databases or functional studies."
            )
            return 'Uncertain', rationale
        
        # All mutations are benign
        if counts['Benign'] > 0:
            rationale = (
                f"Detected {counts['Benign']} benign variant(s). These mutations "
                f"do not change the protein sequence and are not expected to "
                f"cause disease."
            )
            return 'Benign', rationale
        
        # Fallback (shouldn't reach here)
        return 'Uncertain', 'Unable to determine classification with available data.'
    
    def _generate_recommendation(self, classification: str, 
                                 mutations: List[Dict]) -> str:
        """
        Generate clinical recommendation based on classification
        
        Provides actionable advice for healthcare providers based on
        the overall classification result.
        
        Args:
            classification: Overall classification
            mutations: List of all classified mutations
            
        Returns:
            Recommendation string
        """
        # Recommendation templates for each classification
        recommendations = {
            'Pathogenic': (
                'CLINICAL ACTION RECOMMENDED: This analysis detected pathogenic '
                'mutation(s) that may increase disease risk. Recommend: (1) Genetic '
                'counseling, (2) Family screening, (3) Clinical correlation with '
                'patient history and symptoms. This is computational prediction only - '
                'clinical validation required.'
            ),
            
            'Potentially Pathogenic': (
                'FURTHER EVALUATION SUGGESTED: Detected potentially pathogenic '
                'mutation(s). Recommend: (1) Review patient clinical history, '
                '(2) Consider additional genetic testing, (3) Genetic counseling '
                'may be beneficial. Monitor for updates in variant databases.'
            ),
            
            'Uncertain': (
                'UNCERTAIN SIGNIFICANCE: Unable to determine clinical impact with '
                'current data. Recommend: (1) Check variant databases (ClinVar, gnomAD) '
                'for updates, (2) Consider functional studies, (3) Evaluate family '
                'segregation if applicable, (4) Reassess as new evidence emerges.'
            ),
            
            'Benign': (
                'NO IMMEDIATE ACTION REQUIRED: Detected variant(s) appear benign '
                'based on their molecular effects. No protein-level changes detected '
                'that would suggest disease risk. Standard care and monitoring '
                'appropriate. If clinical suspicion exists, consider testing other genes.'
            )
        }
        
        # Return recommendation for this classification
        # Use default message if classification not in dictionary
        return recommendations.get(
            classification,
            'Consult with genetics specialist for interpretation.'
        )

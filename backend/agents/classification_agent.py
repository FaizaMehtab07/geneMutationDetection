"""
Classification Agent
Responsible for risk classification:
- Rule-based classification system
- Classify based on mutation type and impact
- Ready for ML integration in future
"""

from typing import Dict, List

class ClassificationAgent:
    """Agent for classifying mutation pathogenicity and risk"""
    
    def __init__(self):
        # Classification rules based on mutation characteristics
        self.classification_rules = {
            'frameshift': 'Pathogenic',
            'nonsense': 'Pathogenic',
            'missense': 'Potentially Pathogenic',
            'inframe_insertion': 'Potentially Pathogenic',
            'inframe_deletion': 'Potentially Pathogenic',
            'synonymous': 'Likely Benign'
        }
        
        # Risk levels
        self.risk_levels = {
            'Pathogenic': {'level': 'HIGH', 'description': 'High confidence pathogenic variant'},
            'Potentially Pathogenic': {'level': 'MODERATE', 'description': 'Likely disease-causing variant'},
            'Uncertain significance': {'level': 'MODERATE', 'description': 'Uncertain clinical significance'},
            'Likely Benign': {'level': 'LOW', 'description': 'Likely non-pathogenic variant'},
            'Benign': {'level': 'LOW', 'description': 'Non-pathogenic variant'}
        }
    
    def classify(self, annotated_mutations: List[Dict], mutation_stats: Dict) -> Dict:
        """
        Classify mutations and assess overall risk
        
        Args:
            annotated_mutations: List of annotated mutations
            mutation_stats: Statistics about mutations
            
        Returns:
            Classification results with risk assessment
        """
        
        # If no mutations, classify as Benign
        if not annotated_mutations or len(annotated_mutations) == 0:
            return {
                'overall_classification': 'Benign',
                'risk_level': 'LOW',
                'confidence': 'HIGH',
                'rationale': 'No mutations detected. Sequence matches reference gene.',
                'classified_mutations': [],
                'summary': {
                    'pathogenic': 0,
                    'potentially_pathogenic': 0,
                    'uncertain': 0,
                    'benign': 0
                },
                'recommendation': 'No immediate clinical concern. Sequence appears normal.'
            }
        
        # Classify each mutation
        classified_mutations = []
        classification_counts = {
            'Pathogenic': 0,
            'Potentially Pathogenic': 0,
            'Uncertain significance': 0,
            'Likely Benign': 0,
            'Benign': 0
        }
        
        for mutation in annotated_mutations:
            effect = mutation.get('effect', 'unknown')
            
            # Apply classification rules
            classification = self.classification_rules.get(effect, 'Uncertain significance')
            
            # Add special handling for TP53 known hotspots (positions can be checked)
            # This is where ML model would be integrated in the future
            
            mutation_classification = {
                **mutation,
                'classification': classification,
                'risk_level': self.risk_levels.get(classification, {}).get('level', 'MODERATE'),
                'confidence': self._calculate_confidence(mutation, effect)
            }
            
            classified_mutations.append(mutation_classification)
            classification_counts[classification] += 1
        
        # Determine overall classification
        overall_classification, rationale = self._determine_overall_classification(
            classification_counts,
            mutation_stats
        )
        
        # Get risk level
        risk_level = self.risk_levels.get(overall_classification, {}).get('level', 'MODERATE')
        
        # Generate recommendation
        recommendation = self._generate_recommendation(overall_classification, classified_mutations)
        
        return {
            'overall_classification': overall_classification,
            'risk_level': risk_level,
            'confidence': 'MODERATE',  # Could be ML-based in future
            'rationale': rationale,
            'classified_mutations': classified_mutations,
            'summary': {
                'pathogenic': classification_counts['Pathogenic'],
                'potentially_pathogenic': classification_counts['Potentially Pathogenic'],
                'uncertain': classification_counts['Uncertain significance'],
                'benign': classification_counts['Likely Benign'] + classification_counts['Benign']
            },
            'recommendation': recommendation
        }
    
    def _calculate_confidence(self, mutation: Dict, effect: str) -> str:
        """
        Calculate confidence level for mutation classification
        
        Args:
            mutation: Mutation data
            effect: Mutation effect type
            
        Returns:
            Confidence level (HIGH, MODERATE, LOW)
        """
        # High confidence for clear functional impacts
        if effect in ['frameshift', 'nonsense']:
            return 'HIGH'
        
        # Moderate confidence for missense and in-frame mutations
        if effect in ['missense', 'inframe_insertion', 'inframe_deletion']:
            return 'MODERATE'
        
        # High confidence for synonymous (benign)
        if effect == 'synonymous':
            return 'HIGH'
        
        return 'LOW'
    
    def _determine_overall_classification(self, counts: Dict, stats: Dict) -> tuple:
        """
        Determine overall classification based on mutation counts
        
        Args:
            counts: Classification counts
            stats: Mutation statistics
            
        Returns:
            Tuple of (classification, rationale)
        """
        # If any pathogenic mutations found
        if counts['Pathogenic'] > 0:
            rationale = f"Detected {counts['Pathogenic']} pathogenic mutation(s) with high impact (frameshift/nonsense). " \
                       f"These mutations likely disrupt protein function."
            return 'Pathogenic', rationale
        
        # If potentially pathogenic mutations found
        if counts['Potentially Pathogenic'] > 0:
            rationale = f"Detected {counts['Potentially Pathogenic']} potentially pathogenic mutation(s). " \
                       f"These mutations may affect protein function and require clinical correlation."
            return 'Potentially Pathogenic', rationale
        
        # If only uncertain significance
        if counts['Uncertain significance'] > 0:
            rationale = f"Detected {counts['Uncertain significance']} variant(s) of uncertain significance. " \
                       f"Further investigation and clinical data needed."
            return 'Uncertain significance', rationale
        
        # If only benign mutations
        if counts['Likely Benign'] > 0 or counts['Benign'] > 0:
            total_benign = counts['Likely Benign'] + counts['Benign']
            rationale = f"Detected {total_benign} likely benign variant(s). " \
                       f"These mutations do not appear to affect protein function."
            return 'Likely Benign', rationale
        
        # Default
        return 'Uncertain significance', 'Unable to determine classification with available data.'
    
    def _generate_recommendation(self, classification: str, mutations: List[Dict]) -> str:
        """
        Generate clinical recommendation based on classification
        
        Args:
            classification: Overall classification
            mutations: List of classified mutations
            
        Returns:
            Recommendation string
        """
        recommendations = {
            'Pathogenic': 'Immediate clinical review recommended. Consider genetic counseling and family screening. '
                         'Mutation associated with increased disease risk.',
            
            'Potentially Pathogenic': 'Clinical correlation advised. Review patient history and consider additional '
                                     'testing. Genetic counseling may be beneficial.',
            
            'Uncertain significance': 'Variant interpretation uncertain. Consider segregation analysis, functional '
                                     'studies, or additional clinical information. Monitor for updates in variant databases.',
            
            'Likely Benign': 'No immediate clinical action required. Variant likely does not contribute to disease risk. '
                           'Routine monitoring as per standard guidelines.',
            
            'Benign': 'No clinical significance. Standard care and monitoring appropriate.'
        }
        
        return recommendations.get(classification, 'Consult with genetics specialist for interpretation.')
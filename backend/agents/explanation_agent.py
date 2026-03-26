"""
Explanation Agent
Responsible for generating AI-powered explanations:
- Use Gemini API for natural language generation
- Generate explanations based on:
  - Mutation details
  - Classification results
  - Retrieved evidence
- No hardcoded explanations
"""

from emergentintegrations.llm.chat import LlmChat, UserMessage
from typing import Dict, List
import os
import asyncio

class ExplanationAgent:
    """Agent for generating AI-powered clinical explanations using Gemini"""
    
    def __init__(self, api_key: str = None):
        """
        Initialize explanation agent with Gemini API
        
        Args:
            api_key: Emergent LLM API key (or Gemini API key)
        """
        # Use provided key or get from environment
        self.api_key = api_key or os.environ.get('EMERGENT_LLM_KEY')
        
        if not self.api_key:
            raise ValueError("API key not provided. Set EMERGENT_LLM_KEY environment variable.")
    
    async def generate_explanation(self, 
                                  mutations: List[Dict],
                                  classification: Dict,
                                  evidence: Dict,
                                  gene: str = 'TP53') -> Dict:
        """
        Generate comprehensive explanation using Gemini AI
        
        Args:
            mutations: List of classified mutations
            classification: Classification results
            evidence: Retrieved ClinVar evidence
            gene: Gene name
            
        Returns:
            Dictionary with generated explanation
        """
        try:
            # Create chat instance with Gemini
            chat = LlmChat(
                api_key=self.api_key,
                session_id='gene_mutation_analysis',
                system_message="You are a clinical geneticist AI assistant specializing in mutation interpretation. "
                              "Provide clear, accurate, and professional explanations of genetic mutations and their "
                              "clinical significance. Use medical terminology appropriately but explain complex concepts clearly."
            )
            
            # Configure to use Gemini 3 Flash
            chat.with_model("gemini", "gemini-3-flash-preview")
            
            # Construct the prompt with all relevant information
            prompt = self._build_prompt(mutations, classification, evidence, gene)
            
            # Create user message
            user_message = UserMessage(text=prompt)
            
            # Get AI-generated explanation
            response = await chat.send_message(user_message)
            
            return {
                'success': True,
                'explanation': response,
                'model': 'gemini-3-flash-preview',
                'gene': gene
            }
            
        except Exception as e:
            # Fallback to rule-based explanation if AI fails
            fallback_explanation = self._generate_fallback_explanation(mutations, classification)
            
            return {
                'success': False,
                'error': str(e),
                'explanation': fallback_explanation,
                'model': 'fallback',
                'gene': gene
            }
    
    def _build_prompt(self, mutations: List[Dict], classification: Dict, 
                     evidence: Dict, gene: str) -> str:
        """
        Build comprehensive prompt for AI explanation generation
        
        Args:
            mutations: Mutation data
            classification: Classification results
            evidence: ClinVar evidence
            gene: Gene name
            
        Returns:
            Formatted prompt string
        """
        prompt = f"""Analyze the following genetic mutation analysis results for the {gene} gene and provide a comprehensive clinical interpretation.

**GENE INFORMATION:**
Gene: {gene} (Tumor Protein 53)
Function: Tumor suppressor gene, critical for cell cycle regulation and apoptosis

**MUTATION ANALYSIS:**
"""
        
        # Add mutation details
        if mutations:
            prompt += f"\nTotal mutations detected: {len(mutations)}\n\n"
            
            for i, mut in enumerate(mutations, 1):
                prompt += f"Mutation {i}:\n"
                prompt += f"  - Type: {mut.get('type', 'Unknown')}\n"
                prompt += f"  - Position: {mut.get('position', 'N/A')}\n"
                
                if mut.get('type') == 'substitution':
                    prompt += f"  - DNA Change: {mut.get('reference_base', '?')} → {mut.get('alternate_base', '?')}\n"
                    if 'protein_change' in mut:
                        prompt += f"  - Protein Change: {mut.get('protein_change', 'N/A')}\n"
                        prompt += f"  - Effect: {mut.get('effect', 'Unknown')}\n"
                        prompt += f"  - Impact: {mut.get('impact', 'Unknown')}\n"
                
                prompt += f"  - Classification: {mut.get('classification', 'Unknown')}\n"
                prompt += f"  - Risk Level: {mut.get('risk_level', 'Unknown')}\n\n"
        else:
            prompt += "\nNo mutations detected. Sequence matches reference.\n\n"
        
        # Add classification
        prompt += f"**OVERALL CLASSIFICATION:**\n"
        prompt += f"Classification: {classification.get('overall_classification', 'Unknown')}\n"
        prompt += f"Risk Level: {classification.get('risk_level', 'Unknown')}\n"
        prompt += f"Rationale: {classification.get('rationale', 'N/A')}\n\n"
        
        # Add ClinVar evidence
        if evidence.get('evidence'):
            prompt += f"**CLINVAR EVIDENCE:**\n"
            prompt += f"Total evidence records: {len(evidence['evidence'])}\n\n"
            
            for i, ev in enumerate(evidence['evidence'][:3], 1):  # Top 3 evidence
                prompt += f"Evidence {i}:\n"
                prompt += f"  - Clinical Significance: {ev.get('clinical_significance', 'Unknown')}\n"
                prompt += f"  - Condition: {ev.get('condition', 'Not specified')}\n"
                prompt += f"  - Summary: {ev.get('evidence_summary', 'N/A')}\n\n"
        
        # Request structured explanation
        prompt += """\n**PLEASE PROVIDE:**

1. **Clinical Interpretation** (2-3 sentences):
   - Explain the overall significance of these findings in clinical context
   - What does this mean for the patient?

2. **Molecular Impact** (2-3 sentences):
   - Describe how these mutations affect the protein and cellular function
   - Explain the biological mechanism

3. **Clinical Recommendations** (2-3 bullet points):
   - What are the next steps?
   - What should clinicians consider?
   - Are there any specific screening or management recommendations?

4. **Patient Counseling Points** (2-3 bullet points):
   - Key points to communicate to the patient in accessible language
   - What should they understand about these results?

Keep the explanation professional, accurate, and clinically relevant. Use clear language that balances technical accuracy with accessibility.
"""
        
        return prompt
    
    def _generate_fallback_explanation(self, mutations: List[Dict], 
                                      classification: Dict) -> str:
        """
        Generate rule-based explanation as fallback when AI is unavailable
        
        Args:
            mutations: Mutation data
            classification: Classification results
            
        Returns:
            Fallback explanation string
        """
        if not mutations:
            return (
                "**Clinical Interpretation:**\n"
                "No mutations were detected in the analyzed sequence. The sequence matches the reference TP53 gene. "
                "This indicates a normal TP53 gene without pathogenic variants.\n\n"
                "**Recommendation:**\n"
                "No immediate clinical action required based on this analysis. Standard cancer screening guidelines apply."
            )
        
        overall_class = classification.get('overall_classification', 'Unknown')
        risk_level = classification.get('risk_level', 'Unknown')
        
        explanation = f"""**Clinical Interpretation:**
The analysis detected {len(mutations)} mutation(s) in the TP53 gene. Overall classification: {overall_class} (Risk: {risk_level}).

**Detected Mutations:**
"""
        
        for i, mut in enumerate(mutations, 1):
            explanation += f"\n{i}. Position {mut.get('position')}: {mut.get('type')} "
            if mut.get('protein_change'):
                explanation += f"({mut.get('protein_change')}) - {mut.get('effect')}"
        
        explanation += f"\n\n**Recommendation:**\n{classification.get('recommendation', 'Consult with genetics specialist.')}"
        
        return explanation
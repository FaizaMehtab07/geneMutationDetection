import React from 'react';
import { Sparkle, Info, Brain } from '@phosphor-icons/react';
import { Card, CardContent, CardHeader, CardTitle } from './ui/card';
import { Alert, AlertDescription } from './ui/alert';
import { Badge } from './ui/badge';
import { ScrollArea } from './ui/scroll-area';

const AIExplanation = ({ explanation, classification }) => {
  if (!explanation || !explanation.explanation) {
    return (
      <div className="text-center py-12">
        <Brain size={48} weight="duotone" className="mx-auto mb-3 text-slate-400" />
        <p className="text-sm text-slate-600">AI explanation not available.</p>
      </div>
    );
  }

  const isAIGenerated = explanation.success && explanation.model !== 'fallback';

  return (
    <div data-testid="ai-explanation" className="space-y-4">
      {/* Header */}
      <div className="flex items-start justify-between">
        <div className="flex items-start gap-3">
          <div className="p-2 bg-[#E6EBE8] rounded-lg">
            <Sparkle size={24} weight="duotone" className="text-[#52745E]" />
          </div>
          <div>
            <h3 className="text-lg font-medium" style={{ fontFamily: 'Work Sans, sans-serif' }}>
              Clinical Interpretation
            </h3>
            <p className="text-sm text-slate-600 mt-1">
              {isAIGenerated ? (
                <span className="flex items-center gap-1.5">
                  <Badge className="bg-[#E6EBE8] text-[#52745E] border-[#CCD7D1] text-xs">
                    AI-Generated
                  </Badge>
                  <span className="text-xs">Powered by {explanation.model}</span>
                </span>
              ) : (
                <span className="text-xs text-slate-500">Rule-based interpretation</span>
              )}
            </p>
          </div>
        </div>
      </div>

      {/* AI Error Alert */}
      {!explanation.success && explanation.error && (
        <Alert className="border-[#D19B53] bg-[#FEF3E8]">
          <Info size={20} className="text-[#D19B53]" />
          <AlertDescription className="text-sm text-slate-700">
            <strong>Note:</strong> AI explanation unavailable ({explanation.error}). Displaying rule-based interpretation below.
          </AlertDescription>
        </Alert>
      )}

      {/* Explanation Content */}
      <Card className="border border-[#E5E4DE] shadow-sm">
        <CardContent className="pt-6">
          <ScrollArea className="h-[500px] pr-4">
            <div className="prose prose-sm max-w-none">
              <div 
                className="text-slate-700 leading-relaxed whitespace-pre-wrap"
                style={{ fontFamily: 'IBM Plex Sans, sans-serif' }}
              >
                {explanation.explanation}
              </div>
            </div>
          </ScrollArea>
        </CardContent>
      </Card>

      {/* Summary Stats */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
        <Card className="border border-[#E5E4DE]">
          <CardContent className="pt-6">
            <div className="flex items-center gap-3">
              <div className="p-2 bg-[#F4F3EF] rounded-lg">
                <Info size={20} className="text-[#52745E]" />
              </div>
              <div>
                <p className="text-xs font-bold uppercase tracking-wider text-slate-500">Gene Analyzed</p>
                <p className="text-lg font-semibold text-slate-900" style={{ fontFamily: 'IBM Plex Mono, monospace' }}>
                  {explanation.gene || 'Unknown'}
                </p>
              </div>
            </div>
          </CardContent>
        </Card>

        <Card className="border border-[#E5E4DE]">
          <CardContent className="pt-6">
            <div className="flex items-center gap-3">
              <div className="p-2 bg-[#F4F3EF] rounded-lg">
                <Info size={20} className="text-[#52745E]" />
              </div>
              <div>
                <p className="text-xs font-bold uppercase tracking-wider text-slate-500">Classification</p>
                <p className="text-sm font-semibold text-slate-900">
                  {classification?.overall_classification || 'Unknown'}
                </p>
              </div>
            </div>
          </CardContent>
        </Card>

        <Card className="border border-[#E5E4DE]">
          <CardContent className="pt-6">
            <div className="flex items-center gap-3">
              <div className="p-2 bg-[#F4F3EF] rounded-lg">
                <Info size={20} className="text-[#52745E]" />
              </div>
              <div>
                <p className="text-xs font-bold uppercase tracking-wider text-slate-500">Risk Level</p>
                <p className="text-sm font-semibold text-slate-900">
                  {classification?.risk_level || 'Unknown'}
                </p>
              </div>
            </div>
          </CardContent>
        </Card>
      </div>

      {/* Disclaimer */}
      <Alert className="border-[#E5E4DE] bg-[#F4F3EF]">
        <Info size={16} className="text-slate-600" />
        <AlertDescription className="text-xs text-slate-600">
          <strong>Clinical Use Disclaimer:</strong> This AI-generated interpretation is for research and educational purposes only. 
          Always consult with qualified healthcare professionals and certified genetic counselors for clinical decision-making.
        </AlertDescription>
      </Alert>
    </div>
  );
};

export default AIExplanation;
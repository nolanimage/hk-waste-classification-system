'use client';

import { ClassificationResponse } from '@/lib/api';

interface ResultDisplayProps {
  result: ClassificationResponse;
}

const binColorMap: Record<string, { bg: string; text: string; border: string }> = {
  blue: {
    bg: 'bg-blue-100',
    text: 'text-blue-800',
    border: 'border-blue-500',
  },
  yellow: {
    bg: 'bg-yellow-100',
    text: 'text-yellow-800',
    border: 'border-yellow-500',
  },
  brown: {
    bg: 'bg-amber-100',
    text: 'text-amber-800',
    border: 'border-amber-500',
  },
  green: {
    bg: 'bg-green-100',
    text: 'text-green-800',
    border: 'border-green-500',
  },
  other: {
    bg: 'bg-gray-100',
    text: 'text-gray-800',
    border: 'border-gray-500',
  },
};

export default function ResultDisplay({ result }: ResultDisplayProps) {
  const colorScheme = binColorMap[result.binColor.toLowerCase()] || binColorMap.other;

  return (
    <div className="space-y-4">
      <div className={`rounded-lg border-2 ${colorScheme.border} ${colorScheme.bg} p-6`}>
        <h2 className="text-2xl font-bold mb-4 text-gray-900">Classification Result</h2>
        
        <div className="space-y-3">
          <div>
            <span className="text-sm font-medium text-gray-600">Item:</span>
            <p className="text-lg font-semibold text-gray-900">{result.item}</p>
          </div>
          
          <div>
            <span className="text-sm font-medium text-gray-600">Category:</span>
            <p className="text-lg capitalize text-gray-900">{result.category}</p>
          </div>
          
          <div>
            <span className="text-sm font-medium text-gray-600">Bin:</span>
            <p className={`text-lg font-semibold ${colorScheme.text}`}>{result.bin}</p>
          </div>
          
          <div className="pt-3 border-t border-gray-300">
            <span className="text-sm font-medium text-gray-600">Explanation:</span>
            <p className="text-base text-gray-700 mt-1">{result.explanation}</p>
          </div>
        </div>
      </div>
    </div>
  );
}

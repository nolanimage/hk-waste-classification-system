'use client';

import { MultiClassificationResponse, ClassificationResult } from '@/lib/api';
import { useState } from 'react';

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

interface MultiResultDisplayProps {
  result: MultiClassificationResponse;
}

export default function MultiResultDisplay({ result }: MultiResultDisplayProps) {
  const [expandedItems, setExpandedItems] = useState<Set<number>>(new Set());

  const toggleExpand = (index: number) => {
    const newExpanded = new Set(expandedItems);
    if (newExpanded.has(index)) {
      newExpanded.delete(index);
    } else {
      newExpanded.add(index);
    }
    setExpandedItems(newExpanded);
  };

  // Group items by bin color
  const groupedByBin = result.items.reduce((acc, item, index) => {
    const binColor = item.binColor.toLowerCase();
    if (!acc[binColor]) {
      acc[binColor] = [];
    }
    acc[binColor].push({ ...item, originalIndex: index });
    return acc;
  }, {} as Record<string, Array<ClassificationResult & { originalIndex: number }>>);

  // Summary statistics
  const binCounts = Object.entries(groupedByBin).map(([color, items]) => ({
    color,
    count: items.length,
    binName: items[0].bin,
  }));

  return (
    <div className="space-y-6">
      {/* Summary Header */}
      <div className="bg-gradient-to-r from-blue-50 to-green-50 rounded-lg p-6 border-2 border-blue-200">
        <h2 className="text-2xl font-bold mb-2 text-gray-900">
          Classification Results
        </h2>
        <p className="text-lg text-gray-700 mb-4">
          Found <span className="font-bold text-blue-600">{result.total_items}</span> item{result.total_items !== 1 ? 's' : ''} 
          {' '}from {result.input_type} input
        </p>
        
        {/* Bin Summary */}
        {binCounts.length > 0 && (
          <div className="flex flex-wrap gap-2">
            {binCounts.map(({ color, count, binName }) => {
              const colorScheme = binColorMap[color] || binColorMap.other;
              return (
                <span
                  key={color}
                  className={`px-3 py-1 rounded-full text-sm font-semibold ${colorScheme.bg} ${colorScheme.text} border ${colorScheme.border}`}
                >
                  {count} × {binName.split('(')[0].trim()}
                </span>
              );
            })}
          </div>
        )}
      </div>

      {/* Grouped Results */}
      {Object.entries(groupedByBin).map(([binColor, items]) => {
        const colorScheme = binColorMap[binColor] || binColorMap.other;
        return (
          <div key={binColor} className="space-y-3">
            <h3 className={`text-lg font-semibold ${colorScheme.text} flex items-center`}>
              <span className={`w-4 h-4 rounded-full ${colorScheme.bg} border-2 ${colorScheme.border} mr-2`}></span>
              {items[0].bin} ({items.length} item{items.length !== 1 ? 's' : ''})
            </h3>
            
            <div className="space-y-3">
              {items.map((item, groupIndex) => {
                const originalIndex = item.originalIndex;
                const isExpanded = expandedItems.has(originalIndex);
                
                return (
                  <div
                    key={originalIndex}
                    className={`rounded-lg border-2 ${colorScheme.border} ${colorScheme.bg} overflow-hidden transition-all`}
                  >
                    <div
                      className="p-4 cursor-pointer hover:opacity-90"
                      onClick={() => toggleExpand(originalIndex)}
                    >
                      <div className="flex items-center justify-between">
                        <div className="flex-1">
                          <h4 className="font-semibold text-gray-900">{item.item}</h4>
                          <p className="text-sm text-gray-600 capitalize mt-1">
                            Category: {item.category}
                          </p>
                        </div>
                        <div className="flex items-center space-x-2">
                          {item.confidence && (
                            <span className="text-xs text-gray-500">
                              {(item.confidence * 100).toFixed(0)}%
                            </span>
                          )}
                          <svg
                            className={`w-5 h-5 text-gray-600 transition-transform ${
                              isExpanded ? 'transform rotate-180' : ''
                            }`}
                            fill="none"
                            stroke="currentColor"
                            viewBox="0 0 24 24"
                          >
                            <path
                              strokeLinecap="round"
                              strokeLinejoin="round"
                              strokeWidth={2}
                              d="M19 9l-7 7-7-7"
                            />
                          </svg>
                        </div>
                      </div>
                    </div>
                    
                    {isExpanded && (
                      <div className="px-4 pb-4 border-t border-gray-300 pt-3 mt-2">
                        <p className="text-sm text-gray-700">
                          <span className="font-medium">Explanation:</span> {item.explanation}
                        </p>
                        {item.bbox && (
                          <p className="text-xs text-gray-500 mt-2">
                            Location detected in image
                          </p>
                        )}
                      </div>
                    )}
                  </div>
                );
              })}
            </div>
          </div>
        );
      })}

      {/* Single Item Fallback Display */}
      {result.items.length === 1 && (
        <div className={`rounded-lg border-2 ${binColorMap[result.items[0].binColor.toLowerCase()]?.border || binColorMap.other.border} ${binColorMap[result.items[0].binColor.toLowerCase()]?.bg || binColorMap.other.bg} p-6`}>
          <h3 className="text-xl font-bold mb-4 text-gray-900">Item Details</h3>
          <div className="space-y-3">
            <div>
              <span className="text-sm font-medium text-gray-600">Item:</span>
              <p className="text-lg font-semibold text-gray-900">{result.items[0].item}</p>
            </div>
            <div>
              <span className="text-sm font-medium text-gray-600">Category:</span>
              <p className="text-lg capitalize text-gray-900">{result.items[0].category}</p>
            </div>
            <div>
              <span className="text-sm font-medium text-gray-600">Bin:</span>
              <p className={`text-lg font-semibold ${binColorMap[result.items[0].binColor.toLowerCase()]?.text || binColorMap.other.text}`}>
                {result.items[0].bin}
              </p>
            </div>
            <div className="pt-3 border-t border-gray-300">
              <span className="text-sm font-medium text-gray-600">Explanation:</span>
              <p className="text-base text-gray-700 mt-1">{result.items[0].explanation}</p>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}

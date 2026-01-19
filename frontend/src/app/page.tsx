'use client';

import { useState } from 'react';
import InputForm from '@/components/InputForm';
import MultiResultDisplay from '@/components/MultiResultDisplay';
import { MultiClassificationResponse } from '@/lib/api';

export default function Home() {
  const [result, setResult] = useState<MultiClassificationResponse | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [isLoading, setIsLoading] = useState(false);

  const handleResult = (classificationResult: MultiClassificationResponse) => {
    setResult(classificationResult);
    setError(null);
  };

  const handleError = (errorMessage: string) => {
    setError(errorMessage);
    setResult(null);
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-blue-50 to-green-50">
      <div className="container mx-auto px-4 py-12 max-w-4xl">
        {/* Header */}
        <div className="text-center mb-12">
          <h1 className="text-4xl font-bold text-gray-900 mb-4">
            Waste Classification System
          </h1>
          <p className="text-lg text-gray-600">
            Classify your waste items for Hong Kong&apos;s waste management system
          </p>
        </div>

        {/* Main Content */}
        <div className="bg-white rounded-lg shadow-lg p-8 mb-8">
          <InputForm
            onResult={handleResult}
            onError={handleError}
            onLoading={setIsLoading}
          />
        </div>

        {/* Error Display */}
        {error && (
          <div className="bg-red-50 border border-red-200 rounded-lg p-4 mb-8">
            <p className="text-red-800">{error}</p>
          </div>
        )}

        {/* Loading Indicator */}
        {isLoading && (
          <div className="bg-blue-50 border border-blue-200 rounded-lg p-4 mb-8 text-center">
            <p className="text-blue-800">Classifying your item...</p>
          </div>
        )}

        {/* Result Display */}
        {result && (
          <div className="bg-white rounded-lg shadow-lg p-8">
            <MultiResultDisplay result={result} />
          </div>
        )}

        {/* Info Section */}
        <div className="mt-12 bg-white rounded-lg shadow-lg p-8">
          <h2 className="text-2xl font-bold text-gray-900 mb-4">Hong Kong Waste Management Guide</h2>
          <div className="space-y-4">
            <p className="text-sm text-gray-600 mb-4">
              Hong Kong uses a three-colour bin system for source separation, plus GREEN@COMMUNITY facilities for additional recyclables.
              <br />
              <span className="text-xs text-gray-500 mt-2 block">
                Reference: Official guidelines from{' '}
                <a 
                  href="https://www.wastereduction.gov.hk/en-hk/recycling-tips" 
                  target="_blank" 
                  rel="noopener noreferrer"
                  className="text-blue-600 hover:underline"
                >
                  Hong Kong Environmental Protection Department (EPD)
                </a>
                {' '}and{' '}
                <a 
                  href="https://www.wastereduction.gov.hk/sites/default/files/one-stop-shop/1_Pager_on_Clean_Recycling_Tips.pdf" 
                  target="_blank" 
                  rel="noopener noreferrer"
                  className="text-blue-600 hover:underline"
                >
                  Clean Recycling Tips (PDF)
                </a>
              </span>
            </p>
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              <div className="border-l-4 border-blue-500 pl-4">
                <h3 className="font-semibold text-blue-800">Blue Bin - Waste Paper</h3>
                <p className="text-sm text-gray-600">
                  <strong>Accepted:</strong> Clean and dry paper only - newspapers, magazines, office paper, cardboard boxes, paper bags, envelopes, books (remove hard covers)
                  <br />
                  <span className="text-red-600 font-medium">Not accepted:</span> Wet/soiled paper, plastic-lined paper (e.g., coffee cups), composite materials, food containers with residue, thermal paper, laminated paper
                  <br />
                  <span className="text-xs text-gray-500">Must be clean, dry, and free of contamination</span>
                </p>
              </div>
              <div className="border-l-4 border-yellow-500 pl-4">
                <h3 className="font-semibold text-yellow-800">Yellow Bin - Metal Cans</h3>
                <p className="text-sm text-gray-600">
                  <strong>Accepted:</strong> Aluminum and metal cans only (beverage cans, food cans). Must be empty, clean, and rinsed
                  <br />
                  <span className="text-red-600 font-medium">Not accepted:</span> Other metal items (scrap metal, large metal objects, metal utensils) - these go to GREEN@COMMUNITY
                  <br />
                  <span className="text-xs text-gray-500">Must be empty, clean, and preferably flattened</span>
                </p>
              </div>
              <div className="border-l-4 border-amber-500 pl-4">
                <h3 className="font-semibold text-amber-800">Brown Bin - Plastic Bottles</h3>
                <p className="text-sm text-gray-600">
                  <strong>Accepted:</strong> Plastic bottles only (PET #1, HDPE #2). Must be empty and clean
                  <br />
                  <span className="text-red-600 font-medium">Not accepted:</span> Other plastics (containers, bags, toys, styrofoam, utensils, packaging) - these go to GREEN@COMMUNITY or general waste
                  <br />
                  <span className="text-xs text-gray-500">Must be empty, clean, rinsed. Remove caps if different material</span>
                </p>
              </div>
              <div className="border-l-4 border-green-500 pl-4">
                <h3 className="font-semibold text-green-800">GREEN@COMMUNITY</h3>
                <p className="text-sm text-gray-600">
                  <strong>Designated collection points</strong> (NOT the three-colour bins) for: Glass bottles/containers (clean), small electronics, all types of batteries, beverage cartons (Tetra Pak), fluorescent lamps/tubes, and other recyclables not accepted in three-colour bins
                  <br />
                  <span className="text-xs text-gray-500">Take to designated GREEN@COMMUNITY facilities</span>
                </p>
              </div>
            </div>
            <div className="mt-4 p-4 bg-gray-50 rounded-lg">
              <h4 className="font-semibold text-gray-900 mb-2">Important Notes (from EPD Clean Recycling Tips):</h4>
              <ul className="text-sm text-gray-600 space-y-1 list-disc list-inside">
                <li>Items for three-colour bins MUST be clean and dry - contamination can ruin entire batches</li>
                <li>Rinse containers before recycling (especially food containers)</li>
                <li>Remove labels, caps, and non-recyclable components when possible</li>
                <li>Contaminated items go to general waste - do not put contaminated items in recycling bins</li>
                <li>Many recyclables (glass, electronics, cartons, most plastics) require GREEN@COMMUNITY facilities, NOT the three-colour bins</li>
                <li>Composite materials (e.g., plastic-lined paper cups) should be separated if possible, otherwise often go to general waste</li>
                <li>Do not put items in plastic bags when placing in bins - place items directly in bins</li>
                <li>When in doubt, check with your building management or visit a GREEN@COMMUNITY station</li>
              </ul>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}

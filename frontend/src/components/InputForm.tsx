'use client';

import { useState, useRef } from 'react';
import { classifyItem, convertFileToBase64, MultiClassificationResponse } from '@/lib/api';

interface InputFormProps {
  onResult: (result: MultiClassificationResponse) => void;
  onError: (error: string) => void;
  onLoading: (loading: boolean) => void;
}

type InputType = 'image' | 'text';

export default function InputForm({ onResult, onError, onLoading }: InputFormProps) {
  const [inputType, setInputType] = useState<InputType>('text');
  const [text, setText] = useState('');
  const [image, setImage] = useState<File | null>(null);
  const [imagePreview, setImagePreview] = useState<string | null>(null);
  const [isLoading, setIsLoading] = useState(false);
  const fileInputRef = useRef<HTMLInputElement>(null);

  const handleInputTypeChange = (type: InputType) => {
    setInputType(type);
    // Clear the other input when switching
    if (type === 'image') {
      setText('');
    } else {
      setImage(null);
      setImagePreview(null);
      if (fileInputRef.current) {
        fileInputRef.current.value = '';
      }
    }
  };

  const handleImageChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0];
    if (file) {
      setImage(file);
      const reader = new FileReader();
      reader.onloadend = () => {
        setImagePreview(reader.result as string);
      };
      reader.readAsDataURL(file);
    }
  };

  const handleRemoveImage = () => {
    setImage(null);
    setImagePreview(null);
    if (fileInputRef.current) {
      fileInputRef.current.value = '';
    }
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();

    if (inputType === 'image' && !image) {
      onError('Please upload an image');
      return;
    }

    if (inputType === 'text' && !text.trim()) {
      onError('Please enter a text description');
      return;
    }

    setIsLoading(true);
    onLoading(true);

    try {
      let imageBase64: string | undefined;
      let textInput: string | undefined;

      if (inputType === 'image' && image) {
        imageBase64 = await convertFileToBase64(image);
      } else if (inputType === 'text' && text) {
        textInput = text.trim();
      }

      const result = await classifyItem({
        image: imageBase64,
        text: textInput,
      });

      onResult(result);
    } catch (error) {
      onError(error instanceof Error ? error.message : 'Failed to classify item');
    } finally {
      setIsLoading(false);
      onLoading(false);
    }
  };

  const handleReset = () => {
    setText('');
    setImage(null);
    setImagePreview(null);
    if (fileInputRef.current) {
      fileInputRef.current.value = '';
    }
  };

  return (
    <form onSubmit={handleSubmit} className="space-y-6">
      {/* Input Type Selection - Radio Button Style Switch */}
      <div className="bg-gray-50 p-4 rounded-lg border-2 border-gray-200">
        <label className="block text-sm font-semibold text-gray-900 mb-3">
          ⚠️ Choose ONE Input Method Only
        </label>
        <p className="text-xs text-gray-600 mb-4">
          You can use either text description OR image upload, but not both at the same time.
        </p>
        <div className="flex space-x-3">
          <label className="flex-1 cursor-pointer">
            <input
              type="radio"
              name="inputType"
              value="text"
              checked={inputType === 'text'}
              onChange={() => handleInputTypeChange('text')}
              className="sr-only"
            />
            <div
              className={`px-4 py-3 rounded-lg border-2 transition-all text-center ${
                inputType === 'text'
                  ? 'border-blue-500 bg-blue-50 text-blue-700 font-semibold shadow-md ring-2 ring-blue-200'
                  : 'border-gray-300 bg-white text-gray-700 hover:bg-gray-50 hover:border-gray-400'
              }`}
            >
              <div className="flex items-center justify-center space-x-2">
                <span className="text-xl">📝</span>
                <span>Text Description</span>
              </div>
            </div>
          </label>
          <label className="flex-1 cursor-pointer">
            <input
              type="radio"
              name="inputType"
              value="image"
              checked={inputType === 'image'}
              onChange={() => handleInputTypeChange('image')}
              className="sr-only"
            />
            <div
              className={`px-4 py-3 rounded-lg border-2 transition-all text-center ${
                inputType === 'image'
                  ? 'border-blue-500 bg-blue-50 text-blue-700 font-semibold shadow-md ring-2 ring-blue-200'
                  : 'border-gray-300 bg-white text-gray-700 hover:bg-gray-50 hover:border-gray-400'
              }`}
            >
              <div className="flex items-center justify-center space-x-2">
                <span className="text-xl">🖼️</span>
                <span>Upload Image</span>
              </div>
            </div>
          </label>
        </div>
      </div>

      {/* Text Input - Only shown when text is selected */}
      {inputType === 'text' ? (
        <div className="space-y-2">
          <label htmlFor="text" className="block text-sm font-medium text-gray-700">
            Text Description <span className="text-red-500">*</span>
          </label>
          <p className="text-xs text-gray-500 mb-2">
            Enter one or more items separated by commas (e.g., &quot;a can, a bottle, and a newspaper&quot;)
          </p>
          <textarea
            id="text"
            value={text}
            onChange={(e) => setText(e.target.value)}
            placeholder="e.g., a crumpled soda can, a plastic bottle, and an old newspaper"
            rows={4}
            className="block w-full rounded-md border-gray-300 shadow-sm focus:border-blue-500 focus:ring-blue-500 sm:text-sm"
            required
            disabled={inputType !== 'text'}
          />
        </div>
      ) : null}

      {/* Image Upload - Only shown when image is selected */}
      {inputType === 'image' ? (
        <div className="space-y-2">
          <label className="block text-sm font-medium text-gray-700">
            Upload Image <span className="text-red-500">*</span>
          </label>
          <p className="text-xs text-gray-500 mb-2">
                    Upload an image containing one or more waste items
          </p>
          <div className="mt-1 flex items-center space-x-4">
            <div className="flex-1">
              <input
                ref={fileInputRef}
                type="file"
                accept="image/*"
                onChange={handleImageChange}
                className="block w-full text-sm text-gray-500 file:mr-4 file:py-2 file:px-4 file:rounded-md file:border-0 file:text-sm file:font-semibold file:bg-blue-50 file:text-blue-700 hover:file:bg-blue-100"
                required
                disabled={inputType !== 'image'}
              />
            </div>
            {imagePreview && (
              <div className="relative">
                {/* eslint-disable-next-line @next/next/no-img-element */}
                <img
                  src={imagePreview}
                  alt="Preview"
                  className="h-20 w-20 object-cover rounded-md border-2 border-gray-300"
                />
                <button
                  type="button"
                  onClick={handleRemoveImage}
                  className="absolute -top-2 -right-2 bg-red-500 text-white rounded-full w-6 h-6 flex items-center justify-center text-xs hover:bg-red-600"
                >
                  ×
                </button>
              </div>
            )}
          </div>
        </div>
      ) : null}

      {/* Buttons */}
      <div className="flex space-x-4">
        <button
          type="submit"
          disabled={isLoading || (inputType === 'text' && !text.trim()) || (inputType === 'image' && !image)}
          className="flex-1 bg-blue-600 text-white px-4 py-2 rounded-md hover:bg-blue-700 disabled:bg-gray-400 disabled:cursor-not-allowed transition-colors"
        >
          {isLoading ? 'Classifying...' : 'Classify Item'}
        </button>
        <button
          type="button"
          onClick={handleReset}
          disabled={isLoading}
          className="px-4 py-2 border border-gray-300 rounded-md text-gray-700 hover:bg-gray-50 disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
        >
          Reset
        </button>
      </div>
    </form>
  );
}

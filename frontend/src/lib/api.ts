/** API client for backend communication. */

const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';

export interface ClassificationRequest {
  image?: string;
  text?: string;
}

export interface ClassificationResult {
  item: string;
  category: string;
  bin: string;
  binColor: string;
  explanation: string;
  confidence?: number;
  bbox?: {
    coordinates?: number[];
  };
}

export interface MultiClassificationResponse {
  items: ClassificationResult[];
  total_items: number;
  input_type: 'text' | 'image';
}

// Backward compatibility
export interface ClassificationResponse extends ClassificationResult {}

export async function classifyItem(
  request: ClassificationRequest
): Promise<MultiClassificationResponse> {
  const response = await fetch(`${API_BASE_URL}/api/classify`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify(request),
  });

  if (!response.ok) {
    const error = await response.json().catch(() => ({ detail: 'Unknown error' }));
    throw new Error(error.detail || `HTTP error! status: ${response.status}`);
  }

  return response.json();
}

export function convertFileToBase64(file: File): Promise<string> {
  return new Promise((resolve, reject) => {
    const reader = new FileReader();
    reader.onload = () => {
      const result = reader.result as string;
      // Remove data URL prefix if present
      const base64 = result.includes(',') ? result.split(',')[1] : result;
      resolve(base64);
    };
    reader.onerror = reject;
    reader.readAsDataURL(file);
  });
}

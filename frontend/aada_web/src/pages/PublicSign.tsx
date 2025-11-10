import { useState, useEffect, useRef } from 'react';
import { useParams } from 'react-router-dom';
import SignatureCanvas from 'react-signature-canvas';
import axios from 'axios';

import { resolveApiBaseUrl } from '@/utils/apiBase';

const API_BASE_URL = `${resolveApiBaseUrl()}/api`;

interface DocumentData {
  template_name?: string;
  template_description?: string;
  signer_name?: string;
  signer_email?: string;
  expires_at?: string;
}

export default function PublicSign() {
  const { token } = useParams();
  const sigPad = useRef<SignatureCanvas | null>(null);

  const [loading, setLoading] = useState(true);
  const [document, setDocument] = useState<DocumentData | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [typedName, setTypedName] = useState('');
  const [signing, setSigning] = useState(false);
  const [signed, setSigned] = useState(false);
  const [signatureError, setSignatureError] = useState('');

  // Fetch document details
  useEffect(() => {
    const fetchDocument = async () => {
      try {
        setLoading(true);
        const response = await axios.get(`${API_BASE_URL}/public/sign/${token}`);
        setDocument(response.data);
        setTypedName(response.data.signer_name || '');
      } catch (err: any) {
        if (err.response?.status === 404) {
          setError('Document not found or link has expired');
        } else if (err.response?.status === 429) {
          setError('Too many requests. Please try again later.');
        } else if (err.response?.status === 400 && err.response?.data?.detail?.includes('already been signed')) {
          setError('This document has already been signed');
        } else {
          setError('Failed to load document. Please check your link and try again.');
        }
      } finally {
        setLoading(false);
      }
    };

    if (token) {
      fetchDocument();
    } else {
      setError('Invalid signing link');
      setLoading(false);
    }
  }, [token]);

  const clearSignature = () => {
    sigPad.current?.clear();
    setSignatureError('');
  };

  const handleSubmit = async (e: React.FormEvent<HTMLFormElement>) => {
    e.preventDefault();
    setSignatureError('');

    // Validate typed name
    if (!typedName.trim()) {
      setSignatureError('Please type your full name');
      return;
    }

    // Validate signature exists
    if (sigPad.current?.isEmpty()) {
      setSignatureError('Please provide your signature');
      return;
    }

    try {
      setSigning(true);

      // Get signature as base64
      const signatureData = sigPad.current?.toDataURL()?.split(',')[1]; // Remove data:image/png;base64, prefix

      // Submit signature
      await axios.post(`${API_BASE_URL}/public/sign/${token}`, {
        signature_data: signatureData,
        typed_name: typedName.trim()
      });

      setSigned(true);

      // Show success message briefly, then redirect or show completion
      setTimeout(() => {
        // Could redirect to a thank you page or show final status
      }, 2000);

    } catch (err: any) {
      if (err.response?.status === 400) {
        setSignatureError(err.response.data?.detail || 'Invalid signature data');
      } else if (err.response?.status === 404) {
        setSignatureError('Document not found or link has expired');
      } else if (err.response?.status === 429) {
        setSignatureError('Too many requests. Please try again later.');
      } else {
        setSignatureError('Failed to submit signature. Please try again.');
      }
    } finally {
      setSigning(false);
    }
  };

  if (loading) {
    return (
      <div className="min-h-screen flex items-center justify-center bg-gray-50">
        <div className="text-center">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600 mx-auto mb-4"></div>
          <p className="text-gray-600">Loading document...</p>
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="min-h-screen flex items-center justify-center bg-gray-50">
        <div className="max-w-md w-full bg-white shadow-lg rounded-lg p-8">
          <div className="text-center">
            <svg className="mx-auto h-12 w-12 text-red-500" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z" />
            </svg>
            <h2 className="mt-4 text-xl font-semibold text-gray-900">Unable to Load Document</h2>
            <p className="mt-2 text-gray-600">{error}</p>
            <p className="mt-4 text-sm text-gray-500">
              If you believe this is an error, please contact the school administrator.
            </p>
          </div>
        </div>
      </div>
    );
  }

  if (signed) {
    return (
      <div className="min-h-screen flex items-center justify-center bg-gray-50">
        <div className="max-w-md w-full bg-white shadow-lg rounded-lg p-8">
          <div className="text-center">
            <svg className="mx-auto h-12 w-12 text-green-500" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z" />
            </svg>
            <h2 className="mt-4 text-xl font-semibold text-gray-900">Document Signed Successfully!</h2>
            <p className="mt-2 text-gray-600">
              Your signature has been recorded and the document has been completed.
            </p>
            {document?.template_name && (
              <p className="mt-4 text-sm text-gray-500">
                Document: {document.template_name}
              </p>
            )}
            <div className="mt-6 bg-blue-50 border border-blue-200 rounded-lg p-4">
              <p className="text-sm text-blue-800">
                <strong>What's next?</strong>
              </p>
              <p className="text-sm text-blue-700 mt-1">
                You will receive a copy of the signed document via email. A school representative will contact you regarding next steps.
              </p>
            </div>
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gray-50 py-12 px-4 sm:px-6 lg:px-8">
      <div className="max-w-3xl mx-auto">
        {/* Header */}
        <div className="bg-white shadow rounded-lg mb-6 p-6">
          <div className="flex items-center justify-between">
            <div>
              <h1 className="text-2xl font-bold text-gray-900">
                {document?.template_name || 'Document Signature'}
              </h1>
              {document?.template_description && (
                <p className="mt-1 text-sm text-gray-500">{document.template_description}</p>
              )}
            </div>
            <div className="flex-shrink-0">
              <span className="inline-flex items-center px-3 py-1 rounded-full text-sm font-medium bg-yellow-100 text-yellow-800">
                Pending Signature
              </span>
            </div>
          </div>

          {/* Signer Info */}
          <div className="mt-4 pt-4 border-t border-gray-200">
            <dl className="grid grid-cols-1 gap-4 sm:grid-cols-2">
              <div>
                <dt className="text-sm font-medium text-gray-500">Signer Name</dt>
                <dd className="mt-1 text-sm text-gray-900">{document?.signer_name}</dd>
              </div>
              <div>
                <dt className="text-sm font-medium text-gray-500">Email</dt>
                <dd className="mt-1 text-sm text-gray-900">{document?.signer_email}</dd>
              </div>
              {document?.expires_at && (
                <div>
                  <dt className="text-sm font-medium text-gray-500">Link Expires</dt>
                  <dd className="mt-1 text-sm text-gray-900">
                    {new Date(document.expires_at).toLocaleDateString()}
                  </dd>
                </div>
              )}
            </dl>
          </div>
        </div>

        {/* Document Preview (if available) */}
        {/* TODO: Add PDF preview iframe when preview endpoint is implemented */}

        {/* Signature Form */}
        <div className="bg-white shadow rounded-lg p-6">
          <h2 className="text-lg font-medium text-gray-900 mb-4">Sign Document</h2>

          <form onSubmit={handleSubmit} className="space-y-6">
            {/* Typed Name */}
            <div>
              <label htmlFor="typedName" className="block text-sm font-medium text-gray-700">
                Type Your Full Name <span className="text-red-500">*</span>
              </label>
              <p className="mt-1 text-sm text-gray-500">
                By typing your name, you agree that this constitutes a legal signature.
              </p>
              <input
                type="text"
                id="typedName"
                value={typedName}
                onChange={(e) => setTypedName(e.target.value)}
                className="mt-2 block w-full border border-gray-300 rounded-md shadow-sm py-2 px-3 focus:outline-none focus:ring-blue-500 focus:border-blue-500"
                placeholder="Enter your full name"
                required
              />
            </div>

            {/* Signature Pad */}
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Draw Your Signature <span className="text-red-500">*</span>
              </label>
              <div className="border-2 border-gray-300 rounded-lg bg-white">
                <SignatureCanvas
                  ref={sigPad}
                  canvasProps={{
                    className: 'w-full h-48 cursor-crosshair',
                  }}
                  backgroundColor="white"
                />
              </div>
              <div className="mt-2 flex justify-between items-center">
                <p className="text-sm text-gray-500">Sign above using your mouse or touchscreen</p>
                <button
                  type="button"
                  onClick={clearSignature}
                  className="text-sm text-blue-600 hover:text-blue-700 font-medium"
                >
                  Clear Signature
                </button>
              </div>
            </div>

            {/* Legal Notice */}
            <div className="bg-gray-50 border border-gray-200 rounded-lg p-4">
              <p className="text-sm text-gray-700">
                <strong>Electronic Signature Consent:</strong> By clicking "Sign Document" below,
                I agree that my typed name and drawn signature are the electronic representation of my signature
                and have the same legal force and effect as a handwritten signature.
              </p>
            </div>

            {/* Error Message */}
            {signatureError && (
              <div className="bg-red-50 border border-red-200 rounded-lg p-4">
                <p className="text-sm text-red-700">{signatureError}</p>
              </div>
            )}

            {/* Submit Button */}
            <div className="flex justify-end space-x-3">
              <button
                type="button"
                onClick={() => window.close()}
                className="px-4 py-2 border border-gray-300 rounded-md shadow-sm text-sm font-medium text-gray-700 bg-white hover:bg-gray-50 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500"
              >
                Cancel
              </button>
              <button
                type="submit"
                disabled={signing}
                className="px-4 py-2 border border-transparent rounded-md shadow-sm text-sm font-medium text-white bg-blue-600 hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500 disabled:opacity-50 disabled:cursor-not-allowed"
              >
                {signing ? (
                  <>
                    <span className="inline-block animate-spin mr-2">⏳</span>
                    Signing...
                  </>
                ) : (
                  'Sign Document'
                )}
              </button>
            </div>
          </form>
        </div>

        {/* Footer */}
        <div className="mt-6 text-center">
          <p className="text-sm text-gray-500">
            This is a secure document signing process. Your signature is encrypted and legally binding.
          </p>
        </div>
      </div>
    </div>
  );
}

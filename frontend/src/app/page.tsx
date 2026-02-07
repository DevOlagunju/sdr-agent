'use client';

import { useState, useEffect } from 'react';
import axios from 'axios';

const API_URL = 'http://localhost:8000';

interface ResearchResult {
  company_domain: string;
  research: {
    company_name: string;
    industry: string;
    description: string;
    products?: string[];
    recent_news?: string;
    key_highlights?: string[];
  };
  lead: {
    status: string;
    lead_id: number;
    company_domain: string;
    company_name: string;
  };
  email: {
    subject: string;
    body: string;
  };
  status: string;
}

interface Lead {
  id: number;
  company_domain: string;
  company_name: string;
  industry: string;
  description: string;
  research_summary?: string;
  created_at: string;
  updated_at?: string;
}

interface Email {
  id: number;
  lead_id: number;
  subject: string;
  body: string;
  status: string;
  created_at: string;
  sent_at: string | null;
}

export default function Home() {
  const [companyDomain, setCompanyDomain] = useState('');
  const [loading, setLoading] = useState(false);
  const [result, setResult] = useState<ResearchResult | null>(null);
  const [error, setError] = useState('');
  const [leads, setLeads] = useState<Lead[]>([]);
  const [showCRM, setShowCRM] = useState(true);
  const [expandedLeadId, setExpandedLeadId] = useState<number | null>(null);
  const [leadEmails, setLeadEmails] = useState<{ [key: number]: Email[] }>({});

  // Auto-load leads when page opens
  useEffect(() => {
    loadLeads();
  }, []);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setLoading(true);
    setError('');
    setResult(null);

    try {
      const response = await axios.post<ResearchResult>(`${API_URL}/api/research`, {
        company_domain: companyDomain,
      });
      setResult(response.data);
      // Auto-load leads after generating email
      loadLeads();
    } catch (err: any) {
      setError(err.response?.data?.detail || 'An error occurred. Please check if the backend is running.');
    } finally {
      setLoading(false);
    }
  };

  const loadLeads = async () => {
    try {
      const response = await axios.get<Lead[]>(`${API_URL}/api/leads`);
      setLeads(response.data);
    } catch (err: any) {
      console.error('Failed to load leads');
    }
  };

  const loadLeadEmails = async (leadId: number) => {
    try {
      const response = await axios.get<Email[]>(`${API_URL}/api/leads/${leadId}/emails`);
      setLeadEmails(prev => ({ ...prev, [leadId]: response.data }));
    } catch (err: any) {
      console.error('Failed to load emails for lead:', leadId);
    }
  };

  const handleLeadClick = (leadId: number) => {
    const isExpanding = expandedLeadId !== leadId;
    setExpandedLeadId(isExpanding ? leadId : null);
    
    // Load emails when expanding a lead
    if (isExpanding && !leadEmails[leadId]) {
      loadLeadEmails(leadId);
    }
  };

  const deleteLead = async (leadId: number) => {
    if (!confirm('Are you sure you want to delete this lead?')) {
      return;
    }
    
    try {
      await axios.delete(`${API_URL}/api/leads/${leadId}`);
      // Remove lead from local state
      setLeads(leads.filter(lead => lead.id !== leadId));
      // Remove emails from state
      const newLeadEmails = { ...leadEmails };
      delete newLeadEmails[leadId];
      setLeadEmails(newLeadEmails);
    } catch (err: any) {
      alert('Failed to delete lead: ' + (err.response?.data?.detail || 'Unknown error'));
    }
  };

  return (
    <div className="min-h-screen bg-gray-50 py-8 px-4 sm:px-6 lg:px-8">
      <div className="max-w-7xl mx-auto">
        {/* Header */}
        <div className="text-center mb-8">
          <h1 className="text-4xl font-bold text-gray-900 mb-2">
            SDR Agent
          </h1>
          <p className="text-gray-600">
            AI-powered Sales Development Representative
          </p>
        </div>

        {/* CRM Toggle Button */}
        <div className="flex justify-end mb-4">
          <button
            onClick={() => setShowCRM(!showCRM)}
            className="flex items-center gap-2 px-4 py-2 bg-white border border-gray-300 text-gray-700 rounded-lg font-medium hover:bg-gray-50 transition-colors shadow-sm"
          >
            {showCRM ? (
              <>
                <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13.875 18.825A10.05 10.05 0 0112 19c-4.478 0-8.268-2.943-9.543-7a9.97 9.97 0 011.563-3.029m5.858.908a3 3 0 114.243 4.243M9.878 9.878l4.242 4.242M9.88 9.88l-3.29-3.29m7.532 7.532l3.29 3.29M3 3l3.59 3.59m0 0A9.953 9.953 0 0112 5c4.478 0 8.268 2.943 9.543 7a10.025 10.025 0 01-4.132 5.411m0 0L21 21" />
                </svg>
                Hide CRM
              </>
            ) : (
              <>
                <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M15 12a3 3 0 11-6 0 3 3 0 016 0z" />
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M2.458 12C3.732 7.943 7.523 5 12 5c4.478 0 8.268 2.943 9.542 7-1.274 4.057-5.064 7-9.542 7-4.477 0-8.268-2.943-9.542-7z" />
                </svg>
                View CRM
              </>
            )}
          </button>
        </div>

        {/* Two Column Layout */}
        <div className={`grid grid-cols-1 gap-6 ${showCRM ? 'lg:grid-cols-2' : ''}`}>
          {/* Left Column - Generate Email */}
          <div className="space-y-6">
            <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-6">
              <h2 className="text-lg font-semibold text-gray-900 mb-4">Generate Email</h2>
              <form onSubmit={handleSubmit} className="space-y-4">
                <div>
                  <label htmlFor="domain" className="block text-sm font-medium text-gray-700 mb-2">
                    Company Domain
                  </label>
                  <input
                    type="text"
                    id="domain"
                    value={companyDomain}
                    onChange={(e) => setCompanyDomain(e.target.value)}
                    placeholder="e.g., openai.com"
                    className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500 text-gray-900"
                    required
                  />
                </div>

                <button
                  type="submit"
                  disabled={loading}
                  className="w-full bg-blue-600 text-white px-6 py-3 rounded-lg font-medium hover:bg-blue-700 disabled:bg-gray-400 disabled:cursor-not-allowed transition-colors"
                >
                  {loading ? 'Processing...' : 'Generate Email'}
                </button>
              </form>

              {error && (
                <div className="mt-4 p-4 bg-red-50 border border-red-200 text-red-700 rounded-lg">
                  <p className="text-sm">{error}</p>
                </div>
              )}
            </div>

            {/* Results */}
            {result && (
              <div className="space-y-6">
                {/* Research Results */}
                <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-6">
                  <h2 className="text-xl font-semibold text-gray-900 mb-4">Research Results</h2>
                  
                  <div className="space-y-4">
                    <div>
                      <p className="text-sm text-gray-600 mb-1">Company</p>
                      <p className="text-lg font-medium text-gray-900">{result.research.company_name}</p>
                    </div>

                    <div>
                      <p className="text-sm text-gray-600 mb-1">Industry</p>
                      <p className="text-lg font-medium text-gray-900">{result.research.industry}</p>
                    </div>

                    <div>
                      <p className="text-sm text-gray-600 mb-1">Description</p>
                      <p className="text-gray-700">{result.research.description}</p>
                    </div>

                    {result.research.key_highlights && result.research.key_highlights.length > 0 && (
                      <div>
                        <p className="text-sm text-gray-600 mb-2">Key Highlights</p>
                        <ul className="space-y-2">
                          {result.research.key_highlights.map((highlight, idx) => (
                            <li key={idx} className="flex items-start gap-2 text-gray-700">
                              <span className="text-blue-600 mt-1">•</span>
                              <span>{highlight}</span>
                            </li>
                          ))}
                        </ul>
                      </div>
                    )}
                  </div>
                </div>

                {/* CRM Status */}
                <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-6">
                  <h2 className="text-xl font-semibold text-gray-900 mb-4">CRM Status</h2>
                  <div className="flex items-center gap-4">
                    <div>
                      <p className="text-sm text-gray-600">Status</p>
                      <p className="text-lg font-medium text-green-600 capitalize">{result.lead.status}</p>
                    </div>
                    <div>
                      <p className="text-sm text-gray-600">Lead ID</p>
                      <p className="text-lg font-medium text-gray-900">#{result.lead.lead_id}</p>
                    </div>
                  </div>
                </div>

                {/* Generated Email */}
                <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-6">
                  <h2 className="text-xl font-semibold text-gray-900 mb-4">Generated Email</h2>
                  
                  <div className="space-y-4">
                    <div>
                      <p className="text-sm text-gray-600 mb-1">Subject</p>
                      <p className="text-lg font-medium text-gray-900">{result.email.subject}</p>
                    </div>
                    
                    <div>
                      <div className="bg-gray-50 p-4 rounded-lg border border-gray-200">
                        <p className="text-gray-700 whitespace-pre-wrap">{result.email.body}</p>
                      </div>
                    </div>

                    <div className="bg-green-50 border border-green-200 p-4 rounded-lg">
                      <p className="text-green-700 font-medium">✓ Email sent successfully</p>
                    </div>
                  </div>
                </div>
              </div>
            )}
          </div>

          {/* Right Column - CRM Leads */}
          {showCRM && (
            <div className="transition-all duration-300">
              <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-6 sticky top-8">
              <div className="mb-4">
                <h2 className="text-lg font-semibold text-gray-900">CRM Leads</h2>
                <p className="text-xs text-gray-500 mt-1">{leads.length} {leads.length === 1 ? 'lead' : 'leads'}</p>
              </div>
              
              <div className="max-h-[calc(100vh-200px)] overflow-y-auto pr-2">
                {leads.length === 0 ? (
                  <div className="text-center py-12">
                    <svg className="w-12 h-12 text-gray-400 mx-auto mb-3" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M20 13V6a2 2 0 00-2-2H6a2 2 0 00-2 2v7m16 0v5a2 2 0 01-2 2H6a2 2 0 01-2-2v-5m16 0h-2.586a1 1 0 00-.707.293l-2.414 2.414a1 1 0 01-.707.293h-3.172a1 1 0 01-.707-.293l-2.414-2.414A1 1 0 006.586 13H4" />
                    </svg>
                    <p className="text-gray-500 text-sm">No leads yet</p>
                    <p className="text-gray-400 text-xs mt-1">Generate an email to get started</p>
                  </div>
                ) : (
                  <div className="space-y-3">
                    {leads.map((lead) => {
                      const isExpanded = expandedLeadId === lead.id;
                      return (
                        <div 
                          key={lead.id} 
                          className="border border-gray-200 rounded-lg bg-white hover:border-blue-300 hover:shadow-sm transition-all group"
                        >
                          {/* Clickable Header */}
                          <div 
                            className="p-4 cursor-pointer"
                            onClick={() => handleLeadClick(lead.id)}
                          >
                            <div className="flex justify-between items-start mb-2">
                              <div className="flex-1">
                                <div className="flex items-center gap-2">
                                  <h3 className="text-sm font-semibold text-gray-900">{lead.company_name}</h3>
                                  <svg 
                                    className={`w-4 h-4 text-gray-400 transition-transform ${isExpanded ? 'rotate-180' : ''}`} 
                                    fill="none" 
                                    stroke="currentColor" 
                                    viewBox="0 0 24 24"
                                  >
                                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 9l-7 7-7-7" />
                                  </svg>
                                </div>
                                <p className="text-xs text-gray-600 mt-0.5">{lead.company_domain}</p>
                              </div>
                              <div className="flex items-center gap-2">
                                <span className="text-xs text-gray-500 bg-gray-100 px-2 py-1 rounded">#{lead.id}</span>
                                <button
                                  onClick={(e) => {
                                    e.stopPropagation();
                                    deleteLead(lead.id);
                                  }}
                                  className="opacity-0 group-hover:opacity-100 transition-opacity p-1 hover:bg-red-50 rounded text-red-600 hover:text-red-700"
                                  title="Delete lead"
                                >
                                  <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16" />
                                  </svg>
                                </button>
                              </div>
                            </div>
                            <span className="inline-block text-xs text-blue-600 font-medium bg-blue-50 px-2 py-1 rounded mb-2">{lead.industry}</span>
                            {!isExpanded && (
                              <p className="text-gray-700 text-xs mb-2 line-clamp-2">{lead.description}</p>
                            )}
                          </div>

                          {/* Expanded Content */}
                          {isExpanded && (
                            <div className="px-4 pb-4 border-t border-gray-100 pt-3">
                              {/* Full Description */}
                              <div className="mb-3">
                                <p className="text-xs font-semibold text-gray-700 mb-1">Description:</p>
                                <p className="text-xs text-gray-700 leading-relaxed">{lead.description}</p>
                              </div>

                              {/* Research Summary */}
                              {lead.research_summary && (
                                <div className="mb-3 p-3 bg-gray-50 rounded border border-gray-200">
                                  <p className="text-xs font-semibold text-gray-700 mb-2">Research Data:</p>
                                  <div className="text-xs text-gray-600 space-y-1">
                                    {(() => {
                                      try {
                                        const research = JSON.parse(lead.research_summary);
                                        return (
                                          <div className="space-y-1">
                                            {research.company_name && <p><span className="font-medium">Company:</span> {research.company_name}</p>}
                                            {research.industry && <p><span className="font-medium">Industry:</span> {research.industry}</p>}
                                            {research.products && Array.isArray(research.products) && (
                                              <div>
                                                <span className="font-medium">Products:</span>
                                                <ul className="ml-4 mt-1">
                                                  {research.products.map((product: string, idx: number) => (
                                                    <li key={idx} className="list-disc">{product}</li>
                                                  ))}
                                                </ul>
                                              </div>
                                            )}
                                            {research.key_highlights && Array.isArray(research.key_highlights) && (
                                              <div>
                                                <span className="font-medium">Highlights:</span>
                                                <ul className="ml-4 mt-1">
                                                  {research.key_highlights.map((highlight: string, idx: number) => (
                                                    <li key={idx} className="list-disc">{highlight}</li>
                                                  ))}
                                                </ul>
                                              </div>
                                            )}
                                            {research.recent_news && <p><span className="font-medium">Recent News:</span> {research.recent_news}</p>}
                                          </div>
                                        );
                                      } catch {
                                        return <p className="text-xs italic">{lead.research_summary}</p>;
                                      }
                                    })()}
                                  </div>
                                </div>
                              )}

                              {/* Generated Email */}
                              {leadEmails[lead.id] && leadEmails[lead.id].length > 0 && (() => {
                                const email = leadEmails[lead.id][0]; // Get only the first/latest email
                                return (
                                  <div className="mb-3">
                                    <p className="text-xs font-semibold text-gray-700 mb-2">Generated Email:</p>
                                    <div className="p-3 bg-blue-50 rounded border border-blue-200">
                                      <div className="mb-2">
                                        <p className="text-xs font-semibold text-gray-700 mb-1">Subject:</p>
                                        <p className="text-xs text-gray-900 font-medium">{email.subject}</p>
                                      </div>
                                      <div className="mb-2">
                                        <p className="text-xs font-semibold text-gray-700 mb-1">Email:</p>
                                        <div className="text-xs text-gray-800 whitespace-pre-wrap bg-white p-2 rounded border border-blue-100">
                                          {email.body}
                                        </div>
                                      </div>
                                      <div className="flex items-center gap-2 text-xs">
                                        <span className={`px-2 py-0.5 rounded font-medium ${
                                          email.status === 'sent' ? 'bg-green-100 text-green-700' : 'bg-gray-100 text-gray-700'
                                        }`}>
                                          {email.status === 'sent' ? '✓ Sent' : email.status}
                                        </span>
                                        <span className="text-gray-500">
                                          {new Date(email.created_at).toLocaleDateString()}
                                        </span>
                                      </div>
                                    </div>
                                  </div>
                                );
                              })()}

                              {/* Timestamps */}
                              <div className="pt-2 border-t border-gray-200">
                                <p className="text-xs text-gray-500">
                                  <span className="font-medium">Created:</span> {new Date(lead.created_at).toLocaleDateString()} at {new Date(lead.created_at).toLocaleTimeString([], {hour: '2-digit', minute:'2-digit'})}
                                </p>
                              </div>
                            </div>
                          )}
                        </div>
                      );
                    })}
                  </div>
                )}
              </div>
            </div>
            </div>
          )}
        </div>
      </div>
    </div>
  );
}

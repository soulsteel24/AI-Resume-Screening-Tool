import { useState } from 'react';
import { Upload, FileText, CheckCircle, AlertCircle, Loader2, Lightbulb, ArrowRight } from 'lucide-react';

function App() {
  const [file, setFile] = useState(null);
  const [jobDescription, setJobDescription] = useState('');
  const [loading, setLoading] = useState(false);
  const [results, setResults] = useState(null);
  const [error, setError] = useState(null);

  const handleFileChange = (e) => {
    if (e.target.files && e.target.files[0]) {
      setFile(e.target.files[0]);
    }
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    if (!file || !jobDescription) {
      setError("Please provide both a resume and a job description.");
      return;
    }

    setLoading(true);
    setError(null);
    setResults(null);

    const formData = new FormData();
    formData.append('file', file);
    formData.append('job_description', jobDescription);

    try {
      const response = await fetch('http://127.0.0.1:8000/api/v1/analyze', {
        method: 'POST',
        body: formData,
      });

      if (!response.ok) {
        throw new Error('Analysis failed. Please try again.');
      }

      const data = await response.json();
      setResults(data);
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="container">
      <header style={{ textAlign: 'center', marginBottom: '3rem', paddingTop: '2rem' }}>
        <h1>AI Resume Screener</h1>
        <p style={{ color: 'var(--text-secondary)', fontSize: '1.2rem' }}>
          Optimize your resume for any job description using AI-powered analysis.
        </p>
      </header>

      <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(300px, 1fr))', gap: '2rem' }}>
        <div className="card">
          <h2 style={{ marginBottom: '1.5rem', display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
            <FileText size={24} color="var(--accent-primary)" />
            Input Details
          </h2>

          <form onSubmit={handleSubmit} style={{ display: 'flex', flexDirection: 'column', gap: '1.5rem' }}>
            <div>
              <label style={{ display: 'block', marginBottom: '0.5rem', fontWeight: 500 }}>Upload Resume (PDF)</label>
              <div style={{
                border: '2px dashed var(--border-color)',
                borderRadius: 'var(--radius-md)',
                padding: '2rem',
                textAlign: 'center',
                cursor: 'pointer',
                backgroundColor: file ? 'rgba(139, 92, 246, 0.05)' : 'transparent',
                borderColor: file ? 'var(--accent-primary)' : 'var(--border-color)'
              }}
                onClick={() => document.getElementById('file-upload').click()}
              >
                <input
                  id="file-upload"
                  type="file"
                  accept=".pdf"
                  onChange={handleFileChange}
                  style={{ display: 'none' }}
                />
                <Upload size={32} color="var(--text-secondary)" style={{ marginBottom: '1rem' }} />
                <p style={{ color: 'var(--text-secondary)' }}>
                  {file ? file.name : "Click to upload or drag and drop"}
                </p>
              </div>
            </div>

            <div>
              <label style={{ display: 'block', marginBottom: '0.5rem', fontWeight: 500 }}>Job Description</label>
              <textarea
                rows={8}
                placeholder="Paste the job description here..."
                value={jobDescription}
                onChange={(e) => setJobDescription(e.target.value)}
              />
            </div>

            {error && (
              <div style={{
                padding: '1rem',
                backgroundColor: 'rgba(239, 68, 68, 0.1)',
                color: 'var(--error)',
                borderRadius: 'var(--radius-md)',
                display: 'flex',
                alignItems: 'center',
                gap: '0.5rem'
              }}>
                <AlertCircle size={20} />
                {error}
              </div>
            )}

            <button
              type="submit"
              className="btn btn-primary"
              disabled={loading || !file || !jobDescription}
            >
              {loading ? (
                <>
                  <Loader2 size={20} style={{ marginRight: '0.5rem', animation: 'spin 1s linear infinite' }} />
                  Analyzing...
                </>
              ) : (
                "Analyze Match"
              )}
            </button>
          </form>
        </div>

        {results && (
          <div style={{ display: 'flex', flexDirection: 'column', gap: '2rem' }}>
            <div className="card">
              <h2 style={{ marginBottom: '1.5rem', display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
                <CheckCircle size={24} color="var(--success)" />
                Analysis Results
              </h2>

              <div style={{ display: 'flex', flexDirection: 'column', gap: '2rem' }}>
                <div>
                  <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: '0.5rem' }}>
                    <span>Semantic Match Score</span>
                    <span style={{ fontWeight: 700, color: 'var(--accent-primary)' }}>
                      {(results.semantic_score * 100).toFixed(1)}%
                    </span>
                  </div>
                  <div className="progress-bar-container">
                    <div
                      className="progress-bar-fill"
                      style={{ width: `${results.semantic_score * 100}%` }}
                    />
                  </div>
                  <p style={{ fontSize: '0.875rem', color: 'var(--text-secondary)', marginTop: '0.5rem' }}>
                    AI-based similarity between your resume and the job description.
                  </p>
                </div>

                <div>
                  <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: '0.5rem' }}>
                    <span>Keyword Match Score</span>
                    <span style={{ fontWeight: 700, color: 'var(--accent-secondary)' }}>
                      {results.keyword_match_score.toFixed(1)}%
                    </span>
                  </div>
                  <div className="progress-bar-container">
                    <div
                      className="progress-bar-fill"
                      style={{ width: `${results.keyword_match_score}%`, background: 'var(--accent-secondary)' }}
                    />
                  </div>
                </div>

                <div>
                  <h3 style={{ fontSize: '1.1rem', marginBottom: '1rem' }}>Missing Keywords</h3>
                  {results.missing_keywords.length > 0 ? (
                    <div style={{ display: 'flex', flexWrap: 'wrap', gap: '0.5rem' }}>
                      {results.missing_keywords.map((item) => (
                        <span
                          key={item.keyword}
                          className="badge badge-missing"
                          style={item.importance > 1 ? { border: '1px solid var(--error)', fontWeight: 700 } : {}}
                          title={item.importance > 1 ? "High Priority (Frequent in JD)" : ""}
                        >
                          {item.keyword}
                          {item.importance > 1 && <span style={{ marginLeft: '0.25rem', fontSize: '0.7em' }}>🔥</span>}
                        </span>
                      ))}
                    </div>
                  ) : (
                    <p style={{ color: 'var(--success)' }}>Great job! No missing keywords detected.</p>
                  )}
                </div>

                <div>
                  <h3 style={{ fontSize: '1.1rem', marginBottom: '1rem' }}>Detected Keywords</h3>
                  <div style={{ display: 'flex', flexWrap: 'wrap', gap: '0.5rem' }}>
                    {results.detected_keywords.map((keyword) => (
                      <span key={keyword} className="badge">
                        {keyword}
                      </span>
                    ))}
                  </div>
                </div>
              </div>
            </div>

            <div className="card" style={{ borderColor: 'var(--warning)', backgroundColor: 'rgba(245, 158, 11, 0.05)' }}>
              <h2 style={{ marginBottom: '1.5rem', display: 'flex', alignItems: 'center', gap: '0.5rem', color: 'var(--warning)' }}>
                <Lightbulb size={24} />
                Recommendations
              </h2>

              <div style={{ display: 'flex', flexDirection: 'column', gap: '1.5rem' }}>
                {results.missing_keywords.length > 0 && (
                  <div>
                    <h3 style={{ fontSize: '1.1rem', marginBottom: '0.5rem', display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
                      <ArrowRight size={18} color="var(--warning)" />
                      Bridge the Skill Gap
                    </h3>
                    <p style={{ color: 'var(--text-secondary)', marginBottom: '0.5rem' }}>
                      The following keywords are missing from your resume but are important for this role:
                    </p>
                    <p style={{ fontWeight: 500 }}>
                      {results.missing_keywords.map(k => k.keyword).join(', ')}
                    </p>
                    {results.missing_keywords.some(k => k.importance > 1) && (
                      <p style={{ fontSize: '0.9rem', color: 'var(--error)', marginTop: '0.5rem', fontWeight: 600 }}>
                        🔥 Focus on the high-priority skills marked with fire first!
                      </p>
                    )}
                    <p style={{ fontSize: '0.9rem', color: 'var(--text-secondary)', marginTop: '0.5rem' }}>
                      <strong>Action:</strong> Incorporate these skills into your "Skills" section or weave them into your project descriptions where applicable.
                    </p>
                  </div>
                )}

                {results.semantic_score < 0.8 && (
                  <div>
                    <h3 style={{ fontSize: '1.1rem', marginBottom: '0.5rem', display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
                      <ArrowRight size={18} color="var(--warning)" />
                      Improve Semantic Alignment
                    </h3>
                    <p style={{ color: 'var(--text-secondary)' }}>
                      Your resume's content is somewhat aligned, but could be stronger.
                    </p>
                    <ul style={{ listStyleType: 'disc', paddingLeft: '1.5rem', marginTop: '0.5rem', color: 'var(--text-secondary)' }}>
                      <li>Use action verbs (e.g., "Developed", "Led", "Optimized") to start bullet points.</li>
                      <li>Quantify your achievements (e.g., "Improved efficiency by 20%").</li>
                      <li>Mirror the language used in the job description for key responsibilities.</li>
                    </ul>
                  </div>
                )}

                <div>
                  <h3 style={{ fontSize: '1.1rem', marginBottom: '0.5rem', display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
                    <ArrowRight size={18} color="var(--warning)" />
                    General Tips
                  </h3>
                  <p style={{ color: 'var(--text-secondary)' }}>
                    Always proofread for typos and ensure your contact information is up to date. Tailoring your resume for each specific application significantly increases your chances of getting shortlisted.
                  </p>
                </div>
              </div>
            </div>
          </div>
        )}
      </div>

      <style>{`
        @keyframes spin {
          from { transform: rotate(0deg); }
          to { transform: rotate(360deg); }
        }
      `}</style>
    </div>
  );
}

export default App;

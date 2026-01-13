import { useState, useEffect } from 'react';
import { Upload, FileText, CheckCircle, AlertCircle, Loader2, Lightbulb, ArrowRight, TrendingUp, Target, Brain, Briefcase, Sun, Moon } from 'lucide-react';

function App() {
  const [file, setFile] = useState(null);
  const [jobDescription, setJobDescription] = useState('');
  const [loading, setLoading] = useState(false);
  const [results, setResults] = useState(null);
  const [error, setError] = useState(null);
  const [theme, setTheme] = useState(() => {
    if (typeof window !== 'undefined') {
      return localStorage.getItem('theme') || 'dark';
    }
    return 'dark';
  });

  useEffect(() => {
    document.documentElement.setAttribute('data-theme', theme);
    localStorage.setItem('theme', theme);
  }, [theme]);

  const toggleTheme = () => {
    setTheme(prev => prev === 'dark' ? 'light' : 'dark');
  };

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

  const getScoreColor = (score) => {
    if (score >= 80) return '#10b981';
    if (score >= 60) return '#f59e0b';
    return '#ef4444';
  };

  const getScoreLabel = (score) => {
    if (score >= 80) return 'Excellent Match';
    if (score >= 60) return 'Good Match';
    if (score >= 40) return 'Needs Work';
    return 'Poor Match';
  };

  const CircularScore = ({ score, size = 160 }) => {
    const strokeWidth = 10;
    const radius = (size - strokeWidth) / 2;
    const circumference = radius * 2 * Math.PI;
    const offset = circumference - (score / 100) * circumference;
    const color = getScoreColor(score);

    return (
      <div style={{ position: 'relative', width: size, height: size, margin: '0 auto' }}>
        <svg width={size} height={size} style={{ transform: 'rotate(-90deg)' }}>
          <circle
            cx={size / 2}
            cy={size / 2}
            r={radius}
            fill="none"
            stroke="var(--border-color)"
            strokeWidth={strokeWidth}
          />
          <circle
            cx={size / 2}
            cy={size / 2}
            r={radius}
            fill="none"
            stroke={color}
            strokeWidth={strokeWidth}
            strokeDasharray={circumference}
            strokeDashoffset={offset}
            strokeLinecap="round"
            style={{ transition: 'stroke-dashoffset 1s cubic-bezier(0.4, 0, 0.2, 1)' }}
          />
        </svg>
        <div style={{
          position: 'absolute',
          top: '50%',
          left: '50%',
          transform: 'translate(-50%, -50%)',
          textAlign: 'center'
        }}>
          <div style={{ fontSize: '2.25rem', fontWeight: 700, color }}>
            {Math.round(score)}
          </div>
          <div style={{ fontSize: '0.75rem', color: 'var(--text-secondary)', fontWeight: 500, textTransform: 'uppercase', letterSpacing: '0.05em' }}>
            ATS Score
          </div>
          <div style={{ fontSize: '0.7rem', color, fontWeight: 600, marginTop: '0.25rem' }}>
            {getScoreLabel(score)}
          </div>
        </div>
      </div>
    );
  };

  const ScoreBar = ({ label, score, icon: Icon, color }) => {
    const displayScore = score || 0;
    const barWidth = displayScore > 0 ? Math.min(displayScore, 100) : 0;

    return (
      <div style={{ marginBottom: '1rem' }}>
        <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '0.375rem' }}>
          <span style={{ display: 'flex', alignItems: 'center', gap: '0.5rem', fontSize: '0.875rem', fontWeight: 500 }}>
            <Icon size={16} color={color} />
            {label}
          </span>
          <span style={{ fontWeight: 700, color, fontSize: '0.875rem' }}>{displayScore.toFixed(1)}%</span>
        </div>
        <div className="progress-bar-container">
          <div
            style={{
              height: '100%',
              width: `${barWidth}%`,
              backgroundColor: barWidth > 0 ? color : 'transparent',
              borderRadius: '9999px',
              transition: 'width 0.8s cubic-bezier(0.4, 0, 0.2, 1)'
            }}
          />
        </div>
      </div>
    );
  };

  return (
    <div className="container">
      {/* Theme Toggle */}
      <button className="theme-toggle" onClick={toggleTheme} title={`Switch to ${theme === 'dark' ? 'light' : 'dark'} mode`}>
        {theme === 'dark' ? <Sun size={22} color="var(--text-primary)" /> : <Moon size={22} color="var(--text-primary)" />}
      </button>

      <header style={{ textAlign: 'center', marginBottom: '2.5rem', paddingTop: '1rem' }}>
        <h1>AI Resume Screener</h1>
        <p style={{ color: 'var(--text-secondary)', fontSize: '1.1rem', maxWidth: '600px', margin: '0 auto' }}>
          Optimize your resume for any job description using AI-powered analysis
        </p>
      </header>

      <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(320px, 1fr))', gap: '1.5rem' }}>
        <div className="card">
          <h2 style={{ marginBottom: '1.25rem', display: 'flex', alignItems: 'center', gap: '0.5rem', fontSize: '1.25rem' }}>
            <FileText size={22} color="var(--accent-primary)" />
            Input Details
          </h2>

          <form onSubmit={handleSubmit} style={{ display: 'flex', flexDirection: 'column', gap: '1.25rem' }}>
            <div>
              <label style={{ display: 'block', marginBottom: '0.5rem', fontWeight: 500, fontSize: '0.9rem' }}>Upload Resume (PDF)</label>
              <div
                className={`upload-area ${file ? 'has-file' : ''}`}
                onClick={() => document.getElementById('file-upload').click()}
              >
                <input
                  id="file-upload"
                  type="file"
                  accept=".pdf"
                  onChange={handleFileChange}
                  style={{ display: 'none' }}
                />
                <Upload size={28} color={file ? 'var(--accent-primary)' : 'var(--text-secondary)'} style={{ marginBottom: '0.75rem' }} />
                <p style={{ color: file ? 'var(--accent-primary)' : 'var(--text-secondary)', fontWeight: file ? 500 : 400 }}>
                  {file ? file.name : "Click to upload or drag and drop"}
                </p>
              </div>
            </div>

            <div>
              <label style={{ display: 'block', marginBottom: '0.5rem', fontWeight: 500, fontSize: '0.9rem' }}>Job Description</label>
              <textarea
                rows={7}
                placeholder="Paste the job description here..."
                value={jobDescription}
                onChange={(e) => setJobDescription(e.target.value)}
              />
            </div>

            {error && (
              <div style={{
                padding: '0.875rem',
                backgroundColor: 'rgba(239, 68, 68, 0.1)',
                color: 'var(--error)',
                borderRadius: 'var(--radius-md)',
                display: 'flex',
                alignItems: 'center',
                gap: '0.5rem',
                fontSize: '0.9rem'
              }}>
                <AlertCircle size={18} />
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
                  <Loader2 size={18} style={{ marginRight: '0.5rem', animation: 'spin 1s linear infinite' }} />
                  Analyzing...
                </>
              ) : (
                "Analyze Match"
              )}
            </button>
          </form>
        </div>

        {results && (
          <div style={{ display: 'flex', flexDirection: 'column', gap: '1.5rem' }} className="animate-fadeIn">
            {/* Overall ATS Score */}
            <div className="card score-card" style={{ textAlign: 'center' }}>
              <h2 style={{ marginBottom: '1rem', display: 'flex', alignItems: 'center', justifyContent: 'center', gap: '0.5rem', fontSize: '1.25rem' }}>
                <TrendingUp size={22} color="var(--accent-primary)" />
                Overall ATS Score
              </h2>
              <CircularScore score={results.overall_ats_score} />
              <p style={{ color: 'var(--text-secondary)', marginTop: '0.75rem', fontSize: '0.8rem' }}>
                Combined score based on keyword match, semantic similarity, skills coverage, and experience relevance.
              </p>
            </div>

            {/* Score Breakdown */}
            <div className="card">
              <h2 style={{ marginBottom: '1rem', display: 'flex', alignItems: 'center', gap: '0.5rem', fontSize: '1.15rem' }}>
                <CheckCircle size={20} color="var(--success)" />
                Score Breakdown
              </h2>

              <ScoreBar label="Keyword Match" score={results.score_breakdown.keyword_match} icon={Target} color="#8b5cf6" />
              <ScoreBar label="Semantic Similarity" score={results.score_breakdown.semantic_similarity} icon={Brain} color="#6366f1" />
              <ScoreBar label="Skills Coverage" score={results.score_breakdown.skills_coverage} icon={CheckCircle} color="#10b981" />
              <ScoreBar label="Experience Relevance" score={results.score_breakdown.experience_relevance} icon={Briefcase} color="#f59e0b" />
              <ScoreBar label="Grammar & Spelling" score={results.score_breakdown.grammar_score || 100} icon={FileText} color="#06b6d4" />
            </div>

            {/* Keywords */}
            <div className="card">
              <h2 style={{ marginBottom: '1rem', fontSize: '1.15rem' }}>Keywords Analysis</h2>

              <div style={{ marginBottom: '1.25rem' }}>
                <h3 style={{ fontSize: '0.95rem', marginBottom: '0.75rem', color: 'var(--error)', fontWeight: 600 }}>Missing Keywords</h3>
                {results.missing_keywords.length > 0 ? (
                  <div style={{ display: 'flex', flexWrap: 'wrap', gap: '0.5rem' }}>
                    {results.missing_keywords.slice(0, 15).map((item) => (
                      <span
                        key={item.keyword}
                        className="badge badge-missing"
                        style={item.importance > 2 ? { fontWeight: 600 } : {}}
                        title={`Importance: ${item.importance}`}
                      >
                        {item.keyword}
                        {item.importance > 2 && <span style={{ marginLeft: '0.25rem' }}>🔥</span>}
                      </span>
                    ))}
                    {results.missing_keywords.length > 15 && (
                      <span className="badge" style={{ opacity: 0.7 }}>+{results.missing_keywords.length - 15} more</span>
                    )}
                  </div>
                ) : (
                  <p style={{ color: 'var(--success)', fontSize: '0.9rem' }}>✓ Great job! No missing keywords detected.</p>
                )}
              </div>

              <div>
                <h3 style={{ fontSize: '0.95rem', marginBottom: '0.75rem', color: 'var(--success)', fontWeight: 600 }}>Detected Keywords</h3>
                <div style={{ display: 'flex', flexWrap: 'wrap', gap: '0.5rem' }}>
                  {results.detected_keywords.slice(0, 20).map((keyword) => (
                    <span key={keyword} className="badge">{keyword}</span>
                  ))}
                  {results.detected_keywords.length > 20 && (
                    <span className="badge" style={{ opacity: 0.7 }}>+{results.detected_keywords.length - 20} more</span>
                  )}
                </div>
              </div>
            </div>

            {/* Recommendations */}
            <div className="card recommendations-card">
              <h2 style={{ marginBottom: '1rem', display: 'flex', alignItems: 'center', gap: '0.5rem', color: 'var(--warning)', fontSize: '1.15rem' }}>
                <Lightbulb size={20} />
                Improvement Tips
              </h2>

              <div style={{ display: 'flex', flexDirection: 'column', gap: '0.75rem' }}>
                {results.improvement_tips.map((tip, index) => (
                  <div
                    key={index}
                    className={`tip-card ${tip.priority === 1 ? 'tip-high' : tip.priority === 2 ? 'tip-medium' : 'tip-low'}`}
                  >
                    <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem', marginBottom: '0.375rem' }}>
                      <ArrowRight size={14} color={tip.priority === 1 ? 'var(--error)' : tip.priority === 2 ? 'var(--warning)' : 'var(--accent-primary)'} />
                      <span style={{
                        fontWeight: 600,
                        color: tip.priority === 1 ? 'var(--error)' : 'var(--text-primary)',
                        fontSize: '0.85rem'
                      }}>
                        {tip.category}
                        {tip.priority === 1 && <span style={{ marginLeft: '0.5rem', fontSize: '0.75rem' }}>⚡ High Priority</span>}
                      </span>
                    </div>
                    <p style={{ color: 'var(--text-secondary)', fontSize: '0.85rem', margin: 0, lineHeight: 1.5 }}>
                      {tip.tip}
                    </p>
                  </div>
                ))}
              </div>
            </div>
          </div>
        )}
      </div>
    </div>
  );
}

export default App;

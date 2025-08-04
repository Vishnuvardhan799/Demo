import { useState } from "react";
import "./App.css";
import LiveKitModal from "./components/LiveKitModal";

function App() {
  const [showSupport, setShowSupport] = useState(false);
  const [callType, setCallType] = useState(null); // 'Voice Only' or 'Voice + Avatar'
  const [dropdownOpen, setDropdownOpen] = useState(false);

  const handleOptionClick = (type) => {
    setCallType(type);
    setShowSupport(true);
    setDropdownOpen(false);
  };

  return (
    <div className="app">
      {/* Futuristic Background */}
      <div className="futuristic-bg">
        <div className="grid-overlay"></div>
        <div className="floating-elements">
          <div className="float-particle"></div>
          <div className="float-particle"></div>
          <div className="float-particle"></div>
        </div>
      </div>

      {/* Header */}
      <header className="header">
        <div className="logo">
          <span className="logo-icon">🍽️</span>
          <span className="logo-text">RestaurantAI</span>
        </div>
        <nav className="nav">
          <a href="#menu" className="nav-item">
            Menu
          </a>
          <a href="#reservations" className="nav-item">
            Reservations
          </a>
          <a href="#about" className="nav-item">
            About
          </a>
          <a href="#contact" className="nav-item">
            Contact
          </a>
        </nav>
      </header>

      {/* Hero Landing Section */}
      <main className="hero-section">
        <div className="hero-content">
          <div className="status-badge">
            <div className="status-dot"></div>
            <span>AI Assistant Online</span>
          </div>

          <h1 className="hero-title">
            Reserve Your Table with
            <span className="highlight-text"> Voice Commands</span>
          </h1>

          <p className="hero-description">
            Experience seamless dining reservations powered by advanced AI.
            Simply speak your preferences and let our intelligent assistant
            handle the rest.
          </p>

          {/* Primary CTA - Book Now Button */}
          <div className="cta-section">
            <div className="dropdown-container">
              <button
                className="book-now-btn"
                onClick={() => setDropdownOpen((prev) => !prev)}
              >
                <div className="btn-icon">🎤</div>
                <span className="btn-text">Book Now</span>
                <span className="dropdown-arrow">{dropdownOpen ? "▲" : "▼"}</span>
                <div className="btn-pulse"></div>
              </button>
              {dropdownOpen && (
                <div className="dropdown-menu">
                  <button onClick={() => handleOptionClick("Voice Only")}>
                    Voice Only
                  </button>
                  <button onClick={() => handleOptionClick("Voice + Avatar")}>
                    Voice + Avatar
                  </button>
                </div>
              )}
            </div>

            <p className="cta-subtitle">
              Available 24/7 • Instant Confirmation • Natural Language
            </p>
          </div>

          {/* Quick Stats */}
          <div className="stats-grid">
            <div className="stat-item">
              <div className="stat-number">10K+</div>
              <div className="stat-label">Happy Diners</div>
            </div>
            <div className="stat-item">
              <div className="stat-number">99%</div>
              <div className="stat-label">Success Rate</div>
            </div>
            <div className="stat-item">
              <div className="stat-number">30s</div>
              <div className="stat-label">Avg Booking Time</div>
            </div>
          </div>
        </div>

        {/* Visual Element */}
        <div className="hero-visual">
          <div className="ai-interface">
            <div className="interface-ring"></div>
            <div className="interface-core">
              <div className="ai-avatar">🤖</div>
            </div>
          </div>
        </div>
      </main>

      {/* Features Preview */}
      <section className="features-preview">
        <div className="container">
          <h2 className="section-title">How It Works</h2>
          <div className="features-list">
            <div className="feature-item">
              <div className="feature-icon">🗣️</div>
              <h3>Speak Naturally</h3>
              <p>Tell us your preferences in plain English</p>
            </div>
            <div className="feature-item">
              <div className="feature-icon">⚡</div>
              <h3>Instant Processing</h3>
              <p>AI understands and processes immediately</p>
            </div>
            <div className="feature-item">
              <div className="feature-icon">✅</div>
              <h3>Confirmed Booking</h3>
              <p>Receive instant confirmation details</p>
            </div>
          </div>
        </div>
      </section>

      {/* Modal */}
      {showSupport && (
        <LiveKitModal setShowSupport={setShowSupport} callType={callType} />
      )}
    </div>
  );
}

export default App;

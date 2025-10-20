"use client";
import { useState, useEffect, useRef } from "react";
import { useRouter } from "next/navigation";

export default function Round1Page() {
  const [questions, setQuestions] = useState([]);
  const [answers, setAnswers] = useState({});
  const [timeLeft, setTimeLeft] = useState(1500); // 25 minutes
  const [loading, setLoading] = useState(true);
  const [submitting, setSubmitting] = useState(false);
  const [warningCount, setWarningCount] = useState(0);
  const [showWarning, setShowWarning] = useState(false);
  const router = useRouter();
  
  const email = typeof window !== "undefined" ? localStorage.getItem("candidate_email") : null;
  const warningTimeoutRef = useRef(null);

  // Redirect if no email
  useEffect(() => {
    if (!email) {
      router.push("/");
    }
  }, [email, router]);

  // Fetch questions when page loads
  useEffect(() => {
    if (!email) return;
    
    const fetchQuestions = async () => {
      try {
        const response = await fetch(`http://localhost:8000/round1-questions?email=${encodeURIComponent(email)}`);
        const data = await response.json();
        
        if (data.error) {
          alert(data.error);
          router.push("/");
        } else {
          setQuestions(data);
          setLoading(false);
        }
      } catch (err) {
        console.error("Error fetching questions:", err);
        alert("Could not load questions. Please check your connection.");
        router.push("/");
      }
    };

    fetchQuestions();
  }, [email, router]);

  // Timer with auto-submit
  useEffect(() => {
    if (timeLeft <= 0 && questions.length > 0) {
      handleSubmit();
      return;
    }
    
    const timer = setInterval(() => {
      setTimeLeft((prev) => {
        if (prev <= 0) {
          clearInterval(timer);
          return 0;
        }
        return prev - 1;
      });
    }, 1000);

    return () => clearInterval(timer);
  }, [timeLeft, questions.length]);

  // Anti-cheat: Disable copy/paste/right-click
  useEffect(() => {
    const preventCheating = (e) => {
      e.preventDefault();
      return false;
    };

    const handleKeyDown = (e) => {
      // Disable F12, Ctrl+Shift+I, Ctrl+U, Ctrl+S, Ctrl+A, Ctrl+C, Ctrl+V
      if (
        e.key === "F12" ||
        (e.ctrlKey && e.shiftKey && e.key === "I") ||
        (e.ctrlKey && e.key === "u") ||
        (e.ctrlKey && e.key === "s") ||
        (e.ctrlKey && e.key === "a") ||
        (e.ctrlKey && e.key === "c") ||
        (e.ctrlKey && e.key === "v") ||
        (e.ctrlKey && e.key === "x")
      ) {
        e.preventDefault();
        showAntiCheatWarning();
      }
    };

    // Add event listeners
    document.addEventListener("contextmenu", preventCheating);
    document.addEventListener("selectstart", preventCheating);
    document.addEventListener("dragstart", preventCheating);
    document.addEventListener("keydown", handleKeyDown);
    document.addEventListener("copy", preventCheating);
    document.addEventListener("paste", preventCheating);

    return () => {
      document.removeEventListener("contextmenu", preventCheating);
      document.removeEventListener("selectstart", preventCheating);
      document.removeEventListener("dragstart", preventCheating);
      document.removeEventListener("keydown", handleKeyDown);
      document.removeEventListener("copy", preventCheating);
      document.removeEventListener("paste", preventCheating);
    };
  }, []);

  // Anti-cheat: Track focus/blur events
  useEffect(() => {
    if (!email) return;

    const logEvent = async (eventType) => {
      try {
        await fetch("http://localhost:8000/round1-log", {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({ email, event_type: eventType }),
        });
      } catch (err) {
        console.error("Failed to log event:", err);
      }
    };

    const handleBlur = () => {
      logEvent("blur");
      showAntiCheatWarning();
    };

    const handleFocus = () => {
      logEvent("focus");
    };

    window.addEventListener("blur", handleBlur);
    window.addEventListener("focus", handleFocus);

    return () => {
      window.removeEventListener("blur", handleBlur);
      window.removeEventListener("focus", handleFocus);
    };
  }, [email]);

  const showAntiCheatWarning = () => {
    setWarningCount(prev => prev + 1);
    setShowWarning(true);
    
    if (warningTimeoutRef.current) {
      clearTimeout(warningTimeoutRef.current);
    }
    
    warningTimeoutRef.current = setTimeout(() => {
      setShowWarning(false);
    }, 3000);
  };

  const handleChange = (qid, option) => {
    setAnswers({ ...answers, [qid]: option });
  };

  const handleSubmit = async () => {
    if (submitting) return;
    
    setSubmitting(true);
    
    try {
      const response = await fetch("http://localhost:8000/round1-submit", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          email,
          answers,
          duration: 1500 - timeLeft,
        }),
      });

      const result = await response.json();
      
      if (response.ok) {
        // Store results in localStorage for feedback page
        localStorage.setItem("assessment_result", JSON.stringify({
          status: result.status,
          score: result.score,
          answers: answers,
          duration: 1500 - timeLeft
        }));
        
        // Redirect to feedback page instead of home
        router.push("/feedback");
      } else {
        alert("Error submitting assessment. Please try again.");
      }
    } catch (err) {
      console.error("Error submitting answers:", err);
      alert("Network error. Please check your connection.");
    } finally {
      setSubmitting(false);
    }
  };

  const formatTime = (seconds) => {
    const mins = Math.floor(seconds / 60);
    const secs = seconds % 60;
    return `${mins}:${secs.toString().padStart(2, "0")}`;
  };

  const getTimeColor = () => {
    if (timeLeft <= 300) return "#e53e3e"; // Red for last 5 minutes
    if (timeLeft <= 600) return "#dd6b20"; // Orange for last 10 minutes
    return "#38a169"; // Green for normal time
  };

  if (loading) {
    return (
      <div style={{
        display: "flex",
        justifyContent: "center",
        alignItems: "center",
        minHeight: "100vh",
        background: "linear-gradient(135deg, #667eea 0%, #764ba2 100%)",
        fontFamily: "system-ui, -apple-system, sans-serif"
      }}>
        <div style={{
          background: "white",
          padding: "3rem",
          borderRadius: "12px",
          textAlign: "center",
          boxShadow: "0 20px 40px rgba(0,0,0,0.1)"
        }}>
          <div style={{
            width: "40px",
            height: "40px",
            border: "4px solid #e2e8f0",
            borderTop: "4px solid #667eea",
            borderRadius: "50%",
            animation: "spin 1s linear infinite",
            margin: "0 auto 1rem"
          }}></div>
          <h2 style={{ color: "#2d3748", marginBottom: "0.5rem" }}>Loading Assessment</h2>
          <p style={{ color: "#718096" }}>Preparing your questions...</p>
        </div>
      </div>
    );
  }

  return (
    <div style={{
      minHeight: "100vh",
      background: "linear-gradient(135deg, #667eea 0%, #764ba2 100%)",
      fontFamily: "system-ui, -apple-system, sans-serif",
      padding: "2rem 0"
    }}>
      {/* Anti-cheat warning */}
      {showWarning && (
        <div style={{
          position: "fixed",
          top: "20px",
          right: "20px",
          background: "#e53e3e",
          color: "white",
          padding: "1rem 1.5rem",
          borderRadius: "8px",
          boxShadow: "0 10px 20px rgba(0,0,0,0.2)",
          zIndex: 1000,
          animation: "slideIn 0.3s ease-out"
        }}>
          <strong>⚠️ Warning #{warningCount}</strong><br />
          Please stay focused on the assessment. Switching tabs or using shortcuts is not allowed.
        </div>
      )}

      <div style={{ maxWidth: "800px", margin: "0 auto", padding: "0 2rem" }}>
        {/* Header */}
        <div style={{
          background: "white",
          padding: "2rem",
          borderRadius: "12px",
          marginBottom: "2rem",
          boxShadow: "0 10px 30px rgba(0,0,0,0.1)",
          textAlign: "center"
        }}>
          <h1 style={{
            color: "#2d3748",
            marginBottom: "0.5rem",
            fontSize: "2rem",
            fontWeight: "700"
          }}>
            Round 1 Assessment
          </h1>
          <p style={{ color: "#718096", marginBottom: "1.5rem" }}>
            Aptitude, Reasoning & Reading Comprehension
          </p>
          
          {/* Timer */}
          <div style={{
            display: "inline-flex",
            alignItems: "center",
            background: getTimeColor(),
            color: "white",
            padding: "0.75rem 1.5rem",
            borderRadius: "25px",
            fontSize: "1.2rem",
            fontWeight: "600",
            boxShadow: "0 4px 15px rgba(0,0,0,0.2)"
          }}>
            <span style={{ marginRight: "0.5rem" }}>⏱️</span>
            Time Remaining: {formatTime(timeLeft)}
          </div>
        </div>

        {/* Questions */}
        <div style={{
          background: "white",
          padding: "2rem",
          borderRadius: "12px",
          boxShadow: "0 10px 30px rgba(0,0,0,0.1)"
        }}>
          {questions.map((question, index) => (
            <div key={question.id} style={{
              marginBottom: "2.5rem",
              paddingBottom: "2rem",
              borderBottom: index < questions.length - 1 ? "1px solid #e2e8f0" : "none"
            }}>
              <div style={{
                display: "flex",
                alignItems: "flex-start",
                marginBottom: "1.5rem"
              }}>
                <div style={{
                  background: "#667eea",
                  color: "white",
                  width: "30px",
                  height: "30px",
                  borderRadius: "50%",
                  display: "flex",
                  alignItems: "center",
                  justifyContent: "center",
                  fontSize: "0.9rem",
                  fontWeight: "600",
                  marginRight: "1rem",
                  flexShrink: 0
                }}>
                  {index + 1}
                </div>
                <div style={{ flex: 1 }}>
                  <h3 style={{
                    color: "#2d3748",
                    fontSize: "1.1rem",
                    fontWeight: "600",
                    marginBottom: "1rem",
                    lineHeight: "1.5"
                  }}>
                    {question.question_text}
                  </h3>
                  
                  <div style={{ display: "flex", flexDirection: "column", gap: "0.75rem" }}>
                    {Object.entries(question.options).map(([key, value]) => (
                      <label key={key} style={{
                        display: "flex",
                        alignItems: "center",
                        padding: "0.75rem",
                        border: `2px solid ${answers[question.id] === key ? "#667eea" : "#e2e8f0"}`,
                        borderRadius: "8px",
                        cursor: "pointer",
                        transition: "all 0.2s",
                        background: answers[question.id] === key ? "#f7fafc" : "white"
                      }}>
                        <input
                          type="radio"
                          name={`q_${question.id}`}
                          value={key}
                          checked={answers[question.id] === key}
                          onChange={() => handleChange(question.id, key)}
                          style={{
                            marginRight: "0.75rem",
                            transform: "scale(1.2)"
                          }}
                        />
                        <span style={{
                          color: "#2d3748",
                          fontSize: "1rem",
                          userSelect: "none"
                        }}>
                          {value}
                        </span>
                      </label>
                    ))}
                  </div>
                </div>
              </div>
            </div>
          ))}

          {/* Submit Button */}
          <div style={{ textAlign: "center", marginTop: "2rem" }}>
            <button
              onClick={handleSubmit}
              disabled={submitting || timeLeft <= 0}
              style={{
                background: timeLeft <= 0 ? "#a0aec0" : submitting ? "#a0aec0" : "linear-gradient(135deg, #667eea 0%, #764ba2 100%)",
                color: "white",
                padding: "1rem 3rem",
                border: "none",
                borderRadius: "8px",
                fontSize: "1.1rem",
                fontWeight: "600",
                cursor: timeLeft <= 0 || submitting ? "not-allowed" : "pointer",
                transition: "all 0.2s",
                boxShadow: "0 4px 15px rgba(0,0,0,0.2)"
              }}
            >
              {submitting ? "Submitting..." : timeLeft <= 0 ? "Time's Up!" : "Submit Assessment"}
            </button>
          </div>
        </div>
      </div>

      <style jsx>{`
        @keyframes spin {
          0% { transform: rotate(0deg); }
          100% { transform: rotate(360deg); }
        }
        
        @keyframes slideIn {
          from { transform: translateX(100%); opacity: 0; }
          to { transform: translateX(0); opacity: 1; }
        }
      `}</style>
    </div>
  );
}

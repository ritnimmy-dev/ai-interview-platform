"use client";
import { useState, useEffect, useRef } from "react";
import { useRouter } from "next/navigation";

export default function FeedbackPage() {
  const [assessmentResult, setAssessmentResult] = useState(null);
  const [messages, setMessages] = useState([]);
  const [inputMessage, setInputMessage] = useState("");
  const [isLoading, setIsLoading] = useState(false);
  const [isTyping, setIsTyping] = useState(false);
  const messagesEndRef = useRef(null);
  const router = useRouter();

  // Load assessment results
  useEffect(() => {
    const result = localStorage.getItem("assessment_result");
    if (!result) {
      router.push("/");
      return;
    }
    
    try {
      const parsed = JSON.parse(result);
      setAssessmentResult(parsed);
      
      // Add initial welcome message
      const welcomeMessage = generateWelcomeMessage(parsed);
      setMessages([{
        id: 1,
        type: "ai",
        content: welcomeMessage,
        timestamp: new Date()
      }]);
    } catch (err) {
      console.error("Error parsing assessment result:", err);
      router.push("/");
    }
  }, [router]);

  // Auto-scroll to bottom when new messages arrive
  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [messages]);

  const generateWelcomeMessage = (result) => {
    const { status, score } = result;
    
    let message = `🎉 **Assessment Complete!**\n\n`;
    message += `**Your Score:** ${score}%\n`;
    message += `**Status:** ${status.toUpperCase()}\n\n`;
    
    if (status === "pass") {
      message += `🎯 **Excellent work!** You've passed the assessment with a strong score. `;
      message += `You're well-positioned for the next stage of our interview process.\n\n`;
      message += `**What you can do next:**\n`;
      message += `• Prepare for technical interviews\n`;
      message += `• Review your strong areas and build on them\n`;
      message += `• Practice coding challenges in your technology track\n\n`;
    } else if (status === "review") {
      message += `📋 **Good effort!** Your assessment is under review. `;
      message += `This means you're on the right track but there's room for improvement.\n\n`;
      message += `**Areas to focus on:**\n`;
      message += `• Strengthen your fundamentals in your chosen technology\n`;
      message += `• Practice more aptitude and reasoning problems\n`;
      message += `• Consider taking online courses to fill knowledge gaps\n\n`;
    } else {
      message += `💪 **Don't give up!** While this attempt didn't meet our passing criteria, `;
      message += `every assessment is a learning opportunity.\n\n`;
      message += `**How to improve:**\n`;
      message += `• Focus on strengthening your core skills\n`;
      message += `• Practice regularly with coding challenges\n`;
      message += `• Consider additional training in your technology track\n`;
      message += `• You can reapply in 6 weeks with improved skills\n\n`;
    }
    
    message += `🤖 **I'm here to help!** Ask me anything about your performance, `;
    message += `career advice, or how to improve for future opportunities. `;
    message += `I can provide personalized guidance based on your assessment results.`;
    
    return message;
  };

  const handleSendMessage = async () => {
    if (!inputMessage.trim() || isLoading) return;

    const userMessage = {
      id: Date.now(),
      type: "user",
      content: inputMessage.trim(),
      timestamp: new Date()
    };

    setMessages(prev => [...prev, userMessage]);
    setInputMessage("");
    setIsLoading(true);
    setIsTyping(true);

    try {
      const response = await fetch("http://localhost:8000/feedback-chat", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          message: inputMessage.trim(),
          assessment_result: assessmentResult,
          conversation_history: messages
        })
      });

      if (response.ok) {
        const data = await response.json();
        
        // Simulate typing delay
        setTimeout(() => {
          const aiMessage = {
            id: Date.now() + 1,
            type: "ai",
            content: data.response,
            timestamp: new Date()
          };
          
          setMessages(prev => [...prev, aiMessage]);
          setIsTyping(false);
          setIsLoading(false);
        }, 1000 + Math.random() * 2000); // 1-3 second delay
      } else {
        throw new Error("Failed to get response");
      }
    } catch (err) {
      console.error("Error getting AI response:", err);
      
      const errorMessage = {
        id: Date.now() + 1,
        type: "ai",
        content: "I'm sorry, I'm having trouble connecting right now. Please try again in a moment.",
        timestamp: new Date()
      };
      
      setMessages(prev => [...prev, errorMessage]);
      setIsTyping(false);
      setIsLoading(false);
    }
  };

  const handleKeyPress = (e) => {
    if (e.key === "Enter" && !e.shiftKey) {
      e.preventDefault();
      handleSendMessage();
    }
  };

  const formatTime = (timestamp) => {
    return new Date(timestamp).toLocaleTimeString([], { 
      hour: '2-digit', 
      minute: '2-digit' 
    });
  };

  if (!assessmentResult) {
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
          <h2 style={{ color: "#2d3748", marginBottom: "0.5rem" }}>Loading Results</h2>
          <p style={{ color: "#718096" }}>Preparing your personalized feedback...</p>
        </div>
      </div>
    );
  }

  return (
    <div style={{
      minHeight: "100vh",
      background: "linear-gradient(135deg, #667eea 0%, #764ba2 100%)",
      fontFamily: "system-ui, -apple-system, sans-serif",
      display: "flex",
      flexDirection: "column"
    }}>
      {/* Header */}
      <div style={{
        background: "white",
        padding: "1.5rem 2rem",
        boxShadow: "0 2px 10px rgba(0,0,0,0.1)",
        borderBottom: "1px solid #e2e8f0"
      }}>
        <div style={{ maxWidth: "800px", margin: "0 auto" }}>
          <h1 style={{
            color: "#2d3748",
            margin: "0",
            fontSize: "1.5rem",
            fontWeight: "700"
          }}>
            🤖 AI Career Coach
          </h1>
          <p style={{
            color: "#718096",
            margin: "0.5rem 0 0 0",
            fontSize: "1rem"
          }}>
            Get personalized feedback and career advice based on your assessment
          </p>
        </div>
      </div>

      {/* Chat Container */}
      <div style={{
        flex: 1,
        display: "flex",
        flexDirection: "column",
        maxWidth: "800px",
        margin: "0 auto",
        width: "100%",
        padding: "0 2rem"
      }}>
        {/* Messages */}
        <div style={{
          flex: 1,
          overflowY: "auto",
          padding: "2rem 0",
          display: "flex",
          flexDirection: "column",
          gap: "1.5rem"
        }}>
          {messages.map((message) => (
            <div
              key={message.id}
              style={{
                display: "flex",
                justifyContent: message.type === "user" ? "flex-end" : "flex-start",
                alignItems: "flex-start",
                gap: "0.75rem"
              }}
            >
              {message.type === "ai" && (
                <div style={{
                  width: "32px",
                  height: "32px",
                  background: "linear-gradient(135deg, #667eea 0%, #764ba2 100%)",
                  borderRadius: "50%",
                  display: "flex",
                  alignItems: "center",
                  justifyContent: "center",
                  color: "white",
                  fontSize: "0.9rem",
                  fontWeight: "600",
                  flexShrink: 0
                }}>
                  🤖
                </div>
              )}
              
              <div style={{
                maxWidth: "70%",
                background: message.type === "user" ? "#667eea" : "white",
                color: message.type === "user" ? "white" : "#2d3748",
                padding: "1rem 1.25rem",
                borderRadius: message.type === "user" ? "18px 18px 4px 18px" : "18px 18px 18px 4px",
                boxShadow: "0 2px 8px rgba(0,0,0,0.1)",
                wordWrap: "break-word",
                whiteSpace: "pre-wrap"
              }}>
                {message.content}
                <div style={{
                  fontSize: "0.75rem",
                  opacity: 0.7,
                  marginTop: "0.5rem"
                }}>
                  {formatTime(message.timestamp)}
                </div>
              </div>
              
              {message.type === "user" && (
                <div style={{
                  width: "32px",
                  height: "32px",
                  background: "#e2e8f0",
                  borderRadius: "50%",
                  display: "flex",
                  alignItems: "center",
                  justifyContent: "center",
                  color: "#718096",
                  fontSize: "0.9rem",
                  fontWeight: "600",
                  flexShrink: 0
                }}>
                  👤
                </div>
              )}
            </div>
          ))}
          
          {isTyping && (
            <div style={{
              display: "flex",
              justifyContent: "flex-start",
              alignItems: "flex-start",
              gap: "0.75rem"
            }}>
              <div style={{
                width: "32px",
                height: "32px",
                background: "linear-gradient(135deg, #667eea 0%, #764ba2 100%)",
                borderRadius: "50%",
                display: "flex",
                alignItems: "center",
                justifyContent: "center",
                color: "white",
                fontSize: "0.9rem",
                fontWeight: "600",
                flexShrink: 0
              }}>
                🤖
              </div>
              <div style={{
                background: "white",
                padding: "1rem 1.25rem",
                borderRadius: "18px 18px 18px 4px",
                boxShadow: "0 2px 8px rgba(0,0,0,0.1)",
                display: "flex",
                alignItems: "center",
                gap: "0.5rem"
              }}>
                <div style={{
                  width: "8px",
                  height: "8px",
                  background: "#667eea",
                  borderRadius: "50%",
                  animation: "pulse 1.5s ease-in-out infinite"
                }}></div>
                <div style={{
                  width: "8px",
                  height: "8px",
                  background: "#667eea",
                  borderRadius: "50%",
                  animation: "pulse 1.5s ease-in-out infinite 0.2s"
                }}></div>
                <div style={{
                  width: "8px",
                  height: "8px",
                  background: "#667eea",
                  borderRadius: "50%",
                  animation: "pulse 1.5s ease-in-out infinite 0.4s"
                }}></div>
              </div>
            </div>
          )}
          
          <div ref={messagesEndRef} />
        </div>

        {/* Input Area */}
        <div style={{
          background: "white",
          padding: "1.5rem",
          borderRadius: "12px 12px 0 0",
          boxShadow: "0 -2px 10px rgba(0,0,0,0.1)",
          borderTop: "1px solid #e2e8f0"
        }}>
          <div style={{
            display: "flex",
            gap: "0.75rem",
            alignItems: "flex-end"
          }}>
            <textarea
              value={inputMessage}
              onChange={(e) => setInputMessage(e.target.value)}
              onKeyPress={handleKeyPress}
              placeholder="Ask me anything about your performance, career advice, or how to improve..."
              disabled={isLoading}
              style={{
                flex: 1,
                padding: "0.75rem 1rem",
                border: "2px solid #e2e8f0",
                borderRadius: "8px",
                fontSize: "1rem",
                fontFamily: "inherit",
                resize: "none",
                minHeight: "44px",
                maxHeight: "120px",
                outline: "none",
                transition: "border-color 0.2s",
                background: isLoading ? "#f7fafc" : "white",
                color: "#2d3748"  // Dark text color for visibility
              }}
              onFocus={(e) => {
                e.target.style.borderColor = "#667eea";
              }}
              onBlur={(e) => {
                e.target.style.borderColor = "#e2e8f0";
              }}
            />
            <button
              onClick={handleSendMessage}
              disabled={!inputMessage.trim() || isLoading}
              style={{
                background: (!inputMessage.trim() || isLoading) ? "#a0aec0" : "linear-gradient(135deg, #667eea 0%, #764ba2 100%)",
                color: "white",
                border: "none",
                borderRadius: "8px",
                padding: "0.75rem 1.5rem",
                fontSize: "1rem",
                fontWeight: "600",
                cursor: (!inputMessage.trim() || isLoading) ? "not-allowed" : "pointer",
                transition: "all 0.2s",
                display: "flex",
                alignItems: "center",
                gap: "0.5rem"
              }}
            >
              {isLoading ? "..." : "Send"}
            </button>
          </div>
        </div>
      </div>

      <style jsx>{`
        @keyframes spin {
          0% { transform: rotate(0deg); }
          100% { transform: rotate(360deg); }
        }
        
        @keyframes pulse {
          0%, 100% { opacity: 0.4; transform: scale(1); }
          50% { opacity: 1; transform: scale(1.1); }
        }
      `}</style>
    </div>
  );
}

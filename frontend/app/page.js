"use client";
import { useState } from "react";
import { useRouter } from "next/navigation";

export default function LandingPage() {
  const [formData, setFormData] = useState({
    full_name: "",
    email: "",
    technology_track: "",
    resume: null,
  });
  const [loading, setLoading] = useState(false);
  const [errors, setErrors] = useState({});
  const router = useRouter();

  const handleChange = (e) => {
    const { name, value, files } = e.target;
    setFormData({ ...formData, [name]: files ? files[0] : value });
    
    // Clear error when user starts typing
    if (errors[name]) {
      setErrors({ ...errors, [name]: "" });
    }
  };

  const validateForm = () => {
    const newErrors = {};
    
    if (!formData.full_name.trim()) {
      newErrors.full_name = "Full name is required";
    }
    
    if (!formData.email.trim()) {
      newErrors.email = "Email is required";
    } else if (!/\S+@\S+\.\S+/.test(formData.email)) {
      newErrors.email = "Please enter a valid email";
    }
    
    if (!formData.technology_track) {
      newErrors.technology_track = "Please select a technology track";
    }
    
    if (!formData.resume) {
      newErrors.resume = "Please upload your resume";
    } else if (formData.resume.type !== "application/pdf") {
      newErrors.resume = "Only PDF files are allowed";
    }
    
    setErrors(newErrors);
    return Object.keys(newErrors).length === 0;
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    
    if (!validateForm()) {
      return;
    }

    const form = new FormData();
    form.append("full_name", formData.full_name);
    form.append("email", formData.email);
    form.append("technology_track", formData.technology_track);
    form.append("resume", formData.resume);

    try {
      setLoading(true);
      const response = await fetch("http://localhost:8000/start-interview", {
        method: "POST",
        body: form,
      });

      if (response.ok) {
        // Save email in localStorage for Round 1
        localStorage.setItem("candidate_email", formData.email);
        
        alert("Interview started successfully!");
        router.push("/round1");
      } else {
        const errorData = await response.json();
        alert(`Error: ${errorData.detail || "Failed to start interview"}`);
      }
    } catch (err) {
      console.error("Submission error:", err);
      alert("Network error. Please check if the backend server is running.");
    } finally {
      setLoading(false);
    }
  };

  return (
    <div style={{
      width: "100%",
      margin: "0",
      padding: "2rem",
      fontFamily: "system-ui, -apple-system, sans-serif",
      background: "linear-gradient(135deg, #667eea 0%, #764ba2 100%)",
      minHeight: "100vh",
      display: "flex",
      alignItems: "center",
      justifyContent: "center"
    }}>
      <div style={{
        background: "white",
        padding: "3rem",
        borderRadius: "12px",
        boxShadow: "0 20px 40px rgba(0,0,0,0.1)",
        width: "100%"
      }}>
        <div style={{ textAlign: "center", marginBottom: "2rem" }}>
          <h1 style={{ 
            color: "#2d3748", 
            marginBottom: "0.5rem",
            fontSize: "2rem",
            fontWeight: "700"
          }}>
            AI Interview Portal
          </h1>
          <p style={{ color: "#718096", fontSize: "1.1rem" }}>
            Welcome to our intelligent interview platform
          </p>
        </div>

        <form onSubmit={handleSubmit} style={{ display: "flex", flexDirection: "column", gap: "1.5rem" }}>
          <div>
            <label style={{ 
              display: "block", 
              marginBottom: "0.5rem", 
              fontWeight: "600", 
              color: "#2d3748" 
            }}>
              Full Name *
            </label>
            <input
              type="text"
              name="full_name"
              value={formData.full_name}
              onChange={handleChange}
              style={{
                width: "100%",
                padding: "0.75rem",
                border: `2px solid ${errors.full_name ? "#e53e3e" : "#e2e8f0"}`,
                borderRadius: "8px",
                fontSize: "1rem",
                transition: "border-color 0.2s"
              }}
              placeholder="Enter your full name"
            />
            {errors.full_name && (
              <p style={{ color: "#e53e3e", fontSize: "0.875rem", marginTop: "0.25rem" }}>
                {errors.full_name}
              </p>
            )}
          </div>

          <div>
            <label style={{ 
              display: "block", 
              marginBottom: "0.5rem", 
              fontWeight: "600", 
              color: "#2d3748" 
            }}>
              Email Address *
            </label>
            <input
              type="email"
              name="email"
              value={formData.email}
              onChange={handleChange}
              style={{
                width: "100%",
                padding: "0.75rem",
                border: `2px solid ${errors.email ? "#e53e3e" : "#e2e8f0"}`,
                borderRadius: "8px",
                fontSize: "1rem",
                transition: "border-color 0.2s"
              }}
              placeholder="Enter your email address"
            />
            {errors.email && (
              <p style={{ color: "#e53e3e", fontSize: "0.875rem", marginTop: "0.25rem" }}>
                {errors.email}
              </p>
            )}
          </div>

          <div>
            <label style={{ 
              display: "block", 
              marginBottom: "0.5rem", 
              fontWeight: "600", 
              color: "#2d3748" 
            }}>
              Technology Track *
            </label>
            <select
              name="technology_track"
              value={formData.technology_track}
              onChange={handleChange}
              style={{
                width: "100%",
                padding: "0.75rem",
                border: `2px solid ${errors.technology_track ? "#e53e3e" : "#e2e8f0"}`,
                borderRadius: "8px",
                fontSize: "1rem",
                backgroundColor: "white",
                transition: "border-color 0.2s",
                color: formData.technology_track ? "#2d3748" : "#718096"
              }}
            >
              <option value="">Select your technology track</option>
              <option value="python">Python Development</option>
              <option value="javascript">JavaScript/React</option>
              <option value="salesforce">Salesforce</option>
              <option value="fullstack">Full Stack Development</option>
            </select>
            {errors.technology_track && (
              <p style={{ color: "#e53e3e", fontSize: "0.875rem", marginTop: "0.25rem" }}>
                {errors.technology_track}
              </p>
            )}
          </div>

          <div>
            <label style={{ 
              display: "block", 
              marginBottom: "0.5rem", 
              fontWeight: "600", 
              color: "#2d3748" 
            }}>
              Resume (PDF only) *
            </label>
            <input
              type="file"
              name="resume"
              accept=".pdf,application/pdf"
              onChange={handleChange}
              style={{
                width: "100%",
                padding: "0.75rem",
                border: `2px solid ${errors.resume ? "#e53e3e" : "#e2e8f0"}`,
                borderRadius: "8px",
                fontSize: "1rem",
                transition: "border-color 0.2s"
              }}
            />
            {errors.resume && (
              <p style={{ color: "#e53e3e", fontSize: "0.875rem", marginTop: "0.25rem" }}>
                {errors.resume}
              </p>
            )}
            <p style={{ color: "#718096", fontSize: "0.875rem", marginTop: "0.25rem" }}>
              Please upload your resume in PDF format
            </p>
          </div>

          <button
            type="submit"
            disabled={loading}
            style={{
              background: loading ? "#a0aec0" : "linear-gradient(135deg, #667eea 0%, #764ba2 100%)",
              color: "white",
              padding: "1rem 2rem",
              border: "none",
              borderRadius: "8px",
              fontSize: "1.1rem",
              fontWeight: "600",
              cursor: loading ? "not-allowed" : "pointer",
              transition: "all 0.2s",
              marginTop: "1rem"
            }}
            onMouseOver={(e) => {
              if (!loading) {
                e.target.style.transform = "translateY(-2px)";
                e.target.style.boxShadow = "0 10px 20px rgba(0,0,0,0.2)";
              }
            }}
            onMouseOut={(e) => {
              if (!loading) {
                e.target.style.transform = "translateY(0)";
                e.target.style.boxShadow = "none";
              }
            }}
          >
            {loading ? "Starting Interview..." : "Start Interview"}
          </button>
        </form>
      </div>
    </div>
  );
}

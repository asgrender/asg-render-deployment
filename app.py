# app.py
# Vehicle Workshop Management (Flask + Bootstrap + Vanilla JS + Vue on /reception)
# Run: python app.py

import os
import json
import uuid
from typing import Any, Dict, List
from flask import Flask, request, jsonify, render_template_string, redirect, session, url_for

###############################################################################
# App & Config
###############################################################################
app = Flask(__name__)
app.secret_key = os.getenv("SECRET_KEY", "supersecretkey123")

# ---------- Files ----------
VEHICLES_FILE = "vehicles.json"
DEPARTMENTS_FILE = "departments.json"
TECHS_FILE = "technicians.json"
SERVICES_FILE = "services.json"

# ---------- Constants ----------
STATUSES: List[str] = ["Waiting", "In Service", "Done"]
PAYMENTS: List[str] = ["Paid", "Advance Paid", "Unpaid"]
PARTS_OPTIONS: List[str] = ["Arrived", "Not Arrived"]

USERS: Dict[str, str] = {
    "admin": "admin123",
    "staff": "staff123",
    "dashboard": "dashboard123",
    "display": "display123",
    "reception": "reception123",
}

###############################################################################
# Helpers
###############################################################################

def load_json(path: str) -> Any:
    if os.path.exists(path):
        with open(path, "r", encoding="utf-8") as f:
            try:
                return json.load(f)
            except json.JSONDecodeError:
                # tolerate corrupted/empty files
                return []
    return []


def save_json(path: str, data: Any) -> None:
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)


def read_vehicles():
    """Read vehicles from file and ensure proper formatting"""
    global vehicles
    vehicles = load_json(VEHICLES_FILE) or []
    
    # Backfill defaults for all records
    for v in vehicles:
        v.setdefault("id", str(uuid.uuid4()))
        v.setdefault("customer", "")
        v.setdefault("vehicle_no", "")
        v.setdefault("vehicle_name", "")
        v.setdefault("department", departments[0] if departments else "")
        v.setdefault("service", services[0] if services else "")
        v.setdefault("technician", technicians[0] if technicians else "")
        v.setdefault("status", STATUSES[0])
        v.setdefault("payment", "Unpaid")
        v.setdefault("parts", "Not Arrived")
        v.setdefault("visible", True)
    
    return vehicles

# Load initial data with sensible defaults
departments: List[str] = load_json(DEPARTMENTS_FILE) or ["Mechanical", "Electrical", "Body Shop"]
technicians: List[str] = load_json(TECHS_FILE) or ["Rajesh", "Syon"]
services: List[str] = load_json(SERVICES_FILE) or ["General Service", "Oil Change", "Full Inspection"]
vehicles: List[Dict[str, Any]] = read_vehicles()

###############################################################################
# Auth (fixed: new UI, original USERS, added logout)
###############################################################################
@app.route("/", methods=["GET", "POST"])
def login():
    error = ""
    if request.method == "POST":
        username = request.form.get("username", "").strip()
        password = request.form.get("password", "").strip()
        if username in USERS and USERS[username] == password:
            session["user"] = username
            return redirect(f"/{username}") if username != "admin" else redirect("/admin")
        error = "Invalid username or password"

    return render_template_string(
        r"""<!doctype html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0, user-scalable=no">
  <title>Login</title>
  <style>
    /* === Enhanced Ultra-Responsive CSS === */
    * { 
      margin: 0; 
      padding: 0; 
      box-sizing: border-box; 
      font-family: "Segoe UI", Tahoma, Geneva, Verdana, sans-serif;
      -webkit-font-smoothing: antialiased;
      -moz-osx-font-smoothing: grayscale;
    }
    
    html { 
      font-size: clamp(14px, 2vw, 16px); 
      height: 100%;
      overflow: hidden;
    }
    
    body { 
      display: flex; 
      justify-content: center; 
      align-items: center; 
      min-height: 100vh; 
      height: 100vh;
      overflow: hidden; 
      position: relative;
      touch-action: manipulation;
    }
    
    .background { 
      position: fixed; 
      inset: 0; 
      background: url("{{ url_for('static', filename='background.png') }}") no-repeat center center/cover; 
      animation: zoom 20s infinite alternate ease-in-out;
      will-change: transform;
    }
    
    .background.back { 
      filter: brightness(1.4) blur(clamp(4px, 1vw, 8px)); 
      transform: scale(1.3); 
      z-index: -2; 
    }
    
    .background.front { 
      filter: brightness(0.5); 
      transform: scale(1.3); 
      z-index: -1; 
    }
    
    @keyframes zoom { 
      0% { transform: scale(1.3); } 
      100% { transform: scale(1.8); } 
    }
    
    .big-box { 
      position: fixed; 
      top: clamp(10px, 5vh, 5cm); 
      bottom: clamp(10px, 5vh, 5cm); 
      left: clamp(10px, 5vw, 5cm); 
      right: clamp(10px, 5vw, 5cm); 
      background: url("{{ url_for('static', filename='background.png') }}") no-repeat center center/cover; 
      border-radius: clamp(10px, 2vw, 20px); 
      overflow: hidden; 
      z-index: 0; 
      box-shadow: 0 0 clamp(20px, 4vw, 40px) rgba(0,0,0,0.6);
      will-change: transform;
    }
    
    .container { 
      width: 100%; 
      max-width: min(90vw, 900px); 
      display: flex; 
      justify-content: center; 
      align-items: center; 
      padding: clamp(10px, 3vw, 20px); 
      position: relative; 
      z-index: 1; 
    }
    
    .login-box { 
      position: relative; 
      border-radius: clamp(15px, 2vw, 20px); 
      padding: clamp(20px, 4vw, 30px); 
      width: min(90vw, 350px); 
      max-width: 350px;
      text-align: center; 
      color: #fff; 
      box-shadow: 0 clamp(4px, 1vw, 8px) clamp(10px, 2vw, 20px) rgba(0,0,0,0.3); 
      backdrop-filter: blur(clamp(8px, 1.5vw, 12px)); 
      background: linear-gradient(135deg, rgba(0,0,0,0.65), rgba(0,0,0,0.85)); 
      overflow: hidden; 
      opacity: 0; 
      transform: translateY(30px); 
      animation: fadeInUp 1s forwards ease-out;
      will-change: transform, opacity;
    }
    
    .login-box img { 
      width: clamp(60px, 12vw, 100px); 
      height: clamp(60px, 12vw, 100px); 
      object-fit: cover; 
      border-radius: 50%; 
      margin-bottom: clamp(10px, 2vw, 15px); 
      animation: bounceIn 1s ease-out;
      will-change: transform;
    }
    
    @keyframes bounceIn { 
      0% { transform: scale(0.3); opacity: 0; } 
      60% { transform: scale(1.2); opacity: 1; } 
      80% { transform: scale(0.9); } 
      100% { transform: scale(1); } 
    }
    
    .login-box h2 { 
      font-size: clamp(20px, 4vw, 26px); 
      margin-bottom: clamp(15px, 3vw, 20px); 
      font-weight: 600;
    }
    
    .login-box input[type="text"], 
    .login-box input[type="password"] { 
      width: 100%; 
      padding: clamp(10px, 2vw, 12px); 
      margin-bottom: 5px; 
      border: none; 
      border-radius: clamp(4px, 1vw, 6px); 
      outline: none; 
      background: rgba(255,255,255,0.95); 
      color: #333; 
      transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
      font-size: clamp(14px, 2vw, 16px);
      will-change: box-shadow, transform;
      -webkit-appearance: none;
      appearance: none;
    }
    
    .login-box input:focus { 
      box-shadow: 0 0 0 3px rgba(230,57,70,0.3), 0 0 clamp(6px, 1vw, 8px) rgba(230,57,70,0.8); 
      transform: scale(1.02); 
      background: #fff;
    }
    
    .login-box input:hover:not(:focus) {
      background: #fff;
      transform: translateY(-1px);
    }
    
    .field-error { 
      text-align: left; 
      font-size: clamp(12px, 2vw, 13px); 
      color: #ff3b30; 
      margin-bottom: 10px; 
      opacity: 0; 
      height: 0; 
      transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
      transform: translateY(-5px);
    }
    
    .field-error.visible { 
      opacity: 1; 
      height: auto;
      transform: translateY(0);
    }
    
    .password-wrapper { 
      position: relative; 
    }
    
    .toggle-password { 
      position: absolute; 
      right: clamp(8px, 2vw, 12px); 
      top: 50%; 
      transform: translateY(-50%); 
      cursor: pointer; 
      color: #666; 
      width: clamp(18px, 3vw, 22px); 
      height: clamp(18px, 3vw, 22px); 
      opacity: 0.6; 
      transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
      touch-action: manipulation;
    }
    
    .toggle-password:hover, .toggle-password:active { 
      opacity: 1; 
      transform: translateY(-50%) scale(1.1);
    }
    
    .login-box button { 
      width: 100%; 
      padding: clamp(10px, 2vw, 12px); 
      border: none; 
      border-radius: clamp(4px, 1vw, 6px); 
      background: linear-gradient(135deg, #e63946, #d62828); 
      color: #fff; 
      font-weight: 600; 
      font-size: clamp(14px, 2vw, 16px);
      cursor: pointer; 
      transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
      position: relative;
      overflow: hidden;
      will-change: transform, background;
      touch-action: manipulation;
      -webkit-appearance: none;
      appearance: none;
    }
    
    .login-box button::before {
      content: '';
      position: absolute;
      top: 0;
      left: -100%;
      width: 100%;
      height: 100%;
      background: linear-gradient(90deg, transparent, rgba(255,255,255,0.3), transparent);
      transition: left 0.6s;
    }
    
    .login-box button:hover::before {
      left: 100%;
    }
    
    .login-box button:hover:not(:disabled) { 
      background: linear-gradient(135deg, #d62828, #b71c1c); 
      transform: translateY(-2px) scale(1.02); 
      box-shadow: 0 clamp(4px, 1vw, 8px) clamp(15px, 3vw, 25px) rgba(230,57,70,0.4);
    }
    
    .login-box button:active:not(:disabled) {
      transform: translateY(0) scale(1);
      transition: all 0.1s;
    }
    
    .login-box button:disabled { 
      background: #999; 
      cursor: not-allowed; 
      transform: none;
      box-shadow: none;
    }
    
    .error { 
      margin-top: clamp(10px, 2vw, 15px); 
      color: #ffcccc; 
      font-size: clamp(13px, 2vw, 14px); 
      opacity: 0; 
      transform: translateY(-10px); 
      animation: fadeInError 0.5s forwards cubic-bezier(0.4, 0, 0.2, 1);
    }
    
    @keyframes fadeInError { 
      to { 
        opacity: 1; 
        transform: translateY(0); 
      } 
    }
    
    @keyframes fadeInUp { 
      to { 
        opacity: 1; 
        transform: translateY(0); 
      } 
    }
    
    .spinner { 
      width: clamp(16px, 3vw, 20px); 
      height: clamp(16px, 3vw, 20px); 
      border: 2px solid rgba(255,255,255,0.3); 
      border-top-color: white; 
      border-radius: 50%; 
      animation: spin 0.8s linear infinite; 
      margin: auto;
    }
    
    @keyframes spin { 
      to { transform: rotate(360deg); } 
    }
    
    /* === Ultra Responsive Breakpoints === */
    
    /* Small phones (320px - 480px) */
    @media (max-width: 480px) {
      .big-box {
        top: 5px;
        bottom: 5px;
        left: 5px;
        right: 5px;
      }
      
      .login-box {
        padding: 20px 15px;
        width: calc(100vw - 20px);
        margin: 0 10px;
      }
      
      .login-box img { 
        width: 70px; 
        height: 70px; 
      }
      
      .login-box h2 { 
        font-size: 20px; 
      }
      
      .login-box input, 
      .login-box button { 
        padding: 12px 10px;
        font-size: 16px; /* Prevent zoom on iOS */
      }
    }
    
    /* Medium phones (481px - 768px) */
    @media (min-width: 481px) and (max-width: 768px) {
      .login-box {
        width: min(80vw, 320px);
      }
    }
    
    /* Tablets (769px - 1024px) */
    @media (min-width: 769px) and (max-width: 1024px) {
      .login-box {
        width: min(60vw, 350px);
      }
    }
    
    /* Large screens (1025px+) */
    @media (min-width: 1025px) {
      .login-box {
        width: 350px;
      }
    }
    
    /* Ultra-wide screens */
    @media (min-width: 1440px) {
      .big-box {
        top: 8vh;
        bottom: 8vh;
        left: 8vw;
        right: 8vw;
      }
    }
    
    /* Portrait orientation adjustments */
    @media (orientation: portrait) and (max-height: 600px) {
      .login-box {
        padding: 15px;
      }
      
      .login-box img {
        width: 60px;
        height: 60px;
        margin-bottom: 10px;
      }
    }
    
    /* Landscape orientation adjustments */
    @media (orientation: landscape) and (max-height: 500px) {
      .big-box {
        top: 2vh;
        bottom: 2vh;
        left: 10vw;
        right: 10vw;
      }
      
      .login-box {
        padding: 20px;
        max-height: 90vh;
      }
      
      .login-box img {
        width: 50px;
        height: 50px;
        margin-bottom: 8px;
      }
    }
    
    /* High-DPI displays */
    @media (-webkit-min-device-pixel-ratio: 2), (min-resolution: 192dpi) {
      .login-box {
        border: 0.5px solid rgba(255,255,255,0.1);
      }
    }
    
    /* Dark mode support */
    @media (prefers-color-scheme: dark) {
      .login-box input[type="text"], 
      .login-box input[type="password"] {
        background: rgba(255,255,255,0.95);
      }
    }
    
    /* Reduced motion support */
    @media (prefers-reduced-motion: reduce) {
      *,
      *::before,
      *::after {
        animation-duration: 0.01ms !important;
        animation-iteration-count: 1 !important;
        transition-duration: 0.01ms !important;
      }
    }
    
    /* Focus visible for accessibility */
    .login-box button:focus-visible {
      outline: 2px solid #fff;
      outline-offset: 2px;
    }
    
    .login-box input:focus-visible {
      outline: none; /* We handle this with box-shadow */
    }
    
    /* Hover support detection */
    @media (hover: none) {
      .login-box button:hover {
        transform: none;
        box-shadow: none;
        background: linear-gradient(135deg, #e63946, #d62828);
      }
      
      .toggle-password:hover {
        transform: translateY(-50%);
        opacity: 0.6;
      }
    }
  </style>
</head>
<body>
  <div class="background back"></div>
  <div class="background front"></div>
  <div class="big-box"></div>
  <div class="container">
    <div class="login-box">
      <img src="{{ url_for('static', filename='logo.png') }}" alt="Logo">
      <h2>Login</h2>
      <form method="POST" id="loginForm" novalidate>
        <input type="text" id="username" name="username" placeholder="Username" autofocus autocomplete="username" inputmode="text">
        <div id="usernameError" class="field-error">Please enter your username</div>

        <div class="password-wrapper">
          <input type="password" id="password" name="password" placeholder="Password" autocomplete="current-password">
          <span class="toggle-password" id="togglePassword" onclick="togglePassword()" role="button" tabindex="0" aria-label="Toggle password visibility">
            <svg id="eyeIcon" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2"
                d="M15 12a3 3 0 11-6 0 3 3 0 016 0z" />
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2"
                d="M2.458 12C3.732 7.943 7.523 5 12 5c4.477 0 8.268 2.943 9.542 7-1.274 4.057-5.065 7-9.542 7-4.477 0-8.268-2.943-9.542-7z" />
            </svg>
          </span>
        </div>
        <div id="passwordError" class="field-error">Please enter your password</div>

        <button type="submit" id="loginBtn">Login</button>
      </form>
      {% if error %}
      <div class="error">{{ error }}</div>
      {% endif %}
    </div>
  </div>

  <script>
    // Enhanced JavaScript with performance optimizations
    let isSubmitting = false;
    
    function togglePassword() {
      if (isSubmitting) return;
      
      const pass = document.getElementById("password");
      const eyeIcon = document.getElementById("eyeIcon");
      
      // Use requestAnimationFrame for smooth updates
      requestAnimationFrame(() => {
        if (pass.type === "password") {
          pass.type = "text";
          eyeIcon.innerHTML = `
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2"
              d="M13.875 18.825A10.05 10.05 0 0112 19c-4.477 0-8.268-2.943-9.542-7a9.956 9.956 0 012.582-4.419M9.88 9.88a3 3 0 104.24 4.24M3 3l18 18" />`;
        } else {
          pass.type = "password";
          eyeIcon.innerHTML = `
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2"
              d="M15 12a3 3 0 11-6 0 3 3 0 016 0z" />
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2"
              d="M2.458 12C3.732 7.943 7.523 5 12 5c4.477 0 8.268 2.943 9.542 7-1.274 4.057-5.065 7-9.542 7-4.477 0-8.268-2.943-9.542-7z" />`;
        }
      });
    }
    
    // Enhanced keyboard support for toggle button
    document.getElementById("togglePassword").addEventListener("keydown", function(e) {
      if (e.key === "Enter" || e.key === " ") {
        e.preventDefault();
        togglePassword();
      }
    });

    const form = document.getElementById("loginForm");
    const username = document.getElementById("username");
    const password = document.getElementById("password");
    const btn = document.getElementById("loginBtn");
    const usernameError = document.getElementById("usernameError");
    const passwordError = document.getElementById("passwordError");

    // Real-time validation with debouncing
    let usernameTimeout, passwordTimeout;
    
    username.addEventListener("input", function() {
      clearTimeout(usernameTimeout);
      usernameTimeout = setTimeout(() => {
        if (this.value.trim()) {
          usernameError.classList.remove("visible");
        }
      }, 300);
    });
    
    password.addEventListener("input", function() {
      clearTimeout(passwordTimeout);
      passwordTimeout = setTimeout(() => {
        if (this.value.trim()) {
          passwordError.classList.remove("visible");
        }
      }, 300);
    });
    
    // Enhanced form submission
    form.addEventListener("submit", function(e) {
      if (isSubmitting) {
        e.preventDefault();
        return;
      }
      
      let valid = true;
      
      // Reset errors first
      usernameError.classList.remove("visible");
      passwordError.classList.remove("visible");
      
      // Use requestAnimationFrame for smooth error display
      requestAnimationFrame(() => {
        if (!username.value.trim()) {
          usernameError.classList.add("visible");
          valid = false;
        }

        if (!password.value.trim()) {
          passwordError.classList.add("visible");
          valid = false;
        }

        if (!valid) {
          // Focus first invalid field
          const firstInvalid = !username.value.trim() ? username : password;
          firstInvalid.focus();
          return;
        }
        
        // If validation passes, show loading state
        isSubmitting = true;
        btn.disabled = true;
        btn.innerHTML = `<div class="spinner"></div>`;
        
        // Add small delay to show loading animation before form submits
        setTimeout(() => {
          form.submit();
        }, 100);
      });
      
      if (!valid) {
        e.preventDefault();
      }
    });
    
    // Enhanced focus management
    document.addEventListener("DOMContentLoaded", function() {
      // Ensure username field gets focus after animations
      setTimeout(() => {
        username.focus();
      }, 1000);
    });
    
    // Performance optimization: Preload background image
    const img = new Image();
    img.src = "{{ url_for('static', filename='background.png') }}";
    
    // Handle form reset on page show (for back button)
    window.addEventListener("pageshow", function(e) {
      if (e.persisted || performance.navigation.type === 2) {
        isSubmitting = false;
        btn.disabled = false;
        btn.innerHTML = "Login";
        usernameError.classList.remove("visible");
        passwordError.classList.remove("visible");
      }
    });
    
    // Prevent double-tap zoom on mobile
    let lastTouchEnd = 0;
    document.addEventListener('touchend', function (event) {
      const now = (new Date()).getTime();
      if (now - lastTouchEnd <= 300) {
        event.preventDefault();
      }
      lastTouchEnd = now;
    }, false);
  </script>
</body>
</html>
""",
        error=error,
    )

@app.route("/logout")
def logout():
    session.pop("user", None)
    return redirect("/")
###############################################################################
# Reception (Vue wizard)
###############################################################################
@app.route("/reception")
def reception():
    if session.get("user") != "reception":
        return redirect("/")
    return render_template_string(r"""
<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8" />
<meta name="viewport" content="width=device-width,initial-scale=1,user-scalable=no" />
<title>Reception — 7-Step Wizard</title>
<link rel="stylesheet" href="https://unpkg.com/@phosphor-icons/web@2.0.3/src/regular/style.css">
<style>
  :root{
    --bg1:#0b0d10; --bg2:#0f1418;
    --card:#E63946; --white:#fff; --muted:rgba(255,255,255,.75);
    --glass:rgba(255,255,255,.06); --radius:20px;
    --shadow-lg:0 22px 60px rgba(2,6,23,.6);
    --ease-spring:cubic-bezier(.22,.61,.36,1);
    
    /* Base dimensions */
    --base-card-width: 380px;
    --base-card-height: 600px;
    --base-font: 16px;
    --base-icon: 120px;
    --base-padding: 28px;
    --base-spacing: 8px;
    --base-border-radius: 12px;
    
    /* Default scale factor */
    --scale: 1;
    
    /* Calculated responsive values */
    --card-width: calc(var(--base-card-width) * var(--scale));
    --card-height: calc(var(--base-card-height) * var(--scale));
    --font-size: calc(var(--base-font) * var(--scale));
    --font-heading: calc(18px * var(--scale));
    --icon-size: calc(var(--base-icon) * var(--scale));
    --padding: calc(var(--base-padding) * var(--scale));
    --spacing: calc(var(--base-spacing) * var(--scale));
    --border-radius: calc(var(--base-border-radius) * var(--scale));
    --touch-target: max(44px, calc(44px * var(--scale)));
  }

  /* Ultra-wide displays (4K+) */
  @media (min-width: 3840px) {
    :root { --scale: 2.5; }
  }

  /* Large 4K displays */
  @media (min-width: 2560px) and (max-width: 3839px) {
    :root { --scale: 2.0; }
  }
  
  /* Standard 4K displays */
  @media (min-width: 1920px) and (max-width: 2559px) {
    :root { --scale: 1.6; }
  }
  
  /* Large desktop */
  @media (min-width: 1440px) and (max-width: 1919px) {
    :root { --scale: 1.3; }
  }
  
  /* Standard desktop */
  @media (min-width: 1200px) and (max-width: 1439px) {
    :root { --scale: 1.1; }
  }
  
  /* Small desktop */
  @media (min-width: 1024px) and (max-width: 1199px) {
    :root { --scale: 1.0; }
  }
  
  /* Large tablet */
  @media (min-width: 768px) and (max-width: 1023px) {
    :root { --scale: 0.85; }
  }
  
  /* Small tablet / Large mobile */
  @media (min-width: 600px) and (max-width: 767px) {
    :root { --scale: 0.75; }
  }
  
  /* Standard mobile */
  @media (min-width: 480px) and (max-width: 599px) {
    :root { --scale: 0.65; }
  }
  
  /* Small mobile */
  @media (min-width: 360px) and (max-width: 479px) {
    :root { --scale: 0.58; }
  }
  
  /* Very small mobile */
  @media (min-width: 320px) and (max-width: 359px) {
    :root { --scale: 0.52; }
  }
  
  /* Tiny displays */
  @media (max-width: 319px) {
    :root { --scale: 0.45; }
  }

  /* Landscape mobile adjustments */
  @media (max-width: 767px) and (orientation: landscape) and (max-height: 500px) {
    :root { --scale: calc(var(--scale) * 0.8); }
  }

  /* Portrait tablet adjustments */
  @media (min-width: 768px) and (max-width: 1023px) and (orientation: portrait) {
    :root { --scale: calc(var(--scale) * 0.9); }
  }

  *{box-sizing:border-box}
  html,body{height:100%}
  body{
    margin:0; font-family:Inter,"Segoe UI",system-ui,-apple-system,sans-serif;
    background:
      radial-gradient(800px 500px at 10% 10%, #11141a 0%, rgba(0,0,0,0) 30%),
      linear-gradient(180deg,var(--bg1),var(--bg2));
    color:var(--white);
    display:flex; justify-content:center; align-items:flex-start;
    padding:calc(56px * var(--scale)) calc(16px * var(--scale)) calc(80px * var(--scale));
    font-size: var(--font-size);
  }

  /* ===== Top Chrome ===== */
  .topbar{
    position:fixed; 
    top:calc(14px * var(--scale)); 
    right:calc(14px * var(--scale)); 
    z-index:1200; 
    display:flex; 
    gap:calc(10px * var(--scale));
  }
  .hamburger{
    width:var(--touch-target); 
    height:var(--touch-target); 
    border-radius:calc(var(--base-border-radius) * var(--scale)); 
    display:flex; align-items:center; justify-content:center;
    background:var(--glass); 
    border:1px solid rgba(255,255,255,.08); 
    cursor:pointer;
    transition:transform .12s ease, background .12s ease;
  }
  .hamburger:hover{
    transform:translateY(calc(-2px * var(--scale))); 
    background:rgba(255,255,255,.12);
  }
  .hamburger svg {
    width:calc(24px * var(--scale));
    height:calc(24px * var(--scale));
    stroke-width: calc(2 * var(--scale));
  }
  .hamburger svg line {
    stroke-width: calc(2 * var(--scale));
  }

  /* ===== Overlay ===== */
  #overlay {
    position: fixed;
    inset: 0;
    background: rgba(0, 0, 0, 0.35);
    opacity: 0;
    pointer-events: none;
    transition: opacity .24s ease;
    z-index: 1198;
  }
  #overlay.active {
    opacity: 1;
    pointer-events: auto;
  }

  /* ===== Drawer (full-height right panel) ===== */
  .drawer {
    position: fixed;
    top: 0;
    right: calc(-280px * var(--scale));
    width: calc(280px * var(--scale));
    height: 100vh;
    z-index: 1199;
    background: #0e1116;
    border-left: 1px solid #1b1f27;
    box-shadow: calc(-16px * var(--scale)) 0 calc(48px * var(--scale)) rgba(0,0,0,.5);
    display: flex;
    flex-direction: column;
    transition: right .3s cubic-bezier(0.22, 1, 0.36, 1);
  }
  .drawer.active { right: 0; }

  /* ===== Drawer Header ===== */
  .drawer-header {
    display: flex;
    align-items: center;
    justify-content: space-between;
    padding: calc(16px * var(--scale)) calc(20px * var(--scale));
    border-bottom: 1px solid #1b1f27;
  }
  .drawer-header h3 { 
    font-size: var(--font-heading); 
    font-weight: 600; 
    color: #fff; 
    margin: 0;
  }
  .drawer-header button {
    font-size: calc(20px * var(--scale)); 
    color: #888; 
    background: none; 
    border: none; 
    cursor: pointer; 
    transition: color .2s ease;
    width: var(--touch-target);
    height: var(--touch-target);
    display: flex;
    align-items: center;
    justify-content: center;
  }
  .drawer-header button:hover { color: #fff; }

  /* ===== Logout at the TOP ===== */
  .drawer .logout {
    margin: calc(16px * var(--scale)) calc(20px * var(--scale));
    padding: calc(14px * var(--scale)) calc(16px * var(--scale));
    border-radius: calc(var(--base-border-radius) * var(--scale));
    border: none;
    cursor: pointer;
    background: linear-gradient(90deg, #e63946, #d2353f);
    color: #fff;
    font-weight: 900;
    font-size: var(--font-size);
    text-align: center;
    box-shadow: 0 calc(10px * var(--scale)) calc(30px * var(--scale)) rgba(0,0,0,.2);
    transition: transform .15s ease, background .3s ease;
    min-height: var(--touch-target);
  }
  .drawer .logout:hover {
    transform: translateY(calc(-2px * var(--scale)));
    background: linear-gradient(90deg, #f04755, #e63946);
  }

  /* ===== Menu Links (Optional Future Items) ===== */
  .drawer .menu-items {
    flex: 1; 
    padding: calc(20px * var(--scale)); 
    display: flex; 
    flex-direction: column; 
    gap: calc(12px * var(--scale));
  }
  .drawer .menu-items a {
    display: block; 
    padding: calc(12px * var(--scale)) calc(14px * var(--scale)); 
    border-radius: calc(10px * var(--scale)); 
    background: #1b1f27; 
    color: #eee; 
    text-decoration: none; 
    font-size: calc(15px * var(--scale)); 
    transition: background .2s ease, color .2s ease;
    min-height: var(--touch-target);
    display: flex;
    align-items: center;
  }
  .drawer .menu-items a:hover { background: #2a2f3a; color: #fff; }

/* === Apple-style fast-start, slow-end card slide === */
.card.left-off, .card.prev, .card.active, .card.next, .card.right-off {
    transition: transform 0.18s cubic-bezier(0.4, 0, 0.2, 1), 
                opacity 0.18s ease-out, 
                filter 0.18s ease-out;
}

/* Off-screen cards slightly closer to avoid overlap */
.card.left-off  { 
  transform: translateX(-105%) scale(0.92); 
  opacity: 0; 
  z-index: 1; 
  filter: blur(calc(1px * var(--scale))); 
}
.card.prev      { 
  transform: translateX(-50%) scale(0.92) rotateY(4deg); 
  opacity: 0.84; 
  z-index: 2; 
  filter: blur(calc(0.8px * var(--scale))); 
}
.card.active    { 
  transform: translateX(0) scale(1) rotateY(0); 
  opacity: 1; 
  z-index: 3; 
  filter: blur(0); 
}
.card.next      { 
  transform: translateX(50%) scale(0.92) rotateY(-4deg); 
  opacity: 0.84; 
  z-index: 2; 
  filter: blur(calc(0.8px * var(--scale))); 
}
.card.right-off { 
  transform: translateX(105%) scale(0.92); 
  opacity: 0; 
  z-index: 1; 
  filter: blur(calc(1px * var(--scale))); 
}

  /* ===== Reception Card Container (Centered + Smooth Animations) ===== */
  .cards-container {
    position: fixed;
    top: 50%;
    left: 50%;
    transform: translate(-50%, -50%);
    width: 100%;
    height: 100%;
    display: flex;
    justify-content: center;
    align-items: center;
    overflow: hidden;
    z-index: 1000;
  }

  /* Stage (Wrapper for the stack of cards) */
  .stage {
    width: 100%;
    max-width: 96vw;
    height: auto;
    position: relative;
    display: flex;
    justify-content: center;
    align-items: center;
    padding: calc(20px * var(--scale));
  }

  /* Stack of cards */
  .stack {
    position: relative;
    width: 100%;
    max-width: calc(760px * var(--scale));
    height: calc(var(--card-height) + 40px * var(--scale));
    perspective: calc(1600px * var(--scale));
    display: flex;
    justify-content: center;
    align-items: center;
  }

  /* ===== Individual Cards ===== */
  .card {
    width: var(--card-width);
    min-height: var(--card-height);
    border-radius: calc(18px * var(--scale));
    background: var(--card);
    color: #fff;
    box-shadow: var(--shadow-lg);
    padding: var(--padding);
    display: flex;
    flex-direction: column;
    align-items: center;
    text-align: center;

    position: absolute;
    top: 0; bottom: 0; left: 0; right: 0;
    margin: auto;
    transform-origin: center;
    will-change: transform, filter, opacity;
    transition:
      transform 0.9s cubic-bezier(0.22, 1, 0.36, 1),
      opacity 0.6s ease,
      filter 0.6s ease;
  }

  /* Animation effects for each card in different states */
  .card.left-off { 
    transform: translateX(-140%) scale(.92); 
    opacity: 0; 
    filter: blur(calc(1px * var(--scale))); 
    z-index: 1; 
  }
  .card.prev { 
    transform: translateX(-52%) scale(.92) rotateY(4deg); 
    opacity: .84; 
    filter: blur(calc(.8px * var(--scale))); 
    z-index: 2; 
  }
  .card.active { 
    transform: translateX(0) scale(1) rotateY(0); 
    opacity: 1; 
    filter: blur(0); 
    z-index: 3; 
  }
  .card.next { 
    transform: translateX(52%) scale(.92) rotateY(-4deg); 
    opacity: .84; 
    filter: blur(calc(.8px * var(--scale))); 
    z-index: 2; 
  }
  .card.right-off {
    transform: translateX(140%) scale(.92); 
    opacity: 0; 
    filter: blur(calc(1px * var(--scale))); 
    z-index: 1;
  }

  /* Back button inside each card */
  .card .back {
    width: var(--touch-target); 
    height: var(--touch-target); 
    border-radius: calc(var(--base-border-radius) * var(--scale));
    display: flex; align-items: center; justify-content: center;
    background: rgba(255, 255, 255, .12); 
    border: 1px solid rgba(255, 255, 255, .18); 
    cursor: pointer;
    visibility: hidden; opacity: 0;
    transition: transform .12s ease, opacity .12s ease;
    font-size: calc(20px * var(--scale));
  }

  /* Input fields inside each card */
  .card input, .card select {
    width: calc(260px * var(--scale));
    margin: 0 auto calc(20px * var(--scale)) auto;
    padding: calc(12px * var(--scale));
    border-radius: calc(8px * var(--scale));
    border: 1px solid rgba(255, 255, 255, .2);
    background: transparent;
    color: #fff;
    font-size: var(--font-size);
    outline: none;
    min-height: var(--touch-target);
  }

  /* Button styling */
  .card button {
    width: calc(160px * var(--scale));
    height: calc(48px * var(--scale));
    min-height: var(--touch-target);
    font-size: var(--font-size);
    border-radius: calc(24px * var(--scale));
    margin: calc(20px * var(--scale)) auto 0 auto;
  }

  /* ===== Fix Body and Overflow ===== */
  html, body {
    margin: 0;
    padding: 0;
    height: 100%;
    overflow: hidden;
  }

  .card-top{ 
    width:100%; 
    display:flex; 
    align-items:center; 
    justify-content:space-between; 
    margin-bottom: calc(12px * var(--scale));
  }
  .back{
    width: var(--touch-target); 
    height: var(--touch-target); 
    border-radius: calc(var(--base-border-radius) * var(--scale)); 
    display:flex; align-items:center; justify-content:center;
    background:rgba(255,255,255,.12); 
    border:1px solid rgba(255,255,255,.18); 
    cursor:pointer; 
    visibility:hidden; opacity:0;
    transition:transform .12s ease, opacity .12s ease;
    font-size: calc(20px * var(--scale));
  }
  .back.show{ visibility:visible; opacity:1; }
  .back:hover{ transform:translateX(calc(-3px * var(--scale))); }
  
  .plate-icon {
    width: calc(150px * var(--scale)); 
    height: calc(44px * var(--scale)); 
    border: calc(10px * var(--scale)) solid #fff; 
    border-radius: calc(6px * var(--scale)); 
    background: transparent; 
    display: inline-block;
  }

  .icon {
    margin: calc(8px * var(--scale)) auto calc(6px * var(--scale)); 
    display:flex; 
    align-items:center; 
    justify-content:center; 
    color:#fff; 
    min-height: var(--icon-size);
  }
  .icon i { font-size: var(--icon-size); }

  .icon svg{ 
    width: calc(44px * var(--scale)); 
    height: calc(44px * var(--scale)); 
    stroke:#e63946; 
    fill:none; 
    stroke-width:1.8; 
    stroke-linecap:round; 
    stroke-linejoin:round; 
  }
  .heading{ 
    font-size: var(--font-heading); 
    letter-spacing:.12em; 
    font-weight:900; 
    text-transform:uppercase; 
    margin-top: calc(4px * var(--scale)); 
    margin-bottom: calc(8px * var(--scale)); 
  }

  .field{ 
    width:100%; 
    margin: calc(12px * var(--scale)) 0; 
  }
  .input{ 
    width:100%; 
    border-radius: calc(var(--base-border-radius) * var(--scale)); 
    padding: calc(14px * var(--scale)) calc(14px * var(--scale)); 
    background:#fff; 
    border:0; 
    color:#111; 
    font-size: var(--font-size); 
    outline:none;
    min-height: var(--touch-target);
  }
  .row-2{ 
    display:grid; 
    grid-template-columns: calc(110px * var(--scale)) 1fr; 
    gap: calc(10px * var(--scale)); 
  }
  /* FIX: keep step-2 inputs inside the card and aligned with grid */
  .row-2 .input{ 
    width:100%; 
    margin:0; 
  }
  .select-toggle{
    width:100%; 
    display:flex; 
    align-items:center; 
    justify-content:space-between; 
    gap: calc(10px * var(--scale));
    padding: calc(14px * var(--scale)); 
    border-radius: calc(var(--base-border-radius) * var(--scale)); 
    background:#fff; 
    color:#111; 
    cursor:pointer; 
    font-weight:700;
    font-size: var(--font-size);
    min-height: var(--touch-target);
  }

  .error{ 
    color:#FFD2D2; 
    font-size: calc(13px * var(--scale)); 
    margin-top: calc(8px * var(--scale)); 
    display:none; 
  }

  .progress{ 
    display:flex; 
    justify-content:center; 
    gap: calc(8px * var(--scale)); 
    margin-top:auto; 
    padding-bottom: calc(8px * var(--scale)); 
  }
  .dot{ 
    width: calc(10px * var(--scale)); 
    height: calc(10px * var(--scale)); 
    border-radius:50%; 
    background:rgba(255,255,255,.46); 
  }
  .dot.on{ 
    background:#fff; 
    transform:scale(1.1); 
  }

  .footer{ 
    display:flex; 
    justify-content:center; 
    gap: calc(12px * var(--scale)); 
    margin-top: calc(12px * var(--scale)); 
  }
  .pill{ 
    background:#fff; 
    color:#0b0d10; 
    border:none; 
    padding: calc(12px * var(--scale)) calc(22px * var(--scale)); 
    border-radius:999px; 
    font-weight:900; 
    cursor:pointer; 
    box-shadow:0 calc(10px * var(--scale)) calc(30px * var(--scale)) rgba(2,6,23,.45);
    font-size: var(--font-size);
    min-height: var(--touch-target);
  }
  .pill:disabled{ 
    opacity:.55; 
    cursor:not-allowed; 
    box-shadow:none; 
  }

  /* Picker Modal */
  .picker-overlay{ 
    position:fixed; 
    inset:0; 
    display:flex; 
    align-items:center; 
    justify-content:center; 
    background:rgba(0,0,0,.45); 
    z-index:1400; 
    opacity:0; 
    pointer-events:none; 
    transition:opacity .18s ease; 
  }
  .picker-overlay.show{ opacity:1; pointer-events:auto; }
  .picker {
    width: min(calc(520px * var(--scale)), 94vw); 
    max-height:68vh; 
    background:#000; 
    border-radius: calc(16px * var(--scale)); 
    padding: calc(12px * var(--scale)); 
    border:1px solid #1a1a1a; 
    box-shadow:0 calc(30px * var(--scale)) calc(90px * var(--scale)) rgba(0,0,0,.6);
  }
  .picker-head{ 
    font-weight:800; 
    font-size: calc(13px * var(--scale)); 
    color:#bbb; 
    padding: calc(6px * var(--scale)) calc(8px * var(--scale)); 
    text-transform:uppercase; 
    letter-spacing:.08em; 
  }
  .wheel{ 
    overflow:auto; 
    max-height:44vh; 
    scroll-snap-type:y mandatory; 
    padding-right: calc(8px * var(--scale)); 
    margin-top: calc(6px * var(--scale)); 
  }
  .opt {
    width: 90%; 
    height: var(--touch-target); 
    margin: calc(6px * var(--scale)) auto; 
    border-radius: calc(8px * var(--scale)); 
    background: #0f0f0f; 
    border: 1px solid #1b1b1b; 
    color: #fff; 
    font-size: var(--font-size);
    display: flex; 
    justify-content: center; 
    align-items: center; 
    cursor: pointer; 
    text-align: center;
  }
  .opt:hover { background: #131313; }
  .opt.sel{ outline:2px solid #fff; }
  .picker-actions{ 
    display:flex; 
    justify-content:flex-end; 
    gap: calc(10px * var(--scale)); 
    padding-top: calc(8px * var(--scale)); 
  }
  .btn-ghost{ 
    background:transparent; 
    border:1px solid #222; 
    color:#fff; 
    padding: calc(8px * var(--scale)) calc(12px * var(--scale)); 
    border-radius: calc(10px * var(--scale)); 
    cursor:pointer;
    font-size: var(--font-size);
    min-height: var(--touch-target);
  }

  /* === Toasts (centered, fade, one-at-a-time) === */
  .toast {
    position: fixed;
    top: 50%;
    left: 50%;
    transform: translate(-50%, -50%);
    padding: calc(18px * var(--scale)) calc(28px * var(--scale));
    border-radius: calc(16px * var(--scale));
    font-size: calc(14px * var(--scale));
    font-weight: 500;
    display: flex;
    align-items: center;
    justify-content: space-between;
    gap: calc(20px * var(--scale));
    box-shadow: 0 calc(6px * var(--scale)) calc(20px * var(--scale)) rgba(0,0,0,0.25);
    z-index: 2000;
    min-width: calc(360px * var(--scale));
    max-width: calc(360px * var(--scale));
    opacity: 0;
    pointer-events: none;
    transition: all 0.35s ease;
  }
  .toast.show {
    opacity: 1;
    pointer-events: auto;
    transform: translate(-50%, -50%) scale(1.02);
  }
  .toast.hide {
    opacity: 0;
    pointer-events: none;
    transform: translate(-50%, -50%) scale(0.98);
  }
  .toast-success { background: linear-gradient(135deg, #2ecc71, #27ae60); color: #fff; }
  .toast-error { background: #b71c1c; color: #fff; }
  .toast-close { 
    font-size: calc(14px * var(--scale)); 
    font-weight: 400; 
    color: rgba(255,255,255,0.85); 
    cursor: pointer; 
    transition: color 0.2s ease;
    min-width: calc(40px * var(--scale));
    text-align: center;
  }
  .toast-close:hover { color: #fff; }

  /* Responsive adjustments for specific screen sizes */
  @media (max-width: 767px) {
    .cards-container {
      padding: calc(10px * var(--scale));
    }
    
    body {
      padding: calc(40px * var(--scale)) calc(10px * var(--scale)) calc(60px * var(--scale));
    }
  }

  /* High DPI displays enhancement */
  @media (-webkit-min-device-pixel-ratio: 2), (min-resolution: 192dpi) {
    .card {
      box-shadow: 0 calc(22px * var(--scale)) calc(60px * var(--scale)) rgba(2,6,23,.8);
    }
  }
</style>
</head>
<body>

<!-- Top chrome -->
<div class="topbar">
  <div class="hamburger" id="menuToggle" aria-label="Menu" title="Menu">
    <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="none" stroke="white" stroke-linecap="round" stroke-linejoin="round">
      <line x1="4" y1="8" x2="20" y2="8"/>
      <line x1="4" y1="12" x2="20" y2="12"/>
      <line x1="4" y1="16" x2="20" y2="16"/>
    </svg>
  </div>
</div>

<!-- Overlay -->
<div id="overlay"></div>

<!-- Drawer -->
<div class="drawer" id="drawer">
  <div class="drawer-header">
    <h3>MENU</h3>
  </div>
  <button class="logout" onclick="logout()">Logout</button>
</div>

<div class="cards-container">
  <div class="stage" id="stage">
    <div class="stack" id="stack">
    <!-- STEP 1 -->
    <div class="card" data-step="0">
      <div class="card-top">
        <div class="back" id="back-0" aria-label="Go back"></div>
        <div style="width:44px"></div>
      </div>
      <div class="icon"><i class="ph ph-user-circle"></i></div>
      <div class="heading">ADD CUSTOMER NAME</div>
      <div class="field">
        <input id="customer" class="input" placeholder="Customer Name" minlength="2" oninput="this.value=this.value.replace(/[^A-Za-z ]/g,'')" />
        <div class="error" id="err_customer">At least 2 letters (A–Z and spaces).</div>
      </div>
      <div class="progress"></div>
      <div class="footer">
        <button class="pill" id="next-0" disabled>Next</button>
      </div>
    </div>

    <!-- STEP 2 -->
    <div class="card" data-step="1">
      <div class="card-top">
        <div class="back" id="back-1" aria-label="Go back">&#8592;</div>
        <div style="width:44px"></div>
      </div>
      <div class="icon"><div class="plate-icon"></div></div>
      <div class="heading">ADD VEHICLE NUMBER</div>
      <div class="field row-2">
        <input id="vehicle_code" class="input" placeholder="Code" maxlength="2" oninput="this.value=this.value.toUpperCase().replace(/[^A-Z]/g,'')" />
        <input id="vehicle_number" class="input" placeholder="Number" maxlength="5" oninput="this.value=this.value.replace(/[^0-9]/g,'')" />
      </div>
      <div class="error" id="err_vehicle">Vehicle code (1–2 letters) & number (1–5 digits) required.</div>
      <div class="progress"></div>
      <div class="footer">
        <button class="pill" id="next-1" disabled>Next</button>
      </div>
    </div>

    <!-- STEP 3 -->
    <div class="card" data-step="2">
      <div class="card-top">
        <div class="back" id="back-2" aria-label="Go back">&#8592;</div>
        <div style="width:44px"></div>
      </div>
      <div class="icon"><i class="ph ph-car"></i></div>
      <div class="heading">ADD VEHICLE NAME</div>
      <div class="field">
        <input id="vehicle_name" class="input" placeholder="Vehicle Name" minlength="2" oninput="this.value=this.value.replace(/[^A-Za-z0-9 ]/g,'')" />
        <div class="error" id="err_vehicle_name">At least 2 characters (letters/numbers allowed).</div>
      </div>
      <div class="progress"></div>
      <div class="footer">
        <button class="pill" id="next-2" disabled>Next</button>
      </div>
    </div>

    <!-- STEP 4 -->
    <div class="card" data-step="3">
      <div class="card-top">
        <div class="back" id="back-3" aria-label="Go back">&#8592;</div>
        <div style="width:44px"></div>
      </div>
      <div class="icon"><i class="ph ph-gear"></i></div>
      <div class="heading">SELECT DEPARTMENT</div>
      <div class="field">
        <input type="hidden" id="department" />
        <div class="select-toggle" data-target="department" id="toggle-department">
          <span class="val" id="label_department">Tap to select...</span>
          <span class="chev" aria-hidden="true">▾</span>
        </div>
        <div class="error" id="err_department">Please select a department.</div>
      </div>
      <div class="progress"></div>
      <div class="footer">
        <button class="pill" id="next-3" disabled>Next</button>
      </div>
    </div>

    <!-- STEP 5 -->
    <div class="card" data-step="4">
      <div class="card-top">
        <div class="back" id="back-4" aria-label="Go back">&#8592;</div>
        <div style="width:44px"></div>
      </div>
      <div class="icon"><i class="ph ph-user"></i></div>
      <div class="heading">SELECT TECHNICIAN</div>
      <div class="field">
        <input type="hidden" id="technician" />
        <div class="select-toggle" data-target="technician" id="toggle-technician">
          <span class="val" id="label_technician">Tap to select...</span>
          <span class="chev" aria-hidden="true">▾</span>
        </div>
        <div class="error" id="err_technician">Please select a technician.</div>
      </div>
      <div class="progress"></div>
      <div class="footer">
        <button class="pill" id="next-4" disabled>Next</button>
      </div>
    </div>

    <!-- STEP 6 -->
    <div class="card" data-step="5">
      <div class="card-top">
        <div class="back" id="back-5" aria-label="Go back">&#8592;</div>
        <div style="width:44px"></div>
      </div>
      <div class="icon"><i class="ph ph-wrench"></i></div>
      <div class="heading">SELECT SERVICE</div>
      <div class="field">
        <input type="hidden" id="service" />
        <div class="select-toggle" data-target="service" id="toggle-service">
          <span class="val" id="label_service">Tap to select...</span>
          <span class="chev" aria-hidden="true">▾</span>
        </div>
        <div class="error" id="err_service">Please select a service.</div>
      </div>
      <div class="progress"></div>
      <div class="footer">
        <button class="pill" id="next-5" disabled>Next</button>
      </div>
    </div>

    <!-- STEP 7 -->
    <div class="card" data-step="6">
      <div class="card-top">
        <div class="back" id="back-6" aria-label="Go back">&#8592;</div>
        <div style="width:44px"></div>
      </div>
      <div class="icon"><i class="ph ph-flag"></i></div>
      <div class="heading">SELECT STATUS</div>
      <div class="field">
        <input type="hidden" id="status" />
        <div class="select-toggle" data-target="status" id="toggle-status">
          <span class="val" id="label_status">Tap to select...</span>
          <span class="chev" aria-hidden="true">▾</span>
        </div>
        <div class="error" id="err_status">Please select a status.</div>
      </div>
      <div class="progress"></div>
      <div class="footer">
        <button class="pill" id="next-6" disabled>Submit</button>
      </div>
   </div>
  </div>
</div>

<!-- Picker modal -->
<div class="picker-overlay" id="pickerOverlay" aria-hidden="true">
  <div class="picker" role="dialog" aria-modal="true" aria-labelledby="pickerTitle">
    <div class="picker-head" id="pickerTitle">Select</div>
    <div class="wheel" id="pickerWheel"></div>
    <div class="picker-actions">
      <button class="btn-ghost" id="pickerCancel">Cancel</button>
    </div>
  </div>
</div>

<!-- Toasts -->
<div id="toast-success" class="toast toast-success" onclick="closeToast('toast-success')">
  <span>Vehicle added successfully</span>
  <span class="toast-close">Close</span>
</div>
<div id="toast-error" class="toast toast-error" onclick="closeToast('toast-error')">
  <span>Sorry, network issue. Please try again later</span>
  <span class="toast-close">Close</span>
</div>

<script>
/* ===== Server options ===== */
const OPTIONS = {
  department: {{ departments|tojson }},
  technician: {{ technicians|tojson }},
  service:    {{ services|tojson }},
  status:     {{ statuses|tojson }}
};

/* ===== Cards / stack ===== */
const cards = Array.from(document.querySelectorAll('.card'));
let current = 0;
let submitLock = false; // guard to prevent double-submit

function renderDots(){
  cards.forEach((c, idx)=>{
    const p = c.querySelector('.progress');
    if(!p) return;
    if(p.children.length === 0){
      for(let i=0;i<7;i++){
        const d = document.createElement('div');
        d.className = 'dot';
        p.appendChild(d);
      }
    }
    [...p.children].forEach((d,i)=> d.classList.toggle('on', i===idx));
  });
}
function layout(){
  cards.forEach((c,i)=>{
    c.classList.remove('left-off','prev','active','next','right-off');
    const d = i - current;
    if(d === 0) c.classList.add('active');
    else if(d === -1) c.classList.add('prev');
    else if(d === 1) c.classList.add('next');
    else if(d < -1) c.classList.add('left-off');
    else c.classList.add('right-off');
    const back = c.querySelector('.back');
    if(back){ back.classList.toggle('show', current > 0 && i===current); }
  });
  renderDots();
  updateNextState();
}
layout();

/* ===== Validation ===== */
function validateName(){
  const v = document.getElementById('customer').value.trim();
  return /^[A-Za-z ]{2,}$/.test(v);
}
function validateVehicle(){
  const code = (document.getElementById('vehicle_code').value||'').trim();
  const num  = (document.getElementById('vehicle_number').value||'').trim();
  return /^[A-Z]{1,2}$/.test(code) && /^[0-9]{1,5}$/.test(num);
}
function validateVehicleName(){
  const v = document.getElementById('vehicle_name').value.trim();
  return /^[A-Za-z0-9 ]{2,}$/.test(v);
}
function hasValHidden(id){ return !!(document.getElementById(id).value || '').trim(); }

function isStepValid(i){
  switch(i){
    case 0: return validateName();
    case 1: return validateVehicle();
    case 2: return validateVehicleName();
    case 3: return hasValHidden('department');
    case 4: return hasValHidden('technician');
    case 5: return hasValHidden('service');
    case 6: return hasValHidden('status');
    default: return true;
  }
}
function showErrors(i){
  switch(i){
    case 0: document.getElementById('err_customer').style.display = validateName()?'none':'block'; break;
    case 1: document.getElementById('err_vehicle').style.display = validateVehicle()?'none':'block'; break;
    case 2: document.getElementById('err_vehicle_name').style.display = validateVehicleName()?'none':'block'; break;
    case 3: document.getElementById('err_department').style.display = hasValHidden('department')?'none':'block'; break;
    case 4: document.getElementById('err_technician').style.display = hasValHidden('technician')?'none':'block'; break;
    case 5: document.getElementById('err_service').style.display = hasValHidden('service')?'none':'block'; break;
    case 6: document.getElementById('err_status').style.display = hasValHidden('status')?'none':'block'; break;
  }
}
function updateNextState(){
  const nextBtn = cards[current].querySelector('.pill');
  if(nextBtn) nextBtn.disabled = !isStepValid(current);
}

/* live validation hooks */
['customer','vehicle_code','vehicle_number','vehicle_name'].forEach(id=>{
  const el = document.getElementById(id);
  if(el) el.addEventListener('input', updateNextState);
});
['department','technician','service','status'].forEach(id=>{
  const el = document.getElementById(id);
  if(el) el.addEventListener('change', updateNextState);
});

/* ===== Navigation ===== */
function next(){
  if(!isStepValid(current)){
    showErrors(current);
    updateNextState();
    return;
  }
  if(current < cards.length - 1){
    current++;
    layout();
    focusFirst(current);
  } else {
    submitData();
  }
}
function back(){
  if(current > 0){
    current--;
    layout();
    focusFirst(current);
  }
}
/* buttons */
for(let i=0;i<7;i++){
  const btn = document.getElementById('next-'+i);
  if(btn) btn.addEventListener('click', ()=>{ if(i===current) next(); });
}
document.querySelectorAll('.back').forEach(b=> b.addEventListener('click', back));
/* enter key advances if valid (disabled while picker is open) */
document.addEventListener('keydown', (e)=>{
  if(e.key === 'Enter'){
    if(document.getElementById('pickerOverlay').classList.contains('show')) return;
    e.preventDefault();
    const btn = cards[current].querySelector('.pill');
    if(btn && !btn.disabled) next();
  }
});
function focusFirst(i){
  const el = cards[i].querySelector('input:not([type="hidden"]),.select-toggle');
  if(el && el.focus) el.focus();
}

/* ===== Picker modal ===== */
const pickerOverlay = document.getElementById('pickerOverlay');
const pickerWheel = document.getElementById('pickerWheel');
const pickerCancel = document.getElementById('pickerCancel');
const pickerTitle = document.getElementById('pickerTitle');
let pickerTarget = null;
let tempValue = null;

function openPicker(target){
  pickerTarget = target;
  tempValue = document.getElementById(target).value || null;
  pickerTitle.textContent = 'Select ' + target.charAt(0).toUpperCase() + target.slice(1);
  pickerWheel.innerHTML = '';
  const items = OPTIONS[target] || [];
  items.forEach(val=>{
    const row = document.createElement('div');
    row.className = 'opt' + (val === tempValue ? ' sel' : '');
    row.textContent = val;
    row.onclick = ()=>{ tempValue = val; commitPicker(); };
    pickerWheel.appendChild(row);
  });
  pickerOverlay.classList.add('show');
}
function commitPicker(){
  if(!pickerTarget) return;
  document.getElementById(pickerTarget).value = tempValue || '';
  const label = document.getElementById('label_'+pickerTarget);
  if(label) label.textContent = tempValue || 'Tap to select...';
  pickerOverlay.classList.remove('show');
  updateNextState();
  pickerTarget = null; tempValue = null;
}
function closePicker(){ pickerOverlay.classList.remove('show'); pickerTarget=null; tempValue=null; }
pickerCancel.addEventListener('click', closePicker);
pickerOverlay.addEventListener('click', (e)=>{ if(e.target === pickerOverlay) closePicker(); });
document.querySelectorAll('.select-toggle').forEach(el=>{
  el.addEventListener('click', ()=> openPicker(el.getAttribute('data-target')));
});

/* ===== Toasts ===== */
function showToast(id) {
  document.querySelectorAll(".toast.show").forEach(t => {
    t.classList.remove("show");
    t.classList.add("hide");
  });
  const toast = document.getElementById(id);
  if (!toast) return;
  toast.classList.remove("hide");
  toast.classList.add("show");
  const duration = (id === "toast-error") ? 5000 : 3000;
  setTimeout(() => closeToast(id), duration);
}
function closeToast(id) {
  const toast = document.getElementById(id);
  if (!toast) return;
  toast.classList.remove("show");
  toast.classList.add("hide");
}

/* ===== Submit ===== */
async function submitData(){
  if(submitLock) return;

  // final sweep for validation
  for(let i=0;i<cards.length;i++){
    if(!isStepValid(i)){
      current = i; layout(); showErrors(i); return;
    }
  }

  const payload = {
    customer: (document.getElementById('customer').value||'').trim(),
    vehicle_name: (document.getElementById('vehicle_name').value||'').trim(),
    department: (document.getElementById('department').value||'').trim(),
    technician: (document.getElementById('technician').value||'').trim(),
    service: (document.getElementById('service').value||'').trim(),
    status: (document.getElementById('status').value||'').trim()
  };
  const code = (document.getElementById('vehicle_code').value||'').toUpperCase().trim();
  const num  = (document.getElementById('vehicle_number').value||'').trim();
  payload.vehicle_no = [code, num].filter(Boolean).join(' ');

  submitLock = true;
  const btn = cards[current].querySelector('.pill');
  if(btn) btn.disabled = true;

  try {
    const res = await fetch('/api/add', {
      method:'POST',
      headers:{'Content-Type':'application/json'},
      body: JSON.stringify(payload)
    });

    if (res.ok) {
      showToast('toast-success');
     setTimeout(()=> location.reload(), 1200);
    } else {
      showToast('toast-error');
      submitLock = false; if(btn) btn.disabled = false;
    }
  } catch(e){
    showToast('toast-error');
    submitLock = false; if(btn) btn.disabled = false;
  }
}

/* ===== Drawer ===== */
const menuToggle = document.getElementById('menuToggle');
const drawer = document.getElementById('drawer');
const overlay = document.getElementById('overlay');

function openDrawer() {
  drawer.classList.add('active');
  overlay.classList.add('active');
  drawer.setAttribute('aria-hidden','false');
  menuToggle.style.opacity = '0';
  menuToggle.style.pointerEvents = 'none';
}
function closeDrawer() {
  drawer.classList.remove('active');
  overlay.classList.remove('active');
  drawer.setAttribute('aria-hidden','true');
  menuToggle.style.opacity = '1';
  menuToggle.style.pointerEvents = 'auto';
}
menuToggle.addEventListener('click', openDrawer);
overlay.addEventListener('click', closeDrawer);

/* ===== Logout ===== */
function logout() {
  window.location.href = "{{ url_for('logout') }}";
}

/* init */
renderDots();
updateNextState();
</script>
</body>
</html>
""",
        departments=departments, technicians=technicians, services=services, statuses=STATUSES
    )
###############################################################################
# Staff
###############################################################################
@app.route("/staff")
def staff():
    if session.get("user") != "staff":
        return redirect("/")

    vehicles = read_vehicles()

    return render_template_string(
        r"""<!doctype html>
<html>
<head>
  <meta name="viewport" content="width=device-width, initial-scale=1, maximum-scale=1, user-scalable=no">
  <title>Staff Panel</title>
  <link rel="stylesheet" href="https://unpkg.com/@phosphor-icons/web@2.0.3/src/regular/style.css">
  <style>
      /* Hide scrollbars */
    ::-webkit-scrollbar {
      display: none;
    }
    * {
      scrollbar-width: none;
      -ms-overflow-style: none;
    }
    .scrollable::-webkit-scrollbar {
      display: none;
    }

    body {
      margin: 0;
      font-family: Inter, "Segoe UI", system-ui, -apple-system, sans-serif;
      background: radial-gradient(800px 500px at 10% 10%, #11141a 0%, rgba(0,0,0,0) 30%), linear-gradient(180deg, #0b0d10, #0f1418);
      color: #fff;
      min-height: 100vh;
      overflow-x: hidden;
      -webkit-overflow-scrolling: touch;
      overscroll-behavior: none;
      background-attachment: fixed;
    }
    
    html {
      -webkit-overflow-scrolling: touch;
      overscroll-behavior: none;
    }

    /* Top Controls - Responsive */
    .top-controls {
      position: fixed;
      top: 16px;
      right: 16px;
      z-index: 50;
      display: flex;
      gap: 12px;
      transition: opacity 0.15s ease;
    }
    
    @media (max-width: 480px) {
      .top-controls {
        top: 8px;
        right: 8px;
        gap: 8px;
      }
    }
    
    @media (max-width: 360px) {
      .top-controls {
        top: 4px;
        right: 4px;
        gap: 6px;
      }
    }
    
    .top-controls.fade {
      opacity: 0;
      transform: translateY(-10px);
      pointer-events: none;
    }

    .top-controls.fade .search-input-container {
      opacity: 0.5;
      transition: opacity 0.3s ease;
    }
    
    .control-btn {
      width: 44px;
      height: 44px;
      border-radius: 12px;
      display: flex;
      align-items: center;
      justify-content: center;
      background: rgba(255,255,255,.06);
      border: 1px solid rgba(255,255,255,.08);
      backdrop-filter: blur(8px);
      cursor: pointer;
      transition: transform 0.3s ease;
      position: relative;
    }
    
    @media (max-width: 480px) {
      .control-btn {
        width: 40px;
        height: 40px;
        border-radius: 10px;
      }
    }
    
    @media (max-width: 360px) {
      .control-btn {
        width: 36px;
        height: 36px;
        border-radius: 8px;
      }
    }
    
    .control-btn:hover {
      transform: translateY(-2px);
    }

    /* Search - Responsive */
    .search-container {
      display: flex;
      align-items: center;
      gap: 8px;
    }
    
    .search-input-container {
      display: none;
      align-items: center;
      background: rgba(255,255,255,.06);
      border: 1px solid rgba(255,255,255,.08);
      border-radius: 12px;
      padding: 12px 16px;
      backdrop-filter: blur(8px);
      transition: all 0.3s ease;
      animation: slideInFromRight 0.3s ease;
    }
    
    @media (max-width: 768px) {
      .search-input-container {
        padding: 10px 12px;
        border-radius: 10px;
      }
    }
    
    @media (max-width: 480px) {
      .search-input-container {
        padding: 8px 10px;
        border-radius: 8px;
      }
    }
    
    .search-input-container.show {
      display: flex;
    }
    
    .search-input {
      background: transparent;
      border: none;
      color: #fff;
      outline: none;
      width: 256px;
      margin-left: 8px;
    }
    
    @media (max-width: 768px) {
      .search-input {
        width: 200px;
      }
    }
    
    @media (max-width: 480px) {
      .search-input {
        width: 150px;
        margin-left: 6px;
      }
    }
    
    @media (max-width: 360px) {
      .search-input {
        width: 120px;
        margin-left: 4px;
      }
    }
    
    .search-input::placeholder {
      color: rgba(255,255,255,0.5);
    }
    
    .search-clear {
      margin-left: 8px;
      color: rgba(255,255,255,0.75);
      background: none;
      border: none;
      cursor: pointer;
    }

    /* Watch List - Responsive */
    .watch-badge {
      position: absolute;
      top: -4px;
      right: -4px;
      width: 20px;
      height: 20px;
      border-radius: 50%;
      background: #E63946;
      color: #fff;
      font-size: 12px;
      font-weight: 600;
      display: flex;
      align-items: center;
      justify-content: center;
    }
    
    @media (max-width: 480px) {
      .watch-badge {
        width: 18px;
        height: 18px;
        font-size: 10px;
        top: -3px;
        right: -3px;
      }
    }

    .watch-dropdown {
      position: absolute;
      top: 100%;
      right: 0;
      margin-top: 8px;
      width: 384px;
      background: #0e1116;
      border: 1px solid #1b1f27;
      border-radius: 16px;
      backdrop-filter: blur(8px);
      box-shadow: 0 25px 50px rgba(0,0,0,0.25);
      z-index: 60;
      display: none;
      opacity: 0;
      transform: translateY(-8px);
      transition: opacity 0.3s ease, transform 0.3s ease;
    }
    
    @media (max-width: 768px) {
      .watch-dropdown {
        width: 320px;
        border-radius: 12px;
      }
    }
    
    @media (max-width: 480px) {
      .watch-dropdown {
        width: 280px;
        border-radius: 10px;
        margin-top: 6px;
      }
    }
    
    @media (max-width: 360px) {
      .watch-dropdown {
        width: 250px;
        border-radius: 8px;
        margin-top: 4px;
      }
    }
    
    .watch-dropdown.show {
      display: block;
      opacity: 1;
      transform: translateY(0);
    }
    
    .watch-dropdown-header {
      padding: 20px;
      border-bottom: 1px solid #1b1f27;
    }
    
    @media (max-width: 480px) {
      .watch-dropdown-header {
        padding: 16px;
      }
    }
    
    @media (max-width: 360px) {
      .watch-dropdown-header {
        padding: 12px;
      }
    }
    
    .watch-dropdown-header h3 {
      font-size: 18px;
      font-weight: 600;
      color: #fff;
      margin: 0;
    }
    
    @media (max-width: 480px) {
      .watch-dropdown-header h3 {
        font-size: 16px;
      }
    }
    
    .watch-dropdown-content {
      max-height: 384px;
      overflow-y: auto;
      scroll-behavior: smooth;
    }
    
    @media (max-width: 480px) {
      .watch-dropdown-content {
        max-height: 300px;
      }
    }

    .watch-dropdown-content:hover {
      overscroll-behavior: contain;
    }
    
    .watch-item {
      padding: 16px;
      border-bottom: 1px solid rgba(27,31,39,0.3);
      display: flex;
      justify-content: space-between;
      align-items: flex-start;
      transition: transform 0.2s ease;
    }
    
    @media (max-width: 480px) {
      .watch-item {
        padding: 12px;
      }
    }
    
    .watch-item:hover {
      transform: scale(1.02);
    }
    
    .watch-item-info {
      flex: 1;
    }
    
    .watch-item-title {
      color: #fff;
      font-weight: 600;
      margin-bottom: 4px;
    }
    
    @media (max-width: 480px) {
      .watch-item-title {
        font-size: 14px;
      }
    }
    
    .watch-item-service {
      color: rgba(255,255,255,0.75);
      font-size: 14px;
      margin-bottom: 4px;
    }
    
    @media (max-width: 480px) {
      .watch-item-service {
        font-size: 12px;
      }
    }
    
    .watch-item-tech {
      color: rgba(255,255,255,0.6);
      font-size: 12px;
    }
    
    @media (max-width: 480px) {
      .watch-item-tech {
        font-size: 10px;
      }
    }
    
    .watch-remove {
      padding: 8px;
      background: none;
      border: none;
      border-radius: 4px;
      cursor: pointer;
      transition: transform 0.2s ease;
    }
    
    .watch-remove:hover {
      transform: scale(1.1);
    }

    /* Overlay */
    .overlay {
      position: fixed;
      inset: 0;
      background: rgba(0,0,0,0);
      backdrop-filter: blur(0px);
      z-index: 40;
      opacity: 0;
      pointer-events: none;
      transition: all 0.3s ease;
    }
    
    .overlay.show {
      backdrop-filter: blur(4px);
      opacity: 1;
      pointer-events: auto;
    }

    /* Drawer - Responsive */
    .drawer {
      position: fixed;
      top: 0;
      right: -320px;
      width: 320px;
      height: 100vh;
      background: #0e1116;
      border-left: 1px solid #1b1f27;
      box-shadow: -16px 0 48px rgba(0,0,0,0.5);
      z-index: 50;
      transition: right 0.3s cubic-bezier(0.22, 1, 0.36, 1);
    }
    
    @media (max-width: 480px) {
      .drawer {
        width: 280px;
        right: -280px;
      }
    }
    
    @media (max-width: 360px) {
      .drawer {
        width: 250px;
        right: -250px;
      }
    }
    
    .drawer.show {
      right: 0;
    }
    
    .drawer-header {
      padding: 20px;
      border-bottom: 1px solid #1b1f27;
    }
    
    @media (max-width: 480px) {
      .drawer-header {
        padding: 16px;
      }
    }
    
    .drawer-header h3 {
      font-size: 18px;
      font-weight: 600;
      color: #fff;
      margin: 0;
    }
    
    @media (max-width: 480px) {
      .drawer-header h3 {
        font-size: 16px;
      }
    }
    
    .logout-btn {
      margin: 20px;
      padding: 12px 16px;
      border-radius: 12px;
      border: none;
      background: linear-gradient(90deg, #e63946, #d2353f);
      color: #fff;
      font-weight: 900;
      cursor: pointer;
      width: calc(100% - 40px);
      transition: transform 0.3s ease;
    }
    
    @media (max-width: 480px) {
      .logout-btn {
        margin: 16px;
        padding: 10px 14px;
        border-radius: 10px;
        width: calc(100% - 32px);
      }
    }
    
    .logout-btn:hover {
      transform: translateY(-2px);
    }

    /* Main Content - Responsive */
    .main-content {
      padding: 24px;
      padding-top: 80px;
      max-width: 1280px;
      margin: 0 auto;
    }
    
    @media (max-width: 768px) {
      .main-content {
        padding: 20px;
        padding-top: 70px;
      }
    }
    
    @media (max-width: 480px) {
      .main-content {
        padding: 16px;
        padding-top: 60px;
      }
    }
    
    @media (max-width: 360px) {
      .main-content {
        padding: 12px;
        padding-top: 50px;
      }
    }

    .page-title {
      font-size: 30px;
      font-weight: 700;
      color: #fff;
      margin-bottom: 32px;
    }
    
    @media (max-width: 768px) {
      .page-title {
        font-size: 26px;
        margin-bottom: 24px;
      }
    }
    
    @media (max-width: 480px) {
      .page-title {
        font-size: 22px;
        margin-bottom: 20px;
      }
    }
    
    @media (max-width: 360px) {
      .page-title {
        font-size: 20px;
        margin-bottom: 16px;
      }
    }

    /* Table Container - Responsive */
    .table-container {
      background: rgba(255,255,255,.06);
      border: 1px solid rgba(255,255,255,.08);
      border-radius: 16px;
      backdrop-filter: blur(8px);
      box-shadow: 0 25px 50px rgba(0,0,0,0.25);
      overflow: hidden;
    }
    
    @media (max-width: 768px) {
      .table-container {
        border-radius: 12px;
      }
    }
    
    @media (max-width: 480px) {
      .table-container {
        border-radius: 10px;
      }
    }

    .table-wrapper {
      overflow-x: auto;
    }

    /* Desktop Table */
    .desktop-table {
      width: 100%;
      border-collapse: collapse;
      display: table;
    }
    
    .desktop-table th {
      text-align: left;
      padding: 16px;
      color: #fff;
      font-weight: 600;
      border-bottom: 1px solid rgba(255,255,255,0.1);
    }
    
    @media (max-width: 768px) {
      .desktop-table th {
        padding: 12px 8px;
        font-size: 14px;
      }
    }
    
    .desktop-table tr {
      transition: all 0.2s ease-out;
    }
    
    .desktop-table tr:not(:last-child) {
      border-bottom: 1px solid rgba(255,255,255,0.05);
    }
    
    .desktop-table tbody tr:hover {
      transform: scale(1.01);
      box-shadow: 0 4px 12px rgba(0,0,0,0.15);
    }

    .desktop-table td {
      padding: 16px;
      color: rgba(255,255,255,0.9);
    }
    
    @media (max-width: 768px) {
      .desktop-table td {
        padding: 12px 8px;
        font-size: 14px;
      }
    }

    /* Mobile Cards - Hidden on Desktop */
    .mobile-cards {
      display: none;
    }
    
    @media (max-width: 640px) {
      .desktop-table {
        display: none;
      }
      
      .mobile-cards {
        display: block;
        padding: 16px;
      }
    }
    
    @media (max-width: 480px) {
      .mobile-cards {
        padding: 12px;
      }
    }
    
    .vehicle-card {
      background: rgba(255,255,255,.04);
      border: 1px solid rgba(255,255,255,.06);
      border-radius: 12px;
      padding: 16px;
      margin-bottom: 16px;
      backdrop-filter: blur(4px);
      transition: transform 0.2s ease, box-shadow 0.2s ease;
    }
    
    @media (max-width: 480px) {
      .vehicle-card {
        border-radius: 10px;
        padding: 14px;
        margin-bottom: 14px;
      }
    }
    
    .vehicle-card:hover {
      transform: translateY(-2px);
      box-shadow: 0 8px 24px rgba(0,0,0,0.2);
    }
    
    .card-header {
      display: flex;
      justify-content: space-between;
      align-items: flex-start;
      margin-bottom: 12px;
      border-bottom: 1px solid rgba(255,255,255,0.1);
      padding-bottom: 8px;
    }
    
    .card-title {
      font-size: 16px;
      font-weight: 600;
      color: #fff;
      margin: 0;
    }
    
    @media (max-width: 480px) {
      .card-title {
        font-size: 15px;
      }
    }
    
    .card-number {
      font-size: 14px;
      color: rgba(255,255,255,0.6);
      font-weight: 500;
    }
    
    @media (max-width: 480px) {
      .card-number {
        font-size: 13px;
      }
    }
    
    .card-row {
      display: flex;
      justify-content: space-between;
      align-items: center;
      margin: 8px 0;
    }
    
    .card-label {
      font-size: 13px;
      color: rgba(255,255,255,0.7);
      font-weight: 500;
    }
    
    @media (max-width: 480px) {
      .card-label {
        font-size: 12px;
      }
    }
    
    .card-value {
      font-size: 14px;
      color: rgba(255,255,255,0.9);
      text-align: right;
    }
    
    @media (max-width: 480px) {
      .card-value {
        font-size: 13px;
      }
    }
    
    .card-actions {
      display: flex;
      justify-content: space-between;
      align-items: center;
      margin-top: 16px;
      padding-top: 12px;
      border-top: 1px solid rgba(255,255,255,0.1);
    }
    
    @media (max-width: 480px) {
      .card-actions {
        margin-top: 14px;
        padding-top: 10px;
      }
    }

    /* Parts Status Button - Responsive */
    .parts-btn {
      display: flex;
      align-items: center;
      justify-content: space-between;
      width: 128px;
      max-width: 128px;
      padding: 8px 12px;
      background: rgba(255,255,255,.06);
      border: 1px solid rgba(255,255,255,.08);
      border-radius: 12px;
      color: #fff;
      font-weight: 600;
      cursor: pointer;
      transition: all 0.2s ease;
      backdrop-filter: blur(8px);
    }
    
    @media (max-width: 768px) {
      .parts-btn {
        width: 110px;
        max-width: 110px;
        padding: 6px 10px;
        border-radius: 10px;
        font-size: 13px;
      }
    }
    
    @media (max-width: 640px) {
      .parts-btn {
        width: 120px;
        max-width: 120px;
        padding: 8px 10px;
        border-radius: 8px;
        font-size: 12px;
      }
    }
    
    @media (max-width: 480px) {
      .parts-btn {
        width: 100px;
        max-width: 100px;
        padding: 6px 8px;
        font-size: 11px;
      }
    }
    
    .parts-btn:hover {
      background: rgba(255,255,255,.1);
    }

    /* Badges - Responsive */
    .badge {
      display: inline-block;
      white-space: nowrap;
      font-size: 14px !important;
      font-weight: 600 !important;
      padding: 6px 12px !important;
      border-radius: 8px !important;
      letter-spacing: 0.5px;
      box-shadow: 0 2px 8px rgba(0,0,0,0.4);
      text-transform: uppercase;
    }
    
    @media (max-width: 768px) {
      .badge {
        font-size: 12px !important;
        padding: 5px 10px !important;
        border-radius: 6px !important;
      }
    }
    
    @media (max-width: 640px) {
      .badge {
        font-size: 11px !important;
        padding: 4px 8px !important;
        border-radius: 5px !important;
      }
    }
    
    @media (max-width: 480px) {
      .badge {
        font-size: 10px !important;
        padding: 3px 6px !important;
        border-radius: 4px !important;
      }
    }

    .badge-success {
      background-color: #28d17c !important;
      color: #fff !important;
    }

    .badge-warning {
      background-color: #ffc107 !important;
      color: #212529 !important;
    }

    .badge-danger {
      background-color: #ff3b30 !important;
      color: #fff !important;
    }
    
    .badge-paid {
      background: #10b981;
      color: #fff;
    }
    
    .badge-advance {
      background: #f59e0b;
      color: #fff;
    }
    
    .badge-unpaid {
      background: #ef4444;
      color: #fff;
    }

    /* Watch Button - Responsive */
    .watch-btn {
      padding: 8px;
      background: none;
      border: none;
      border-radius: 8px;
      cursor: pointer;
      transition: transform 0.2s ease;
    }
    
    @media (max-width: 640px) {
      .watch-btn {
        padding: 6px;
        border-radius: 6px;
      }
    }
    
    .watch-btn:hover {
      transform: scale(1.1);
    }

    /* Picker Modal - Responsive */
    .picker-modal {
      position: fixed;
      inset: 0;
      display: flex;
      align-items: center;
      justify-content: center;
      z-index: 50;
      opacity: 0;
      pointer-events: none;
      transition: all 0.3s ease;
      padding: 16px;
    }
    
    .picker-modal.show {
      opacity: 1;
      pointer-events: auto;
    }
    
    .picker-content {
      width: 100%;
      max-width: 512px;
      max-height: 384px;
      background: #000;
      border: 1px solid #1a1a1a;
      border-radius: 16px;
      padding: 12px;
      box-shadow: 0 25px 50px rgba(0,0,0,0.6);
    }
    
    @media (max-width: 768px) {
      .picker-content {
        max-width: 400px;
        border-radius: 12px;
      }
    }
    
    @media (max-width: 480px) {
      .picker-content {
        max-width: 320px;
        border-radius: 10px;
        padding: 10px;
      }
    }
    
    @media (max-width: 360px) {
      .picker-content {
        max-width: 280px;
        border-radius: 8px;
      }
    }
    
    .picker-header {
      font-weight: 800;
      font-size: 12px;
      color: #bbb;
      padding: 8px;
      text-transform: uppercase;
      letter-spacing: 0.08em;
    }
    
    @media (max-width: 480px) {
      .picker-header {
        font-size: 11px;
        padding: 6px;
      }
    }
    
    .picker-options {
      overflow: auto;
      max-height: 256px;
      margin-top: 8px;
      padding-right: 8px;
    }
    
    @media (max-width: 480px) {
      .picker-options {
        max-height: 200px;
      }
    }
    
    .picker-option {
      width: 90%;
      height: 44px;
      margin: 6px auto;
      border-radius: 8px;
      background: #0f0f0f;
      border: 1px solid #1b1b1b;
      color: #fff;
      font-size: 18px;
      display: flex;
      justify-content: center;
      align-items: center;
      cursor: pointer;
      text-align: center;
      transition: all 0.2s ease;
    }
    
    @media (max-width: 480px) {
      .picker-option {
        height: 40px;
        font-size: 16px;
        border-radius: 6px;
      }
    }
    
    .picker-option:hover {
      background: #131313;
    }
    
    .picker-option.selected {
      outline: 2px solid #fff;
    }
    
    .picker-actions {
      display: flex;
      justify-content: flex-end;
      gap: 10px;
      padding-top: 8px;
    }
    
    .picker-cancel {
      background: transparent;
      border: 1px solid #222;
      color: #fff;
      padding: 8px 12px;
      border-radius: 10px;
      cursor: pointer;
      transition: all 0.2s ease;
    }
    
    @media (max-width: 480px) {
      .picker-cancel {
        padding: 6px 10px;
        border-radius: 8px;
        font-size: 14px;
      }
    }
    
    .picker-cancel:hover {
      background: #222;
    }

    /* Toast - Responsive */
    .toast {
      position: fixed;
      top: 50%;
      left: 50%;
      transform: translate(-50%, -50%);
      padding: 20px 28px;
      border-radius: 16px;
      font-size: 14px;
      font-weight: 500;
      display: flex;
      align-items: center;
      justify-content: center;
      box-shadow: 0 25px 50px rgba(0,0,0,0.25);
      z-index: 100;
      min-width: 384px;
      max-width: 384px;
      opacity: 0;
      pointer-events: none;
      transition: all 0.35s ease;
    }
    
    @media (max-width: 768px) {
      .toast {
        min-width: 320px;
        max-width: 320px;
        padding: 16px 24px;
        border-radius: 12px;
      }
    }
    
    @media (max-width: 480px) {
      .toast {
        min-width: 280px;
        max-width: 280px;
        padding: 14px 20px;
        border-radius: 10px;
        font-size: 13px;
      }
    }
    
    @media (max-width: 360px) {
      .toast {
        min-width: 240px;
        max-width: 240px;
        padding: 12px 16px;
        border-radius: 8px;
        font-size: 12px;
      }
    }
    
    .toast.show {
      opacity: 1;
      pointer-events: auto;
      transform: translate(-50%, -50%) scale(1.02);
    }
    
    .toast-success {
      background: linear-gradient(135deg, #10b981, #059669);
      color: #fff;
    }
    
    .toast-error {
      background: #ef4444;
      color: #fff;
    }

    /* No Results - Responsive */
    .no-results {
      text-align: center;
      color: rgba(255,255,255,0.75);
      margin-top: 32px;
    }
    
    @media (max-width: 768px) {
      .no-results {
        margin-top: 24px;
        font-size: 14px;
      }
    }
    
    @media (max-width: 480px) {
      .no-results {
        margin-top: 20px;
        font-size: 13px;
      }
    }

    /* Icons - Responsive */
    .ph {
      font-size: 28px !important;
      color: #fff !important;
    }
    
    @media (max-width: 480px) {
      .ph {
        font-size: 24px !important;
      }
    }
    
    @media (max-width: 360px) {
      .ph {
        font-size: 20px !important;
      }
    }

    /* Animations */
    @keyframes slideInFromRight {
      from {
        transform: translateX(16px);
        opacity: 0;
      }
      to {
        transform: translateX(0);
        opacity: 1;
      }
    }

    /* Enhanced Badge Colors */
    .badge-danger  { 
      background-color: #ff1744 !important; 
      color: #fff !important; 
      box-shadow: 0 0 10px rgba(255,23,68,.9); 
    }
    
    .badge-warning { 
      background-color: #faff00 !important; 
      color: #000 !important; 
      box-shadow: 0 0 10px rgba(250,255,0,.9); 
    }
    
    .badge-success { 
      background-color: #39ff14 !important; 
      color: #000 !important; 
      box-shadow: 0 0 10px rgba(57,255,20,.9); 
    }

    /* Landscape orientation fixes for mobile */
    @media (max-height: 500px) and (orientation: landscape) {
      .main-content {
        padding-top: 50px;
      }
      
      .page-title {
        font-size: 18px;
        margin-bottom: 12px;
      }
      
      .vehicle-card {
        padding: 12px;
        margin-bottom: 12px;
      }
      
      .watch-dropdown {
        max-height: 200px;
      }
      
      .watch-dropdown-content {
        max-height: 150px;
      }
    }

    /* Ultra small screens (below 320px) */
    @media (max-width: 320px) {
      .top-controls {
        gap: 4px;
        top: 2px;
        right: 2px;
      }
      
      .control-btn {
        width: 32px;
        height: 32px;
      }
      
      .search-input {
        width: 100px;
      }
      
      .watch-dropdown {
        width: 220px;
      }
      
      .drawer {
        width: 220px;
        right: -220px;
      }
      
      .main-content {
        padding: 8px;
        padding-top: 45px;
      }
      
      .page-title {
        font-size: 18px;
        margin-bottom: 12px;
      }
      
      .vehicle-card {
        padding: 10px;
        margin-bottom: 10px;
      }
      
      .parts-btn {
        width: 80px;
        max-width: 80px;
        padding: 4px 6px;
        font-size: 10px;
      }
      
      .badge {
        font-size: 9px !important;
        padding: 2px 4px !important;
        border-radius: 3px !important;
      }
    }

  </style>
</head>
<body>

<!-- Top Controls -->
<div class="top-controls">
  <!-- Search -->
  <div class="search-container">
    <div id="searchInput" class="search-input-container">
      <i class="ph ph-magnifying-glass"></i>
      <input id="searchField" class="search-input" placeholder="Search" />
      <button id="searchClear" class="search-clear" style="display: none;">✕</button>
    </div>
    <button id="searchToggle" class="control-btn">
      <i class="ph ph-magnifying-glass"></i>
    </button>
  </div>

  <!-- Watch List -->
  <div class="watch-container" style="position: relative;">
    <button id="watchToggle" class="control-btn">
      <i class="ph ph-eye"></i>
      <span id="watchBadge" class="watch-badge" style="display: none;">0</span>
    </button>
    <div id="watchDropdown" class="watch-dropdown">
      <div class="watch-dropdown-header">
        <h3>Watch List</h3>
      </div>
      <div id="watchContent" class="watch-dropdown-content">
        <div style="padding: 24px; text-align: center; color: rgba(255,255,255,0.75);">
          No vehicles in watch list
        </div>
      </div>
    </div>
  </div>

  <!-- Menu -->
  <button id="menuToggle" class="control-btn">
    <i class="ph ph-list"></i>
  </button>
</div>

<!-- Overlay -->
<div id="overlay" class="overlay"></div>

<!-- Drawer -->
<div id="drawer" class="drawer">
  <div class="drawer-header">
    <h3>MENU</h3>
  </div>
  <button class="logout-btn" onclick="logout()">Logout</button>
</div>

<!-- Main Content -->
<div class="main-content">
  <h1 class="page-title">Staff Panel</h1>
  
  <div class="table-container">
    <!-- Desktop Table -->
    <div class="table-wrapper">
      <table class="desktop-table">
        <thead>
          <tr>
           <th>S.No</th>
           <th>Customer</th>
           <th>Vehicle No</th>
           <th>Vehicle Name</th>
           <th>Department</th>
           <th>Service</th>
           <th>Technician</th>
           <th>Parts Status</th>
           <th>Status</th>
           <th>Payment</th>
           <th>Watch</th>
          </tr>
        </thead>
        <tbody id="tableBody"></tbody>
      </table>
    </div>
    
    <!-- Mobile Cards -->
    <div class="mobile-cards" id="mobileCards"></div>
  </div>

  <div id="noResults" class="no-results" style="display: none;">
    No vehicles found matching "<span id="searchTerm"></span>"
  </div>
</div>

<!-- Picker Modal -->
<div id="pickerModal" class="picker-modal">
  <div class="overlay"></div>
  <div class="picker-content">
    <div class="picker-header">Select Parts Status</div>
    <div class="picker-options">
      <div class="picker-option" data-value="Arrived">Arrived</div>
      <div class="picker-option" data-value="Not Arrived">Not Arrived</div>
    </div>
    <div class="picker-actions">
      <button id="pickerCancel" class="picker-cancel">Cancel</button>
    </div>
  </div>
</div>

<!-- Toast -->
<div id="toast" class="toast">
  <span id="toastMessage"></span>
</div>


<script>

// Simple unified status badge (only 3 neon statuses)
function statusBadge(status) {
  const val = (status || '').toLowerCase();
  if (val === 'done') return '<span class="badge badge-success">Done</span>';
  if (val === 'in service') return '<span class="badge badge-warning">In Service</span>';
  return '<span class="badge badge-danger">Waiting</span>';
}

// Global variables
let vehicles = {{ vehicles|tojson }};
let filteredVehicles = [...vehicles];
let currentPickerVehicle = null;

// DOM elements
const searchToggle = document.getElementById('searchToggle');
const searchInput = document.getElementById('searchInput');
const searchField = document.getElementById('searchField');
const searchClear = document.getElementById('searchClear');
const watchToggle = document.getElementById('watchToggle');
const watchDropdown = document.getElementById('watchDropdown');
const watchBadge = document.getElementById('watchBadge');
const watchContent = document.getElementById('watchContent');
const menuToggle = document.getElementById('menuToggle');
const overlay = document.getElementById('overlay');
const drawer = document.getElementById('drawer');
const tableBody = document.getElementById('tableBody');
const mobileCards = document.getElementById('mobileCards');
const noResults = document.getElementById('noResults');
const searchTerm = document.getElementById('searchTerm');
const pickerModal = document.getElementById('pickerModal');
const pickerCancel = document.getElementById('pickerCancel');
const toast = document.getElementById('toast');
const toastMessage = document.getElementById('toastMessage');

// Initialize
updateWatchList();
renderTable();

// Fade top controls on scroll
const topControls = document.querySelector('.top-controls');

window.addEventListener('scroll', () => {
  const scrollY = window.scrollY || window.pageYOffset;
  if (scrollY > 20) {
    topControls.classList.add('fade');
  } else {
    topControls.classList.remove('fade');
  }
});

// Responsive screen size detection
function isMobile() {
  return window.innerWidth <= 640;
}

// Fixed API update function to match your exact API structure
async function updateVehicleAPI(vehicleId, key, value) {
  try {
    console.log('Updating:', vehicleId, key, value);
    
    const response = await fetch('/api/update', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({
        id: String(vehicleId),
        key: key,
        value: value
      })
    });

    const result = await response.json();
    console.log('API Response:', result);

    if (result.success) {
      const vehicle = vehicles.find(v => String(v.id) === String(vehicleId));
      if (vehicle) {
        vehicle[key] = value;
      }

      renderTable();
      updateWatchList();

      const messages = {
        parts: 'Parts status updated successfully',
        watch: 'Watch status updated successfully'
      };
      showToast(messages[key] || 'Updated successfully', 'success');

      return true;
    } else {
      console.error('API Error:', result.error);
      showToast(result.error || 'Update failed', 'error');
      return false;
    }

  } catch (error) {
    console.error('Network Error:', error);
    showToast('Network error. Please check your connection.', 'error');
    return false;
  }
}

// Search functionality - Fixed for exact matching
searchToggle.addEventListener('click', () => {
  const isVisible = searchInput.classList.contains('show');
  if (isVisible) {
    searchInput.classList.remove('show');
  } else {
    searchInput.classList.add('show');
    setTimeout(() => searchField.focus(), 200);
  }
});

searchField.addEventListener('input', () => {
  const query = searchField.value.trim();
  if (query) {
    searchClear.style.display = 'block';
  } else {
    searchClear.style.display = 'none';
    filteredVehicles = [...vehicles];
    renderTable();
    noResults.style.display = 'none';
  }
});

// Fixed search functionality for exact matching (case insensitive)
searchField.addEventListener('keyup', () => {
  const query = searchField.value.trim().toLowerCase();
  if (!query) {
    filteredVehicles = [...vehicles];
    renderTable();
    noResults.style.display = 'none';
    return;
  }

  filteredVehicles = vehicles.filter(vehicle => {
    const fields = [
      vehicle.customer?.toLowerCase() || '',
      vehicle.vehicle_no?.toLowerCase() || '',
      vehicle.vehicle_name?.toLowerCase() || '',
      vehicle.department?.toLowerCase() || '',
      vehicle.service?.toLowerCase() || '',
      vehicle.technician?.toLowerCase() || '',
      vehicle.parts?.toLowerCase() || '',
      vehicle.payment?.toLowerCase() || ''
    ];
    return fields.some(field => field === query);
  });

  renderTable();
  
  if (filteredVehicles.length === 0) {
    searchTerm.textContent = searchField.value.trim();
    noResults.style.display = 'block';
  } else {
    noResults.style.display = 'none';
  }
});

searchClear.addEventListener('click', () => {
  searchField.value = '';
  searchClear.style.display = 'none';
  filteredVehicles = [...vehicles];
  renderTable();
  noResults.style.display = 'none';
});

// Watch list functionality  
watchToggle.addEventListener('click', () => {
  const isVisible = watchDropdown.classList.contains('show');
  if (isVisible) {
    watchDropdown.classList.remove('show');
    if (
      !drawer.classList.contains('show') &&
      !searchInput.classList.contains('show') &&
      !pickerModal.classList.contains('show')
    ) {
      overlay.classList.remove('show');
    }
  } else {
    watchDropdown.classList.add('show');
    overlay.classList.add('show');
  }
});

// Menu functionality
menuToggle.addEventListener('click', () => {
  drawer.classList.add('show');
  overlay.classList.add('show');
});

// Overlay click
overlay.addEventListener('click', () => {
  if (watchDropdown.classList.contains('show')) watchDropdown.classList.remove('show');
  if (drawer.classList.contains('show')) drawer.classList.remove('show');
  if (searchInput.classList.contains('show')) searchInput.classList.remove('show');
  overlay.classList.remove('show');
});

// Picker modal
pickerCancel.addEventListener('click', () => {
  pickerModal.classList.remove('show');
  overlay.classList.remove('show');
});

// Master click handler for all watch and parts interactions
document.addEventListener('click', async (e) => {
  // Close search if clicked outside
  if (!searchInput.contains(e.target) && !searchToggle.contains(e.target) && searchInput.classList.contains('show')) {
    searchInput.classList.remove('show');
  }
 
  // Close watch dropdown if clicked outside
  if (!watchDropdown.contains(e.target) && !watchToggle.contains(e.target) && watchDropdown.classList.contains('show')) {
    watchDropdown.classList.remove('show');
    if (
      !drawer.classList.contains('show') &&
      !searchInput.classList.contains('show') &&
      !pickerModal.classList.contains('show')
    ) {
      overlay.classList.remove('show');
    }
  }

  // Watch button clicks in table
  const watchBtn = e.target.closest('.watch-btn');
  if (watchBtn) {
    e.preventDefault();
    e.stopPropagation();
    
    const vehicleId = watchBtn.dataset.id;
    const vehicle = vehicles.find(v => String(v.id) === String(vehicleId));
    const newWatchStatus = !vehicle?.watch;
    
    await updateVehicleAPI(vehicleId, 'watch', newWatchStatus);
    return;
  }

  // Watch remove buttons in dropdown
  const removeBtn = e.target.closest('.watch-remove');
  if (removeBtn) {
    e.preventDefault();
    e.stopPropagation();
    
    const vehicleId = removeBtn.dataset.id;
    await updateVehicleAPI(vehicleId, 'watch', false);
    return;
  }

  // Parts button clicks
  const partsBtn = e.target.closest('.parts-btn');
  if (partsBtn) {
    e.preventDefault();
    e.stopPropagation();
    
    const vehicleId = partsBtn.dataset.id;
    const vehicle = vehicles.find(v => String(v.id) === String(vehicleId));
    
    currentPickerVehicle = vehicleId;
    
    document.querySelectorAll('.picker-option').forEach(option => {
      option.classList.toggle('selected', option.dataset.value === vehicle?.parts);
    });
    
    pickerModal.classList.add('show');
    overlay.classList.add('show');
    return;
  }

  // Picker option selection
  const pickerOption = e.target.closest('.picker-option');
  if (pickerOption && currentPickerVehicle) {
    e.preventDefault();
    e.stopPropagation();
    
    const selectedValue = pickerOption.dataset.value;
    
    pickerModal.classList.remove('show');
    overlay.classList.remove('show');
    
    await updateVehicleAPI(currentPickerVehicle, 'parts', selectedValue);
    
    currentPickerVehicle = null;
    return;
  }
});

// Enhanced render table function with mobile support
function renderTable() {
  // Clear both desktop and mobile containers
  tableBody.innerHTML = '';
  mobileCards.innerHTML = '';
  
  filteredVehicles.forEach((vehicle, index) => {
    // Desktop table row
    const row = document.createElement('tr');
    row.innerHTML = `
      <td>${index + 1}</td>
      <td>${vehicle.customer || ''}</td>
      <td>${vehicle.vehicle_no || ''}</td>
      <td>${vehicle.vehicle_name || ''}</td>
      <td>${vehicle.department || ''}</td>
      <td>${vehicle.service || ''}</td>
      <td>${vehicle.technician || ''}</td>
      <td>
        <button class="parts-btn" data-id="${vehicle.id}">
          <span>${vehicle.parts || 'Not Arrived'}</span>
          <i class="ph ph-caret-down" style="color: #e63946;"></i>
        </button>
      </td>
      <td>${statusBadge(vehicle.status)}</td>
      <td>
        <span class="badge ${getPaymentBadgeClass(vehicle.payment)}">${vehicle.payment || 'Unpaid'}</span>
      </td>
      <td>
        <button class="watch-btn" data-id="${vehicle.id}">
          ${vehicle.watch ? 
            '<i class="ph ph-eye" style="color: #e63946;"></i>' :
            '<i class="ph ph-eye-slash" style="color: #9ca3af;"></i>'
          }
        </button>
      </td>
    `;
    tableBody.appendChild(row);

    // Mobile card
    const card = document.createElement('div');
    card.className = 'vehicle-card';
    card.innerHTML = `
      <div class="card-header">
        <h4 class="card-title">${vehicle.vehicle_no || 'N/A'} - ${vehicle.vehicle_name || 'N/A'}</h4>
        <span class="card-number">#${index + 1}</span>
      </div>
      
      <div class="card-row">
        <span class="card-label">Customer:</span>
        <span class="card-value">${vehicle.customer || 'N/A'}</span>
      </div>
      
      <div class="card-row">
        <span class="card-label">Department:</span>
        <span class="card-value">${vehicle.department || 'N/A'}</span>
      </div>
      
      <div class="card-row">
        <span class="card-label">Service:</span>
        <span class="card-value">${vehicle.service || 'N/A'}</span>
      </div>
      
      <div class="card-row">
        <span class="card-label">Technician:</span>
        <span class="card-value">${vehicle.technician || 'N/A'}</span>
      </div>
      
      <div class="card-row">
        <span class="card-label">Status:</span>
        <span class="card-value">${statusBadge(vehicle.status)}</span>
      </div>
      
      <div class="card-row">
        <span class="card-label">Payment:</span>
        <span class="card-value">
          <span class="badge ${getPaymentBadgeClass(vehicle.payment)}">${vehicle.payment || 'Unpaid'}</span>
        </span>
      </div>
      
      <div class="card-actions">
        <button class="parts-btn" data-id="${vehicle.id}">
          <span>${vehicle.parts || 'Not Arrived'}</span>
          <i class="ph ph-caret-down" style="color: #e63946;"></i>
        </button>
        <button class="watch-btn" data-id="${vehicle.id}">
          ${vehicle.watch ? 
            '<i class="ph ph-eye" style="color: #e63946;"></i>' :
            '<i class="ph ph-eye-slash" style="color: #9ca3af;"></i>'
          }
        </button>
      </div>
    `;
    mobileCards.appendChild(card);
  });
}

// Update watch list
function updateWatchList() {
  const watchedVehicles = vehicles.filter(v => v.watch);
  
  if (watchedVehicles.length > 0) {
    watchBadge.textContent = watchedVehicles.length;
    watchBadge.style.display = 'flex';
  } else {
    watchBadge.style.display = 'none';
  }
  
  if (watchedVehicles.length === 0) {
    watchContent.innerHTML = '<div style="padding: 24px; text-align: center; color: rgba(255,255,255,0.75);">No vehicles in watch list</div>';
  } else {
    watchContent.innerHTML = watchedVehicles.map(vehicle => `
      <div class="watch-item">
        <div class="watch-item-info">
          <div class="watch-item-title">${vehicle.vehicle_no} - ${vehicle.vehicle_name}</div>
          <div class="watch-item-service">${vehicle.service}</div>
          <div class="watch-item-tech">${vehicle.technician}</div>
        </div>
        <button class="watch-remove" data-id="${vehicle.id}">
          <i class="ph ph-eye-slash" style="color: #e63946;"></i>
        </button>
      </div>
    `).join('');
  }
}

// Get payment badge class
function getPaymentBadgeClass(payment) {
  switch (payment) {
    case 'Paid': return 'badge-paid';
    case 'Advance Paid': return 'badge-advance';
    case 'Unpaid': return 'badge-unpaid';
    default: return 'badge-unpaid';
  }
}

// Show toast
function showToast(message, type) {
  toastMessage.textContent = message;
  toast.className = `toast toast-${type}`;
  toast.classList.add('show');
  
  setTimeout(() => {
    toast.classList.remove('show');
  }, type === 'error' ? 5000 : 3000);
}

// Logout
function logout() {
  window.location.href = '/logout';
}

// Auto-refresh with responsive handling
setInterval(async () => {
  try {
    const response = await fetch('/api/vehicles');
    if (response.ok) {
      const freshData = await response.json();
      vehicles = freshData;
      const currentQuery = searchField.value.trim().toLowerCase();
      if (currentQuery) {
        filteredVehicles = vehicles.filter(vehicle => {
          const fields = [
            vehicle.customer?.toLowerCase() || '',
            vehicle.vehicle_no?.toLowerCase() || '',
            vehicle.vehicle_name?.toLowerCase() || '',
            vehicle.department?.toLowerCase() || '',
            vehicle.service?.toLowerCase() || '',
            vehicle.technician?.toLowerCase() || '',
            vehicle.parts?.toLowerCase() || '',
            vehicle.payment?.toLowerCase() || ''
          ];
          return fields.some(field => field === currentQuery);
        });
      } else {
        filteredVehicles = [...freshData];
      }
      renderTable();
      updateWatchList();
    }
  } catch (error) {
    console.log('Auto-refresh failed:', error);
  }
}, 5000);

// Handle window resize for responsive adjustments
window.addEventListener('resize', () => {
  // Re-render table if switching between desktop/mobile view
  renderTable();
});

</script>
</body>
</html>""",
        vehicles=vehicles,
    )
###############################################################################
# Admin
###############################################################################
@app.route("/admin")
def admin():
    if session.get("user") != "admin":
        return redirect("/")

    # Load initial data
    departments = load_json('departments.json')
    technicians = load_json('technicians.json')
    services = load_json('services.json')
    vehicles = read_vehicles()
    
    STATUSES = ["Waiting", "In Service", "Done"];


    return render_template_string(
        r"""<!doctype html>
<html>
<head>
  <meta name="viewport" content="width=device-width, initial-scale=1, user-scalable=no">
  <title>Admin Panel</title>
  <link rel="stylesheet" href="https://unpkg.com/@phosphor-icons/web@2.0.3/src/regular/style.css">
  <style>
    /* Prevent zoom on input focus */
    input, select, textarea {
      font-size: 16px !important;
      transform-origin: left top;
    }
    
    /* Dynamic font size and spacing based on screen size */
    :root {
      --base-font: clamp(12px, 2.5vw, 16px);
      --small-font: clamp(10px, 2vw, 14px);
      --large-font: clamp(16px, 3vw, 24px);
      --xl-font: clamp(20px, 4vw, 30px);
      --spacing-xs: clamp(4px, 1vw, 8px);
      --spacing-sm: clamp(8px, 1.5vw, 12px);
      --spacing-md: clamp(12px, 2vw, 16px);
      --spacing-lg: clamp(16px, 3vw, 24px);
      --spacing-xl: clamp(20px, 4vw, 32px);
      --button-height: clamp(36px, 8vw, 44px);
      --input-height: clamp(32px, 6vw, 40px);
      --border-radius: clamp(6px, 1.5vw, 12px);
      --border-radius-lg: clamp(8px, 2vw, 16px);
    }

    /* Hide scrollbars */
    ::-webkit-scrollbar {
      display: none;
    }
    * {
      scrollbar-width: none;
      -ms-overflow-style: none;
    }
    .scrollable::-webkit-scrollbar {
      display: none;
    }

    /* Fix white flash on scroll */
    html, body {
      background-color: #0b0d10 !important;
    }

    body {
      margin: 0;
      font-family: Inter, "Segoe UI", system-ui, -apple-system, sans-serif;
      background: radial-gradient(800px 500px at 10% 10%, #11141a 0%, rgba(0,0,0,0) 30%), linear-gradient(180deg, #0b0d10, #0f1418);
      color: #fff;
      min-height: 100vh;
      overflow-x: auto;
      font-size: var(--base-font);
    }
    
    .main-content,
    .table-wrapper {
      will-change: transform;
      transform: translateZ(0);
    }

    /* Top Controls - Responsive */
    .top-controls {
      position: fixed;
      top: var(--spacing-md);
      right: var(--spacing-md);
      z-index: 50;
      display: flex;
      gap: var(--spacing-sm);
      transition: opacity 0.15s ease;
    }
    
    @media (max-width: 480px) {
      .top-controls {
        top: var(--spacing-sm);
        right: var(--spacing-sm);
        gap: var(--spacing-xs);
      }
    }
    
    .top-controls.fade {
      opacity: 0;
      transform: translateY(-10px);
      pointer-events: none;
    }
    
    .control-btn {
      width: var(--button-height);
      height: var(--button-height);
      border-radius: var(--border-radius);
      display: flex;
      align-items: center;
      justify-content: center;
      background: rgba(255,255,255,.06);
      border: 1px solid rgba(255,255,255,.08);
      backdrop-filter: blur(8px);
      cursor: pointer;
      transition: transform 0.3s ease;
      position: relative;
    }
    .control-btn:hover {
      transform: translateY(-2px);
    }

    /* Search - Responsive */
    .search-container {
      display: flex;
      align-items: center;
      gap: var(--spacing-xs);
    }
    .search-input-container {
      display: none;
      align-items: center;
      background: rgba(255,255,255,.06);
      border: 1px solid rgba(255,255,255,.08);
      border-radius: var(--border-radius);
      padding: var(--spacing-sm) var(--spacing-md);
      backdrop-filter: blur(8px);
      transition: all 0.3s ease;
      animation: slideInFromRight 0.3s ease;
    }
    .search-input-container.show {
      display: flex;
    }
    .search-input {
      background: transparent;
      border: none;
      color: #fff;
      outline: none;
      width: clamp(200px, 40vw, 256px);
      margin-left: var(--spacing-xs);
      font-size: var(--base-font) !important;
    }
    
    @media (max-width: 480px) {
      .search-input {
        width: clamp(150px, 60vw, 200px);
      }
    }
    
    .search-input::placeholder {
      color: rgba(255,255,255,0.5);
    }
    .search-clear {
      margin-left: var(--spacing-xs);
      color: rgba(255,255,255,0.75);
      background: none;
      border: none;
      cursor: pointer;
    }

    /* Top Controls Fade Animation */
    .top-controls.fade .search-input-container {
      opacity: 0.5;
      transition: opacity 0.3s ease;
    }

    /* Watch List - Enhanced responsiveness for ultra small screens */
    .watch-badge {
      position: absolute;
      top: -4px;
      right: -4px;
      width: clamp(16px, 4vw, 20px);
      height: clamp(16px, 4vw, 20px);
      border-radius: 50%;
      background: #E63946;
      color: #fff;
      font-size: clamp(10px, 2.5vw, 12px);
      font-weight: 600;
      display: flex;
      align-items: center;
      justify-content: center;
    }

    .watch-dropdown {
      position: absolute;
      top: 100%;
      right: 0;
      margin-top: var(--spacing-xs);
      width: clamp(280px, 80vw, 384px);
      background: #0e1116;
      border: 1px solid #1b1f27;
      border-radius: var(--border-radius-lg);
      backdrop-filter: blur(8px);
      box-shadow: 0 25px 50px rgba(0,0,0,0.25);
      z-index: 60;
      display: none;
      opacity: 0;
      transform: translateY(-8px);
      transition: opacity 0.3s ease, transform 0.3s ease;
    }
    
    @media (max-width: 480px) {
  .watch-dropdown {
    width: min(320px, calc(100vw - 32px));
    right: 0; /* Keep it aligned to the right edge of button */
  }
}

@media (max-width: 360px) {
  .watch-dropdown {
    width: min(280px, calc(100vw - 24px));
  }
}

@media (max-width: 320px) {
  .watch-dropdown {
    width: min(260px, calc(100vw - 16px));
    margin-top: 4px;
  }
}
    .watch-dropdown.show {
      display: block;
      opacity: 1;
      transform: translateY(0);
    }
    .watch-dropdown-header {
      padding: var(--spacing-lg);
      border-bottom: 1px solid #1b1f27;
    }
    
    @media (max-width: 360px) {
      .watch-dropdown-header {
        padding: var(--spacing-md);
      }
    }
    
    @media (max-width: 320px) {
      .watch-dropdown-header {
        padding: 12px;
      }
    }
    
    .watch-dropdown-header h3 {
      font-size: var(--large-font);
      font-weight: 600;
      color: #fff;
      margin: 0;
    }
    
    @media (max-width: 320px) {
      .watch-dropdown-header h3 {
        font-size: 16px;
      }
    }
    
    .watch-dropdown-content {
      max-height: clamp(250px, 60vh, 384px);
      overflow-y: auto;
      scroll-behavior: smooth;
    }
    
    @media (max-width: 360px) {
      .watch-dropdown-content {
        max-height: clamp(200px, 50vh, 300px);
      }
    }
    
    @media (max-width: 320px) {
      .watch-dropdown-content {
        max-height: 200px;
      }
    }
    
    .watch-dropdown-content:hover {
      overscroll-behavior: contain;
    }
    .watch-item {
      padding: var(--spacing-md);
      border-bottom: 1px solid rgba(27,31,39,0.3);
      display: flex;
      justify-content: space-between;
      align-items: flex-start;
      transition: transform 0.2s ease;
    }
    
    @media (max-width: 360px) {
      .watch-item {
        padding: var(--spacing-sm);
      }
    }
    
    @media (max-width: 320px) {
      .watch-item {
        padding: 8px;
      }
    }
    
    .watch-item:hover {
      transform: scale(1.02);
    }
    .watch-item-info {
      flex: 1;
    }
    .watch-item-title {
      color: #fff;
      font-weight: 600;
      margin-bottom: 4px;
      font-size: var(--base-font);
    }
    
    @media (max-width: 320px) {
      .watch-item-title {
        font-size: 12px;
      }
    }
    
    .watch-item-service {
      color: rgba(255,255,255,0.75);
      font-size: var(--small-font);
      margin-bottom: 4px;
    }
    
    @media (max-width: 320px) {
      .watch-item-service {
        font-size: 10px;
      }
    }
    
    .watch-item-tech {
      color: rgba(255,255,255,0.6);
      font-size: var(--small-font);
    }
    
    @media (max-width: 320px) {
      .watch-item-tech {
        font-size: 10px;
      }
    }
    
    .watch-remove {
      padding: var(--spacing-xs);
      background: none;
      border: none;
      border-radius: 4px;
      cursor: pointer;
      transition: transform 0.2s ease;
    }
    
    @media (max-width: 320px) {
      .watch-remove {
        padding: 4px;
      }
    }
    
    .watch-remove:hover {
      transform: scale(1.1);
    }

    /* Overlay */
    .overlay {
      position: fixed;
      inset: 0;
      background: rgba(0,0,0,0);
      backdrop-filter: blur(0px);
      z-index: 40;
      opacity: 0;
      pointer-events: none;
      transition: all 0.3s ease;
    }
    .overlay.show {
      backdrop-filter: blur(4px);
      opacity: 1;
      pointer-events: auto;
    }

    /* Drawer - Responsive */
    .drawer {
      position: fixed;
      top: 0;
      right: -100%;
      width: clamp(280px, 80vw, 320px);
      height: 100vh;
      background: #0e1116;
      border-left: 1px solid #1b1f27;
      box-shadow: -16px 0 48px rgba(0,0,0,0.5);
      z-index: 60;
      transition: right 0.3s cubic-bezier(0.22, 1, 0.36, 1);
    }
    .drawer.show {
      right: 0;
    }
    .drawer-header {
      padding: var(--spacing-lg);
      border-bottom: 1px solid #1b1f27;
    }
    .drawer-header h3 {
      font-size: var(--large-font);
      font-weight: 600;
      color: #fff;
      margin: 0; 
    }
    .logout-btn {
      margin: var(--spacing-lg);
      padding: var(--spacing-sm) var(--spacing-md);
      border-radius: var(--border-radius);
      border: none;
      background: linear-gradient(90deg, #e63946, #d2353f);
      color: #fff;
      font-weight: 900;
      cursor: pointer;
      width: calc(100% - calc(var(--spacing-lg) * 2));
      transition: transform 0.3s ease;
      font-size: var(--base-font);
      height: var(--input-height);
    }
    .logout-btn:hover {
      transform: translateY(-2px);
    }

    /* Main Content - Responsive */
    .main-content {
      padding: var(--spacing-lg);
      padding-top: calc(var(--button-height) + var(--spacing-xl));
      max-width: none;
      margin: 0 auto;
    }
    
    @media (max-width: 480px) {
      .main-content {
        padding: var(--spacing-md);
        padding-top: calc(var(--button-height) + var(--spacing-lg));
      }
    }

    .page-title {
      font-size: var(--xl-font);
      font-weight: 700;
      color: #fff;
      margin-bottom: var(--spacing-xl);
    }

    /* CRUD Panels - Responsive */
    .crud-panels {
      display: grid;
      grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
      gap: var(--spacing-lg);
      margin-bottom: var(--spacing-xl);
    }
    
    @media (max-width: 768px) {
      .crud-panels {
        grid-template-columns: 1fr;
        gap: var(--spacing-md);
      }
    }

    .crud-panel {
      background: rgba(255,255,255,.06);
      border: 1px solid rgba(255,255,255,.08);
      border-radius: var(--border-radius-lg);
      backdrop-filter: blur(8px);
      box-shadow: 0 25px 50px rgba(0,0,0,0.25);
      overflow: hidden;
    }

    .crud-panel-header {
      padding: var(--spacing-lg);
      border-bottom: 1px solid rgba(255,255,255,0.1);
      display: flex;
      align-items: center;
      gap: var(--spacing-xs);
    }

    .crud-panel-title {
      font-size: var(--large-font);
      font-weight: 600;
      color: #fff;
      margin: 0;
      display: flex;
      align-items: center;
      gap: var(--spacing-xs);
    }

    .crud-panel-content {
      padding: var(--spacing-lg);
    }

    .crud-input-group {
      display: flex;
      gap: var(--spacing-xs);
      margin-bottom: var(--spacing-md);
    }
    
    @media (max-width: 480px) {
      .crud-input-group {
        flex-direction: column;
        gap: var(--spacing-sm);
      }
    }

    .crud-input {
      flex: 1;
      padding: var(--spacing-sm) var(--spacing-md);
      background: rgba(255,255,255,.06);
      border: 1px solid rgba(255,255,255,.08);
      border-radius: var(--border-radius);
      color: #fff;
      outline: none;
      font-size: var(--base-font) !important;
      height: var(--input-height);
      box-sizing: border-box;
    }

    .crud-input::placeholder {
      color: rgba(255,255,255,0.5);
    }

    .crud-btn {
      padding: var(--spacing-sm) var(--spacing-md);
      border-radius: var(--border-radius);
      border: none;
      font-weight: 600;
      cursor: pointer;
      transition: all 0.2s ease;
      font-size: var(--base-font);
      height: var(--input-height);
      display: flex;
      align-items: center;
      justify-content: center;
    }

    .crud-btn-add {
      background: #10b981;
      color: #fff;
      min-width: var(--button-height);
    }

    .crud-btn-add:hover {
      background: #059669;
    }

    .crud-btn-delete {
      background: #ef4444;
      color: #fff;
    }

    .crud-btn-delete:hover {
      background: #dc2626;
    }

    /* CRUD Lists - Responsive */
    .crud-list {
      max-height: clamp(120px, 25vh, 150px);
      overflow-y: auto;
      scroll-behavior: smooth;
    }

    .crud-list:hover {
      overscroll-behavior: contain;
    }

    .crud-item {
      display: flex;
      align-items: center;
      justify-content: space-between;
      padding: var(--spacing-xs) var(--spacing-sm);
      margin-bottom: 4px;
      background: rgba(255,255,255,0.03);
      border-radius: var(--border-radius);
      transition: all 0.2s ease;
    }

    .crud-item:hover {
      background: rgba(255,255,255,0.08);
    }

    .crud-item-text {
      color: rgba(255,255,255,0.9);
      flex: 1;
      font-size: var(--small-font);
    }

    .crud-item-delete {
      padding: 4px;
      background: none;
      border: none;
      cursor: pointer;
      color: #ef4444;
      transition: color 0.2s ease;
    }

    .crud-item-delete:hover {
      color: #dc2626;
    }

    /* Table Container - Responsive */
    .table-container {
      background: rgba(255,255,255,.06);
      border: 1px solid rgba(255,255,255,.08);
      border-radius: var(--border-radius-lg);
      backdrop-filter: blur(8px);
      box-shadow: 0 25px 50px rgba(0,0,0,0.25);
      overflow: hidden;
      width: 100%;
    }

    /* Desktop Table */
    .table-wrapper {
      overflow-x: auto;
      overflow-y: visible;
    }
    
    @media (min-width: 1200px) {
      .table-wrapper {
        min-width: 1400px;
      }
    }

    table {
      width: 100%;
      border-collapse: collapse;
      min-width: 1400px;
    }
    
    @media (max-width: 1199px) {
      table {
        display: none;
      }
    }

    th {
      text-align: left;
      padding: var(--spacing-md) var(--spacing-sm);
      color: #fff;
      font-weight: 600;
      border-bottom: 1px solid rgba(255,255,255,0.1);
      white-space: nowrap;
      font-size: var(--small-font);
    }

    th:nth-child(1) { min-width: 60px; }
    th:nth-child(2) { min-width: 150px; }
    th:nth-child(3) { min-width: 120px; }
    th:nth-child(4) { min-width: 150px; }
    th:nth-child(5) { min-width: 120px; }
    th:nth-child(6) { min-width: 120px; }
    th:nth-child(7) { min-width: 120px; }
    th:nth-child(8) { min-width: 140px; }
    th:nth-child(9) { min-width: 120px; }
    th:nth-child(10) { min-width: 120px; }
    th:nth-child(11) { min-width: 80px; }
    th:nth-child(12) { min-width: 80px; }
    th:nth-child(13) { min-width: 100px; }

    tr {
      transition: all 0.2s ease-out;
    }
    tr:not(:last-child) {
      border-bottom: 1px solid rgba(255,255,255,0.05);
    }
    tbody tr:hover {
      transform: scale(1.01);
      box-shadow: 0 4px 12px rgba(0,0,0,0.15);
    }

    td {
      padding: var(--spacing-md) var(--spacing-sm);
      color: rgba(255,255,255,0.9);
      white-space: nowrap;
    }

    /* Card Layout for Mobile/Tablet */
    .cards-container {
      display: none;
    }
    
    @media (max-width: 1199px) {
      .cards-container {
        display: block;
      }
    }

    .vehicle-card {
      background: rgba(255,255,255,.04);
      border: 1px solid rgba(255,255,255,.06);
      border-radius: var(--border-radius);
      margin-bottom: var(--spacing-md);
      padding: var(--spacing-md);
      transition: all 0.2s ease;
    }
    
    .vehicle-card:hover {
      transform: translateY(-2px);
      box-shadow: 0 8px 24px rgba(0,0,0,0.2);
    }

    .card-header {
      display: flex;
      justify-content: space-between;
      align-items: flex-start;
      margin-bottom: var(--spacing-md);
      flex-wrap: wrap;
      gap: var(--spacing-sm);
    }

    .card-title {
      font-size: var(--large-font);
      font-weight: 600;
      color: #fff;
      margin: 0;
    }

    .card-subtitle {
      font-size: var(--small-font);
      color: rgba(255,255,255,0.75);
      margin: var(--spacing-xs) 0 0 0;
    }

    .card-actions {
      display: flex;
      gap: var(--spacing-xs);
      flex-shrink: 0;
    }

    .card-content {
      display: grid;
      grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
      gap: var(--spacing-md);
    }
    
    @media (max-width: 768px) {
      .card-content {
        grid-template-columns: 1fr;
        gap: var(--spacing-sm);
      }
    }

    .card-field {
      display: flex;
      flex-direction: column;
      gap: var(--spacing-xs);
    }

    .card-label {
      font-size: var(--small-font);
      color: rgba(255,255,255,0.6);
      font-weight: 500;
      text-transform: uppercase;
      letter-spacing: 0.5px;
    }

    /* Hide field positioning for small screens */
    .card-hide-field {
      display: flex;
      flex-direction: column;
      gap: var(--spacing-xs);
      grid-column: 1 / -1;
      margin-top: var(--spacing-sm);
      padding-top: var(--spacing-sm);
      border-top: 1px solid rgba(255,255,255,0.1);
    }

    /* Admin Input Fields - Responsive */
    .admin-input {
      background: rgba(255,255,255,.06);
      border: 1px solid rgba(255,255,255,.08);
      border-radius: var(--border-radius);
      color: #fff;
      padding: var(--spacing-xs) var(--spacing-sm);
      outline: none;
      width: 95%;
      max-width: 95%;
      font-size: var(--base-font) !important;
      height: var(--input-height);
      box-sizing: border-box;
    }

    .admin-input::placeholder {
      color: rgba(255,255,255,0.5);
    }

    /* Picker Modal Buttons - Responsive */
    .picker-btn {
      display: flex;
      align-items: center;
      justify-content: space-between;
      width: 120px;
      max-width: 120px;
      padding: var(--spacing-xs) var(--spacing-sm);
      background: rgba(255,255,255,.06);
      border: 1px solid rgba(255,255,255,.08);
      border-radius: var(--border-radius);
      color: #fff;
      font-weight: 600;
      cursor: pointer;
      transition: all 0.2s ease;
      backdrop-filter: blur(8px);
      font-size: var(--small-font);
      height: var(--input-height);
      box-sizing: border-box;
    }
    
    @media (max-width: 768px) {
      .picker-btn {
        width: 100%;
        max-width: 100%;
        min-height: var(--button-height);
      }
    }
    
    .picker-btn:hover {
      background: rgba(255,255,255,.1);
    }

    /* Watch and Visibility Buttons - Responsive */
    .watch-btn, .visibility-btn {
      padding: var(--spacing-xs);
      background: none;
      border: none;
      border-radius: var(--border-radius);
      cursor: pointer;
      transition: transform 0.2s ease;
      min-width: var(--button-height);
      min-height: var(--button-height);
      display: flex;
      align-items: center;
      justify-content: center;
    }
    .watch-btn:hover, .visibility-btn:hover {
      transform: scale(1.1);
    }

    .delete-btn {
      padding: var(--spacing-xs) var(--spacing-sm);
      background: #ef4444;
      border: none;
      border-radius: var(--border-radius);
      color: #fff;
      font-size: var(--small-font);
      cursor: pointer;
      transition: all 0.2s ease;
      height: var(--input-height);
      display: flex;
      align-items: center;
      justify-content: center;
    }
    .delete-btn:hover {
      background: #dc2626;
      transform: translateY(-1px);
    }

    /* Picker Modal - Responsive */
    .picker-modal {
      position: fixed;
      inset: 0;
      display: flex;
      align-items: center;
      justify-content: center;
      z-index: 70;
      opacity: 0;
      pointer-events: none;
      transition: all 0.3s ease;
      padding: var(--spacing-md);
    }
    .picker-modal.show {
      opacity: 1;
      pointer-events: auto;
    }
    .picker-content {
      position: relative;
      width: 100%;
      max-width: clamp(300px, 80vw, 512px);
      max-height: clamp(300px, 70vh, 384px);
      background: #000;
      border: 1px solid #1a1a1a;
      border-radius: var(--border-radius-lg);
      padding: var(--spacing-sm);
      box-shadow: 0 25px 50px rgba(0,0,0,0.6);
      transform: scale(0.95);
      transition: transform 0.3s ease;
    }
    .picker-modal.show .picker-content {
      transform: scale(1);
    }

    .picker-header {
      font-weight: 800;
      font-size: var(--small-font);
      color: #bbb;
      padding: var(--spacing-xs);
      text-transform: uppercase;
      letter-spacing: 0.08em;
    }
    .picker-options {
      overflow: auto;
      max-height: clamp(200px, 50vh, 256px);
      margin-top: var(--spacing-xs);
      padding-right: var(--spacing-xs);
    }
    .picker-option {
      width: 90%;
      min-height: clamp(36px, 8vw, 44px);
      margin: var(--spacing-xs) auto;
      border-radius: var(--border-radius);
      background: #0f0f0f;
      border: 1px solid #1b1b1b;
      color: #fff;
      font-size: var(--base-font);
      display: flex;
      justify-content: center;
      align-items: center;
      cursor: pointer;
      text-align: center;
      transition: all 0.2s ease;
      padding: var(--spacing-xs);
      box-sizing: border-box;
    }
    .picker-option:hover {
      background: #131313;
    }
    .picker-option.selected {
      outline: 2px solid #fff;
    }
    .picker-actions {
      display: flex;
      justify-content: flex-end;
      gap: var(--spacing-sm);
      padding-top: var(--spacing-xs);
    }
    .picker-cancel {
      background: transparent;
      border: 1px solid #222;
      color: #fff;
      padding: var(--spacing-xs) var(--spacing-sm);
      border-radius: var(--border-radius);
      cursor: pointer;
      transition: all 0.2s ease;
      font-size: var(--base-font);
      min-height: var(--input-height);
    }
    .picker-cancel:hover {
      background: #222;
    }

    /* Toast Notification System - Responsive */
    .toast {
      position: fixed;
      top: 50%;
      left: 50%;
      transform: translate(-50%, -50%);
      padding: var(--spacing-lg) var(--spacing-xl);
      border-radius: var(--border-radius-lg);
      font-size: var(--small-font);
      font-weight: 500;
      display: flex;
      align-items: center;
      justify-content: center;
      box-shadow: 0 25px 50px rgba(0,0,0,0.25);
      z-index: 100;
      width: clamp(280px, 80vw, 384px);
      opacity: 0;
      pointer-events: none;
      transition: all 0.35s ease;
    }
    .toast.show {
      opacity: 1;
      pointer-events: auto;
      transform: translate(-50%, -50%) scale(1.02);
    }
    .toast-success {
      background: linear-gradient(135deg, #10b981, #059669);
      color: #fff;
    }
    .toast-error {
      background: #ef4444;
      color: #fff;
    }

    /* No Results - Responsive */
    .no-results {
      text-align: center;
      color: rgba(255,255,255,0.75);
      margin-top: var(--spacing-xl);
      font-size: var(--base-font);
    }

    .ph {
      font-size: clamp(20px, 5vw, 28px) !important;
      color: #fff !important;
    }

    @keyframes slideInFromRight {
      from {
        transform: translateX(16px);
        opacity: 0;
      }
      to {
        transform: translateX(0);
        opacity: 1;
      }
    }
  </style>
</head>
<body>

<!-- Top Controls -->
<div class="top-controls">
  <!-- Search -->
  <div class="search-container">
    <div id="searchInput" class="search-input-container">
      <i class="ph ph-magnifying-glass"></i>
      <input id="searchField" class="search-input" placeholder="Search" />
      <button id="searchClear" class="search-clear" style="display: none;">✕</button>
    </div>
    <button id="searchToggle" class="control-btn">
      <i class="ph ph-magnifying-glass"></i>
    </button>
  </div>

  <!-- Watch List -->
  <div class="watch-container" style="position: relative;">
    <button id="watchToggle" class="control-btn">
      <i class="ph ph-eye"></i>
      <span id="watchBadge" class="watch-badge" style="display: none;">0</span>
    </button>
    <div id="watchDropdown" class="watch-dropdown">
      <div class="watch-dropdown-header">
        <h3>Watch List</h3>
      </div>
      <div id="watchContent" class="watch-dropdown-content">
        <div style="padding: 24px; text-align: center; color: rgba(255,255,255,0.75);">
          No vehicles in watch list
        </div>
      </div>
    </div>
  </div>

  <!-- Menu -->
  <button id="menuToggle" class="control-btn">
    <i class="ph ph-list"></i>
  </button>
</div>

<!-- Overlay -->
<div id="overlay" class="overlay"></div>

<!-- Drawer -->
<div id="drawer" class="drawer">
  <div class="drawer-header">
    <h3>MENU</h3>
  </div>
  <button class="logout-btn" onclick="logout()">Logout</button>
</div>

<!-- Main Content -->
<div class="main-content">
  <h1 class="page-title">Admin Panel</h1>
  
  <!-- CRUD Panels -->
  <div class="crud-panels">
    <!-- Departments Panel -->
    <div class="crud-panel">
      <div class="crud-panel-header">
        <h3 class="crud-panel-title">
          <i class="ph ph-list"></i>
          Departments
        </h3>
      </div>
      <div class="crud-panel-content">
        <div class="crud-input-group">
          <input id="deptInput" class="crud-input" placeholder="New Department" />
          <button id="addDept" class="crud-btn crud-btn-add">
            <i class="ph ph-plus"></i>
          </button>
        </div>
        <div id="deptList" class="crud-list"></div>
      </div>
    </div>

    <!-- Technicians Panel -->
    <div class="crud-panel">
      <div class="crud-panel-header">
        <h3 class="crud-panel-title">
          <i class="ph ph-wrench"></i>
          Technicians
        </h3>
      </div>
      <div class="crud-panel-content">
        <div class="crud-input-group">
          <input id="techInput" class="crud-input" placeholder="New Technician" />
          <button id="addTech" class="crud-btn crud-btn-add">
            <i class="ph ph-plus"></i>
          </button>
        </div>
        <div id="techList" class="crud-list"></div>
      </div>
    </div>

    <!-- Services Panel -->
    <div class="crud-panel">
      <div class="crud-panel-header">
        <h3 class="crud-panel-title">
          <i class="ph ph-gear"></i>
          Services
        </h3>
      </div>
      <div class="crud-panel-content">
        <div class="crud-input-group">
          <input id="serviceInput" class="crud-input" placeholder="New Service" />
          <button id="addService" class="crud-btn crud-btn-add">
            <i class="ph ph-plus"></i>
          </button>
        </div>
        <div id="serviceList" class="crud-list"></div>
      </div>
    </div>
  </div>

  <!-- Desktop Table -->
  <div class="table-container">
    <div class="table-wrapper">
      <table>
        <thead>
          <tr>
            <th>S.No</th>
            <th>Customer</th>
            <th>Vehicle No</th>
            <th>Vehicle Name</th>
            <th>Department</th>
            <th>Service</th>
            <th>Technician</th>
            <th>Parts Status</th>
            <th>Status</th>
            <th>Payment</th>
            <th>Watch</th>
            <th>Actions</th>
            <th style="display: flex; align-items: center; gap: 6px;">
            <i class="ph ph-eye" style="font-size: 16px !important;"></i>
             Hide
            </th>
          </tr>
        </thead>
        <tbody id="tableBody"></tbody>
      </table>
    </div>
    
    <!-- Mobile/Tablet Cards -->
    <div id="cardsContainer" class="cards-container"></div>
  </div>

  <div id="noResults" class="no-results" style="display: none;">
    No vehicles found matching "<span id="searchTerm"></span>"
  </div>
</div>

<!-- Picker Modal -->
<div id="pickerModal" class="picker-modal">
  <div class="overlay"></div>
  <div class="picker-content">
    <div id="pickerHeader" class="picker-header">Select Option</div>
    <div id="pickerOptions" class="picker-options">
      <!-- Options will be populated dynamically -->
    </div>
    <div class="picker-actions">
      <button id="pickerCancel" class="picker-cancel">Cancel</button>
    </div>
  </div>
</div>

<!-- Toast -->
<div id="toast" class="toast">
  <span id="toastMessage"></span>
</div>

<script>
// Global variables
let vehicles = {{ vehicles|tojson }};
let departments = {{ departments|tojson }};
let technicians = {{ technicians|tojson }};
let services = {{ services|tojson }};
let statuses = {{ statuses|tojson }};
let filteredVehicles = [...vehicles];
let isUserEditing = false;
let autoRefreshPaused = false;
let editTimeout = null;
let currentPickerVehicle = null;
let currentPickerField = null;

const payments = ["Paid", "Advance Paid", "Unpaid"];
const partsOptions = ["Arrived", "Not Arrived"];

// DOM elements
const searchToggle = document.getElementById('searchToggle');
const searchInput = document.getElementById('searchInput');
const searchField = document.getElementById('searchField');
const searchClear = document.getElementById('searchClear');
const watchToggle = document.getElementById('watchToggle');
const watchDropdown = document.getElementById('watchDropdown');
const watchBadge = document.getElementById('watchBadge');
const watchContent = document.getElementById('watchContent');
const menuToggle = document.getElementById('menuToggle');
const overlay = document.getElementById('overlay');
const drawer = document.getElementById('drawer');
const tableBody = document.getElementById('tableBody');
const cardsContainer = document.getElementById('cardsContainer');
const noResults = document.getElementById('noResults');
const searchTerm = document.getElementById('searchTerm');
const pickerModal = document.getElementById('pickerModal');
const pickerHeader = document.getElementById('pickerHeader');
const pickerOptions = document.getElementById('pickerOptions');
const pickerCancel = document.getElementById('pickerCancel');
const toast = document.getElementById('toast');
const toastMessage = document.getElementById('toastMessage');

// CRUD elements
const deptInput = document.getElementById('deptInput');
const addDept = document.getElementById('addDept');
const deptList = document.getElementById('deptList');
const techInput = document.getElementById('techInput');
const addTech = document.getElementById('addTech');
const techList = document.getElementById('techList');
const serviceInput = document.getElementById('serviceInput');
const addService = document.getElementById('addService');
const serviceList = document.getElementById('serviceList');

// Initialize
updateWatchList();
renderTable();
renderCRUDLists();

// Auto-refresh pause system for smooth editing
let ticking = false;
const topControls = document.querySelector('.top-controls');

function updateScrollControls() {
  const scrollY = window.scrollY || window.pageYOffset;
  if (scrollY > 20) {
    topControls.classList.add('fade');
  } else {
    topControls.classList.remove('fade');
  }
  ticking = false;
}

window.addEventListener('scroll', () => {
  if (!ticking) {
    requestAnimationFrame(updateScrollControls);
    ticking = true;
  }
}, { passive: true });

// Enhanced auto-refresh pause for ALL input interactions
document.addEventListener('focusin', (e) => {
  if (e.target.tagName === 'INPUT' || e.target.tagName === 'SELECT' || e.target.tagName === 'TEXTAREA') {
    isUserEditing = true;
    autoRefreshPaused = true;
    clearTimeout(editTimeout);
    console.log('Auto-refresh PAUSED - User editing');
  }
});

document.addEventListener('focusout', (e) => {
  if (e.target.tagName === 'INPUT' || e.target.tagName === 'SELECT' || e.target.tagName === 'TEXTAREA') {
    clearTimeout(editTimeout);
    editTimeout = setTimeout(() => {
      isUserEditing = false;
      autoRefreshPaused = false;
      console.log('Auto-refresh RESUMED - User stopped editing');
    }, 3000); // 3 second delay after focus out
  }
});

// Also pause on any button/picker interactions
function pauseAutoRefresh() {
  isUserEditing = true;
  autoRefreshPaused = true;
  clearTimeout(editTimeout);
  editTimeout = setTimeout(() => {
    isUserEditing = false;
    autoRefreshPaused = false;
    console.log('Auto-refresh RESUMED - After interaction');
  }, 3000);
}

// API Functions with unified endpoint for live sync
async function updateVehicleAPI(vehicleId, key, value) {
  if (!vehicleId || !key || value === undefined || value === null) {
    return false;
  }

  try {
    const response = await fetch('/api/update', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        id: String(vehicleId),
        key: key,
        value: value
      })
    });

    const result = await response.json();
    if (result.success) {
      const vehicle = vehicles.find(v => String(v.id) === String(vehicleId));
      if (vehicle) {
        vehicle[key] = value;
      }
      renderTable();
      updateWatchList();

      const messages = {
        customer: 'Customer updated successfully',
        vehicle_no: 'Vehicle number updated successfully',
        vehicle_name: 'Vehicle name updated successfully',
        department: 'Department updated successfully',
        service: 'Service updated successfully',
        technician: 'Technician updated successfully',
        parts: 'Parts status updated successfully',
        status: 'Status updated successfully',
        payment: 'Payment updated successfully',
        watch: 'Watch status updated successfully',
        visible: 'Visibility updated successfully'
      };
      showToast(messages[key] || 'Updated successfully', 'success');
      return true;
    } else {
      showToast(result.error || result.message || 'Update failed', 'error');
      return false;
    }
  } catch (error) {
    showToast('Network error. Please check your connection.', 'error');
    return false;
  }
}

async function addDepartment() {
  const name = deptInput.value.trim();
  if (!name) {
    showToast('Please enter a department name', 'error');
    return;
  }
  
  try {
    const response = await fetch('/api/add_department', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ department: name })
    });
    
    const result = await response.json();
    if (result.success) {
      departments.push(name);
      deptInput.value = '';
      renderCRUDLists();
      renderTable();
      showToast('Department added successfully', 'success');
    } else {
      showToast(result.message || 'Failed to add department', 'error');
    }
  } catch (error) {
    showToast('Network error occurred', 'error');
  }
}

async function deleteDepartment(name) {
  try {
    const response = await fetch('/api/delete_department', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ department: name })
    });
    
    const result = await response.json();
    if (result.success) {
      departments = departments.filter(d => d !== name);
      renderCRUDLists();
      renderTable();
      showToast('Department deleted successfully', 'success');
    } else {
      showToast(result.message || 'Failed to delete department', 'error');
    }
  } catch (error) {
    showToast('Network error occurred', 'error');
  }
}

async function addTechnician() {
  const name = techInput.value.trim();
  if (!name) {
    showToast('Please enter a technician name', 'error');
    return;
  }
  
  try {
    const response = await fetch('/api/add_technician', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ technician: name })
    });
    
    const result = await response.json();
    if (result.success) {
      technicians.push(name);
      techInput.value = '';
      renderCRUDLists();
      renderTable();
      showToast('Technician added successfully', 'success');
    } else {
      showToast(result.message || 'Failed to add technician', 'error');
    }
  } catch (error) {
    showToast('Network error occurred', 'error');
  }
}

async function deleteTechnician(name) {
  try {
    const response = await fetch('/api/delete_technician', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ technician: name })
    });
    
    const result = await response.json();
    if (result.success) {
      technicians = technicians.filter(t => t !== name);
      renderCRUDLists();
      renderTable();
      showToast('Technician deleted successfully', 'success');
    } else {
      showToast(result.message || 'Failed to delete technician', 'error');
    }
  } catch (error) {
    showToast('Network error occurred', 'error');
  }
}

async function addServiceItem() {
  const name = serviceInput.value.trim();
  if (!name) {
    showToast('Please enter a service name', 'error');
    return;
  }
  
  try {
    const response = await fetch('/api/add_service', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ service: name })
    });
    
    const result = await response.json();
    if (result.success) {
      services.push(name);
      serviceInput.value = '';
      renderCRUDLists();
      renderTable();
      showToast('Service added successfully', 'success');
    } else {
      showToast(result.message || 'Failed to add service', 'error');
    }
  } catch (error) {
    showToast('Network error occurred', 'error');
  }
}

async function deleteService(name) {
  try {
    const response = await fetch('/api/delete_service', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ service: name })
    });
    
    const result = await response.json();
    if (result.success) {
      services = services.filter(s => s !== name);
      renderCRUDLists();
      renderTable();
      showToast('Service deleted successfully', 'success');
    } else {
      showToast(result.message || 'Failed to delete service', 'error');
    }
  } catch (error) {
    showToast('Network error occurred', 'error');
  }
}

async function deleteVehicle(vehicleId) {
  try {
    const response = await fetch('/api/delete_vehicle', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ id: String(vehicleId) })
    });
    
    const result = await response.json();
    if (result.success) {
      vehicles = vehicles.filter(v => String(v.id) !== String(vehicleId));
      filteredVehicles = filteredVehicles.filter(v => String(v.id) !== String(vehicleId));
      renderTable();
      updateWatchList();
      showToast('Vehicle deleted successfully', 'success');
    } else {
      showToast(result.message || 'Delete failed', 'error');
    }
  } catch (error) {
    showToast('Network error occurred', 'error');
  }
}

async function fetchAllData() {
  if (isUserEditing || autoRefreshPaused) {
    console.log('Skipping refresh - user is editing');
    return;
  }
  
  try {
    const [deptRes, techRes, servRes, vehicleRes] = await Promise.all([
      fetch('/api/departments'),
      fetch('/api/technicians'), 
      fetch('/api/services'),
      fetch('/api/vehicles')
    ]);
    
    if (deptRes.ok) departments = await deptRes.json();
    if (techRes.ok) technicians = await techRes.json();
    if (servRes.ok) services = await servRes.json();
    if (vehicleRes.ok) {
      vehicles = await vehicleRes.json();
      
      const currentQuery = searchField.value.trim().toLowerCase();
      if (currentQuery) {
        applySearch();
      } else {
        filteredVehicles = [...vehicles];
      }
    }
    
    renderCRUDLists();
    renderTable();
    updateWatchList();
  } catch (error) {
    console.log('Auto-refresh failed:', error);
  }
}

// Search functionality with exact matching
searchToggle.addEventListener('click', () => {
  const isVisible = searchInput.classList.contains('show');
  if (isVisible) {
    searchInput.classList.remove('show');
  } else {
    searchInput.classList.add('show');
    setTimeout(() => searchField.focus(), 200);
  }
});

searchField.addEventListener('input', () => {
  const query = searchField.value.trim();
  if (query) {
    searchClear.style.display = 'block';
  } else {
    searchClear.style.display = 'none';
    filteredVehicles = [...vehicles];
    renderTable();
    noResults.style.display = 'none';
  }
});

function applySearch() {
  const query = searchField.value.trim().toLowerCase();
  if (!query) {
    filteredVehicles = [...vehicles];
    renderTable();
    noResults.style.display = 'none';
    return;
  }

  filteredVehicles = vehicles.filter(vehicle => {
    const fields = [
      vehicle.customer?.toLowerCase() || '',
      vehicle.vehicle_no?.toLowerCase() || '',
      vehicle.vehicle_name?.toLowerCase() || '',
      vehicle.department?.toLowerCase() || '',
      vehicle.service?.toLowerCase() || '',
      vehicle.technician?.toLowerCase() || '',
      vehicle.parts?.toLowerCase() || '',
      vehicle.payment?.toLowerCase() || '',
      vehicle.status?.toLowerCase() || ''
    ];
    return fields.some(field => field === query);
  });

  renderTable();
  
  if (filteredVehicles.length === 0) {
    searchTerm.textContent = searchField.value.trim();
    noResults.style.display = 'block';
  } else {
    noResults.style.display = 'none';
  }
}

searchField.addEventListener('keyup', applySearch);

searchClear.addEventListener('click', () => {
  searchField.value = '';
  searchClear.style.display = 'none';
  filteredVehicles = [...vehicles];
  renderTable();
  noResults.style.display = 'none';
});

// Watch list functionality  
watchToggle.addEventListener('click', () => {
  const isVisible = watchDropdown.classList.contains('show');
  if (isVisible) {
    watchDropdown.classList.remove('show');
    overlay.classList.remove('show');
  } else {
    if (drawer.classList.contains('show')) {
      drawer.classList.remove('show');
    }
    watchDropdown.classList.add('show');
    overlay.classList.add('show');
  }
});

// Menu functionality
menuToggle.addEventListener('click', () => {
  if (watchDropdown.classList.contains('show')) {
    watchDropdown.classList.remove('show');
  }
  drawer.classList.add('show');
  overlay.classList.add('show');
});

// Overlay click handler
overlay.addEventListener('click', () => {
  let hasOpenDropdowns = false;
  
  if (watchDropdown.classList.contains('show')) {
    watchDropdown.classList.remove('show');
    hasOpenDropdowns = true;
  }
  
  if (drawer.classList.contains('show')) {
    drawer.classList.remove('show');
    hasOpenDropdowns = true;
  }
  
  if (searchInput.classList.contains('show')) {
    searchInput.classList.remove('show');
    hasOpenDropdowns = true;
  }
  
  if (pickerModal.classList.contains('show')) {
    pickerModal.classList.remove('show');
    hasOpenDropdowns = true;
  }
  
  if (hasOpenDropdowns) {
    overlay.classList.remove('show');
  }
});

// Picker modal functionality
pickerCancel.addEventListener('click', () => {
  pickerModal.classList.remove('show');
  overlay.classList.remove('show');
  currentPickerVehicle = null;
  currentPickerField = null;
});

function openPicker(vehicleId, field, options, currentValue) {
  pauseAutoRefresh();
  
  currentPickerVehicle = vehicleId;
  currentPickerField = field;
  
  const titles = {
    department: 'Select Department',
    service: 'Select Service', 
    technician: 'Select Technician',
    parts: 'Select Parts Status',
    status: 'Select Status',
    payment: 'Select Payment'
  };
  
  pickerHeader.textContent = titles[field] || 'Select Option';
  
  pickerOptions.innerHTML = options.map(option => `
    <div class="picker-option ${option === currentValue ? 'selected' : ''}" data-value="${option}">
      ${option}
    </div>
  `).join('');
  
  pickerModal.classList.add('show');
  overlay.classList.add('show');
}

// CRUD Event Listeners
addDept.addEventListener('click', addDepartment);
deptInput.addEventListener('keypress', (e) => {
  if (e.key === 'Enter') addDepartment();
});

addTech.addEventListener('click', addTechnician);
techInput.addEventListener('keypress', (e) => {
  if (e.key === 'Enter') addTechnician();
});

addService.addEventListener('click', addServiceItem);
serviceInput.addEventListener('keypress', (e) => {
  if (e.key === 'Enter') addServiceItem();
});

// Master click handler
document.addEventListener('click', async (e) => {
  // Close dropdowns if clicked outside
  if (!searchInput.contains(e.target) && !searchToggle.contains(e.target) && searchInput.classList.contains('show')) {
    searchInput.classList.remove('show');
  }
  
  if (!watchDropdown.contains(e.target) && !watchToggle.contains(e.target) && watchDropdown.classList.contains('show')) {
    watchDropdown.classList.remove('show');
    overlay.classList.remove('show');
  }

  // CRUD delete buttons
  const deptDeleteBtn = e.target.closest('[data-delete-dept]');
  if (deptDeleteBtn) {
    e.preventDefault();
    e.stopPropagation();
    const name = deptDeleteBtn.dataset.deleteDept;
    if (confirm(`Are you sure you want to delete department "${name}"?`)) {
      await deleteDepartment(name);
    }
    return;
  }

  const techDeleteBtn = e.target.closest('[data-delete-tech]');
  if (techDeleteBtn) {
    e.preventDefault();
    e.stopPropagation();
    const name = techDeleteBtn.dataset.deleteTech;
    if (confirm(`Are you sure you want to delete technician "${name}"?`)) {
      await deleteTechnician(name);
    }
    return;
  }

  const serviceDeleteBtn = e.target.closest('[data-delete-service]');
  if (serviceDeleteBtn) {
    e.preventDefault();
    e.stopPropagation();
    const name = serviceDeleteBtn.dataset.deleteService;
    if (confirm(`Are you sure you want to delete service "${name}"?`)) {
      await deleteService(name);
    }
    return;
  }

  // Picker buttons for all select fields
  const pickerBtn = e.target.closest('.picker-btn');
  if (pickerBtn) {
    e.preventDefault();
    e.stopPropagation();
    
    const vehicleId = pickerBtn.dataset.id;
    const field = pickerBtn.dataset.field;
    if (!vehicleId || !field) return;
    
    const vehicle = vehicles.find(v => String(v.id) === String(vehicleId));
    if (!vehicle) return;
    
    let options = [];
    let currentValue = '';
    
    switch (field) {
      case 'department':
        options = departments;
        currentValue = vehicle.department || departments[0];
        break;
      case 'service':
        options = services;
        currentValue = vehicle.service || services[0];
        break;
      case 'technician':
        options = technicians;
        currentValue = vehicle.technician || technicians[0];
        break;
      case 'parts':
        options = partsOptions;
        currentValue = vehicle.parts || 'Not Arrived';
        break;
      case 'status':
        options = statuses;
        currentValue = vehicle.status || statuses[0];
        break;
      case 'payment':
        options = payments;
        currentValue = vehicle.payment || 'Unpaid';
        break;
    }
    
    openPicker(vehicleId, field, options, currentValue);
    return;
  }

  // Picker option selection
  const pickerOption = e.target.closest('.picker-option');
  if (pickerOption && currentPickerVehicle && currentPickerField) {
    e.preventDefault();
    e.stopPropagation();
    
    const selectedValue = pickerOption.dataset.value;
    
    // Close modal
    pickerModal.classList.remove('show');
    overlay.classList.remove('show');
    
    // Update field
    await updateVehicleAPI(currentPickerVehicle, currentPickerField, selectedValue);
    
    currentPickerVehicle = null;
    currentPickerField = null;
    return;
  }

  // Watch button clicks
  const watchBtn = e.target.closest('.watch-btn');
  if (watchBtn) {
    e.preventDefault();
    e.stopPropagation();
    pauseAutoRefresh();
    
    const vehicleId = watchBtn.dataset.id;
    if (!vehicleId) return;
    
    const vehicle = vehicles.find(v => String(v.id) === String(vehicleId));
    if (!vehicle) return;
    
    const newWatchStatus = !vehicle.watch;
    await updateVehicleAPI(vehicleId, 'watch', newWatchStatus);
    return;
  }

  // Visibility button (hide/show for display route)
  const visibilityBtn = e.target.closest('.visibility-btn');
  if (visibilityBtn) {
    e.preventDefault();
    e.stopPropagation();
    pauseAutoRefresh();
    
    const vehicleId = visibilityBtn.dataset.id;
    if (!vehicleId) return;
    
    const vehicle = vehicles.find(v => String(v.id) === String(vehicleId));
    if (!vehicle) return;
    
    const newVisibility = !vehicle.visible;
    await updateVehicleAPI(vehicleId, 'visible', newVisibility);
    return;
  }

  // Delete vehicle button
  const deleteBtn = e.target.closest('.delete-btn');
  if (deleteBtn) {
    e.preventDefault();
    e.stopPropagation();
    pauseAutoRefresh();
    
    const vehicleId = deleteBtn.dataset.id;
    const vehicle = vehicles.find(v => String(v.id) === String(vehicleId));
    const vehicleInfo = vehicle ? `${vehicle.vehicle_no} - ${vehicle.vehicle_name}` : 'this vehicle';
    
    if (confirm(`Are you sure you want to delete ${vehicleInfo}?`)) {
      await deleteVehicle(vehicleId);
    }
    return;
  }

  // Watch remove buttons in dropdown
  const removeBtn = e.target.closest('.watch-remove');
  if (removeBtn) {
    e.preventDefault();
    e.stopPropagation();
    pauseAutoRefresh();
    
    const vehicleId = removeBtn.dataset.id;
    await updateVehicleAPI(vehicleId, 'watch', false);
    return;
  }
});

// Handle input changes for text fields only with debouncing
document.addEventListener('input', async (e) => {
  const input = e.target;
  if (!input.classList.contains('admin-input')) return;
  
  pauseAutoRefresh();
  
  const vehicleId = input.dataset.id;
  const field = input.dataset.field;
  const value = input.value;
  
  if (vehicleId && field) {
    // Debounce the API call to avoid too many requests while typing
    clearTimeout(input.updateTimeout);
    input.updateTimeout = setTimeout(async () => {
      await updateVehicleAPI(vehicleId, field, value);
    }, 1500); // Wait 1.5 seconds after user stops typing
  }
});

// Render functions
function renderCRUDLists() {
  // Departments
  deptList.innerHTML = departments.map(dept => `
    <div class="crud-item">
      <span class="crud-item-text">${dept}</span>
      <button class="crud-item-delete" data-delete-dept="${dept}">
        <i class="ph ph-trash"></i>
      </button>
    </div>
  `).join('');

  // Technicians
  techList.innerHTML = technicians.map(tech => `
    <div class="crud-item">
      <span class="crud-item-text">${tech}</span>
      <button class="crud-item-delete" data-delete-tech="${tech}">
        <i class="ph ph-trash"></i>
      </button>
    </div>
  `).join('');

  // Services
  serviceList.innerHTML = services.map(service => `
    <div class="crud-item">
      <span class="crud-item-text">${service}</span>
      <button class="crud-item-delete" data-delete-service="${service}">
        <i class="ph ph-trash"></i>
      </button>
    </div>
  `).join('');
}

function renderTable() {
  // Desktop Table
  tableBody.innerHTML = '';
  
  filteredVehicles.forEach((vehicle, index) => {
    const row = document.createElement('tr');
    row.innerHTML = `
      <td>${index + 1}</td>
      <td>
        <input class="admin-input" data-id="${vehicle.id}" data-field="customer" value="${vehicle.customer || ''}" placeholder="Customer Name" />
      </td>
      <td>
        <input class="admin-input" data-id="${vehicle.id}" data-field="vehicle_no" value="${vehicle.vehicle_no || ''}" placeholder="Vehicle No" />
      </td>
      <td>
        <input class="admin-input" data-id="${vehicle.id}" data-field="vehicle_name" value="${vehicle.vehicle_name || ''}" placeholder="Vehicle Name" />
      </td>
      <td>
        <button class="picker-btn" data-id="${vehicle.id}" data-field="department">
          <span>${vehicle.department || (departments[0] || 'N/A')}</span>
          <i class="ph ph-caret-down" style="color: #e63946;"></i>
        </button>
      </td>
      <td>
        <button class="picker-btn" data-id="${vehicle.id}" data-field="service">
          <span>${vehicle.service || (services[0] || 'N/A')}</span>
          <i class="ph ph-caret-down" style="color: #e63946;"></i>
        </button>
      </td>
      <td>
        <button class="picker-btn" data-id="${vehicle.id}" data-field="technician">
          <span>${vehicle.technician || (technicians[0] || 'N/A')}</span>
          <i class="ph ph-caret-down" style="color: #e63946;"></i>
        </button>
      </td>
      <td>
        <button class="picker-btn" data-id="${vehicle.id}" data-field="parts">
          <span>${vehicle.parts || 'Not Arrived'}</span>
          <i class="ph ph-caret-down" style="color: #e63946;"></i>
        </button>
      </td>
      <td>
        <button class="picker-btn" data-id="${vehicle.id}" data-field="status">
          <span>${vehicle.status || (statuses[0] || 'N/A')}</span>
          <i class="ph ph-caret-down" style="color: #e63946;"></i>
        </button>
      </td>
      <td>
        <button class="picker-btn" data-id="${vehicle.id}" data-field="payment">
          <span>${vehicle.payment || 'Unpaid'}</span>
          <i class="ph ph-caret-down" style="color: #e63946;"></i>
        </button>
      </td>
      <td>
        <button class="watch-btn" data-id="${vehicle.id}">
          ${vehicle.watch ? 
            '<i class="ph ph-eye" style="color: #e63946;"></i>' :
            '<i class="ph ph-eye-slash" style="color: #9ca3af;"></i>'
          }
        </button>
      </td>
      <td>
        <button class="delete-btn" data-id="${vehicle.id}">
          Delete
        </button>
      </td>
      <td>
        <button class="visibility-btn" data-id="${vehicle.id}">
          ${vehicle.visible !== false ? 
            '<i class="ph ph-eye" style="color: #10b981;"></i>' :
            '<i class="ph ph-eye-slash" style="color: #ef4444;"></i>'
          }
        </button>
      </td>
    `;
    tableBody.appendChild(row);
  });

  // Mobile/Tablet Cards with swapped positions
  cardsContainer.innerHTML = '';
  
  filteredVehicles.forEach((vehicle, index) => {
    const card = document.createElement('div');
    card.className = 'vehicle-card';
    card.innerHTML = `
      <div class="card-header">
        <div>
          <h3 class="card-title">#${index + 1} - ${vehicle.vehicle_no || 'N/A'}</h3>
          <p class="card-subtitle">${vehicle.vehicle_name || 'No Name'}</p>
        </div>
        <div class="card-actions">
          <button class="watch-btn" data-id="${vehicle.id}">
            ${vehicle.watch ? 
              '<i class="ph ph-eye" style="color: #e63946;"></i>' :
              '<i class="ph ph-eye-slash" style="color: #9ca3af;"></i>'
            }
          </button>
          <button class="delete-btn" data-id="${vehicle.id}">
            Delete
          </button>
        </div>
      </div>
      
      <div class="card-content">
        <div class="card-field">
          <label class="card-label">Customer</label>
          <input class="admin-input" data-id="${vehicle.id}" data-field="customer" value="${vehicle.customer || ''}" placeholder="Customer Name" />
        </div>
        
        <div class="card-field">
          <label class="card-label">Vehicle Number</label>
          <input class="admin-input" data-id="${vehicle.id}" data-field="vehicle_no" value="${vehicle.vehicle_no || ''}" placeholder="Vehicle No" />
        </div>
        
        <div class="card-field">
          <label class="card-label">Vehicle Name</label>
          <input class="admin-input" data-id="${vehicle.id}" data-field="vehicle_name" value="${vehicle.vehicle_name || ''}" placeholder="Vehicle Name" />
        </div>
        
        <div class="card-field">
          <label class="card-label">Department</label>
          <button class="picker-btn" data-id="${vehicle.id}" data-field="department">
            <span>${vehicle.department || (departments[0] || 'N/A')}</span>
            <i class="ph ph-caret-down" style="color: #e63946;"></i>
          </button>
        </div>
        
        <div class="card-field">
          <label class="card-label">Service</label>
          <button class="picker-btn" data-id="${vehicle.id}" data-field="service">
            <span>${vehicle.service || (services[0] || 'N/A')}</span>
            <i class="ph ph-caret-down" style="color: #e63946;"></i>
          </button>
        </div>
        
        <div class="card-field">
          <label class="card-label">Technician</label>
          <button class="picker-btn" data-id="${vehicle.id}" data-field="technician">
            <span>${vehicle.technician || (technicians[0] || 'N/A')}</span>
            <i class="ph ph-caret-down" style="color: #e63946;"></i>
          </button>
        </div>
        
        <div class="card-field">
          <label class="card-label">Parts Status</label>
          <button class="picker-btn" data-id="${vehicle.id}" data-field="parts">
            <span>${vehicle.parts || 'Not Arrived'}</span>
            <i class="ph ph-caret-down" style="color: #e63946;"></i>
          </button>
        </div>
        
        <div class="card-field">
          <label class="card-label">Status</label>
          <button class="picker-btn" data-id="${vehicle.id}" data-field="status">
            <span>${vehicle.status || (statuses[0] || 'N/A')}</span>
            <i class="ph ph-caret-down" style="color: #e63946;"></i>
          </button>
        </div>
        
        <div class="card-field">
          <label class="card-label">Payment</label>
          <button class="picker-btn" data-id="${vehicle.id}" data-field="payment">
            <span>${vehicle.payment || 'Unpaid'}</span>
            <i class="ph ph-caret-down" style="color: #e63946;"></i>
          </button>
        </div>
        
        <div class="card-hide-field">
          <label class="card-label">Hide</label>
          <button class="visibility-btn" data-id="${vehicle.id}">
            ${vehicle.visible !== false ? 
              '<i class="ph ph-eye" style="color: #10b981;"></i>' :
              '<i class="ph ph-eye-slash" style="color: #ef4444;"></i>'
            }
          </button>
        </div>
      </div>
    `;
    cardsContainer.appendChild(card);
  });
}

function updateWatchList() {
  const watchedVehicles = vehicles.filter(v => v.watch);
  
  if (watchedVehicles.length > 0) {
    watchBadge.textContent = watchedVehicles.length;
    watchBadge.style.display = 'flex';
  } else {
    watchBadge.style.display = 'none';
  }
  
  if (watchedVehicles.length === 0) {
    watchContent.innerHTML = '<div style="padding: 24px; text-align: center; color: rgba(255,255,255,0.75);">No vehicles in watch list</div>';
  } else {
    watchContent.innerHTML = watchedVehicles.map(vehicle => `
      <div class="watch-item">
        <div class="watch-item-info">
          <div class="watch-item-title">${vehicle.vehicle_no || 'N/A'} - ${vehicle.vehicle_name || 'N/A'}</div>
          <div class="watch-item-service">${vehicle.service || 'N/A'}</div>
          <div class="watch-item-tech">${vehicle.technician || 'N/A'}</div>
        </div>
        <button class="watch-remove" data-id="${vehicle.id}">
          <i class="ph ph-eye-slash" style="color: #e63946;"></i>
        </button>
      </div>
    `).join('');
  }
}

// Toast notification system
function showToast(message, type) {
  toastMessage.textContent = message;
  toast.className = `toast toast-${type}`;
  toast.classList.add('show');
  
  setTimeout(() => {
    toast.classList.remove('show');
  }, type === 'error' ? 5000 : 3000);
}

function logout() {
  window.location.href = '/logout';
}

// Auto-refresh every 5 seconds with pause detection
setInterval(fetchAllData, 5000);
</script>
</body>
</html>
""",
vehicles=vehicles,
departments=departments,
technicians=technicians,
services=services,
statuses=STATUSES,
)
###############################################################################
# Dashboard (read-only)
###############################################################################
from flask import render_template_string, redirect, session
# assuming you have read_vehicles() available as in staff route
# from your_module import read_vehicles

@app.route("/dashboard")
def dashboard():
    if session.get("user") != "dashboard":
        return redirect("/")

    vehicles = read_vehicles()

    return render_template_string(
        r"""<!doctype html>
<html>
<head>
  <meta name="viewport" content="width=device-width, initial-scale=1, maximum-scale=1, user-scalable=no">
  <title>Dashboard</title>
  <link rel="stylesheet" href="https://unpkg.com/@phosphor-icons/web@2.0.3/src/regular/style.css">
  <style>
      /* Hide scrollbars */
    ::-webkit-scrollbar {
      display: none;
    }
    * {
      scrollbar-width: none;
      -ms-overflow-style: none;
    }
    .scrollable::-webkit-scrollbar {
      display: none;
    }

    body {
      margin: 0;
      font-family: Inter, "Segoe UI", system-ui, -apple-system, sans-serif;
      background: radial-gradient(800px 500px at 10% 10%, #11141a 0%, rgba(0,0,0,0) 30%), linear-gradient(180deg, #0b0d10, #0f1418);
      color: #fff;
      min-height: 100vh;
      overflow-x: hidden;
      -webkit-overflow-scrolling: touch;
      overscroll-behavior: none;
      background-attachment: fixed;
    }
    
    html {
      -webkit-overflow-scrolling: touch;
      overscroll-behavior: none;
    }

    /* Top Controls - Responsive */
    .top-controls {
      position: fixed;
      top: 16px;
      right: 16px;
      z-index: 50;
      display: flex;
      gap: 12px;
      transition: opacity 0.15s ease;
    }
    
    @media (max-width: 480px) {
      .top-controls {
        top: 8px;
        right: 8px;
        gap: 8px;
      }
    }
    
    @media (max-width: 360px) {
      .top-controls {
        top: 4px;
        right: 4px;
        gap: 6px;
      }
    }
    
    .top-controls.fade {
      opacity: 0;
      transform: translateY(-10px);
      pointer-events: none;
    }

    .top-controls.fade .search-input-container {
      opacity: 0.5;
      transition: opacity 0.3s ease;
    }
    
    .control-btn {
      width: 44px;
      height: 44px;
      border-radius: 12px;
      display: flex;
      align-items: center;
      justify-content: center;
      background: rgba(255,255,255,.06);
      border: 1px solid rgba(255,255,255,.08);
      backdrop-filter: blur(8px);
      cursor: pointer;
      transition: transform 0.3s ease;
      position: relative;
    }
    
    @media (max-width: 480px) {
      .control-btn {
        width: 40px;
        height: 40px;
        border-radius: 10px;
      }
    }
    
    @media (max-width: 360px) {
      .control-btn {
        width: 36px;
        height: 36px;
        border-radius: 8px;
      }
    }
    
    .control-btn:hover {
      transform: translateY(-2px);
    }

    /* Search - Responsive */
    .search-container {
      display: flex;
      align-items: center;
      gap: 8px;
    }
    
    .search-input-container {
      display: none;
      align-items: center;
      background: rgba(255,255,255,.06);
      border: 1px solid rgba(255,255,255,.08);
      border-radius: 12px;
      padding: 12px 16px;
      backdrop-filter: blur(8px);
      transition: all 0.3s ease;
      animation: slideInFromRight 0.3s ease;
    }
    
    @media (max-width: 768px) {
      .search-input-container {
        padding: 10px 12px;
        border-radius: 10px;
      }
    }
    
    @media (max-width: 480px) {
      .search-input-container {
        padding: 8px 10px;
        border-radius: 8px;
      }
    }
    
    .search-input-container.show {
      display: flex;
    }
    
    .search-input {
      background: transparent;
      border: none;
      color: #fff;
      outline: none;
      width: 256px;
      margin-left: 8px;
    }
    
    @media (max-width: 768px) {
      .search-input {
        width: 200px;
      }
    }
    
    @media (max-width: 480px) {
      .search-input {
        width: 150px;
        margin-left: 6px;
      }
    }
    
    @media (max-width: 360px) {
      .search-input {
        width: 120px;
        margin-left: 4px;
      }
    }
    
    .search-input::placeholder {
      color: rgba(255,255,255,0.5);
    }
    
    .search-clear {
      margin-left: 8px;
      color: rgba(255,255,255,0.75);
      background: none;
      border: none;
      cursor: pointer;
    }

    /* Watch List - Responsive */
    .watch-badge {
      position: absolute;
      top: -4px;
      right: -4px;
      width: 20px;
      height: 20px;
      border-radius: 50%;
      background: #E63946;
      color: #fff;
      font-size: 12px;
      font-weight: 600;
      display: flex;
      align-items: center;
      justify-content: center;
    }
    
    @media (max-width: 480px) {
      .watch-badge {
        width: 18px;
        height: 18px;
        font-size: 10px;
        top: -3px;
        right: -3px;
      }
    }

    .watch-dropdown {
      position: absolute;
      top: 100%;
      right: 0;
      margin-top: 8px;
      width: 384px;
      background: #0e1116;
      border: 1px solid #1b1f27;
      border-radius: 16px;
      backdrop-filter: blur(8px);
      box-shadow: 0 25px 50px rgba(0,0,0,0.25);
      z-index: 60;
      display: none;
      opacity: 0;
      transform: translateY(-8px);
      transition: opacity 0.3s ease, transform 0.3s ease;
    }
    
    @media (max-width: 768px) {
      .watch-dropdown {
        width: 320px;
        border-radius: 12px;
      }
    }
    
    @media (max-width: 480px) {
      .watch-dropdown {
        width: 280px;
        border-radius: 10px;
        margin-top: 6px;
      }
    }
    
    @media (max-width: 360px) {
      .watch-dropdown {
        width: 250px;
        border-radius: 8px;
        margin-top: 4px;
      }
    }
    
    .watch-dropdown.show {
      display: block;
      opacity: 1;
      transform: translateY(0);
    }
    
    .watch-dropdown-header {
      padding: 20px;
      border-bottom: 1px solid #1b1f27;
    }
    
    @media (max-width: 480px) {
      .watch-dropdown-header {
        padding: 16px;
      }
    }
    
    @media (max-width: 360px) {
      .watch-dropdown-header {
        padding: 12px;
      }
    }
    
    .watch-dropdown-header h3 {
      font-size: 18px;
      font-weight: 600;
      color: #fff;
      margin: 0;
    }
    
    @media (max-width: 480px) {
      .watch-dropdown-header h3 {
        font-size: 16px;
      }
    }
    
    .watch-dropdown-content {
      max-height: 384px;
      overflow-y: auto;
      scroll-behavior: smooth;
    }
    
    @media (max-width: 480px) {
      .watch-dropdown-content {
        max-height: 300px;
      }
    }

    .watch-dropdown-content:hover {
      overscroll-behavior: contain;
    }
    
    .watch-item {
      padding: 16px;
      border-bottom: 1px solid rgba(27,31,39,0.3);
      display: flex;
      justify-content: space-between;
      align-items: flex-start;
      transition: transform 0.2s ease;
    }
    
    @media (max-width: 480px) {
      .watch-item {
        padding: 12px;
      }
    }
    
    .watch-item:hover {
      transform: scale(1.02);
    }
    
    .watch-item-info {
      flex: 1;
    }
    
    .watch-item-title {
      color: #fff;
      font-weight: 600;
      margin-bottom: 4px;
    }
    
    @media (max-width: 480px) {
      .watch-item-title {
        font-size: 14px;
      }
    }
    
    .watch-item-service {
      color: rgba(255,255,255,0.75);
      font-size: 14px;
      margin-bottom: 4px;
    }
    
    @media (max-width: 480px) {
      .watch-item-service {
        font-size: 12px;
      }
    }
    
    .watch-item-tech {
      color: rgba(255,255,255,0.6);
      font-size: 12px;
    }
    
    @media (max-width: 480px) {
      .watch-item-tech {
        font-size: 10px;
      }
    }
    
    .watch-remove {
      padding: 8px;
      background: none;
      border: none;
      border-radius: 4px;
      cursor: pointer;
      transition: transform 0.2s ease;
    }
    
    .watch-remove:hover {
      transform: scale(1.1);
    }

    /* Overlay */
    .overlay {
      position: fixed;
      inset: 0;
      background: rgba(0,0,0,0);
      backdrop-filter: blur(0px);
      z-index: 40;
      opacity: 0;
      pointer-events: none;
      transition: all 0.3s ease;
    }
    
    .overlay.show {
      backdrop-filter: blur(4px);
      opacity: 1;
      pointer-events: auto;
    }

    /* Drawer - Responsive */
    .drawer {
      position: fixed;
      top: 0;
      right: -320px;
      width: 320px;
      height: 100vh;
      background: #0e1116;
      border-left: 1px solid #1b1f27;
      box-shadow: -16px 0 48px rgba(0,0,0,0.5);
      z-index: 50;
      transition: right 0.3s cubic-bezier(0.22, 1, 0.36, 1);
    }
    
    @media (max-width: 480px) {
      .drawer {
        width: 280px;
        right: -280px;
      }
    }
    
    @media (max-width: 360px) {
      .drawer {
        width: 250px;
        right: -250px;
      }
    }
    
    .drawer.show {
      right: 0;
    }
    
    .drawer-header {
      padding: 20px;
      border-bottom: 1px solid #1b1f27;
    }
    
    @media (max-width: 480px) {
      .drawer-header {
        padding: 16px;
      }
    }
    
    .drawer-header h3 {
      font-size: 18px;
      font-weight: 600;
      color: #fff;
      margin: 0;
    }
    
    @media (max-width: 480px) {
      .drawer-header h3 {
        font-size: 16px;
      }
    }
    
    .logout-btn {
      margin: 20px;
      padding: 12px 16px;
      border-radius: 12px;
      border: none;
      background: linear-gradient(90deg, #e63946, #d2353f);
      color: #fff;
      font-weight: 900;
      cursor: pointer;
      width: calc(100% - 40px);
      transition: transform 0.3s ease;
    }
    
    @media (max-width: 480px) {
      .logout-btn {
        margin: 16px;
        padding: 10px 14px;
        border-radius: 10px;
        width: calc(100% - 32px);
      }
    }
    
    .logout-btn:hover {
      transform: translateY(-2px);
    }

    /* Main Content - Responsive */
    .main-content {
      padding: 24px;
      padding-top: 80px;
      max-width: 1280px;
      margin: 0 auto;
    }
    
    @media (max-width: 768px) {
      .main-content {
        padding: 20px;
        padding-top: 70px;
      }
    }
    
    @media (max-width: 480px) {
      .main-content {
        padding: 16px;
        padding-top: 60px;
      }
    }
    
    @media (max-width: 360px) {
      .main-content {
        padding: 12px;
        padding-top: 50px;
      }
    }

    .page-title {
      font-size: 30px;
      font-weight: 700;
      color: #fff;
      margin-bottom: 32px;
    }
    
    @media (max-width: 768px) {
      .page-title {
        font-size: 26px;
        margin-bottom: 24px;
      }
    }
    
    @media (max-width: 480px) {
      .page-title {
        font-size: 22px;
        margin-bottom: 20px;
      }
    }
    
    @media (max-width: 360px) {
      .page-title {
        font-size: 20px;
        margin-bottom: 16px;
      }
    }

    /* Table Container - Responsive */
    .table-container {
      background: rgba(255,255,255,.06);
      border: 1px solid rgba(255,255,255,.08);
      border-radius: 16px;
      backdrop-filter: blur(8px);
      box-shadow: 0 25px 50px rgba(0,0,0,0.25);
      overflow: hidden;
    }
    
    @media (max-width: 768px) {
      .table-container {
        border-radius: 12px;
      }
    }
    
    @media (max-width: 480px) {
      .table-container {
        border-radius: 10px;
      }
    }

    .table-wrapper {
      overflow-x: auto;
    }

    /* Desktop Table */
    .desktop-table {
      width: 100%;
      border-collapse: collapse;
      display: table;
    }
    
    .desktop-table th {
      text-align: left;
      padding: 16px;
      color: #fff;
      font-weight: 600;
      border-bottom: 1px solid rgba(255,255,255,0.1);
    }
    
    @media (max-width: 768px) {
      .desktop-table th {
        padding: 12px 8px;
        font-size: 14px;
      }
    }
    
    .desktop-table tr {
      transition: all 0.2s ease-out;
    }
    
    .desktop-table tr:not(:last-child) {
      border-bottom: 1px solid rgba(255,255,255,0.05);
    }
    
    .desktop-table tbody tr:hover {
      transform: scale(1.01);
      box-shadow: 0 4px 12px rgba(0,0,0,0.15);
    }

    .desktop-table td {
      padding: 16px;
      color: rgba(255,255,255,0.9);
    }
    
    @media (max-width: 768px) {
      .desktop-table td {
        padding: 12px 8px;
        font-size: 14px;
      }
    }

    /* Mobile Cards - Hidden on Desktop */
    .mobile-cards {
      display: none;
    }
    
    @media (max-width: 640px) {
      .desktop-table {
        display: none;
      }
      
      .mobile-cards {
        display: block;
        padding: 16px;
      }
    }
    
    @media (max-width: 480px) {
      .mobile-cards {
        padding: 12px;
      }
    }
    
    .vehicle-card {
      background: rgba(255,255,255,.04);
      border: 1px solid rgba(255,255,255,.06);
      border-radius: 12px;
      padding: 16px;
      margin-bottom: 16px;
      backdrop-filter: blur(4px);
      transition: transform 0.2s ease, box-shadow 0.2s ease;
    }
    
    @media (max-width: 480px) {
      .vehicle-card {
        border-radius: 10px;
        padding: 14px;
        margin-bottom: 14px;
      }
    }
    
    .vehicle-card:hover {
      transform: translateY(-2px);
      box-shadow: 0 8px 24px rgba(0,0,0,0.2);
    }
    
    .card-header {
      display: flex;
      justify-content: space-between;
      align-items: flex-start;
      margin-bottom: 12px;
      border-bottom: 1px solid rgba(255,255,255,0.1);
      padding-bottom: 8px;
    }
    
    .card-title {
      font-size: 16px;
      font-weight: 600;
      color: #fff;
      margin: 0;
    }
    
    @media (max-width: 480px) {
      .card-title {
        font-size: 15px;
      }
    }
    
    .card-number {
      font-size: 14px;
      color: rgba(255,255,255,0.6);
      font-weight: 500;
    }
    
    @media (max-width: 480px) {
      .card-number {
        font-size: 13px;
      }
    }
    
    .card-row {
      display: flex;
      justify-content: space-between;
      align-items: center;
      margin: 8px 0;
    }
    
    .card-label {
      font-size: 13px;
      color: rgba(255,255,255,0.7);
      font-weight: 500;
    }
    
    @media (max-width: 480px) {
      .card-label {
        font-size: 12px;
      }
    }
    
    .card-value {
      font-size: 14px;
      color: rgba(255,255,255,0.9);
      text-align: right;
    }
    
    @media (max-width: 480px) {
      .card-value {
        font-size: 13px;
      }
    }
    
    .card-actions {
      display: flex;
      justify-content: space-between;
      align-items: center;
      margin-top: 16px;
      padding-top: 12px;
      border-top: 1px solid rgba(255,255,255,0.1);
    }
    
    @media (max-width: 480px) {
      .card-actions {
        margin-top: 14px;
        padding-top: 10px;
      }
    }

    /* Badges - Responsive */
    .badge {
      display: inline-block;
      white-space: nowrap;
      font-size: 14px !important;
      font-weight: 600 !important;
      padding: 6px 12px !important;
      border-radius: 8px !important;
      letter-spacing: 0.5px;
      box-shadow: 0 2px 8px rgba(0,0,0,0.4);
      text-transform: uppercase;
    }
    
    @media (max-width: 768px) {
      .badge {
        font-size: 12px !important;
        padding: 5px 10px !important;
        border-radius: 6px !important;
      }
    }
    
    @media (max-width: 640px) {
      .badge {
        font-size: 11px !important;
        padding: 4px 8px !important;
        border-radius: 5px !important;
      }
    }
    
    @media (max-width: 480px) {
      .badge {
        font-size: 10px !important;
        padding: 3px 6px !important;
        border-radius: 4px !important;
      }
    }

    .badge-success {
      background-color: #28d17c !important;
      color: #fff !important;
    }

    .badge-warning {
      background-color: #ffc107 !important;
      color: #212529 !important;
    }

    .badge-danger {
      background-color: #ff3b30 !important;
      color: #fff !important;
    }
    
    .badge-paid {
      background: #10b981;
      color: #fff;
    }
    
    .badge-advance {
      background: #f59e0b;
      color: #fff;
    }
    
    .badge-unpaid {
      background: #ef4444;
      color: #fff;
    }

    /* Watch Button - Responsive */
    .watch-btn {
      padding: 8px;
      background: none;
      border: none;
      border-radius: 8px;
      cursor: pointer;
      transition: transform 0.2s ease;
    }
    
    @media (max-width: 640px) {
      .watch-btn {
        padding: 6px;
        border-radius: 6px;
      }
    }
    
    .watch-btn:hover {
      transform: scale(1.1);
    }

    /* Toast - Responsive */
    .toast {
      position: fixed;
      top: 50%;
      left: 50%;
      transform: translate(-50%, -50%);
      padding: 20px 28px;
      border-radius: 16px;
      font-size: 14px;
      font-weight: 500;
      display: flex;
      align-items: center;
      justify-content: center;
      box-shadow: 0 25px 50px rgba(0,0,0,0.25);
      z-index: 100;
      min-width: 384px;
      max-width: 384px;
      opacity: 0;
      pointer-events: none;
      transition: all 0.35s ease;
    }
    
    @media (max-width: 768px) {
      .toast {
        min-width: 320px;
        max-width: 320px;
        padding: 16px 24px;
        border-radius: 12px;
      }
    }
    
    @media (max-width: 480px) {
      .toast {
        min-width: 280px;
        max-width: 280px;
        padding: 14px 20px;
        border-radius: 10px;
        font-size: 13px;
      }
    }
    
    @media (max-width: 360px) {
      .toast {
        min-width: 240px;
        max-width: 240px;
        padding: 12px 16px;
        border-radius: 8px;
        font-size: 12px;
      }
    }
    
    .toast.show {
      opacity: 1;
      pointer-events: auto;
      transform: translate(-50%, -50%) scale(1.02);
    }
    
    .toast-success {
      background: linear-gradient(135deg, #10b981, #059669);
      color: #fff;
    }
    
    .toast-error {
      background: #ef4444;
      color: #fff;
    }

    /* No Results - Responsive */
    .no-results {
      text-align: center;
      color: rgba(255,255,255,0.75);
      margin-top: 32px;
    }
    
    @media (max-width: 768px) {
      .no-results {
        margin-top: 24px;
        font-size: 14px;
      }
    }
    
    @media (max-width: 480px) {
      .no-results {
        margin-top: 20px;
        font-size: 13px;
      }
    }

    /* Icons - Responsive */
    .ph {
      font-size: 28px !important;
      color: #fff !important;
    }
    
    @media (max-width: 480px) {
      .ph {
        font-size: 24px !important;
      }
    }
    
    @media (max-width: 360px) {
      .ph {
        font-size: 20px !important;
      }
    }

    /* Animations */
    @keyframes slideInFromRight {
      from {
        transform: translateX(16px);
        opacity: 0;
      }
      to {
        transform: translateX(0);
        opacity: 1;
      }
    }

    /* Enhanced Badge Colors */
    .badge-danger  { 
      background-color: #ff1744 !important; 
      color: #fff !important; 
      box-shadow: 0 0 10px rgba(255,23,68,.9); 
    }
    
    .badge-warning { 
      background-color: #faff00 !important; 
      color: #000 !important; 
      box-shadow: 0 0 10px rgba(250,255,0,.9); 
    }
    
    .badge-success { 
      background-color: #39ff14 !important; 
      color: #000 !important; 
      box-shadow: 0 0 10px rgba(57,255,20,.9); 
    }

    /* Landscape orientation fixes for mobile */
    @media (max-height: 500px) and (orientation: landscape) {
      .main-content {
        padding-top: 50px;
      }
      
      .page-title {
        font-size: 18px;
        margin-bottom: 12px;
      }
      
      .vehicle-card {
        padding: 12px;
        margin-bottom: 12px;
      }
      
      .watch-dropdown {
        max-height: 200px;
      }
      
      .watch-dropdown-content {
        max-height: 150px;
      }
    }

    /* Ultra small screens (below 320px) */
    @media (max-width: 320px) {
      .top-controls {
        gap: 4px;
        top: 2px;
        right: 2px;
      }
      
      .control-btn {
        width: 32px;
        height: 32px;
      }
      
      .search-input {
        width: 100px;
      }
      
      .watch-dropdown {
        width: 220px;
      }
      
      .drawer {
        width: 220px;
        right: -220px;
      }
      
      .main-content {
        padding: 8px;
        padding-top: 45px;
      }
      
      .page-title {
        font-size: 18px;
        margin-bottom: 12px;
      }
      
      .vehicle-card {
        padding: 10px;
        margin-bottom: 10px;
      }
      
      .badge {
        font-size: 9px !important;
        padding: 2px 4px !important;
        border-radius: 3px !important;
      }
    }

  </style>
</head>
<body>

<!-- Top Controls -->
<div class="top-controls">
  <!-- Search -->
  <div class="search-container">
    <div id="searchInput" class="search-input-container">
      <i class="ph ph-magnifying-glass"></i>
      <input id="searchField" class="search-input" placeholder="Search" />
      <button id="searchClear" class="search-clear" style="display: none;">✕</button>
    </div>
    <button id="searchToggle" class="control-btn">
      <i class="ph ph-magnifying-glass"></i>
    </button>
  </div>

  <!-- Watch List -->
  <div class="watch-container" style="position: relative;">
    <button id="watchToggle" class="control-btn">
      <i class="ph ph-eye"></i>
      <span id="watchBadge" class="watch-badge" style="display: none;">0</span>
    </button>
    <div id="watchDropdown" class="watch-dropdown">
      <div class="watch-dropdown-header">
        <h3>Watch List</h3>
      </div>
      <div id="watchContent" class="watch-dropdown-content">
        <div style="padding: 24px; text-align: center; color: rgba(255,255,255,0.75);">
          No vehicles in watch list
        </div>
      </div>
    </div>
  </div>

  <!-- Menu -->
  <button id="menuToggle" class="control-btn">
    <i class="ph ph-list"></i>
  </button>
</div>

<!-- Overlay -->
<div id="overlay" class="overlay"></div>

<!-- Drawer -->
<div id="drawer" class="drawer">
  <div class="drawer-header">
    <h3>MENU</h3>
  </div>
  <button class="logout-btn" onclick="logout()">Logout</button>
</div>

<!-- Main Content -->
<div class="main-content">
  <h1 class="page-title">Dashboard</h1>
  
  <div class="table-container">
    <!-- Desktop Table -->
    <div class="table-wrapper">
      <table class="desktop-table">
        <thead>
          <tr>
           <th>S.No</th>
           <th>Customer</th>
           <th>Vehicle No</th>
           <th>Vehicle Name</th>
           <th>Department</th>
           <th>Service</th>
           <th>Technician</th>
           <th>Parts Status</th>
           <th>Status</th>
           <th>Payment</th>
           <th>Watch</th>
          </tr>
        </thead>
        <tbody id="tableBody"></tbody>
      </table>
    </div>
    
    <!-- Mobile Cards -->
    <div class="mobile-cards" id="mobileCards"></div>
  </div>

  <div id="noResults" class="no-results" style="display: none;">
    No vehicles found matching "<span id="searchTerm"></span>"
  </div>
</div>

<!-- Toast -->
<div id="toast" class="toast">
  <span id="toastMessage"></span>
</div>


<script>

// Simple unified status badge (only 3 neon statuses)
function statusBadge(status) {
  const val = (status || '').toLowerCase();
  if (val === 'done') return '<span class="badge badge-success">Done</span>';
  if (val === 'in service') return '<span class="badge badge-warning">In Service</span>';
  return '<span class="badge badge-danger">Waiting</span>';
}

// Global variables
let vehicles = {{ vehicles|tojson }};
let filteredVehicles = [...vehicles];

// DOM elements
const searchToggle = document.getElementById('searchToggle');
const searchInput = document.getElementById('searchInput');
const searchField = document.getElementById('searchField');
const searchClear = document.getElementById('searchClear');
const watchToggle = document.getElementById('watchToggle');
const watchDropdown = document.getElementById('watchDropdown');
const watchBadge = document.getElementById('watchBadge');
const watchContent = document.getElementById('watchContent');
const menuToggle = document.getElementById('menuToggle');
const overlay = document.getElementById('overlay');
const drawer = document.getElementById('drawer');
const tableBody = document.getElementById('tableBody');
const mobileCards = document.getElementById('mobileCards');
const noResults = document.getElementById('noResults');
const searchTerm = document.getElementById('searchTerm');
const toast = document.getElementById('toast');
const toastMessage = document.getElementById('toastMessage');

// Initialize
updateWatchList();
renderTable();

// Fade top controls on scroll
const topControls = document.querySelector('.top-controls');

window.addEventListener('scroll', () => {
  const scrollY = window.scrollY || window.pageYOffset;
  if (scrollY > 20) {
    topControls.classList.add('fade');
  } else {
    topControls.classList.remove('fade');
  }
});

// Responsive screen size detection
function isMobile() {
  return window.innerWidth <= 640;
}

// API update function - WATCH ONLY (no parts status picker)
async function updateVehicleAPI(vehicleId, key, value) {
  try {
    console.log('Updating:', vehicleId, key, value);
    
    const response = await fetch('/api/update', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({
        id: String(vehicleId),
        key: key,
        value: value
      })
    });

    const result = await response.json();
    console.log('API Response:', result);

    if (result.success) {
      const vehicle = vehicles.find(v => String(v.id) === String(vehicleId));
      if (vehicle) {
        vehicle[key] = value;
      }

      renderTable();
      updateWatchList();

      showToast('Watch status updated successfully', 'success');

      return true;
    } else {
      console.error('API Error:', result.error);
      showToast(result.error || 'Update failed', 'error');
      return false;
    }

  } catch (error) {
    console.error('Network Error:', error);
    showToast('Network error. Please check your connection.', 'error');
    return false;
  }
}

// Search functionality - Fixed for exact matching
searchToggle.addEventListener('click', () => {
  const isVisible = searchInput.classList.contains('show');
  if (isVisible) {
    searchInput.classList.remove('show');
  } else {
    searchInput.classList.add('show');
    setTimeout(() => searchField.focus(), 200);
  }
});

searchField.addEventListener('input', () => {
  const query = searchField.value.trim();
  if (query) {
    searchClear.style.display = 'block';
  } else {
    searchClear.style.display = 'none';
    filteredVehicles = [...vehicles];
    renderTable();
    noResults.style.display = 'none';
  }
});

// Fixed search functionality for exact matching (case insensitive)
searchField.addEventListener('keyup', () => {
  const query = searchField.value.trim().toLowerCase();
  if (!query) {
    filteredVehicles = [...vehicles];
    renderTable();
    noResults.style.display = 'none';
    return;
  }

  filteredVehicles = vehicles.filter(vehicle => {
    const fields = [
      vehicle.customer?.toLowerCase() || '',
      vehicle.vehicle_no?.toLowerCase() || '',
      vehicle.vehicle_name?.toLowerCase() || '',
      vehicle.department?.toLowerCase() || '',
      vehicle.service?.toLowerCase() || '',
      vehicle.technician?.toLowerCase() || '',
      vehicle.parts?.toLowerCase() || '',
      vehicle.payment?.toLowerCase() || ''
    ];
    return fields.some(field => field === query);
  });

  renderTable();
  
  if (filteredVehicles.length === 0) {
    searchTerm.textContent = searchField.value.trim();
    noResults.style.display = 'block';
  } else {
    noResults.style.display = 'none';
  }
});

searchClear.addEventListener('click', () => {
  searchField.value = '';
  searchClear.style.display = 'none';
  filteredVehicles = [...vehicles];
  renderTable();
  noResults.style.display = 'none';
});

// Watch list functionality  
watchToggle.addEventListener('click', () => {
  const isVisible = watchDropdown.classList.contains('show');
  if (isVisible) {
    watchDropdown.classList.remove('show');
    if (
      !drawer.classList.contains('show') &&
      !searchInput.classList.contains('show')
    ) {
      overlay.classList.remove('show');
    }
  } else {
    watchDropdown.classList.add('show');
    overlay.classList.add('show');
  }
});

// Menu functionality
menuToggle.addEventListener('click', () => {
  drawer.classList.add('show');
  overlay.classList.add('show');
});

// Overlay click
overlay.addEventListener('click', () => {
  if (watchDropdown.classList.contains('show')) watchDropdown.classList.remove('show');
  if (drawer.classList.contains('show')) drawer.classList.remove('show');
  if (searchInput.classList.contains('show')) searchInput.classList.remove('show');
  overlay.classList.remove('show');
});

// Master click handler for watch interactions only (no parts picker)
document.addEventListener('click', async (e) => {
  // Close search if clicked outside
  if (!searchInput.contains(e.target) && !searchToggle.contains(e.target) && searchInput.classList.contains('show')) {
    searchInput.classList.remove('show');
  }
 
  // Close watch dropdown if clicked outside
  if (!watchDropdown.contains(e.target) && !watchToggle.contains(e.target) && watchDropdown.classList.contains('show')) {
    watchDropdown.classList.remove('show');
    if (
      !drawer.classList.contains('show') &&
      !searchInput.classList.contains('show')
    ) {
      overlay.classList.remove('show');
    }
  }

  // Watch button clicks in table
  const watchBtn = e.target.closest('.watch-btn');
  if (watchBtn) {
    e.preventDefault();
    e.stopPropagation();
    
    const vehicleId = watchBtn.dataset.id;
    const vehicle = vehicles.find(v => String(v.id) === String(vehicleId));
    const newWatchStatus = !vehicle?.watch;
    
    await updateVehicleAPI(vehicleId, 'watch', newWatchStatus);
    return;
  }

  // Watch remove buttons in dropdown
  const removeBtn = e.target.closest('.watch-remove');
  if (removeBtn) {
    e.preventDefault();
    e.stopPropagation();
    
    const vehicleId = removeBtn.dataset.id;
    await updateVehicleAPI(vehicleId, 'watch', false);
    return;
  }
});

// Enhanced render table function with mobile support (NO PARTS PICKER - READ ONLY)
function renderTable() {
  // Clear both desktop and mobile containers
  tableBody.innerHTML = '';
  mobileCards.innerHTML = '';
  
  filteredVehicles.forEach((vehicle, index) => {
    // Desktop table row
    const row = document.createElement('tr');
    row.innerHTML = `
      <td>${index + 1}</td>
      <td>${vehicle.customer || ''}</td>
      <td>${vehicle.vehicle_no || ''}</td>
      <td>${vehicle.vehicle_name || ''}</td>
      <td>${vehicle.department || ''}</td>
      <td>${vehicle.service || ''}</td>
      <td>${vehicle.technician || ''}</td>
      <td>
        <span class="badge ${vehicle.parts === 'Arrived' ? 'badge-success' : 'badge-danger'}">${vehicle.parts || 'Not Arrived'}</span>
      </td>
      <td>${statusBadge(vehicle.status)}</td>
      <td>
        <span class="badge ${getPaymentBadgeClass(vehicle.payment)}">${vehicle.payment || 'Unpaid'}</span>
      </td>
      <td>
        <button class="watch-btn" data-id="${vehicle.id}">
          ${vehicle.watch ? 
            '<i class="ph ph-eye" style="color: #e63946;"></i>' :
            '<i class="ph ph-eye-slash" style="color: #9ca3af;"></i>'
          }
        </button>
      </td>
    `;
    tableBody.appendChild(row);

    // Mobile card
    const card = document.createElement('div');
    card.className = 'vehicle-card';
    card.innerHTML = `
      <div class="card-header">
        <h4 class="card-title">${vehicle.vehicle_no || 'N/A'} - ${vehicle.vehicle_name || 'N/A'}</h4>
        <span class="card-number">#${index + 1}</span>
      </div>
      
      <div class="card-row">
        <span class="card-label">Customer:</span>
        <span class="card-value">${vehicle.customer || 'N/A'}</span>
      </div>
      
      <div class="card-row">
        <span class="card-label">Department:</span>
        <span class="card-value">${vehicle.department || 'N/A'}</span>
      </div>
      
      <div class="card-row">
        <span class="card-label">Service:</span>
        <span class="card-value">${vehicle.service || 'N/A'}</span>
      </div>
      
      <div class="card-row">
        <span class="card-label">Technician:</span>
        <span class="card-value">${vehicle.technician || 'N/A'}</span>
      </div>
      
      <div class="card-row">
        <span class="card-label">Parts Status:</span>
        <span class="card-value">
          <span class="badge ${vehicle.parts === 'Arrived' ? 'badge-success' : 'badge-danger'}">${vehicle.parts || 'Not Arrived'}</span>
        </span>
      </div>
      
      <div class="card-row">
        <span class="card-label">Status:</span>
        <span class="card-value">${statusBadge(vehicle.status)}</span>
      </div>
      
      <div class="card-row">
        <span class="card-label">Payment:</span>
        <span class="card-value">
          <span class="badge ${getPaymentBadgeClass(vehicle.payment)}">${vehicle.payment || 'Unpaid'}</span>
        </span>
      </div>
      
      <div class="card-actions">
        <span>Watch Vehicle:</span>
        <button class="watch-btn" data-id="${vehicle.id}">
          ${vehicle.watch ? 
            '<i class="ph ph-eye" style="color: #e63946;"></i>' :
            '<i class="ph ph-eye-slash" style="color: #9ca3af;"></i>'
          }
        </button>
      </div>
    `;
    mobileCards.appendChild(card);
  });
}

// Update watch list
function updateWatchList() {
  const watchedVehicles = vehicles.filter(v => v.watch);
  
  if (watchedVehicles.length > 0) {
    watchBadge.textContent = watchedVehicles.length;
    watchBadge.style.display = 'flex';
  } else {
    watchBadge.style.display = 'none';
  }
  
  if (watchedVehicles.length === 0) {
    watchContent.innerHTML = '<div style="padding: 24px; text-align: center; color: rgba(255,255,255,0.75);">No vehicles in watch list</div>';
  } else {
    watchContent.innerHTML = watchedVehicles.map(vehicle => `
      <div class="watch-item">
        <div class="watch-item-info">
          <div class="watch-item-title">${vehicle.vehicle_no} - ${vehicle.vehicle_name}</div>
          <div class="watch-item-service">${vehicle.service}</div>
          <div class="watch-item-tech">${vehicle.technician}</div>
        </div>
        <button class="watch-remove" data-id="${vehicle.id}">
          <i class="ph ph-eye-slash" style="color: #e63946;"></i>
        </button>
      </div>
    `).join('');
  }
}

// Get payment badge class
function getPaymentBadgeClass(payment) {
  switch (payment) {
    case 'Paid': return 'badge-paid';
    case 'Advance Paid': return 'badge-advance';
    case 'Unpaid': return 'badge-unpaid';
    default: return 'badge-unpaid';
  }
}

// Show toast
function showToast(message, type) {
  toastMessage.textContent = message;
  toast.className = `toast toast-${type}`;
  toast.classList.add('show');
  
  setTimeout(() => {
    toast.classList.remove('show');
  }, type === 'error' ? 5000 : 3000);
}

// Logout
function logout() {
  window.location.href = '/logout';
}

// Auto-refresh with responsive handling
setInterval(async () => {
  try {
    const response = await fetch('/api/vehicles');
    if (response.ok) {
      const freshData = await response.json();
      vehicles = freshData;
      const currentQuery = searchField.value.trim().toLowerCase();
      if (currentQuery) {
        filteredVehicles = vehicles.filter(vehicle => {
          const fields = [
            vehicle.customer?.toLowerCase() || '',
            vehicle.vehicle_no?.toLowerCase() || '',
            vehicle.vehicle_name?.toLowerCase() || '',
            vehicle.department?.toLowerCase() || '',
            vehicle.service?.toLowerCase() || '',
            vehicle.technician?.toLowerCase() || '',
            vehicle.parts?.toLowerCase() || '',
            vehicle.payment?.toLowerCase() || ''
          ];
          return fields.some(field => field === currentQuery);
        });
      } else {
        filteredVehicles = [...freshData];
      }
      renderTable();
      updateWatchList();
    }
  } catch (error) {
    console.log('Auto-refresh failed:', error);
  }
}, 5000);

// Handle window resize for responsive adjustments
window.addEventListener('resize', () => {
  // Re-render table if switching between desktop/mobile view
  renderTable();
});

</script>
</body>
</html>""",
        vehicles=vehicles,
    )
###############################################################################
# Display (big screen)
###############################################################################
from flask import render_template_string, redirect, session

@app.route("/display")
def display():
    if session.get("user") != "display":
        return redirect("/")

    return render_template_string(
        r"""<!doctype html>
<html>
<head>
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>Vehicle Status</title>
  <link rel="stylesheet" href="https://unpkg.com/@phosphor-icons/web@2.0.3/src/regular/style.css">
  <link href="https://fonts.googleapis.com/css2?family=Michroma&display=swap" rel="stylesheet">
  <style>
    .logo-container {
      text-align: center;
      transition: opacity 0.8s ease; /* Added smooth transition */
    }
    .logo-container img {
      background: none; /* ensures no background */
      width: 300px; /* adjust as needed */
      height: auto;
      transition: opacity 0.8s ease; /* Added smooth transition for image */
    }
    
    /* Fixed: Proper targeting for logo fade */
    .logo-container.video-playing {
      opacity: 0 !important;
    }
    
    /* Double safety: Also target the image directly */
    .logo-container.video-playing img {
      opacity: 0 !important;
    }
    
    .page-text {
      text-align: center;
      font-family: 'Michroma', sans-serif;
      font-size: 50px; /* adjust size */
      margin: 5px 0; /* spacing above and below */
      font-weight: 1000; /* optional styling */
      word-spacing: 20px;
      transition: opacity 0.8s ease; /* Added smooth transition */
    }
   h1 {
      text-align: center;
      margin-top: 5px;
    }
    .page-text.video-playing {
      opacity: 0 !important; /* Added !important for priority */
    }
    /* Hide scrollbars */
    ::-webkit-scrollbar { display: none; }
    * { scrollbar-width: none; -ms-overflow-style: none; }
    .scrollable::-webkit-scrollbar { display: none; }

    body {
      margin: 0;
      font-family: Inter, "Segoe UI", system-ui, -apple-system, sans-serif;
      background: #0f1418; /* solid background (no gradient) */
      color: #fff;
      min-height: 100vh;
      overflow: hidden; /* TV optimization - no scrolling */
    }

    /* TV Optimizations - 43" 1080p Full HD */
    * {
      -webkit-font-smoothing: antialiased;
      -moz-osx-font-smoothing: grayscale;
      text-rendering: optimizeLegibility;
    }

    /* Top Controls - Only Menu, Hide during video */
    .top-controls {
      position: fixed;
      top: 24px;
      right: 24px;
      z-index: 50;
      display: flex;
      gap: 12px;
      transition: opacity 0.15s ease;
    }
    .top-controls.fade {
      opacity: 0;
      transform: translateY(-10px);
      pointer-events: none;
    }
    .top-controls.video-playing {
      opacity: 0;
      pointer-events: none;
      z-index: 40;
    }
    .control-btn {
      width: 56px;
      height: 56px;
      border-radius: 16px;
      display: flex;
      align-items: center;
      justify-content: center;
      background: rgba(255,255,255,.06);
      border: 1px solid rgba(255,255,255,.08);
      backdrop-filter: blur(8px);
      cursor: pointer;
      transition: transform 0.3s ease;
      position: relative;
    }
    .control-btn:hover { transform: translateY(-2px); }
    
    /* Fixed: More specific targeting for menu icon color */
    .control-btn i, 
    .control-btn i.ph, 
    .control-btn .ph,
    #menuToggle i,
    #menuToggle .ph {
      font-size: 24px !important; 
      color: #fff !important;
    }

    /* Overlay */
    .overlay {
      position: fixed;
      inset: 0;
      background: rgba(0,0,0,0);
      backdrop-filter: blur(0px);
      z-index: 40;
      opacity: 0;
      pointer-events: none;
      transition: all 0.3s ease;
    }
    .overlay.show {
      backdrop-filter: blur(4px);
      opacity: 1;
      pointer-events: auto;
    }

    /* Drawer */
    .drawer {
      position: fixed;
      top: 0;
      right: -400px;
      width: 400px;
      height: 100vh;
      background: #0e1116;
      border-left: 1px solid #1b1f27;
      box-shadow: -16px 0 48px rgba(0,0,0,0.5);
      z-index: 50;
      transition: right 0.3s cubic-bezier(0.22, 1, 0.36, 1);
    }
    .drawer.show { right: 0; }
    .drawer-header { padding: 30px; border-bottom: 1px solid #1b1f27; }
    .drawer-header h3 { font-size: 24px; font-weight: 600; color: #fff; margin: 0; }
    .logout-btn {
      margin: 30px;
      padding: 18px 24px;
      border-radius: 16px;
      border: none;
      background: linear-gradient(90deg, #e63946, #d2353f);
      color: #fff;
      font-weight: 900;
      cursor: pointer;
      width: calc(100% - 60px);
      transition: transform 0.3s ease;
      font-size: 18px;
    }
    .logout-btn:hover { transform: translateY(-2px); }

    /* Main Content - 1920x1080 Optimized */
    .main-content {
      padding: 40px 50px;
      padding-top: 10px;
      max-width: 100%;
      margin: 0 auto;
      height: calc(100vh - 140px);
      display: flex;
      flex-direction: column;
    }

    /* Page Title - 1080p Optimized */
    .page-title {
      font-size: 52px; /* Optimized for 1920x1080 */
      font-weight: 700;
      color: #fff;
      margin-bottom: 5px;
      margin-top: 5px;
      text-align: center;
      text-shadow: 3px 3px 6px rgba(0,0,0,0.6);
      transition: opacity 0.8s ease;
      letter-spacing: 1px;
    }
    .page-title.video-playing {
      opacity: 0;
    }

    /* Content Wrapper for sliding pages */
    .content-wrapper {
      flex: 1;
      position: relative;
      overflow: hidden;
    }

    /* iOS Home screen style animation for table containers */
    .table-container {
      background: rgba(255,255,255,.06);
      border: 1px solid rgba(255,255,255,.08);
      border-radius: 20px;
      backdrop-filter: blur(8px);
      box-shadow: 0 30px 60px rgba(0,0,0,0.3);
      overflow: hidden;
      height: 100%;
      position: absolute;
      width: 100%;
      transform-origin: center;
      will-change: transform;
      transition: transform 0.8s cubic-bezier(0.4, 0, 0.2, 1);
    }

    /* iOS-style slide states - smooth simultaneous movement */
    .table-container.slide-out-left {
      transform: translateX(-100%);
    }

    .table-container.slide-in-from-right {
      transform: translateX(100%);
    }

    .table-container.slide-active {
      transform: translateX(0);
    }

    .table-wrapper { 
      overflow: hidden; 
      height: 100%;
      display: flex;
      flex-direction: column;
      padding: 16px;
    }

    table { 
      width: 100%; 
      border-collapse: collapse; 
      font-size: 30px; /* 1920x1080 readability */
    }

    tbody {
      vertical-align: top;
    }

    th {
      text-align: left;
      padding: 24px 20px;
      color: #fff;
      font-weight: 700;
      border-bottom: 2px solid rgba(255,255,255,0.15);
      font-size: 42px; /* 1920x1080 headers */
      text-shadow: 2px 2px 4px rgba(0,0,0,0.6);
      letter-spacing: 0.5px;
    }

    tr { transition: all 0.2s ease-out; }
    tr:not(:last-child) { border-bottom: 1px solid rgba(255,255,255,0.08); }
    tbody tr:hover {
      transform: scale(1.005);
      box-shadow: 0 6px 16px rgba(0,0,0,0.2);
    }

    td { 
      padding: 22px 20px; 
      color: rgba(255,255,255,0.95); 
      font-size: 40px; /* 1920x1080 readability */
      line-height: 1.4;
      font-weight: 500;
    }

    /* Badges - 1920x1080 Optimized */
    .badge {
      display: inline-block;
      white-space: nowrap;
      font-size: 26px !important; /* 1920x1080 optimal */
      font-weight: 800 !important;
      padding: 10px 20px !important;
      border-radius: 20px !important;
      letter-spacing: 0.6px;
      box-shadow: 0 3px 12px rgba(0,0,0,0.5);
      text-transform: uppercase;
    }

    .badge-danger  { background-color: #ff1744 !important; color: #fff !important; box-shadow: 0 0 20px rgba(255,23,68,.9); }
    .badge-warning { background-color: #ffeb3b !important; color: #000 !important; box-shadow: 0 0 20px rgba(250,255,0,.9); }
    .badge-success { background-color: #39ff14 !important; color: #000 !important; box-shadow: 0 0 20px rgba(57,255,20,.9); }

    /* Video Container */
    .video-container {
      position: fixed;
      top: 0;
      left: 0;
      right: 0;
      bottom: 0;
      display: flex;
      align-items: center;
      justify-content: center;
      background: rgba(0,0,0,0.95);
      transform: translateX(100%);
      opacity: 0;
      transition: transform 0.8s ease, opacity 0.8s ease;
      z-index: 60;
    }

    .video-container.slide-in {
      transform: translateX(0);
      opacity: 1;
    }

    .video-container video {
      width: 100vw;
      height: 100vh;
      object-fit: cover;
    }

    /* Page Indicator - 1920x1080 optimized */
    .page-indicator {
      position: fixed;
      bottom: 40px;
      left: 50%;
      transform: translateX(-50%);
      background: rgba(255,255,255,.12);
      border: 2px solid rgba(255,255,255,.2);
      border-radius: 24px;
      padding: 12px 24px;
      backdrop-filter: blur(12px);
      color: #fff;
      font-size: 18px; /* 1080p optimized */
      font-weight: 700;
      text-shadow: 2px 2px 4px rgba(0,0,0,0.6);
      transition: opacity 0.8s ease;
      letter-spacing: 0.5px;
    }
    .page-indicator.video-playing {
      opacity: 0;
    }
   
    .no-results { 
      text-align: center; 
      color: rgba(255,255,255,0.8); 
      margin-top: 30px; 
      font-size: 24px; /* 1080p readability */
      font-weight: 600;
    }

    /* Removed the generic .ph rule that was causing conflicts */
 </style>
</head>
<body>
  <div class="logo-container">
    <img src="/static/logo1.png" alt="Logo">
  </div>
    <div class="page-text">
    AL SULAIMAN GARAGE
  </div>
<!-- Top Controls (Menu only - search removed) -->
<div class="top-controls">
  <!-- Menu -->
  <button id="menuToggle" class="control-btn" aria-label="Menu">
    <i class="ph ph-list"></i>
  </button>
</div>

<!-- Overlay -->
<div id="overlay" class="overlay"></div>

<!-- Drawer -->
<div id="drawer" class="drawer">
  <div class="drawer-header">
    <h3>MENU</h3>
  </div>
  <button class="logout-btn" onclick="logout()">Logout</button>
</div>

<!-- Main Content -->
<div class="main-content">
  <h1 class="page-title">Vehicle Status</h1>

  <div class="content-wrapper">
    <div id="tableContainer" class="table-container">
      <div class="table-wrapper">
        <table>
          <thead>
            <tr>
              <th>Vehicle No</th>
              <th>Vehicle Name</th>
              <th>Department</th>
              <th>Technician</th>
              <th>Status</th>
            </tr>
          </thead>
          <tbody id="tableBody"></tbody>
        </table>
      </div>
    </div>

    <div id="videoContainer" class="video-container">
      <video id="displayVideo" autoplay muted loop>
        <source id="videoSource" src="/static/video.mp4" type="video/mp4">
        Your browser does not support the video tag.
      </video>
    </div>
  </div>

  <div id="pageIndicator" class="page-indicator" style="display: none;">
    Page 1 of 1
  </div>

  <div id="noResults" class="no-results" style="display: none;">
    No vehicles found
  </div>
</div>

<script>
// Live data exactly like your baseline: pull from /api/vehicles and refresh
let vehicles = [];
let filteredVehicles = [];
let currentPage = 0;
let totalPages = 0;
let isShowingVideo = false;
let pageTimer = null;
let videoTimer = null;
let currentVideoIndex = 0;

const ROWS_PER_PAGE = 5; // Changed from 9 to 7
const PAGE_DURATION = 6000; // 6 seconds
const VIDEO_DURATION = 30000; // 30 seconds
const VIDEO_FILES = [
  '/static/video.mp4',
  '/static/video1.mp4', 
  '/static/video2.mp4',
  '/static/video3.mp4',
  '/static/video4.mp4'
];

// DOM references
const menuToggle   = document.getElementById('menuToggle');
const overlay      = document.getElementById('overlay');
const drawer       = document.getElementById('drawer');
let tableBody      = document.getElementById('tableBody');
const noResults    = document.getElementById('noResults');
let tableContainer = document.getElementById('tableContainer');
const videoContainer = document.getElementById('videoContainer');
const pageIndicator = document.getElementById('pageIndicator');
const displayVideo = document.getElementById('displayVideo');
const videoSource = document.getElementById('videoSource');
const topControls = document.querySelector('.top-controls');
const pageTitle = document.querySelector('.page-title');
const logoContainer = document.querySelector('.logo-container');
const pageText = document.querySelector('.page-text');


// Fetch vehicles (baseline style)
async function fetchVehicles(){
  const res = await fetch('/api/vehicles');
  if (!res.ok) return [];
  return await res.json();
}

// Render current page with iOS home screen style sliding animation
function renderCurrentPage(slideDirection = null) {
  const visibleVehicles = filteredVehicles.filter(v => v.visible);
  const startIndex = currentPage * ROWS_PER_PAGE;
  const endIndex = Math.min(startIndex + ROWS_PER_PAGE, visibleVehicles.length);
  const pageVehicles = visibleVehicles.slice(startIndex, endIndex);

  // Handle iOS-style sliding animation with two containers
  if (slideDirection === 'right') {
    // Create a duplicate container for the new content
    const newContainer = tableContainer.cloneNode(true);
    newContainer.id = 'tableContainerNew';
    
    // Position new container off-screen to the right
    newContainer.classList.add('slide-in-from-right');
    
    // Update the new container's content
    const newTableBody = newContainer.querySelector('#tableBody');
    newTableBody.id = 'tableBodyNew';
    newTableBody.innerHTML = '';
    pageVehicles.forEach(v => {
      const row = document.createElement('tr');
      row.innerHTML = `
        <td>${v.vehicle_no || ''}</td>
        <td>${v.vehicle_name || ''}</td>
        <td>${v.department || ''}</td>
        <td>${v.technician || ''}</td>
        <td>${statusBadge(v.status)}</td>
      `;
      newTableBody.appendChild(row);
    });
    
    // Add new container to DOM
    tableContainer.parentNode.appendChild(newContainer);
    
    // Force reflow
    newContainer.offsetHeight;
    
    // Start simultaneous animation
    requestAnimationFrame(() => {
      // Current page slides out to left
      tableContainer.classList.add('slide-out-left');
      
      // New page slides in from right
      newContainer.classList.remove('slide-in-from-right');
      newContainer.classList.add('slide-active');
      
      // After animation completes, clean up
      setTimeout(() => {
        // Remove old container
        const oldContainer = document.getElementById('tableContainer');
        if (oldContainer) {
          oldContainer.remove();
        }
        
        // Replace with new container
        newContainer.id = 'tableContainer';
        newContainer.classList.remove('slide-active');
        
        // Update global references
        tableContainer = newContainer;
        tableBody = newContainer.querySelector('#tableBodyNew');
        tableBody.id = 'tableBody';
      }, 800);
    });
  } else {
    renderTableContent(pageVehicles);
  }

  // Update page indicator
  if (totalPages > 1) {
    pageIndicator.textContent = `Page ${currentPage + 1} of ${totalPages}`;
    pageIndicator.style.display = 'block';
  } else {
    pageIndicator.style.display = 'none';
  }
}

// Render table content
function renderTableContent(pageVehicles) {
  const currentTableBody = document.getElementById('tableBody');
  currentTableBody.innerHTML = '';
  pageVehicles.forEach(v => {
    const row = document.createElement('tr');
    row.innerHTML = `
      <td>${v.vehicle_no || ''}</td>
      <td>${v.vehicle_name || ''}</td>
      <td>${v.department || ''}</td>
      <td>${v.technician || ''}</td>
      <td>${statusBadge(v.status)}</td>
    `;
    currentTableBody.appendChild(row);
  });
}

// Status badge (matches dashboard badge tokens)
function statusBadge(s) {
  switch(s) {
    case 'Done':       return '<span class="badge badge-success">Done</span>';
    case 'In Service': return '<span class="badge badge-warning">In Service</span>';
    default:           return '<span class="badge badge-danger">Waiting</span>';
  }
}

// Show video with smooth transition
function showVideo() {
  isShowingVideo = true;
  
  // Hide all UI elements
  topControls.classList.add('video-playing');
  pageTitle.classList.add('video-playing');
  pageIndicator.classList.add('video-playing');
  logoContainer.classList.add('video-playing');  
  pageText.classList.add('video-playing');       
  
  tableContainer.classList.add('slide-out-left');
  
  setTimeout(() => {
    // Set the current video source
    videoSource.src = VIDEO_FILES[currentVideoIndex];
    displayVideo.load(); // Reload video with new source
    
    videoContainer.classList.add('slide-in');
    displayVideo.currentTime = 0; // Reset video
    displayVideo.play();
  }, 400);

  // Hide video after 30 seconds and restart cycle
  videoTimer = setTimeout(() => {
    hideVideo();
  }, VIDEO_DURATION);
}

// Hide video and show table
function hideVideo() {
  isShowingVideo = false;
  videoContainer.classList.remove('slide-in');
  
  // Move to next video for next cycle
  currentVideoIndex = (currentVideoIndex + 1) % VIDEO_FILES.length;
  
  setTimeout(() => {
    // Show all UI elements again
    topControls.classList.remove('video-playing');
    pageTitle.classList.remove('video-playing');
    pageIndicator.classList.remove('video-playing');
    logoContainer.classList.remove('video-playing'); 
    pageText.classList.remove('video-playing');    
    
    tableContainer.classList.remove('slide-out-left');
    currentPage = 0; // Reset to first page
    renderCurrentPage();
    console.log(`Video hidden, restarting page cycle from page 1. Next video will be: ${VIDEO_FILES[currentVideoIndex]}`);
    startPageCycle();
  }, 800);
}

// Start automatic page cycling
function startPageCycle() {
  clearTimeout(pageTimer);
  
  if (totalPages === 0) return;
  if (isShowingVideo) return;

  // Always start the timer for next page change
  pageTimer = setTimeout(() => {
    if (isShowingVideo) return;

    currentPage++;
    console.log(`Moving to page ${currentPage + 1} of ${totalPages}`);
    
    if (currentPage >= totalPages) {
      // All pages shown, show video
      console.log(`All pages shown, showing video: ${VIDEO_FILES[currentVideoIndex]}`);
      showVideo();
    } else {
      // Show next page with Apple-style sliding animation
      renderCurrentPage('right');
      startPageCycle(); // Continue the cycle
    }
  }, PAGE_DURATION);
  
  console.log(`Page timer set for page ${currentPage + 1}, will advance in ${PAGE_DURATION}ms`);
}

// Stop all timers
function stopTimers() {
  clearTimeout(pageTimer);
  clearTimeout(videoTimer);
}

// Initialize + periodic refresh
async function refreshDataAndRender() {
  vehicles = await fetchVehicles();
  filteredVehicles = [...vehicles]; // No search functionality

  const visibleVehicles = filteredVehicles.filter(v => v.visible);
  const previousTotalPages = totalPages;
  totalPages = Math.ceil(visibleVehicles.length / ROWS_PER_PAGE);

  console.log(`Data refreshed: ${visibleVehicles.length} vehicles, ${totalPages} pages`);

  if (visibleVehicles.length === 0) {
    noResults.style.display = 'block';
    pageIndicator.style.display = 'none';
    stopTimers();
  } else {
    noResults.style.display = 'none';
    
    // Reset pagination if current page is beyond available pages
    if (currentPage >= totalPages) {
      currentPage = 0;
    }
    
    // Always render current page
    if (!isShowingVideo) {
      renderCurrentPage();
    }
  }
}

// Menu + overlay behavior
menuToggle.addEventListener('click', () => {
  const wasOpen = drawer.classList.contains('show');
  if (wasOpen) {
    drawer.classList.remove('show');
    overlay.classList.remove('show');
  } else {
    drawer.classList.add('show');
    overlay.classList.add('show');
  }
});

overlay.addEventListener('click', () => {
  drawer.classList.remove('show');
  overlay.classList.remove('show');
});

// Logout
function logout(){ window.location.href = '/logout'; }

// Initialize application
async function initialize() {
  await refreshDataAndRender();
  console.log(`Initialized: ${totalPages} total pages`);
  
  if (totalPages > 0 && !isShowingVideo) {
    console.log('Starting initial page cycle');
    startPageCycle();
  }
}

// Start the application
initialize();

// Refresh data every 3 seconds, but don't interfere with pagination
setInterval(async () => {
  await refreshDataAndRender();
}, 3000);

// Handle video errors
displayVideo.addEventListener('error', (e) => {
  console.error('Video playback error:', e);
  if (isShowingVideo) {
    hideVideo(); // Fallback to table if video fails
  }
});

// Video ended event (backup in case loop fails)
displayVideo.addEventListener('ended', () => {
  if (isShowingVideo) {
    displayVideo.currentTime = 0;
    displayVideo.play();
  }
});
</script>
</body>
</html>""",
    )
###############################################################################
# API
###############################################################################
@app.route("/api/vehicles", methods=["GET"])
def api_vehicles():
    return jsonify(read_vehicles())

@app.post("/api/add")
def api_add_vehicle():
    data = request.get_json(force=True) or {}
    def pick(name: str, default: str = "") -> str:
        val = data.get(name, default)
        return val.strip() if isinstance(val, str) else default

    new_vehicle = {
        "id": str(uuid.uuid4()),
        "customer": pick("customer"),
        "vehicle_no": pick("vehicle_no"),
        "vehicle_name": pick("vehicle_name"),
        "department": pick("department", departments[0] if departments else ""),
        "service": pick("service", services[0] if services else ""),
        "technician": pick("technician", technicians[0] if technicians else ""),
        "status": pick("status", STATUSES[0]),
        "payment": "Unpaid",
        "parts": "Not Arrived",
        "visible": True,
        "watch": False,
    }

    current_vehicles = read_vehicles()
    current_vehicles.append(new_vehicle)
    save_json(VEHICLES_FILE, current_vehicles)

    global vehicles
    vehicles = current_vehicles

    return jsonify({"success": True, "id": new_vehicle["id"]})

@app.post("/api/delete_vehicle")
def api_delete_vehicle():
    vid = (request.get_json(force=True) or {}).get("id")
    if not vid:
        return jsonify({"success": False, "message": "Missing id"}), 400

    current_vehicles = read_vehicles()
    before = len(current_vehicles)
    current_vehicles[:] = [v for v in current_vehicles if v.get("id") != vid]

    if len(current_vehicles) == before:
        return jsonify({"success": False, "message": "Vehicle not found"}), 404

    save_json(VEHICLES_FILE, current_vehicles)
    global vehicles
    vehicles = current_vehicles
    return jsonify({"success": True})

@app.post("/api/toggle_visibility")
def api_toggle_visibility():
    vid = (request.get_json(force=True) or {}).get("id")
    if not vid:
        return jsonify({"success": False, "message": "Missing id"}), 400

    current_vehicles = read_vehicles()

    for v in current_vehicles:
        if v.get("id") == vid:
            v["visible"] = not v.get("visible", True)
            save_json(VEHICLES_FILE, current_vehicles)
            global vehicles
            vehicles = current_vehicles
            return jsonify({"success": True, "visible": v["visible"]})

    return jsonify({"success": False, "message": "Vehicle not found"}), 404

# ---------- Departments ----------
@app.post("/api/add_department")
def api_add_department():
    d = (request.get_json(force=True) or {}).get("department", "").strip()
    if not d:
        return jsonify({"success": False, "message": "Empty name"}), 400
    if d not in departments:
        departments.append(d)
        save_json(DEPARTMENTS_FILE, departments)
    return jsonify({"success": True})

@app.post("/api/delete_department")
def api_delete_department():
    d = (request.get_json(force=True) or {}).get("department", "").strip()
    if not d:
        return jsonify({"success": False, "message": "Empty name"}), 400
    if d in departments:
        departments.remove(d)
        save_json(DEPARTMENTS_FILE, departments)
    return jsonify({"success": True})

# ---------- Technicians ----------
@app.post("/api/add_technician")
def api_add_technician():
    t = (request.get_json(force=True) or {}).get("technician", "").strip()
    if not t:
        return jsonify({"success": False, "message": "Empty name"}), 400
    if t not in technicians:
        technicians.append(t)
        save_json(TECHS_FILE, technicians)
    return jsonify({"success": True})

@app.post("/api/delete_technician")
def api_delete_technician():
    t = (request.get_json(force=True) or {}).get("technician", "").strip()
    if not t:
        return jsonify({"success": False, "message": "Empty name"}), 400
    if t in technicians:
        technicians.remove(t)
        save_json(TECHS_FILE, technicians)
    return jsonify({"success": True})

# ---------- Services ----------
@app.post("/api/add_service")
def api_add_service():
    s = (request.get_json(force=True) or {}).get("service", "").strip()
    if not s:
        return jsonify({"success": False, "message": "Empty name"}), 400
    if s not in services:
        services.append(s)
        save_json(SERVICES_FILE, services)
    return jsonify({"success": True})

@app.post("/api/delete_service")
def api_delete_service():
    s = (request.get_json(force=True) or {}).get("service", "").strip()
    if not s:
        return jsonify({"success": False, "message": "Empty name"}), 400
    if s in services:
        services.remove(s)
        save_json(SERVICES_FILE, services)
    return jsonify({"success": True})

# ---------- GET lists ----------
@app.get("/api/departments")
def api_get_departments():
    return jsonify(departments)

@app.get("/api/technicians")
def api_get_technicians():
    return jsonify(technicians)

@app.get("/api/services")
def api_get_services():
    return jsonify(services)

# ---------- Unified Update Route ----------
@app.post("/api/update")
def api_update():
    data = request.get_json(force=True) or {}
    vid = data.get("id")
    key = data.get("key")
    value = data.get("value")

    if not vid or not key:
        return jsonify({"success": False, "message": "Missing id or key"}), 400

    allowed = {"customer","vehicle_no","vehicle_name","department","service","technician","status","payment","parts","visible","watch"}
    if key not in allowed:
        return jsonify({"success": False, "message": "Invalid field"}), 400

    if key in {"visible","watch"}:
        value = bool(value) if isinstance(value, bool) else str(value).lower() in {"1","true","yes","on"}

    current_vehicles = read_vehicles()
    updated = False

    for v in current_vehicles:
        if v.get("id") == vid:
            v[key] = value
            updated = True
            break

    if not updated:
        return jsonify({"success": False, "message": "Vehicle not found"}), 404

    save_json(VEHICLES_FILE, current_vehicles)
    global vehicles
    vehicles = current_vehicles
    return jsonify({"success": True})

###############################################################################
# Run
###############################################################################
if __name__ == '__main__':
    app.run(host='0.0.0.0', port=int(os.environ.get('PORT', 5000)))
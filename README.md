
# 🛡️ GuardVision AI Dashboard
### Next-Generation Neural Safety Monitoring System

![License](https://img.shields.io/badge/License-MIT-blue.svg)
![AI](https://img.shields.io/badge/Engine-Gemini_3_Flash-cyan.svg)
![UI](https://img.shields.io/badge/Design-iOS_18_Glassmorphism-purple.svg)
![Safety](https://img.shields.io/badge/Safety-Mission_Critical-red.svg)

**GuardVision AI** is a high-performance, real-time safety dashboard designed for industrial, vehicle, and site monitoring. By leveraging the **Gemini 3 Flash Vision API**, it transforms a standard webcam into a sophisticated spatial awareness tool that detects hazards, monitors PPE compliance, and assesses operator alertness.

---

## ✨ Key Features

- 🤖 **Multimodal Neural Vision**: Real-time detection of **Persons**, **Vehicles**, **Animals**, and **Obstacles** with high-confidence filtering.
- 🪖 **Automated PPE Compliance**: Deep-vision helmet detection. Automatically flags safety violations if an operator is detected without head protection.
- 👁️ **Fatigue Monitoring**: Analyzes facial biometrics to estimate operator fatigue levels (0-100%) and triggers critical alerts for microsleep risks.
- 📏 **Spatial Proximity & HUD**: LiDAR-style distance estimation (in meters) with a dynamic "Critical Tether" UI for objects within a 1.2m collision zone.
- 📱 **iOS 18 Inspired UI/UX**: Immersive glassmorphism dashboard featuring high-fidelity animations, a sleek Home Screen, and a mission-critical HUD.
- 📋 **Violation Database**: Real-time logging of safety breaches with severity categorization (LOW, HIGH, CRITICAL) and timestamping.
- 🔊 **Audio Alerts**: Frequency-modulated sonic warnings for critical proximity and safety hazards.

---

## 🛠️ Tech Stack

- **Framework**: React 19 + TypeScript
- **AI Core**: Google Gemini 3 Flash (Vision-Language Model)
- **Styles**: Tailwind CSS + iOS 18 Aesthetic (Glassmorphism)
- **Optics**: WebRTC / MediaStream API for Multi-Camera support
- **Icons**: Lucide-inspired SVG System

---

## 🚀 Getting Started

### Prerequisites
- A modern web browser with Camera permissions.
- A **Google Gemini API Key** (injected via environment variables).

### Installation
1. Clone the repository:
   ```bash
   git clone https://github.com/your-username/guardvision-ai.git
   cd guardvision-ai
   ```
2. Install dependencies (standard React environment):
   ```bash
   npm install
   ```
3. Set your API key:
   The application requires `process.env.API_KEY` to be configured for the Gemini AI engine.

4. Launch the application:
   ```bash
   npm start
   ```

---

## 🖥️ System Architecture

GuardVision operates on a **Neural-Loop Architecture**:
1. **Optics Layer**: Captures high-definition frames from internal or external USB webcams.
2. **Inference Layer**: Periodically sends optimized JPEGs to the Gemini 3 Flash engine with custom spatial-reasoning prompts.
3. **Reasoning Layer**: Processes the JSON response to calculate bounding boxes, distance, and safety status.
4. **UI Layer**: Renders a 60fps HUD with tactical crosshairs and real-time telemetry updates.

---

## 📸 Dashboard Preview

- **Home Screen**: iOS-style widgets showing current safety status, telemetry summaries, and camera device selection.
- **Monitor Mode**: Immersive full-screen HUD with scanlines, CRT effects, and tactical bounding boxes.
- **Violation DB**: Scrolling table showing every confirmed safety breach for post-session review.

---

## ⚖️ License
Distributed under the MIT License. See `LICENSE` for more information.

---

## 🤝 Contributing
Contributions are what make the open-source community such an amazing place to learn, inspire, and create. Any contributions you make are **greatly appreciated**.

1. Fork the Project
2. Create your Feature Branch (`git checkout -b feature/AmazingFeature`)
3. Commit your Changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the Branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

---
**GuardVision AI** — *Vision for a Safer Future.*

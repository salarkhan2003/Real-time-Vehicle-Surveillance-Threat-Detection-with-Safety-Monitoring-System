# 🛡️ GuardVision AI Dashboard
### Next-Generation Neural Safety Monitoring System

![License](https://img.shields.io/badge/License-MIT-blue.svg)
![AI](https://img.shields.io/badge/Engine-Gemini_3_Flash-cyan.svg)
![UI](https://img.shields.io/badge/Design-Premium_Glassmorphism-purple.svg)
![Safety](https://img.shields.io/badge/Safety-Mission_Critical-red.svg)

**GuardVision AI** is a high-performance, real-time safety dashboard designed for industrial, vehicle, and site monitoring. By leveraging the **Gemini 3 Flash Vision API**, it transforms a standard webcam into a sophisticated spatial awareness tool that detects hazards, monitors PPE compliance, and assesses operator alertness.

---

## ✨ Key Features

- 🤖 **Multimodal Neural Vision**: Real-time detection of **Persons**, **Vehicles**, **Animals**, and **Obstacles** using spatial-reasoning prompts.
- 🪖 **PPE Compliance**: Automated helmet detection for industrial safety enforcement.
- 👁️ **Fatigue Analysis**: Real-time biometric monitoring for microsleep and operator fatigue.
- 📏 **Spatial Awareness**: Intelligent distance estimation with a dynamic HUD "Critical Tether" UI.
- 📱 **Premium UI/UX**: Immersive glassmorphism dashboard with tactical crosshairs and real-time telemetry.
- 📋 **Violation DB**: Secure logging of safety breaches with categorized threat levels and timestamps.

---

## 🚀 Deployment & Configuration

### Vercel Deployment
1.  **Push to Git**: Ensure your repository is pushed to GitHub, GitLab, or Bitbucket.
2.  **Import Project**: Link your repository to a new project in the [Vercel Dashboard](https://vercel.com).
3.  **Environment Variables**: In the Vercel project settings, go to the **Environment Variables** tab and add the following:
    - **Key**: `API_KEY`
    - **Value**: `[Your Gemini API Key]`
4.  **Deploy**: Trigger a deployment. Vercel will securely inject the API key into the build environment.

### Local Development
- Ensure you have a `.env` file in your project root (this file is automatically excluded from Git via `.gitignore`).
- Define your API key in the environment as `API_KEY`.

---

## 🛠️ Tech Stack

- **Framework**: React 19 + TypeScript
- **AI Core**: Google Gemini 3 Flash (Vision-Language Model)
- **Styles**: Tailwind CSS + Premium Aesthetic (Glassmorphism)
- **Optics**: WebRTC / MediaStream API for Multi-Camera support

---

## 🖥️ System Architecture

GuardVision operates on a **Neural-Loop Architecture**:
1. **Optics Layer**: Captures high-definition frames from internal or external USB webcams.
2. **Inference Layer**: Periodically sends optimized JPEGs to the Gemini 3 Flash engine.
3. **Reasoning Layer**: Processes the JSON response to calculate bounding boxes and safety status.
4. **UI Layer**: Renders a tactical HUD with real-time telemetry updates.

---

## ⚖️ License
Distributed under the MIT License.

---

## 🤝 Contributing
1. Fork the Project
2. Create your Feature Branch (`git checkout -b feature/AmazingFeature`)
3. Commit your Changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the Branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

---
**GuardVision AI** — *Vision for a Safer Future.*

# 🌐 LRC Frontend (Angular)

The user interface for the **Learning Resolution Coach**, built with Angular 18.

## 🚀 Features
- **Learning Dashboard**: View active resolutions and progress.
- **Goal Wizard**: Interactive flow to define new learning targets.
- **AI Tutoring Interface**: Integrated chat-based mentoring.

## 🛠️ Development Setup

### Prerequisites
- Node.js 20+
- Angular CLI (`npm install -g @angular/cli`)

### Quick Start
```bash
# Install dependencies
npm install

# Run dev server
ng serve
```
Navigate to `http://localhost:4200/`. The app is configured to proxy API requests to the Gateway on port `8000`.

## 🏗️ Docker
The frontend is containerized using a multi-stage Nginx build.
```bash
docker build -t lrc-web .
```

## 🧪 Testing
```bash
ng test
```

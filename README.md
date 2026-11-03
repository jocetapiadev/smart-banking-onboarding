# 🏦 Smart Banking Onboarding & Risk Audit System

![Python](https://img.shields.io/badge/Python-3.11+-blue.svg)
![FastAPI](https://img.shields.io/badge/FastAPI-0.110-green.svg)
![Power Platform](https://img.shields.io/badge/Power%20Platform-PowerApps%20%7C%20Automate-742774.svg)

Sistema integral de automatización y evaluación de riesgo operacional para la recepción e inspección inteligente de solicitudes crediticias. Integración híbrida entre **Power Platform**, **Microservicios Python** e **Inteligencia Artificial Generativa**.

## ⚙️ Arquitectura de la Solución

```mermaid
graph TD
    A[Power Apps: Interfaz Ejecutivo] -->|Sube PDF| B(SharePoint / Dataverse)
    B -->|Trigger Nuevo Archivo| C[Power Automate: Orquestador]
    C -->|Petición HTTP REST| D[Python FastAPI: Microservicio IA]
    D -->|Extracción & Análisis Prompt| E[Azure OpenAI / Copilot]
    E -->|JSON de Riesgo| D
    D -->|Persistencia| F[(Base de Datos SQL)]
    C -->|Notificación Aprobación| G[Microsoft Teams / Email]

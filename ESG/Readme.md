# 🌍 ESG & Financial Performance Dashboard

This project utilizes a dataset from Kaggle titled "ESG & Financial Performance Dataset". This dataset contains the financial and ESG (Environmental, Social, and Governance) performance of 1,000 global companies in 9 industries and 7 regions from 2015 to 2025. The dataset includes realistic financial metrics (e.g., revenue, profit margin, market capitalization) along with comprehensive ESG indicators, including carbon emissions, resource usage, and detailed ESG scores. You can access the complete documentation for this dataset [here](https://www.kaggle.com/datasets/shriyashjagtap/esg-and-financial-performance-dataset).

## 🔄 Project Workflow
```mermaid
%%{init: {"theme": "base", "themeVariables": { "primaryColor": "#ddeeff", "secondaryColor": "#e0f7ea", "tertiaryColor": "#fffbe6" } }}%%
flowchart LR
  %% Baris atas: Notebook (warna biru muda)
  A[Raw Data]:::notebook --> B[Data Preprocessing]:::notebook
  B --> C[Data Cleaning]:::notebook
  C --> D[Exploratory Data Analysis]:::notebook
  D --> E[Train-Test Split]:::notebook
  E --> F[Model Selection & Hyperparameter Tuning]:::notebook
  F --> G[Build Final Predictive Model (Random Forest)]:::notebook
  G --> H[Model Evaluation]:::notebook
  H --> I[Clustering Analysis (K-Means)]:::notebook

  %% Transisi
  I -.-> J[Visualization & Insights]:::app

  %% Baris bawah: App/Deployment (warna hijau muda)
  J --> K[Streamlit App Development]:::app
  K --> L[Interactive Dashboard Deployment]:::app

  %% Definisi styling kelas
  classDef notebook fill:#cfeaff,stroke:#2672b2,stroke-width:2px,color:#000;
  classDef app fill:#e0f7ea,stroke:#1a5f3f,stroke-width:2px,color:#000;
```


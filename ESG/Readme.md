# 🌍 ESG & Financial Performance Dashboard

This project utilizes a dataset from Kaggle titled "ESG & Financial Performance Dataset". This dataset contains the financial and ESG (Environmental, Social, and Governance) performance of 1,000 global companies in 9 industries and 7 regions from 2015 to 2025. The dataset includes realistic financial metrics (e.g., revenue, profit margin, market capitalization) along with comprehensive ESG indicators, including carbon emissions, resource usage, and detailed ESG scores. You can access the complete documentation for this dataset [here](https://www.kaggle.com/datasets/shriyashjagtap/esg-and-financial-performance-dataset).

## 🔄 Project Workflow

```mermaid
flowchart LR
  %% Baris atas
  A[Raw Data] --> B[Data Preprocessing]
  B --> C[Data Cleaning]
  C --> D[Exploratory Data Analysis]
  D --> E[Train-Test Split]
  E --> F[Model Selection & Hyperparameter Tuning]
  F --> G[Build Final Predictive Model (Random Forest)]
  G --> H[Model Evaluation]
  H --> I[Clustering Analysis (K-Means)]
  
  %% Baris bawah
  J[Visualization & Insights] --> K[Streamlit App Development]
  K --> L[Interactive Dashboard Deployment]
  
  %% Hubungkan dua baris
  I -.-> J
```

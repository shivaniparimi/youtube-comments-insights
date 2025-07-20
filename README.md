# 📊 YouTube Comments Insights Dashboard

This project provides insights into the comments of YouTube videos by leveraging cloud infrastructure and scalable microservices to deliver real-time analytics. By inputting a YouTube video link, users can explore a wide range of metrics and visualizations, enabling them to understand viewer engagement and sentiment better.

---

## 🔍 Features

- **Like/Dislike Ratio** — Measures viewer sentiment toward the video.
- **Engagement Ratio** — Compares comments, likes, and reply threads to total views.
- **Sentiment Distribution** — Classifies comments as positive, neutral, or negative.
- **Intent Classification** — Categorizes comments into feedback, requests, or complaints.
- **Keyword Cloud** — Extracts and visualizes frequently used keywords.
- **Comments by Region** — Shows geographic distribution of commenters.
- **Sentiment Over Time** — Tracks changes in sentiment during the video’s lifecycle.
- **Comment Activity Over Time** — Monitors comment volume trends.

---

## 🛠️ Architecture and Workflow

1. **Frontend (React + Tailwind)**  
   The frontend sends the video link to a backend API endpoint, which triggers the Kafka producer and initiates the data processing pipeline.

2. **Backend API and Kafka Producer**  
   The Kafka producer fetches the video's comments and metadata from the YouTube Data API. The producer streams the retrieved comment data to various Kafka topics set up on AWS EC2 clusters. Topics are created for each type of analysis: sentiment, intent, keyword, geographic, and temporal.

3. **Kafka Consumers for Data Analysis**  
   Each Kafka consumer subscribes to a designated topic to perform specific analyses. The consumers are Python services that use the NLTK library to perform the appropriate functions.

4. **Containerization and Orchestration (Docker + Kubernetes)**  
   Each consumer is containerized with Docker, allowing for a consistent environment across deployments. Kubernetes orchestrates the containers, ensuring that consumers scale based on the load (e.g., spikes in comments).

5. **Data Storage (MongoDB)**  
   After analysis, each consumer writes the processed data to MongoDB. Sentiment scores, keywords, intents, geographic distributions, and temporal insights are stored in collections within MongoDB. The frontend queries MongoDB for real-time analytics display.

6. **Infrastructure Setup (Terraform on AWS)**  
   Terraform is used to set up and manage the infrastructure on AWS, specifically EC2 instances that host the Kafka clusters.

---

## 🧰 Tech Stack

| Layer         | Technologies & Libraries                |
|---------------|----------------------------------------|
| Data Fetching | Python, YouTube Data API                |
| Messaging     | Apache Kafka (confluent-kafka Python)  |
| Data Analysis | Python, NLTK                           |
| Data Storage  | MongoDB                               |
| Environment   | Docker                                 |

---

# Capstone Project Proposal  
## Neighborhood check: Crime Risk Awareness Using Public Government Data

---

## 1. Problem Statement

Individuals who are planning to move to a new neighborhood often struggle to accurately assess local safety conditions. While crime data is publicly available, it is typically fragmented across multiple government sources and presented in formats that are difficult for non-experts to interpret. As a result, people rely on anecdotal information or incomplete summaries when making important housing decisions.

There is a need for an accessible, data-driven tool that consolidates publicly available crime data and presents neighborhood-level risk patterns in a clear and interpretable way.

---

## 2. Project Objective

The objective of this project is to develop a machine learning–based web application that helps users understand neighborhood safety conditions by analyzing publicly available crime and incident data. The system provides contextualized risk indicators to support informed decision-making without making definitive judgments about specific locations.

---

## 3. Machine Learning Task

**Prediction and Analysis Task:**  
Given a ZIP code or geographic area, the model analyzes historical crime and incident data to generate:

- Crime-type-specific risk scores  
- Temporal patterns (e.g., time-of-day and seasonal trends)  
- Relative risk indices compared to surrounding areas  

The system focuses on pattern analysis and comparative risk estimation rather than prediction of individual events.

---

## 4. Data Sources

This project uses publicly available and government-maintained datasets, including:

FBI Crime Data API (U.S. Department of Justice)
Provides nationwide crime statistics by law enforcement agency, offense type, and year through the FBI’s Uniform Crime Reporting (UCR) and National Incident-Based Reporting System (NIBRS).
https://api.usa.gov/crime/fbi/cde/

FBI NIBRS Bulk Crime Data
Incident-level, anonymized crime records including offense category, date, and reporting agency, released by the FBI for public research and analysis.
https://crime-data-explorer.fr.cloud.gov/downloads-and-docs

City and County Open Crime Data
Municipal open-data portals providing geocoded crime reports at the ZIP code and neighborhood level (e.g., Chicago, New York City, Los Angeles, and other major U.S. cities).

Public 911 and Emergency Call Data
Government-released call-for-service datasets that capture real-world public safety incidents, including time-of-day and incident type, enabling temporal and neighborhood-level risk analysis.

All datasets are anonymized, publicly released by government agencies, and used in compliance with open data and research guidelines.
---

## 5. Web Application Description

The web-based application, **Neighborhood Reality Check**, allows users to:

- Input a ZIP code or select a geographic area  
- View crime risk indicators broken down by category  
- Explore time-based trends and comparisons with nearby neighborhoods  
- Understand relative risk through visual indexes and charts  

The interface is designed to prioritize clarity, transparency, and contextual understanding rather than alarm or judgment.

---

## 6. Ethical Considerations

This project is designed with ethical safeguards:

- No individual-level or personally identifiable data is used  
- The application does not label neighborhoods as “safe” or “unsafe”  
- All outputs are comparative and informational  
- The system emphasizes awareness rather than fear-based conclusions  

---

## 7. Expected Impact

By transforming publicly available crime data into an accessible decision-support tool, this project demonstrates how machine learning can help individuals, housing seekers, and policymakers better understand neighborhood-level safety patterns. Potential users include individuals planning to relocate, real estate professionals, and local government agencies.

---

## 8. Project Status

This repository contains ongoing development for a capstone project, including:

- Proposal documentation  
- Data exploration and model development  
- Web application implementation  
- Periodic progress updates  

---



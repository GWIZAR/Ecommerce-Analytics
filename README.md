# Distributed Multi-Model Analytics for E-Commerce Data

**Big Data Analytics — Final Project | AUCA**

## Student
- **Name:** GWIZA Rodrigue
- **ID:** 101209
- **University:** Adventist University of Central Africa (AUCA)
- **Course:** Big Data Analytics

## Project Overview
A distributed multi-model analytics system for large-scale e-commerce data demonstrating the complementary strengths of MongoDB, HBase, and Apache Spark.

## Technologies Used
| Technology | Role | Version |
|---|---|---|
| MongoDB | Document Store (users, products, transactions) | 6.0 (Docker) |
| HBase | Wide-Column Store (sessions, product metrics) | 2.4.17 (Simulated) |
| Apache Spark | Distributed Processing & SQL Analytics | 3.5.1 (PySpark) |
| Python | Data generation, loading, analysis | 3.14 |
| Matplotlib/Seaborn | Data Visualization | 3.11 / 0.13 |

## Project Files
| File | Purpose |
|---|---|
| `dataset_generator.py` | Generates synthetic e-commerce dataset |
| `load_mongodb.py` | Loads all data into MongoDB collections |
| `mongodb_queries.py` | 5 MongoDB aggregation pipelines |
| `hbase_simulation.py` | HBase wide-column model simulation |
| `spark_analysis.py` | PySpark batch jobs and SQL analytics |
| `integration.py` | Cross-system integrated analytics |
| `visualizations.py` | 8 business insight charts |
| `Ecommerce_Analytics_Technical_Report.pdf` | Full technical report |

## Dataset
| File | Records |
|---|---|
| users.json | 500 |
| products.json | 500 |
| categories.json | 20 |
| sessions (4 files) | 2,000 |
| transactions.json | 866 |

## Key Findings
- Search engine traffic converts at **46.9%** vs social media **35.0%**
- Top customer CLV: **$12,894** (user_000097)
- Top category: **cat_006** with $57,490 revenue
- Cart abandonment rate: **30.1%** — key optimization opportunity
- Return rate: **23.7%** — needs product quality investigation

## How to Run
```bash
# Install dependencies
pip install faker pandas pymongo pyspark matplotlib seaborn

# Generate dataset
python dataset_generator.py

# Load into MongoDB (requires MongoDB running on port 27017)
python load_mongodb.py

# Run MongoDB queries
python mongodb_queries.py

# Run HBase simulation
python hbase_simulation.py

# Run Spark analysis (requires Java 11)
python spark_analysis.py

# Run integration analysis
python integration.py

# Generate visualizations
python visualizations.py
```

# Calculation coverage checklist

Use this when adding or changing pricing pages to ensure **no calculable offering is missing**. Each row is a `PRICING_PAGES` entry; **calculator_tab** and **App location** must stay in sync.

| # | Category | Page label | calculator_tab | App location |
|---|----------|------------|----------------|--------------|
| 1 | Overview | Databricks Pricing | None | Link only (main overview) |
| 2 | Data Engineering | Lakeflow Jobs | compute | **Compute** tab → workload **Jobs Compute** (or Jobs Light / Photon) |
| 3 | Data Engineering | Lakeflow Spark Declarative Pipelines | compute | **Compute** tab → workload **Lakeflow Pipelines** |
| 4 | Data Engineering | Lakeflow Connect | compute | **Compute** tab → workload **Lakeflow Connect** |
| 5 | Databricks SQL | Databricks SQL | sql | **SQL Warehouse** tab |
| 6 | Operational Database | Lakebase | compute | **Compute** tab → workload **Database Serverless (Lakebase)** |
| 7 | Interactive workloads | Compute for Data Science | compute | **Compute** tab → workload **All-Purpose Compute** (or Photon) |
| 8 | Interactive workloads | Databricks Apps | compute | **Compute** tab → workload **Databricks Apps** |
| 9 | Artificial Intelligence | Agent Bricks | gpu | **Model Serving** tab (CPU/GPU) |
| 10 | Artificial Intelligence | AI Parse Document | ai_parse | **AI Parse** tab |
| 11 | Artificial Intelligence | Mosaic AI Gateway | gpu | **Model Serving** tab (CPU/GPU) |
| 12 | Artificial Intelligence | Model Serving | gpu | **Model Serving** tab (CPU + GPU) |
| 13 | Artificial Intelligence | Foundation Model Serving | gpu | **Foundation Model** tab |
| 14 | Artificial Intelligence | Proprietary Foundation Model Serving | gpu | **Foundation Model** tab |
| 15 | Artificial Intelligence | Shutterstock ImageAI | imageai | **ImageAI** tab |
| 16 | Artificial Intelligence | Vector Search | vector | **Vector Search** tab (+ **Reranker** in expander) |
| 17 | Artificial Intelligence | Agent Evaluation | agent_eval | **Agent Evaluation** tab |
| 18 | Artificial Intelligence | Model Training | training | **Model Training** tab |
| 19 | Platform | Tiers and Add-ons | None | Link only (plan-specific) |
| 20 | Platform | Managed Services | None | Link only (plan-specific) |
| 21 | Platform | Data Transfer and Connectivity | None | SKU list in sidebar; no formula |
| 22 | Platform | Storage | storage | **Storage** tab |
| 23 | Platform | Delta Share from SAP BDC | None | Link only |
| 24 | Collaboration | Clean Rooms | compute | **Compute** tab → workload **Clean Rooms Collaborator** |
| 25 | Collaboration | View Sharing | None | Link only |
| 26 | Beta Products | Beta Products | None | Link only |
| 27 | Calculator | Databricks Pricing Calculator (instance types) | None | Link only (external calculator) |
| 28 | Calculator | Generative AI Pricing Calculator | None | Link only (external) |
| 29 | Calculator | SAP Databricks Sizing Calculator | None | Link only (external) |

## Compute workload dropdown (must include)

Every pricing page that bills as **DBU × $/DBU** and is not a dedicated tab should have an **explicit workload** in `EXAMPLE_PRICE_PER_DBU_BY_WORKLOAD` and in the Compute tab dropdown:

- Jobs Light Compute  
- Jobs Compute  
- **Lakeflow Connect**  
- **Lakeflow Pipelines**  
- Jobs Compute (Photon)  
- All-Purpose Compute / All-Purpose Compute (Photon)  
- **Databricks Apps**  
- SQL Compute / SQL Pro Compute  
- Serverless SQL  
- DLT Core / DLT Pro / DLT Advanced  
- **Data Quality Monitoring**  
- Model Training, Vector Search, Serverless Real-Time Inference  
- Database Serverless (Lakebase)  
- Clean Rooms Collaborator  
- Enhanced Security and Compliance  

## When adding a new pricing page

1. Add the page to `PRICING_PAGES` in `pricing_data.py` with the correct `calculator_tab`.
2. If it has a **calculable formula** (DBU, DSU, tokens, etc.):
   - **Compute-style (DBU × $/DBU):** Add a workload to `EXAMPLE_PRICE_PER_DBU_BY_WORKLOAD` and to the workload_map in `_build_sku_to_product_workload` if there are SKUs.
   - **Dedicated product:** Add an estimate function in `calculator.py`, add a tab (or expander) in `app.py`, and add the data constants in `pricing_data.py`.
3. Update this checklist and `STATUS_AND_COVERAGE.md`.

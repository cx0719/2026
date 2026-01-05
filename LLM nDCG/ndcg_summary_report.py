import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from datetime import datetime

def generate_summary_report():
    """Generate a comprehensive summary report of the nDCG analysis."""
    
    # Read the nDCG results
    try:
        df = pd.read_csv('ndcg_analysis_results.csv')
        print("Successfully loaded nDCG analysis results")
    except FileNotFoundError:
        print("nDCG analysis results file not found. Please run nDCG.py first.")
        return
    
    # Create summary statistics
    summary_stats = {
        'Total_Rows_Analyzed': len(df),
        'Average_nDCG_Score': round(df['nDCG_Score'].mean(), 4),
        'Median_nDCG_Score': round(df['nDCG_Score'].median(), 4),
        'Min_nDCG_Score': round(df['nDCG_Score'].min(), 4),
        'Max_nDCG_Score': round(df['nDCG_Score'].max(), 4),
        'Standard_Deviation': round(df['nDCG_Score'].std(), 4),
        'Average_Skills_Coverage': round(df['Skills_Coverage_Percentage'].mean(), 2),
        'Average_Perfect_Matches': round(df['Perfect_Matches'].mean(), 2)
    }
    
    # Group by thinking budget tokens
    budget_analysis = df.groupby('Thinking_Budget_Tokens').agg({
        'nDCG_Score': ['mean', 'std', 'count'],
        'Skills_Coverage_Percentage': 'mean',
        'Perfect_Matches': 'mean'
    }).round(4)
    
    # Find top and bottom performers
    top_5 = df.nlargest(5, 'nDCG_Score')
    bottom_5 = df.nsmallest(5, 'nDCG_Score')
    
    # Generate report
    report = f"""
# nDCG Analysis Summary Report
Generated on: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

## Overall Statistics
- **Total Rows Analyzed**: {summary_stats['Total_Rows_Analyzed']}
- **Average nDCG Score**: {summary_stats['Average_nDCG_Score']}
- **Median nDCG Score**: {summary_stats['Median_nDCG_Score']}
- **Score Range**: {summary_stats['Min_nDCG_Score']} - {summary_stats['Max_nDCG_Score']}
- **Standard Deviation**: {summary_stats['Standard_Deviation']}
- **Average Skills Coverage**: {summary_stats['Average_Skills_Coverage']}%
- **Average Perfect Matches**: {summary_stats['Average_Perfect_Matches']}

## Ideal Skills Ranking (Reference)
1. Python
2. Golang
3. REST API
4. Microservices Architecture
5. Distributed Systems
6. Databases (MySQL, Postgres, MongoDB)
7. SQL
8. NoSQL
9. AWS
10. Docker
11. Kubernetes (K8s)
12. CI/CD
13. Kafka
14. Terraform
15. Technical Lead

## Top 5 Performers (Highest nDCG Scores)
"""
    
    for idx, row in top_5.iterrows():
        report += f"""
**Rank {idx + 1}**: Row {int(row['Row_Index'])} (Run {row['Test_Run_Number']}, Budget: {row['Thinking_Budget_Tokens']} tokens)
- **nDCG Score**: {row['nDCG_Score']}
- **Skills Extracted**: {row['Total_Skills_Extracted']}
- **Coverage**: {row['Skills_Coverage_Percentage']}%
- **Perfect Matches**: {row['Perfect_Matches']}
- **Extracted Skills**: {row['Extracted_Skills']}
"""
    
    report += f"""
## Bottom 5 Performers (Lowest nDCG Scores)
"""
    
    for idx, row in bottom_5.iterrows():
        report += f"""
**Rank {idx + 1}**: Row {int(row['Row_Index'])} (Run {row['Test_Run_Number']}, Budget: {row['Thinking_Budget_Tokens']} tokens)
- **nDCG Score**: {row['nDCG_Score']}
- **Skills Extracted**: {row['Total_Skills_Extracted']}
- **Coverage**: {row['Skills_Coverage_Percentage']}%
- **Perfect Matches**: {row['Perfect_Matches']}
- **Extracted Skills**: {row['Extracted_Skills']}
"""
    
    report += f"""
## Analysis by Thinking Budget Tokens
"""
    
    for budget in sorted(df['Thinking_Budget_Tokens'].unique()):
        budget_data = df[df['Thinking_Budget_Tokens'] == budget]
        report += f"""
**Budget {budget} tokens**:
- **Average nDCG**: {budget_data['nDCG_Score'].mean():.4f}
- **Standard Deviation**: {budget_data['nDCG_Score'].std():.4f}
- **Number of Runs**: {len(budget_data)}
- **Average Coverage**: {budget_data['Skills_Coverage_Percentage'].mean():.2f}%
- **Average Perfect Matches**: {budget_data['Perfect_Matches'].mean():.2f}
"""
    
    report += f"""
## Key Insights

1. **Score Range**: The nDCG scores range from {summary_stats['Min_nDCG_Score']} to {summary_stats['Max_nDCG_Score']}, indicating varying levels of alignment with the ideal skills ranking.

2. **Coverage Analysis**: On average, the extracted skills cover {summary_stats['Average_Skills_Coverage']}% of the ideal skills list, suggesting room for improvement in skill identification.

3. **Perfect Matches**: The average number of perfect matches is {summary_stats['Average_Perfect_Matches']}, indicating that most skills are either missing from the ideal ranking or placed in incorrect positions.

4. **Budget Impact**: Analysis by thinking budget shows how different token allocations affect the quality of skill extraction and ranking.

5. **Improvement Opportunities**: 
   - Better skill normalization and matching
   - More comprehensive coverage of ideal skills
   - Improved positioning of skills in the ranking

## Recommendations

1. **Skill Normalization**: Improve the skill matching algorithm to better handle variations in skill names and descriptions.

2. **Coverage Enhancement**: Focus on extracting more skills from the ideal ranking to improve coverage percentage.

3. **Positioning Accuracy**: Work on better understanding the relative importance of skills to improve their positioning in the ranking.

4. **Budget Optimization**: Analyze the relationship between thinking budget and performance to optimize token allocation.

---
*Report generated by nDCG Analysis System*
"""
    
    # Save the report
    with open('ndcg_summary_report.txt', 'w') as f:
        f.write(report)
    
    print("Summary report generated: ndcg_summary_report.txt")
    print("\n" + "="*80)
    print(report)
    print("="*80)
    
    return report

if __name__ == "__main__":
    generate_summary_report() 
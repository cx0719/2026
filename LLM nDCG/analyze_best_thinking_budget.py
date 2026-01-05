import pandas as pd
import os
import csv
import json
from datetime import datetime
from process.common_finder.common_finder import CommonFeatureFinder
from util.thinking_parser import parse_gemini_thinking
from database.mongodb_connection import MongoDBConnection
from process.cdd_jd_matcher.matcher import MatcherManager
from process.jd_extractor import JDParser
jd_parser = JDParser()
import pickle
from api.llm import LLMManager

# Set Gemini API key directly for Gemini LLM calls - MUST be set before any LLM imports
os.environ['GEMINI_API_KEY'] = 'AIzaSyDGovgKS16G-Zugw7byyq-40ok5Ehzou7Y'
print('Gemini API key set for Gemini-pro.')

def load_job_and_candidates():
    """Load the original job and candidate data from MongoDB."""
    job_id = '9572'
    task_uuid = 'a76a6c3e-6164-42da-a16e-cb11eaf8d3ed'
    db = MongoDBConnection()
    job = db.read_job_by_job_id(job_id)
    candidates = db.read_candidate_by_task_uuid(task_uuid)
    db.close_connection()
    # Format job and candidates for prompt
    job_info = {
        'job_id': job.get('job_id', ''),
        'job_title': job.get('job_name', ''),
        'jd_content': job.get('jd_content', '')
    } if job else {}
    candidate_infos = []
    for c in candidates:
        candidate_infos.append({
            'name': c.get('talent', {}).get('fullName', c.get('name', 'Unknown')),
            'profile': c
        })
    return job_info, candidate_infos

def analyze_thinking_budget_performance():
    print("Analyzing thinking budget performance from gemini_results.csv...")
    csv_path = os.path.join(os.path.dirname(__file__), 'gemini_results.csv')
    if not os.path.exists(csv_path):
        print("gemini_results.csv not found!")
        return
    df = pd.read_csv(csv_path, encoding='utf-8')
    print(f"Loaded {len(df)} rows from gemini_results.csv")
    budget_summary = df['Thinking Budget (Tokens)'].value_counts().sort_index()
    print("\nData Summary by Thinking Budget:")
    for budget, count in budget_summary.items():
        print(f"  {budget}: {count} runs")
    performance_metrics = {}
    for budget in df['Thinking Budget (Tokens)'].unique():
        budget_data = df[df['Thinking Budget (Tokens)'] == budget]
        avg_thinking_ratio = budget_data['Thinking Ratio (%)'].mean()
        avg_total_tokens = budget_data['Total Tokens Used'].mean()
        avg_thinking_tokens = budget_data['Thinking Process Tokens'].mean()
        successful_runs = budget_data[budget_data['Extracted Keywords'].str.len() > 0].shape[0]
        total_runs = len(budget_data)
        success_rate = (successful_runs / total_runs) * 100 if total_runs > 0 else 0
        performance_metrics[budget] = {
            'avg_thinking_ratio': round(avg_thinking_ratio, 2),
            'avg_total_tokens': round(avg_total_tokens, 2),
            'avg_thinking_tokens': round(avg_thinking_tokens, 2),
            'success_rate': round(success_rate, 2),
            'total_runs': total_runs,
            'successful_runs': successful_runs
        }
    print("\nPerformance Metrics by Thinking Budget:")
    for budget, metrics in sorted(performance_metrics.items()):
        print(f"  {budget}:")
        print(f"    Success Rate: {metrics['success_rate']}% ({metrics['successful_runs']}/{metrics['total_runs']})")
        print(f"    Avg Thinking Ratio: {metrics['avg_thinking_ratio']}%")
        print(f"    Avg Total Tokens: {metrics['avg_total_tokens']}")
        print(f"    Avg Thinking Tokens: {metrics['avg_thinking_tokens']}")
    analysis_data = {
        'performance_metrics': performance_metrics,
        'total_tests': len(df),
        'budgets_tested': list(df['Thinking Budget (Tokens)'].unique()),
        'sample_keywords': {}
    }
    for budget in df['Thinking Budget (Tokens)'].unique():
        budget_data = df[df['Thinking Budget (Tokens)'] == budget]
        if len(budget_data) > 0:
            sample_keywords = budget_data.iloc[0]['Extracted Keywords']
            analysis_data['sample_keywords'][budget] = sample_keywords
    # Convert performance_metrics keys to str to avoid json serialization issues
    performance_metrics = {str(k): v for k, v in performance_metrics.items()}
    # Convert sample_keywords keys to str to avoid json serialization issues
    analysis_data['sample_keywords'] = {str(k): v for k, v in analysis_data['sample_keywords'].items()}
    job, candidates = load_job_and_candidates()
    
    # Load cached candidate matches
    cache_file = os.path.join(os.path.dirname(__file__), 'deepseek_candidate_matches.pkl')
    if not os.path.exists(cache_file):
        print("Deepseek candidate match cache not found!")
        print("Please run the deepseek_candidate_matching.py script first.")
        return
    
    print("📂 Loading cached candidate matches...")
    with open(cache_file, 'rb') as f:
        all_candidate_matches = pickle.load(f)
    print(f"Loaded {len(all_candidate_matches)} candidate matches from cache")
    
    # Parse and summarize the CSV by budget
    input_csv_file = os.path.join(os.path.dirname(__file__), 'gemini_results.csv')
    df_csv = pd.read_csv(input_csv_file)
    # Group by budget if column exists, else use index
    budget_col = None
    for col in df_csv.columns:
        if 'budget' in col.lower():
            budget_col = col
            break
    if not budget_col:
        raise ValueError('No budget column found in CSV!')
    
    print("\nUsing CommonFeatureFinder to analyze budget performance...")
    
    # Initialize CommonFeatureFinder (same as working notebook)
    finder = CommonFeatureFinder(template_name="common_finder.j2")
    
    # Transform data format for common finder (same as notebook)
    multi_candidate_matches = {}
    
    # Initialize each dimension
    for dimension in ['skill']:  # Focus on skill dimension for budget analysis
        multi_candidate_matches[dimension] = []
    
    # Collect matches for each dimension across all candidates
    for candidate_matches in all_candidate_matches:
        for dimension, matches in candidate_matches.items():
            if dimension in multi_candidate_matches:
                multi_candidate_matches[dimension].append(matches)
    
    print("Data transformed for budget analysis")
    
    # Use the working pattern from notebook to analyze each budget
    unique_budgets = list(df_csv[budget_col].unique())
    results = []
    
    for budget in unique_budgets:
        print(f"\nAnalyzing budget: {budget}")
        
        # Get data for this budget
        budget_data = df_csv[df_csv[budget_col] == budget]
        
        # Create a custom prompt for budget analysis
        budget_summary = f"Budget: {budget}\n"
        for idx, row in budget_data.iterrows():
            budget_summary += f"- Extracted Keywords: {row.get('Extracted Keywords', '')}\n"
            budget_summary += f"- Candidate Recommendation: {row.get('qualification', row.get('recommendations', ''))}\n"
        
        # Use CommonFeatureFinder with custom prompt for budget analysis
        try:
            # Create a custom analysis using the working pattern
            budget_analysis_result = finder.analyze_dimension(
                dimension='skill',
                candidate_matches=multi_candidate_matches['skill'],
                job_title=job.get('job_title', 'Senior Backend Engineer - Connectivity'),
                execute=True,
                provider="gemini",
                model="gemini-2.5-pro",
                thinking_budget=2000,
                include_thoughts=True,
                original_response=True
            )
            
            # Parse the result to get readable format
            if isinstance(budget_analysis_result, str):
                parsed_result = parse_gemini_thinking(budget_analysis_result)
                # Extract the candidate_tokens which contains the keywords
                keywords_text = parsed_result.get('candidate_tokens', 'N/A')
                thinking_text = parsed_result.get('thinking_tokens', 'N/A')
            elif isinstance(budget_analysis_result, dict):
                keywords_text = budget_analysis_result.get('candidate_tokens', 'N/A')
                thinking_text = budget_analysis_result.get('thinking_tokens', 'N/A')
            else:
                keywords_text = str(budget_analysis_result)
                thinking_text = 'N/A'
            
            # Create budget judgment in readable format
            budget_judgment = {
                "budget": budget,
                "extracted_keywords": keywords_text,
                "analysis_reasoning": thinking_text,
                "performance_summary": f"Budget {budget} analysis completed successfully"
            }
            
            results.append(budget_judgment)
            print(f"Budget {budget} analysis completed")
            
        except Exception as e:
            print(f"Error analyzing budget {budget}: {e}")
            # Add error result
            budget_judgment = {
                "budget": budget,
                "extracted_keywords": "ERROR",
                "analysis_reasoning": f"Error: {str(e)}",
                "performance_summary": f"Budget {budget} analysis failed"
            }
            results.append(budget_judgment)
            continue
    
    # Save all results to CSV in readable format
    if results:
        csv_file = os.path.join(os.path.dirname(__file__), 'gemini_best_budget_judgment.csv')
        with open(csv_file, 'w', encoding='utf-8', newline='') as f:
            writer = csv.DictWriter(f, fieldnames=['budget', 'extracted_keywords', 'analysis_reasoning', 'performance_summary'])
            writer.writeheader()
            for row in results:
                writer.writerow(row)
        print(f"\nBudget analysis results saved to: {csv_file}")
        print(f"Total results saved: {len(results)}")
        
        # Also save a summary file
        summary_file = os.path.join(os.path.dirname(__file__), 'budget_analysis_summary.txt')
        with open(summary_file, 'w', encoding='utf-8') as f:
            f.write("=== Thinking Budget Analysis Summary ===\n\n")
            f.write(f"Analysis Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
            f.write(f"Total Budgets Analyzed: {len(results)}\n\n")
            
            for result in results:
                f.write(f"Budget: {result['budget']}\n")
                f.write(f"Performance: {result['performance_summary']}\n")
                f.write(f"Keywords: {result['extracted_keywords']}\n")
                f.write(f"Reasoning: {result['analysis_reasoning'][:200]}...\n")
                f.write("-" * 50 + "\n\n")
        
        print(f"Analysis summary saved to: {summary_file}")
        
        # FINAL STEP: Analyze CSV results to determine best budget
        print("\nPerforming final analysis to determine best thinking budget...")
        
        # Read the CSV results for final analysis
        df_final = pd.read_csv(csv_file)
        
        # Create a comprehensive prompt for the final judgment
        final_prompt = f"""
You are an expert LLM performance analyst. I have analyzed different thinking budgets for a recruitment keyword extraction task and need your expert judgment on which budget performs best.

## TASK
Analyze the results from {len(results)} different thinking budgets and recommend the BEST thinking budget for this recruitment keyword extraction task.

## ANALYSIS CRITERIA
1. **Keyword Quality**: Which budget extracts the most relevant, specific, and actionable keywords?
2. **Analysis Depth**: Which budget provides the most insightful reasoning about the recruitment context?
3. **Practical Value**: Which budget's keywords would be most effective for LinkedIn recruiting searches?
4. **Consistency**: Which budget shows the most consistent and reliable performance?

## RESULTS TO ANALYZE
"""
        
        # Add each budget's results to the prompt
        for _, row in df_final.iterrows():
            budget = row['budget']
            keywords = row['extracted_keywords']
            reasoning = row['analysis_reasoning'][:500]  # Limit reasoning length
            
            final_prompt += f"""
### Budget {budget}:
**Keywords Extracted:**
{keywords}

**Analysis Reasoning:**
{reasoning}

---
"""
        
        final_prompt += """
## YOUR TASK
Based on the above analysis, provide:

1. **RECOMMENDED BUDGET**: Which thinking budget (number) is the best choice?
2. **REASONING**: Detailed explanation of why this budget is superior
3. **KEY STRENGTHS**: What makes this budget's results better than others?
4. **PRACTICAL IMPACT**: How will this budget improve recruitment keyword extraction?

## OUTPUT FORMAT
Provide your analysis in a clear, readable format (not JSON). Focus on practical insights and actionable recommendations.

Your expert analysis:
"""
        
        # Call LLM for final judgment
        try:
            llm_manager = LLMManager()
            final_judgment = llm_manager.chat(
                final_prompt,
                provider="gemini",
                model="gemini-2.5-pro",
                temperature=0.1,
                top_p=0.9
            )
            
            # Save the final judgment
            judgment_file = os.path.join(os.path.dirname(__file__), 'final_budget_judgment.txt')
            with open(judgment_file, 'w', encoding='utf-8') as f:
                f.write("=== FINAL THINKING BUDGET JUDGMENT ===\n\n")
                f.write(f"Analysis Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
                f.write(f"Budgets Analyzed: {len(results)}\n\n")
                f.write("EXPERT ANALYSIS:\n")
                f.write("=" * 50 + "\n")
                f.write(final_judgment)
                f.write("\n\n" + "=" * 50 + "\n")
                f.write("END OF ANALYSIS")
            
            print(f"Final budget judgment saved to: {judgment_file}")
            print("\n📋 FINAL JUDGMENT:")
            print("=" * 50)
            print(final_judgment)
            print("=" * 50)
            
        except Exception as e:
            print(f"Error in final judgment analysis: {e}")
            print("The individual budget analyses are still available in the CSV file.")
        
    else:
        print("\n No valid results to save. Check the analysis above.")

if __name__ == "__main__":
    analyze_thinking_budget_performance() 
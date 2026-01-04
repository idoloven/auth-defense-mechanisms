import os
import json
import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt


LOG_FILES = {
    "No Protections": "first-experiment-logs.json",
    "Pepper": "second-experiment-logs.json"
}

def resolve_path(filename):
    if os.path.exists(filename):
        return filename
    
    script_dir = os.path.dirname(os.path.abspath(__file__))
    file_in_script_dir = os.path.join(script_dir, filename)
    
    if os.path.exists(file_in_script_dir):
        return file_in_script_dir
        
    return filename

def load_data(name, filepath):
    actual_path = resolve_path(filepath)
    
    timestamps = []
    with open(actual_path, 'r') as f:
        for line in f:
            entry = json.loads(line)
            timestamps.append(pd.to_datetime(entry['timestamp']))
   
        
    df = pd.DataFrame({'timestamp': timestamps})
    df = df.sort_values('timestamp')
    
    start_time = df['timestamp'].iloc[0]
    df['seconds_elapsed'] = (df['timestamp'] - start_time).dt.total_seconds()
    
    df['cumulative_attempts'] = range(1, len(df) + 1)
    df['Mechanism'] = name
    return df

def main():
    all_data = []
    for name, filepath in LOG_FILES.items():
        df = load_data(name, filepath)
        if df is not None:
            all_data.append(df)

    full_df = pd.concat(all_data)

    plt.figure(figsize=(12, 7))
    sns.set_style("whitegrid")
    sns.lineplot(
        data=full_df, 
        x='seconds_elapsed', 
        y='cumulative_attempts', 
        hue='Mechanism', 
        linewidth=2.5
    )

    plt.title('No Protections VS Pepper over time', fontsize=16, fontweight='bold')
    plt.xlabel('Time Elapsed (Seconds)', fontsize=12)
    plt.ylabel('Cumulative Login Attempts', fontsize=12)
    
    plt.xlim(left=0)
    plt.ylim(bottom=0)

    plt.legend(title="Mechanism", fontsize=10, title_fontsize=12)
    plt.tight_layout()
    
    output_filename = 'defense_timeline_graph.png'
    plt.savefig(output_filename, dpi=300)
    plt.show()

if __name__ == "__main__":
    main()
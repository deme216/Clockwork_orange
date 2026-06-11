import pandas as pd
import os

LOG_PATH = "logs/episode-log.csv"


def generate_report():
    if not os.path.exists(LOG_PATH):
        print(f"Error: {LOG_PATH} not found.")
        return

    try:
        # on_bad_lines='skip' ignores the corrupted rows so the script doesn't crash
        df = pd.read_csv(LOG_PATH, on_bad_lines='skip')

        if df.empty:
            print("Log file is empty.")
            return

        # 1. Total Cost
        total_cost = df['cost_usd'].sum()

        # 2. Cache Hit Rate
        # Check if column exists (Lab 8 requirement)
        if 'cache_read_tokens' in df.columns:
            cache_hits = df[df['cache_read_tokens'] > 0].shape[0]
            hit_rate = (cache_hits / len(df)) * 100
        else:
            hit_rate = 0

        # 3. Median Latency (P50)
        p50_latency = df['latency_ms'].median()

        # 4. Fallback Rate
        if 'fallback_triggered' in df.columns:
            # Handle both string 'True' and boolean True
            df['fallback_triggered'] = df['fallback_triggered'].astype(str).str.lower() == 'true'
            fallbacks = df[df['fallback_triggered'] == True].shape[0]
            fallback_rate = (fallbacks / len(df)) * 100
        else:
            fallback_rate = 0

        print("\n" + "=" * 30)
        print("  VECTORFLOW METRICS REPORT")
        print("=" * 30)
        print(f"Total Valid Entries:  {len(df)}")
        print(f"Total Semester Spend: ${total_cost:.4f}")
        print(f"P50 Latency:          {int(p50_latency)}ms")
        print(f"Cache Hit Rate:       {hit_rate:.1f}%")
        print(f"Fallback Rate:        {fallback_rate:.1f}%")
        print("=" * 30 + "\n")

    except Exception as e:
        print(f"Critical Error parsing CSV: {e}")


if __name__ == "__main__":
    generate_report()

import pandas as pd
import numpy as np

class PacketDatasetAnalyzer:
    def __init__(self, file_path_1, file_path_2):
        # Load the large datasets locally
        print("Loading datasets...")
        self.df1 = pd.read_csv(file_path_1)
        self.df2 = pd.read_csv(file_path_2)
        self.combined_df = pd.concat([self.df1, self.df2], ignore_index=True)
        self.baseline_stats = {}
        self.train_baseline()

    def train_baseline(self):
        """Calculates normal behavior baselines from your friend's datasets."""
        # Clean / fill missing values for numerical checks
        frame_lens = self.combined_df['frame.len'].dropna()
        
        self.baseline_stats = {
            'mean_len': frame_lens.mean(),
            'std_len': frame_lens.std(),
            'max_len': frame_lens.max(),
            'common_protocols': self.combined_df['ip.proto'].dropna().unique().tolist()
        }
        print("Baseline established successfully from normal datasets.")

    def analyze_packet(self, packet_row):
        """
        Analyzes a single packet dictionary/row against the baseline 
        to detect potential anomalies (e.g., unusual frame lengths or protocols).
        """
        threats = []
        risk_score = 0

        length = packet_row.get('frame.len', 0)
        proto = packet_row.get('ip.proto', None)

        # Check for abnormal frame length (e.g., beyond 3 standard deviations)
        upper_limit = self.baseline_stats['mean_len'] + (3 * self.baseline_stats['std_len'])
        if length > upper_limit:
            threats.append(f"Unusually high frame length detected: {length} bytes (Baseline limit: {upper_limit:.2f})")
            risk_score += 50

        # Check for unexpected protocols not seen in normal training data
        if proto and proto not in self.baseline_stats['common_protocols']:
            threats.append(f"Unrecognized protocol ID detected: {proto}")
            risk_score += 40

        is_anomaly = risk_score > 35
        return {
            "is_anomaly": is_anomaly,
            "risk_score": risk_score,
            "threats": threats
        }

# --- Example Usage for Testing ---
if __name__ == '__main__':
    # Initialize with your local dataset filenames
    analyzer = PacketDatasetAnalyzer('normal_01.csv', 'normal_02.csv')
    
    # Simulate testing a suspicious packet row
    test_packet = {'frame.len': 18000, 'ip.proto': 99}
    result = analyzer.analyze_packet(test_packet)
    print("Analysis Result:", result)
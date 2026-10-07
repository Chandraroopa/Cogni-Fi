import time
from backend.capture.adapter import TSharkAdapter
from backend.capture.feature_window import FeatureWindowAggregator

def run_live_capture(interface="wlan0mon"):
    adapter = TSharkAdapter(interface=interface)
    aggregator = FeatureWindowAggregator(window_size=1.0)
    
    print(f"[*] Starting live capture on interface: {interface}")
    adapter.start_capture()
    
    last_window_time = time.time()
    
    try:
        for packet in adapter.read_packets():
            # Add packet into the 1-second sliding window buffer
            aggregator.add_packet(packet)
            
            current_time = time.time()
            # Every 1 second, emit the 30-feature vector
            if current_time - last_window_time >= 1.0:
                features = aggregator.compute_features()
                
                print(f"[Window] Packets: {features['packet_count']} | "
                      f"Pkts/sec: {features['packets_per_second']:.2f} | "
                      f"Deauth Rate: {features['deauth_rate']:.2f}")
                
                # TODO: Pass `list(features.values())` into your trained AWID3 ML model here
                
                last_window_time = current_time
                
    except KeyboardInterrupt:
        print("\n[*] Stopping live capture...")
    finally:
        adapter.stop_capture()

if __name__ == "__main__":
    run_live_capture()
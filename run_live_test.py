import csv
import time
from backend.capture import TSharkCapture, FeatureExtractor, feature_dict_to_vector

def get_packet_length(packet):
    """Extracts packet length accurately from the TShark frame layer."""
    if isinstance(packet, dict):
        # 1. Check inside the 'frame' dictionary layer
        layers = packet.get("layers", {})
        if isinstance(layers, dict):
            frame_layer = layers.get("frame", {})
            if isinstance(frame_layer, dict):
                for k in ["frame_frame_len", "frame_len", "len", "length"]:
                    if k in frame_layer and frame_layer[k] is not None:
                        try:
                            return float(frame_layer[k])
                        except (ValueError, TypeError):
                            pass
                            
        # 2. Fallback to direct keys or other layers just in case
        for k in ["length", "len", "frame_len", "frame_frame_len"]:
            if k in packet and packet[k] is not None:
                try:
                    return float(packet[k])
                except (ValueError, TypeError):
                    pass
                    
    return 0.0

def main():
    interface_id = "Wi-Fi" 
    print(f"Initializing TShark capture on interface: {interface_id}...")
    
    # Open CSV file to save features
    csv_file = open("live_capture_log.csv", mode="w", newline="", encoding="utf-8")
    writer = csv.writer(csv_file)
    
    # Write CSV headers: Timestamp, Packet Count, Byte Count + 30 Features
    headers = ["timestamp", "packet_count", "byte_count"] + [f"feature_{i+1}" for i in range(30)]
    writer.writerow(headers)

    try:
        capture = TSharkCapture(interface_id)
        extractor = FeatureExtractor()

        print("Capturing packets... Open your browser and visit a site (e.g., github.com) to generate traffic.")
        print("Press Ctrl+C to stop.")

        window_start = time.time()
        window_packets = []
        first_packet_received = False

        for packet in capture.packets():
            if not first_packet_received:
                print("\n[INFO] First packet successfully captured from interface! Streaming active...")
                first_packet_received = True

            current_time = time.time()
            window_packets.append(packet)

            # Process window every 1 second
            if current_time - window_start >= 1.0:
                if window_packets:
                    feature_dict = extractor.extract_window_features(window_packets)
                    vector = feature_dict_to_vector(feature_dict)
                    
                    packet_count = float(len(window_packets))
                    
                    # Calculate total bytes using the correct frame layer key
                    total_bytes = sum(get_packet_length(p) for p in window_packets)
                    byte_count = float(total_bytes)
                    
                    # Print window summary to terminal
                    print(f"\n[Window Captured at {time.strftime('%H:%M:%S')}]")
                    print(f"  - Packets in window: {packet_count}")
                    print(f"  - Bytes in window: {byte_count}")
                    print(f"  - Feature vector length: {len(vector)} features")

                    # Write row data to CSV and flush to disk
                    row_data = [current_time, packet_count, byte_count] + list(vector)
                    writer.writerow(row_data)
                    csv_file.flush()

                window_packets = []
                window_start = current_time

    except KeyboardInterrupt:
        print("\nLive capture stopped by user.")
        
    finally:
        csv_file.close()
        print("Feature vectors safely saved to live_capture_log.csv")

if __name__ == "__main__":
    main()
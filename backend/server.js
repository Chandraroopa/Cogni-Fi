const express = require('express');
const cors = require('cors');
const app = express();

app.use(cors());
app.use(express.json());

app.get('/api/scan', (req, res) => {
    res.json({
        status: "success",
        networks: [
            { id: 1, ssid: "Home_WiFi_5G", bssid: "00:11:22:33:44:55", signal: "-45 dBm", security: "WPA3", riskLevel: "Low", isTrusted: true },
            { id: 2, ssid: "Public_Free_WiFi", bssid: "66:77:88:99:AA:BB", signal: "-62 dBm", security: "Open", riskLevel: "High", isTrusted: false }
        ]
    });
});

app.post('/api/analyze', (req, res) => {
    res.json({
        status: "success",
        analysis: {
            riskScore: 85,
            threatType: "Evil Twin / Rogue Access Point",
            recommendations: ["Avoid entering credentials on this network."]
        }
    });
});

app.listen(8000, () => {
    console.log("Server running on http://localhost:8000");
});
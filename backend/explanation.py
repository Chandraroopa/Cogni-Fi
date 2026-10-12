class RiskExplanationEngine:
    @staticmethod
    def build_reasons(binary_result=None, multiclass_result=None, factors=None,
                      security_type=None, assessment='partial', ml_is_threat=None,
                      ml_model_type=None):
        factors = factors or {}
        reasons = []
        if security_type == 'OPEN':
            reasons.append('The access point has no Wi-Fi link-layer encryption.')
        elif security_type == 'WEP':
            reasons.append('The access point uses obsolete WEP encryption.')
        elif security_type == 'WPA':
            reasons.append('The access point uses an older WPA security standard.')
        if ml_is_threat is True:
            reasons.append('The ML classifier flagged the observed traffic window as a threat.')
        elif ml_is_threat is False:
            reasons.append('The ML classifier labelled the observed traffic window Normal; this does not guarantee safety.')
        if ml_model_type == 'legacy_binary' and binary_result:
            reasons.append('The legacy binary ML decision uses its supplied, frozen threshold.')
        if multiclass_result and ml_is_threat is True:
            attack = multiclass_result.get('predicted_class')
            if isinstance(attack, str) and attack and attack != 'Normal':
                reasons.append(f'The multiclass model predicted {attack} for this window; this is not proof of an attack.')
        b = factors.get('behavior')
        if b is not None and b >= 70:
            reasons.append('Behavioral measurements strongly deviate from the validated normal reference.')
        elif b is not None and b >= 30:
            reasons.append('Behavioral measurements are elevated against the validated normal reference.')
        if assessment != 'full':
            reasons.append('Security evidence is incomplete; interpret the score as provisional.')
        if not reasons:
            reasons.append('No strong indicators were found in the evidence supplied.')
        return reasons

    @staticmethod
    def build_recommendations(status, assessment='partial', attack_type=None):
        if status == 'Risky':
            items = ['Avoid sensitive activity on this network until verified.',
                     'Consider switching to a trusted connection.']
            if attack_type in ('Evil_Twin', 'RogueAP'):
                items.append('Verify the SSID and BSSID with the legitimate network operator.')
            elif attack_type in ('Deauth', 'Disas'):
                items.append('Investigate unexpected disconnections and access point identity.')
            return items
        if status == 'Suspicious':
            return ['Treat the ML/security warning as provisional and verify the access point.',
                    'Avoid sensitive activity until further examination.']
        if status == 'Unverified':
            return ['Collect additional ML, behavioral and Wi-Fi security evidence before calling this network safe.']
        if status == 'Safe':
            return ['No strong indicators were observed in this assessment; continue ordinary security precautions.']
        return ['Not enough evidence was supplied to assess the network.']

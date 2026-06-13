def deidentify_patient_data(patient_data):
    deidentified_data = {}
    patient_id_map = {}
    claim_id_map = {}

    patient_counter = 1
    claim_counter = 1

    for patient_id, claims in patient_data.items():
        if patient_id not in patient_id_map:
            patient_id_map[patient_id] = f"PATIENT_{patient_counter:03d}"
            patient_counter += 1

        masked_patient_id = patient_id_map[patient_id]
        deidentified_data[masked_patient_id] = {}

        for claim_id, claim_info in claims.items():
            if claim_id not in claim_id_map:
                claim_id_map[claim_id] = f"CLAIM_{claim_counter:03d}"
                claim_counter += 1

            masked_claim_id = claim_id_map[claim_id]

            deidentified_data[masked_patient_id][masked_claim_id] = claim_info.copy()

    return deidentified_data
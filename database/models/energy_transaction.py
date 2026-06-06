class EnergyTransaction:

    def __init__(
        self,
        entity_id,
        entity_type,
        district,
        energy_consumed,
        energy_generated,
        anomaly,
        energy_price,
        bill_amount,
    ):

        self.entity_id = entity_id
        self.entity_type = entity_type
        self.district = district
        self.energy_consumed = energy_consumed
        self.energy_generated = energy_generated
        self.anomaly = anomaly
        self.energy_price = energy_price
        self.bill_amount = bill_amount

    def to_dict(self):

        return {
            "transaction_type": "energy_record",
            "entity_id": self.entity_id,
            "entity_type": self.entity_type,
            "district": self.district,
            "energy_consumed": self.energy_consumed,
            "energy_generated": self.energy_generated,
            "anomaly": self.anomaly,
            "energy_price": self.energy_price,
            "bill_amount": self.bill_amount,
        }

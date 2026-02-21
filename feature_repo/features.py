from datetime import timedelta
from feast import Entity, FeatureView, Field, FileSource
from feast.types import Float32, Int64, String

# 1. The Offline Data Lake
patient_data = FileSource(
    path="../data/insurance_claims.parquet",
    timestamp_field="event_timestamp"
)

# 2. The Primary Key
patient = Entity(name="patient", join_keys=["patient_id"])

# 3. The Feature View (Saved to Redis for live prediction)
patient_demographics = FeatureView(
    name="patient_stats",
    entities=[patient],
    ttl=timedelta(days=3650),
    schema=[
        Field(name="age", dtype=Int64),
        Field(name="bmi", dtype=Float32),
        Field(name="smoker", dtype=String),
    ],
    online=True,
    source=patient_data
)
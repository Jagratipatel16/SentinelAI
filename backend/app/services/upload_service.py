import os
import uuid
import joblib
import pandas as pd

# --------------------------------------------------
# Load Trained Model
# --------------------------------------------------

BASE_DIR = os.path.dirname(os.path.dirname(__file__))

MODEL_PATH = os.path.join(
    BASE_DIR,
    "models",
    "fraud_model.pkl"
)

model = joblib.load(MODEL_PATH)


# --------------------------------------------------
# Upload Folder
# --------------------------------------------------

UPLOAD_FOLDER = os.path.join(
    BASE_DIR,
    "uploads"
)

os.makedirs(
    UPLOAD_FOLDER,
    exist_ok=True
)


# --------------------------------------------------
# Process Uploaded CSV
# --------------------------------------------------

def process_csv(file):

    # ---------- Save Uploaded File ----------

    filename = str(uuid.uuid4()) + ".csv"

    input_path = os.path.join(
        UPLOAD_FOLDER,
        filename
    )

    with open(input_path, "wb") as buffer:

        buffer.write(file.file.read())

    # ---------- Read CSV ----------

    df = pd.read_csv(input_path)

    # ---------- Required Features ----------

    features = [

        "step",

        "type",

        "amount",

        "oldbalanceOrg",

        "newbalanceOrig",

        "oldbalanceDest",

        "newbalanceDest",

        "isFlaggedFraud"

    ]

    X = df[features]

    # ---------- Prediction ----------

    prediction = model.predict(X)

    probability = model.predict_proba(X)[:, 1]

    # ---------- Add Columns ----------

    df["Prediction"] = prediction

    df["Prediction"] = df["Prediction"].map(

        {

            0: "Safe",

            1: "Fraud"

        }

    )

    df["Probability"] = probability.round(4)

    df["Risk Score"] = (probability * 100).round(2)

    # ---------- Save Result ----------

    output_file = "prediction_" + filename

    output_path = os.path.join(

        UPLOAD_FOLDER,

        output_file

    )

    df.to_csv(

        output_path,

        index=False

    )

    # ---------- Summary ----------

    total_records = len(df)

    fraud_transactions = (df["Prediction"] == "Fraud").sum()

    safe_transactions = (df["Prediction"] == "Safe").sum()

    return {

        "total_records": total_records,

        "fraud_transactions": int(fraud_transactions),

        "safe_transactions": int(safe_transactions),

        "download_file": output_file

    }
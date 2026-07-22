import os
import uuid
import joblib
import pandas as pd

from app.models.transaction import Transaction

# --------------------------------------------------
# Load Trained Model
# --------------------------------------------------

BASE_DIR = os.path.dirname(os.path.dirname(__file__))

MODEL_PATH = os.path.join(
    BASE_DIR,
    "models",
    "fraud_model.pkl"
)

ENCODER_PATH = os.path.join(
    BASE_DIR,
    "models",
    "type_encoder.pkl"
)

model = joblib.load(MODEL_PATH)
type_encoder = joblib.load(ENCODER_PATH)


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

def process_csv(file, db=None):

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

    X = df[features].copy()

    # ---------- Encode "type" column ----------
    # Model was trained on numeric type codes (see type_encoder.pkl),
    # but uploaded CSVs contain text labels like "PAYMENT", "TRANSFER".

    unknown_types = set(X["type"].astype(str).unique()) - set(
        type_encoder.classes_
    )

    if unknown_types:
        raise ValueError(
            "Unknown transaction type(s) in CSV: "
            + ", ".join(unknown_types)
            + ". Expected one of: "
            + ", ".join(type_encoder.classes_)
        )

    X["type"] = type_encoder.transform(X["type"].astype(str))

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

    # ---------- Persist to MySQL so Dashboard & Graph Analytics can use it ----------
    # nameOrig/nameDest are the account-id columns from the raw PaySim CSV.
    # If they aren't present, we fall back to generated per-row account ids
    # so the upload still succeeds, but graph analytics won't find
    # meaningful shared connections.

    if db is not None:

        has_accounts = "nameOrig" in df.columns and "nameDest" in df.columns

        for idx, row in df.iterrows():

            sender = row["nameOrig"] if has_accounts else f"ACC{idx}_SRC"
            receiver = row["nameDest"] if has_accounts else f"ACC{idx}_DST"

            db_transaction = Transaction(
                sender=str(sender),
                receiver=str(receiver),
                amount=float(row["amount"]),
                transaction_type=str(row["type"]),
                status=row["Prediction"],
                user_id=None
            )

            db.add(db_transaction)

        db.commit()

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
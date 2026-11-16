# FreshCart Pipelines

## Submission

- **Repository:** https://github.com/sahanareddy18/freshcart-pipelines
- **Report:** `report/23BCS124_Kanukuntla_Sahana_Pipelines.pdf`
- **FreshCart ELT notebook:** `elt/freshcart_elt.ipynb`
- **Mage Iris project and notebook:** `iris_project/` and `iris_project/iris_pipeline.ipynb`
- **RabbitMQ stream scripts:** `stream/dispatcher.py` and `stream/driver.py`
- **Captured evidence:** `screenshots/`

The RabbitMQ-to-Snowflake bonus implementation is included in
`stream/consumer_to_landing.py` and `stream/publish_freshcart_orders.py`. It
requires valid RabbitMQ and Snowflake environment variables for a live run.

Coursework workspace for the "From Git to Gold" assignment. It contains a
Snowflake-ready FreshCart ELT flow, an import-safe Mage Iris pipeline, and
RabbitMQ topic-routing scripts.

## Local setup

Use Python 3.12, then install the project dependencies:

```powershell
py -3.12 -m venv .venv
.venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
python -m pytest
```

The unit tests do not require Snowflake or RabbitMQ credentials. Snowflake
account-backed runs use `SNOWFLAKE_ACCOUNT`, `SNOWFLAKE_USER`,
`SNOWFLAKE_PASSWORD`, `SNOWFLAKE_WAREHOUSE`, `SNOWFLAKE_DATABASE`, and
`SNOWFLAKE_SCHEMA`. RabbitMQ scripts use `RABBITMQ_URL`; keep credentials in
environment variables and never commit them.

## Project map

- `elt/`: notebook, Python landing helpers, and Snowflake SQL transforms.
- `iris_project/`: Mage-compatible Iris blocks and pipeline metadata.
- `stream/`: dispatcher, topic-bound drivers, and the optional ELT consumer.
- `tests/`: local tests used by GitHub Actions.

The named submission report (`RollNo_Name_Pipelines.pdf`) is delivered separately
from this code repository. Keep account screenshots and credentials private unless
your instructor specifically requests them in the shared repository.

The class-provided FreshCart and Mage notebooks were not present in the
workspace. The SQL and sample data here therefore make their assumptions
explicit; compare those assumptions with your lecture materials before the
Snowflake run. Account results, GitHub Actions screenshots, the required
pre-run predictions, and the personal reflection must be completed from your
own runs.

## Run the Iris pipeline

For standalone local execution, run the blocks through the helper in
`iris_project/run_local.py`. To use Mage's CLI/UI, install Mage separately and
launch the project from this repository's parent directory:

```powershell
mage start iris_project
mage run iris_project iris_classifier --test
```

## Run the stream

Set `RABBITMQ_URL`, then run one dispatcher and several drivers in separate
terminals:

```powershell
python -m stream.dispatcher --duration 120
python -m stream.driver Ravi "bangalore.koramangala.*"
python -m stream.driver Arjun "bangalore.*.ride"
python -m stream.driver Control "bangalore.#"
```

The dispatcher publishes one deliberately malformed message for every ten
messages. Drivers reject malformed messages without requeueing them.

## Snowflake notebook

Set the six `SNOWFLAKE_*` variables listed above, open `elt/freshcart_elt.ipynb`,
and run its cells from top to bottom. The local fixture is designed to reproduce
the assignment's baseline counts, INR 7,785 revenue, and 126 points. Compare its
field mappings and customer history with the class materials before submitting.

## Bonus: RabbitMQ to Snowflake

Start the consumer first, then publish the sample order batch from another
terminal. Both terminals need `RABBITMQ_URL`; the consumer also needs the
Snowflake environment variables.

```powershell
python -m stream.consumer_to_landing --duration 60 --pattern "orders.#"
python -m stream.publish_freshcart_orders --interval 0.1 --repeat 1
```

The consumer compares gold row count and revenue before and after replaying
the transforms. The same order IDs are merged into gold rather than appended.

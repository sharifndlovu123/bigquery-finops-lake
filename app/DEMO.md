# Demo: budget ladder

**Framework:** none, plain Python. **Moving parts locally:** none, but in the cloud this runs off a Pub/Sub message.

`decide(percent, env)` maps a budget alert to an action: notify at 50%, open a ticket at 90%, stop resources at 100% for `dev`, and only page a human for anything else.

## Run it

```bash
cd app
python3 -m venv .venv && . .venv/bin/activate
pip install -r requirements.txt
```

```bash
pytest                    # 3 tests
python -c "from ladder import decide; print(decide(100, 'dev'), decide(100, 'prod'))"
# stop_resources page_owner
```

## What is missing locally (added in the cloud work)

- The budget alert arriving on Pub/Sub, which will trigger a Cloud Run function.
- The function reading the project's `env` label.
- Actually stopping VMs, and the BigQuery ledger of savings.

To simulate a message locally, pass the percentage in by hand as above.

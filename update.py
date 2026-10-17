"""Daily pipeline: fetch → (re)learn → rebuild map data.

    python update.py           # news, disasters, IFRC, Gaza data + self-training + dashboard
    python update.py --full    # also re-download UCDP, GHI, FSI, IFRC societies (weekly)

Schedule it with Windows Task Scheduler / cron to keep the assistant current.
"""
import sys

from src import build_dashboard, ingest, self_train

if __name__ == "__main__":
    if "--full" in sys.argv:
        ingest.ingest_countries()
        ingest.ingest_structured()
    ingest.ingest_live()
    self_train.run()
    build_dashboard.build()

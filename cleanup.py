from database import GameDatabase
from ensemble_models import EnsembleManager
import os

def run_cleanup():
    print("Starting daily cleanup...")
    db = GameDatabase()
    db.cleanup_old_data(days=7)
    
    ensemble = EnsembleManager()
    ensemble.cleanup_old_data(days=7)
    print("Cleanup completed successfully.")

if __name__ == "__main__":
    run_cleanup()

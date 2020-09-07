SFREQ = 10
DATADIR_PROCESSED = "C:/Users/JohnDoe/surfdrive/Biochill_RITE/20200818_v3.0.0/data/processed"
DATADIR_RAW = "C:/Users/JohnDoe/surfdrive/Biochill_RITE/20200818_v3.0.0/data/raw"
SUBJECTS = [f"subj-{str(i).zfill(2)}" for i in range(1, 9)]
sessions = [f"sess-{str(i).zfill(2)}" for i in range(1, 11)]
conditions = ["cond-A", "cond-B", "cond-B", "cond-A", "cond-B", "cond-A", "cond-B", "cond-A", "cond-B", "cond-A"]
SESSIONS = [f"{s}_{c}" for s, c in zip(sessions, conditions)]    # sessions and conditions are linked

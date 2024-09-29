
def create_communicas(obj):
    # Section selection
    # Full examination
    obj.h1.setToolTip("Artifacts will be identified/corrected in the whole signal.")
    # Selected length
    obj.h2.setToolTip("Artifacts will be identified/corrected in the part of signal defined by 'Initial interval' and 'Last interval'.")
    # Set boundries
    obj.recount.setToolTip("Apply new boundaries based on the selection.")


    # Methods of identification
    # T1-T3
    obj.auto_art.setToolTip("""T1: identified as a difference too big between two intervals corresponding with a sample.
T2: identified as an interval too short taking into consideration previous sample.
T2: identified as an interval too short taking into consideration previous sample.""")
    # Tarvainen
    obj.poin_art.setToolTip("The Tarvainen method of RR artifact correction involves applying a frequency-domain adaptive filter to the RR interval series.")
    # Quotient
    obj.quot_art.setToolTip("Quotient filtering proposed by Piskorski and Guzik.")
    # Square
    obj.square_art.setToolTip("Square filtering proposed by Piskorski and Guzik.")
    # Manual
    obj.art_btn.setToolTip("Selected sample of RR Signal will be identified as an artifact.")
    # Delete single
    obj.del_btn.setToolTip("Selected sample of RR Signal will be removed from identified artifacts set.")
    # Delete all
    obj.clear_art.setToolTip("All artifacts selected with all algorithms will be removed from the set.")
       
    # Methods of correction
    # linear interpolation
    obj.m1.setToolTip("Correction with linear interpolation.")
    # cubic splain
    obj.m2.setToolTip("Correction with cubic slain.")
    # deletion
    obj.m3.setToolTip("Deleting corrupted samples from examination. Recommended if artifacts occurs in the first or last sample.")
    # moving average
    obj.m4.setToolTip("Correction with a moving average algorithm with a window of length 7.")
    # pre mean
    obj.m5.setToolTip("Correction by replacing the artifact with a mean of few last samples defined by user.")
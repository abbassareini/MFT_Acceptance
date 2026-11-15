import uproot
import numpy as np
import glob
import os
from collections import Counter

FOLDER  = r"C:\Users\USER\Downloads"
PREVIEW = 10        # how many example tracks to print

def read_mc_labels(branch):

    raw = np.asarray(branch.debug_array(0), dtype=np.uint8)

    offset = None
    for off in range(0, 256):
        if off + 8 > len(raw):
            break
        nH, nT = np.frombuffer(raw[off:off + 8].tobytes(), dtype="<u4")
        nH, nT = int(nH), int(nT)
        if nH == 0 or nT == 0:
            continue
        if off + 8 + 4 * nH + 8 * nT == len(raw):
            offset = off
            break

    if offset is None:
        return None, None

    start = offset + 8
    idx    = np.frombuffer(raw[start : start + 4 * nH].tobytes(), dtype="<u4").astype(np.int64)
    labels = np.frombuffer(raw[start + 4 * nH :].tobytes(), dtype="<u8")

    return idx, labels

def decode_label(labels):
    trackID = (labels & ((1 << 31) - 1)).astype(np.int64)
    eventID = ((labels >> 31) & ((1 << 19) - 1)).astype(np.int64)
    sourceID = ((labels >> 50) & 0xFF).astype(np.int64)
    return trackID, eventID, sourceID

def analyse_file(path):

    print("\n" + "=" * 70)
    print(f"FILE: {os.path.basename(path)}")
    print("=" * 70)

    tree = uproot.open(path)["o2sim"]

    chipID = np.asarray(tree["MFTClusterComp.mChipID"].array()[0])
    n_clusters = len(chipID)

    idx, labels = read_mc_labels(tree["MFTClusterMCTruth"])

    if idx is None:
        print("  Could not unpack the MC truth block in this file.")
        return

    trackID, eventID, sourceID = decode_label(labels)

    first = idx

    is_noise = sourceID[first] == 255
    is_real  = ~is_noise

    print(f"  clusters in this file      : {n_clusters}")
    print(f"  clusters from a particle   : {int(is_real.sum())}")
    print(f"  clusters that are noise    : {int(is_noise.sum())}")

       key = ((sourceID[first] << 50)
           | (eventID[first] << 31)
           | trackID[first])

    key_real  = key[is_real]
    chip_real = chipID[is_real]

    counts = Counter(key_real.tolist())

    print(f"  different particles (tracks): {len(counts)}")

    hist = Counter(counts.values())
    total = sum(n * k for n, k in hist.items())

    print("\n  clusters per track:")
    for n in sorted(hist):
        bar = "#" * min(50, hist[n] // 10)
        print(f"    {n:>3} cluster(s): {hist[n]:>5} tracks  {bar}")

    print(f"\n  mean clusters per track: {total / len(counts):.2f}")
    print("  (the MFT has 5 disks, and each disk carries TWO")
    print("   sensor planes -- front and back -- so 10 planes.")
    print("   A particle crossing the whole MFT can leave up to")
    print("   10 clusters. Tracks with only 1-2 clusters just")
    print("   clipped the edge of the detector.)")
    
    print(f"\n  --- {PREVIEW} example tracks ---")
    print(f"  {'trackID':>9} {'evID':>6} {'nClus':>6}   chipIDs")

    shown = 0
    for k, c in counts.items():
        if c < 2:
            continue                     # need at least 2 to be interesting
        mask = key_real == k
        chips = sorted(chip_real[mask].tolist())
        print(f"  {k & ((1<<31)-1):>9} {(k >> 31) & ((1<<19)-1):>6} {c:>6}   {chips}")
        shown += 1
        if shown >= PREVIEW:
            break

def main():

    files = sorted(glob.glob(os.path.join(FOLDER, "*.root")))

    print(f"Looking in: {FOLDER}")
    print(f"Found {len(files)} root file(s)")

    if not files:
        print("No .root files here! Check the FOLDER setting at the top.")
        return

    for path in files:
        analyse_file(path)

    print("\n" + "=" * 70)
    print("Done.")
    print("=" * 70)
    
main()
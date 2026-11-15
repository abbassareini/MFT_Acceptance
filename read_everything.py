import uproot
import numpy as np
import glob
import os

FOLDER  = r"C:\Users\USER\Downloads"   
PREVIEW = 10                           
def decode_mData(mData):
    row       = mData & 0x1FF
    col       = (mData >> 9) & 0x3FF
    patternID = (mData >> 19)
    return row, col, patternID


def preview_values(values):
    """Turn the first few values into a short readable string."""
    shown = values[:PREVIEW]
    try:
        shown = [v.item() if hasattr(v, "item") else v for v in shown]
    except Exception:
        pass
    text = ", ".join(str(v) for v in shown)
    if len(values) > PREVIEW:
        text += ", ..."
    return text


def read_branch(tree, name, branch):
    """
    Read ONE branch and print what is inside it.

    This is the Python version of:
        tree->SetBranchAddress(name, &myVariable);
        tree->GetEntry(i);
    """
    print(f"\n    BRANCH: {name}")
    print(f"      type: {branch.typename}")

    try:
        data = branch.array()
    except Exception as e:
        # Some O2 objects cannot be decoded without the O2 software.
        print(f"      [cannot read in Python: {type(e).__name__}]")
        print(f"      reason: {str(e).splitlines()[0][:90]}")
        return None

        for i in range(len(data)):
        entry = data[i]

        try:
            values = list(entry)
        except TypeError:
            # not a list, just a single value
            print(f"      entry {i}: {entry}")
            continue

        print(f"      entry {i}: {len(values)} values")
        if len(values) > 0:
            print(f"        -> {preview_values(values)}")
        else:
            print("        -> (empty)")

    return data


def read_tree(tree, treename):
    """Read every branch of one tree."""

    print(f"\n  TREE: '{treename}'")
    print(f"  entries (rows): {tree.num_entries}")
    print(f"  branches: {len(tree.keys())}")

    collected = {}

    for name, branch in tree.items():
        data = read_branch(tree, name, branch)
        if data is not None:
            collected[name] = data

    if "MFTClusterComp.mChipID" in collected and "MFTClusterComp.mData" in collected:
        print("\n  ---------- DECODED CLUSTERS ----------")

        chip_all = collected["MFTClusterComp.mChipID"]
        data_all = collected["MFTClusterComp.mData"]

        for i in range(len(chip_all)):
            chip = np.asarray(chip_all[i])
            mdat = np.asarray(data_all[i])

            print(f"\n  entry {i}: {len(chip)} clusters")
            print(f"    {'#':>4}  {'chipID':>7}  {'row':>5}  {'col':>5}  {'pattID':>7}")

            for j in range(min(PREVIEW, len(chip))):
                row, col, pattID = decode_mData(int(mdat[j]))
                print(f"    {j:>4}  {int(chip[j]):>7}  {row:>5}  {col:>5}  {pattID:>7}")

            if len(chip) > 0:
                print(f"    chipID range: {chip.min()} -> {chip.max()}")
                print(f"    different chips hit: {len(np.unique(chip))} (MFT has 936 sensors)")

    return collected


def read_file(path):
    """Open ONE root file and read everything inside it."""

    print("\n" + "=" * 70)
    print(f"FILE: {os.path.basename(path)}")
    print("=" * 70)

    file = uproot.open(path)

    print(f"objects inside: {len(file.keys(cycle=False))}")

    for key in file.keys(cycle=False):
        obj = file[key]
        classname = getattr(obj, "classname", type(obj).__name__)

        print(f"\n  OBJECT: '{key}'   (type: {classname})")

        if classname == "TTree":
            read_tree(obj, key)
        else:
            print("    (not a tree, nothing to loop over)")

    file.close()


def main():

    pattern = os.path.join(FOLDER, "*.root")
    files = sorted(glob.glob(pattern))

    print(f"Looking in: {FOLDER}")
    print(f"Found {len(files)} root file(s)\n")

    if len(files) == 0:
        print("No .root files here! Check the FOLDER setting at the top.")
        return

    for path in files:
        read_file(path)

    print("\n" + "=" * 70)
    print(f"Done. {len(files)} file(s) opened and read.")
    print("=" * 70)


main()

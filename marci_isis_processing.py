#!/usr/bin/env python3
# @author: mp10
# @coding assistant: [TGC-DD26092025]
# pip install

"""
Python refactoring of the original C shell script to process MRO-MARCI images
using ISIS (Integrated Software for Imagers and Spectrometers) tools.

Workflow:
- Convert *.IMG to *.cub with marci2isis
- Initialize SPICE kernels with spiceinit (web=true)
- Calibrate with marcical
- Explode bands into separate files
- Map project with cam2map using a given map template
- Convert final cubes to PNG images with isis2std

Supports optional deletion of intermediate files to save disk space.

Original C shell script functionality is fully preserved.

Usage:
    python marci_isis_processing.py path/to/maptemplate.map [0|1]

    Arguments:
        maptemplate.map  Path to the ISIS map template file.
        0                Keep all intermediate files.
        1                Delete old intermediate files as processing progresses.
"""

import subprocess
from pathlib import Path
from typing import Literal


def run_command(command: list[str]) -> None:
    """Run a system command and stream output to console."""
    print(f"Running: {' '.join(command)}")
    subprocess.run(command, check=True)


def process_images(
    input_dir: Path,
    map_template: Path,
    delete_intermediate: Literal[0, 1] = 0,
) -> None:
    """
    Process MRO-MARCI images through the ISIS pipeline.

    Args:
        input_dir (Path): Directory containing the image files (*.IMG).
        map_template (Path): Path to the ISIS map template file.
        delete_intermediate (Literal[0, 1]): Whether to delete intermediate files (1 = yes).
    """
    # Step 1: Convert .IMG to .cub with marci2isis
    for img_file in sorted(input_dir.glob("*.IMG")):
        base_name = img_file.stem
        cub_file = input_dir / f"{base_name}.cub"
        run_command(["marci2isis", f"from={img_file}", f"to={cub_file}"])
        if cub_file.exists() and delete_intermediate:
            img_file.unlink()
            print(f"Deleted intermediate file: {img_file}")

    # Step 2: Initialize SPICE with spiceinit (web = True)
    for cub_file in sorted(input_dir.glob("*.cub")):
        run_command(["spiceinit", f"from={cub_file}", "web=true"])

    # Step 3: Calibrate with marcical
    for cub_file in sorted(input_dir.glob("*.cub")):
        base_name = cub_file.stem
        lev1_file = input_dir / f"{base_name}.lev1.cub"
        run_command(["marcical", f"from={cub_file}", f"to={lev1_file}"])
        if lev1_file.exists() and delete_intermediate:
            cub_file.unlink()
            print(f"Deleted intermediate file: {cub_file}")

    # Step 4: Explode bands into separate files (*.band#.cub)
    for lev1_file in sorted(input_dir.glob("*.lev1.cub")):
        base_name = lev1_file.stem.replace(".lev1", "")
        # explode outputs multiple band files with base_name.band#.cub pattern
        run_command(["explode", f"from={lev1_file}", f"to={input_dir / base_name}"])
        if delete_intermediate:
            lev1_file.unlink()
            print(f"Deleted intermediate file: {lev1_file}")

    # Step 5: Map project each band with cam2map using the provided map template
    # Pattern: *.band*.cub
    for band_file in sorted(input_dir.glob("*.band*.cub")):
        base_name = band_file.stem.replace(".band", "")
        lev2_file = input_dir / f"{base_name}.lev2.cub"
        run_command(
            [
                "cam2map",
                f"from={band_file}",
                f"map={map_template}",
                f"to={lev2_file}",
            ]
        )
        if lev2_file.exists() and delete_intermediate:
            band_file.unlink()
            print(f"Deleted intermediate file: {band_file}")

    # Step 6: Convert final .lev2.cub to PNG images with isis2std
    for lev2_file in sorted(input_dir.glob("*.lev2.cub")):
        base_name = lev2_file.stem.replace(".lev2", "")
        run_command(["isis2std", f"from={lev2_file}", f"to={input_dir / base_name}"])
        # Commented out in original: do not delete lev2_file
        # if lev2_file.exists() and delete_intermediate:
        #     lev2_file.unlink()
        #     print(f"Deleted intermediate file: {lev2_file}")

    print("Processing complete.")


def main() -> None:
    import sys

    if len(sys.argv) != 3:
        print(
            f"Usage: {sys.argv[0]} path/to/maptemplate.map [0|1]\n"
            "0 = keep all files as you go\n"
            "1 = delete old files as you go"
        )
        sys.exit(1)

    map_template_path = Path(sys.argv[1])
    if not map_template_path.is_file():
        print(f"Error: Map template file '{map_template_path}' not found.")
        sys.exit(1)

    try:
        delete_flag: Literal[0, 1] = int(sys.argv[2])  # type: ignore
        if delete_flag not in (0, 1):
            raise ValueError
    except ValueError:
        print("Error: Second argument must be 0 or 1.")
        sys.exit(1)

    current_dir = Path.cwd()
    process_images(current_dir, map_template_path, delete_flag)


if __name__ == "__main__":
    main()

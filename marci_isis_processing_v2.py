marci_isis_processing.py

#!/usr/bin/env python3
# @author: mp10
# @coding assistant: [TGC-DD26092025]
# pip install

"""
Enhanced MARCI image processor using ISIS and Python 3.10+

Features:
- Logging (console + log file)
- Graceful fallback to SPICE Web Services
- Optional deletion of intermediate files
"""

import logging
import subprocess
import sys
from pathlib import Path
from typing import Literal


# ============ CONFIGURATION ============ #
LOG_FILE = Path("marci_isis_processing.log")
DELETE_OPTIONS = Literal[0, 1]
# ======================================= #


def setup_logging() -> None:
    """Configure logging to console and file."""
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s [%(levelname)s] %(message)s",
        handlers=[
            logging.FileHandler(LOG_FILE),
            logging.StreamHandler(sys.stdout),
        ],
    )


def run_command(command: list[str], fail_message: str = "") -> bool:
    """
    Execute a shell command, logging output and errors.

    Args:
        command (list[str]): The command to run.
        fail_message (str): Optional message to log on failure.

    Returns:
        bool: True if command succeeded, False otherwise.
    """
    logging.info(f"Running: {' '.join(command)}")
    try:
        subprocess.run(command, check=True)
        return True
    except subprocess.CalledProcessError as e:
        logging.error(f"{fail_message}\nCommand failed: {e}")
        return False


def try_spiceinit_with_web(cub_file: Path) -> None:
    """Attempt SPICE initialization using web kernels."""
    logging.warning(f"Falling back to SPICE Web Services for {cub_file}")
    run_command(
        ["spiceinit", f"from={cub_file}", "web=true"],
        fail_message=f"SPICE Web Services also failed for {cub_file}",
    )


def process_images(
    input_dir: Path,
    map_template: Path,
    delete_intermediate: DELETE_OPTIONS,
) -> None:
    """
    Process MARCI images through the ISIS pipeline.

    Args:
        input_dir (Path): Directory with input files.
        map_template (Path): Map template file path.
        delete_intermediate (0|1): Whether to delete intermediate files.
    """
    # Step 1: Convert .IMG to .cub
    for img in sorted(input_dir.glob("*.IMG")):
        cub = input_dir / f"{img.stem}.cub"
        if run_command(["marci2isis", f"from={img}", f"to={cub}"]):
            if cub.exists() and delete_intermediate:
                img.unlink()
                logging.info(f"Deleted: {img}")

    # Step 2: spiceinit (try web fallback on failure)
    for cub in sorted(input_dir.glob("*.cub")):
        if not run_command(
            ["spiceinit", f"from={cub}"],
            fail_message=f"spiceinit failed for {cub}. Trying web=true...",
        ):
            try_spiceinit_with_web(cub)

    # Step 3: Calibration
    for cub in sorted(input_dir.glob("*.cub")):
        lev1 = input_dir / f"{cub.stem}.lev1.cub"
        if run_command(["marcical", f"from={cub}", f"to={lev1}"]):
            if lev1.exists() and delete_intermediate:
                cub.unlink()
                logging.info(f"Deleted: {cub}")

    # Step 4: Explode bands
    for lev1 in sorted(input_dir.glob("*.lev1.cub")):
        base = lev1.stem.replace(".lev1", "")
        if run_command(["explode", f"from={lev1}", f"to={input_dir / base}"]):
            if delete_intermediate:
                lev1.unlink()
                logging.info(f"Deleted: {lev1}")

    # Step 5: cam2map projection
    for band in sorted(input_dir.glob("*.band*.cub")):
        base = band.stem.replace(".band", "")
        lev2 = input_dir / f"{base}.lev2.cub"
        run_command(
            ["cam2map", f"from={band}", f"map={map_template}", f"to={lev2}"],
            fail_message=f"cam2map failed for {band}",
        )
        if lev2.exists() and delete_intermediate:
            band.unlink()
            logging.info(f"Deleted: {band}")

    # Step 6: Export to PNG
    for lev2 in sorted(input_dir.glob("*.lev2.cub")):
        base = lev2.stem.replace(".lev2", "")
        run_command(
            ["isis2std", f"from={lev2}", f"to={input_dir / base}"],
            fail_message=f"isis2std failed for {lev2}",
        )

    logging.info("✅ MARCI processing pipeline complete.")


def main() -> None:
    setup_logging()

    if len(sys.argv) != 3:
        logging.error(
            f"Usage: {sys.argv[0]} path/to/maptemplate.map [0|1]\n"
            "0 = keep all intermediate files\n"
            "1 = delete intermediate files as you go"
        )
        sys.exit(1)

    map_template = Path(sys.argv[1])
    if not map_template.is_file():
        logging.error(f"Map template not found: {map_template}")
        sys.exit(1)

    try:
        delete_flag: DELETE_OPTIONS = int(sys.argv[2])  # type: ignore
        if delete_flag not in (0, 1):
            raise ValueError
    except ValueError:
        logging.error("Second argument must be 0 or 1.")
        sys.exit(1)

    current_dir = Path.cwd()
    logging.info(f"Processing started in {current_dir}")
    logging.info(f"Using map template: {map_template}")
    logging.info(f"Delete intermediate files: {'Yes' if delete_flag else 'No'}")

    process_images(current_dir, map_template, delete_flag)


if __name__ == "__main__":
    main()




#!/usr/bin/env python3
# @author: mp10
# @coding assistant: [TGC-DD26092025]
# pip install

"""
Enhanced MARCI ISIS pipeline with:
- Logging
- SPICE Web fallback
- Projection presets via --projection
Usage Examples
🎯 Use a predefined projection:
python marci_isis_processing.py --projection simplecyl --delete 1

"""

import sys
import logging
import subprocess
import argparse
from pathlib import Path
from typing import Literal

# ===================== CONFIG ===================== #
LOG_FILE = Path("marci_isis_processing.log")
DELETE_OPTIONS = Literal[0, 1]

PROJECTION_PRESETS: dict[str, str] = {
    "simplecyl": (
        "Group=Mapping\n"
        "  TargetName=Mars\n"
        "  LongitudeDomain=360\n"
        "  ProjectionName=SimpleCylindrical\n"
        "  CenterLongitude=0.0\n"
        "  CenterLatitude=0.0\n"
        "End_Group\n"
        "End\n"
    ),
    "polar": (
        "Group=Mapping\n"
        "  TargetName=Mars\n"
        "  LongitudeDomain=360\n"
        "  ProjectionName=PolarStereographic\n"
        "  CenterLongitude=0.0\n"
        "  CenterLatitude=90.0\n"
        "  TrueScaleLatitude=90.0\n"
        "  MinimumLatitude=60.0\n"
        "  MaximumLatitude=90.0\n"
        "End_Group\n"
        "End\n"
    ),
    "eqc": (
        "Group=Mapping\n"
        "  TargetName=Mars\n"
        "  LongitudeDomain=360\n"
        "  ProjectionName=Equirectangular\n"
        "  CenterLongitude=0.0\n"
        "  CenterLatitude=0.0\n"
        "End_Group\n"
        "End\n"
    ),
}
# ================================================== #


def setup_logging() -> None:
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s [%(levelname)s] %(message)s",
        handlers=[logging.FileHandler(LOG_FILE), logging.StreamHandler(sys.stdout)],
    )


def run_command(command: list[str], fail_message: str = "") -> bool:
    logging.info(f"Running: {' '.join(command)}")
    try:
        subprocess.run(command, check=True)
        return True
    except subprocess.CalledProcessError as e:
        logging.error(f"{fail_message}\nCommand failed: {e}")
        return False


def try_spiceinit_with_web(cub_file: Path) -> None:
    logging.warning(f"Falling back to SPICE Web Services for {cub_file}")
    run_command(
        ["spiceinit", f"from={cub_file}", "web=true"],
        fail_message=f"SPICE Web Services also failed for {cub_file}",
    )


def create_projection_map(projection: str, output_path: Path) -> None:
    if projection not in PROJECTION_PRESETS:
        logging.error(f"Unknown projection preset: {projection}")
        sys.exit(1)

    output_path.write_text(PROJECTION_PRESETS[projection])
    logging.info(f"Projection map template written: {output_path}")


def process_images(
    input_dir: Path,
    map_template: Path,
    delete_intermediate: DELETE_OPTIONS,
) -> None:
    for img in sorted(input_dir.glob("*.IMG")):
        cub = input_dir / f"{img.stem}.cub"
        if run_command(["marci2isis", f"from={img}", f"to={cub}"]):
            if cub.exists() and delete_intermediate:
                img.unlink()
                logging.info(f"Deleted: {img}")

    for cub in sorted(input_dir.glob("*.cub")):
        if not run_command(
            ["spiceinit", f"from={cub}"],
            fail_message=f"spiceinit failed for {cub}, trying web...",
        ):
            try_spiceinit_with_web(cub)

    for cub in sorted(input_dir.glob("*.cub")):
        lev1 = input_dir / f"{cub.stem}.lev1.cub"
        if run_command(["marcical", f"from={cub}", f"to={lev1}"]):
            if lev1.exists() and delete_intermediate:
                cub.unlink()
                logging.info(f"Deleted: {cub}")

    for lev1 in sorted(input_dir.glob("*.lev1.cub")):
        base = lev1.stem.replace(".lev1", "")
        if run_command(["explode", f"from={lev1}", f"to={input_dir / base}"]):
            if delete_intermediate:
                lev1.unlink()
                logging.info(f"Deleted: {lev1}")

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

    for lev2 in sorted(input_dir.glob("*.lev2.cub")):
        base = lev2.stem.replace(".lev2", "")
        run_command(
            ["isis2std", f"from={lev2}", f"to={input_dir / base}"],
            fail_message=f"isis2std failed for {lev2}",
        )

    logging.info("✅ MARCI processing complete.")


def parse_args():
    parser = argparse.ArgumentParser(description="Process MARCI images using ISIS.")
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument("--map", type=Path, help="Path to custom ISIS .map template")
    group.add_argument(
        "--projection",
        choices=list(PROJECTION_PRESETS.keys()),
        help="Use a predefined projection (e.g., simplecyl, polar, eqc)",
    )
    parser.add_argument(
        "--delete",
        type=int,
        choices=[0, 1],
        default=0,
        help="1 = delete intermediate files, 0 = keep them (default: 0)",
    )
    parser.add_argument(
        "--dir",
        type=Path,
        default=Path.cwd(),
        help="Directory containing .IMG files (default: current directory)",
    )
    return parser.parse_args()


def main() -> None:
    setup_logging()
    args = parse_args()

    input_dir: Path = args.dir.resolve()
    delete_flag: DELETE_OPTIONS = args.delete

    if args.map:
        map_template = args.map.resolve()
        if not map_template.is_file():
            logging.error(f"Map template not found: {map_template}")
            sys.exit(1)
    else:
        projection = args.projection
        map_template = input_dir / f"{projection}.map"
        create_projection_map(projection, map_template)

    logging.info(f"Using map: {map_template}")
    logging.info(f"Processing directory: {input_dir}")
    logging.info(f"Delete intermediate files: {'Yes' if delete_flag else 'No'}")

    process_images(input_dir, map_template, delete_flag)


if __name__ == "__main__":
    main()



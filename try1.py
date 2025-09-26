try1.map

from pathlib import Path


def create_map_template(output_path: Path) -> None:
    """
    Creates a standard ISIS map template file for MRO MARCI images.

    Args:
        output_path (Path): File path where the template will be written.
    """
    content = (
        "Group=Mapping\n"
        "  TargetName=Mars\n"
        "  LongitudeDomain=360\n"
        "  ProjectionName=SimpleCylindrical\n"
        "  CenterLongitude=0.0\n"
        "  CenterLatitude=0.0\n"
        "End_Group\n"
        "End\n"
    )

    output_path.write_text(content)
    print(f"✅ Map template written to: {output_path}")


# if __name__ == "__main__":
    # from pathlib import Path

    # output_map = Path("try1.map")
    # create_map_template(output_map)

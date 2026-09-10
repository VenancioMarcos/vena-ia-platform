"""Generate synthetic millimetre STEP fixtures with fixed, nonpersonal headers."""

from __future__ import annotations

import re
from pathlib import Path


def generate(output: Path) -> None:
    from OCP.BRepAlgoAPI import BRepAlgoAPI_Cut, BRepAlgoAPI_Fuse
    from OCP.BRepPrimAPI import BRepPrimAPI_MakeBox, BRepPrimAPI_MakeCylinder
    from OCP.gp import gp_Ax2, gp_Dir, gp_Pnt
    from OCP.IFSelect import IFSelect_RetDone
    from OCP.Interface import Interface_Static
    from OCP.STEPControl import STEPControl_AsIs, STEPControl_Writer
    from OCP.TopAbs import TopAbs_SOLID
    from OCP.TopExp import TopExp_Explorer

    axis = lambda z: gp_Ax2(gp_Pnt(0, 0, z), gp_Dir(0, 0, 1))  # noqa: E731
    cylinder = BRepPrimAPI_MakeCylinder(axis(-100), 25, 100).Shape()
    stepped = BRepAlgoAPI_Fuse(BRepPrimAPI_MakeCylinder(axis(-100), 30, 60).Shape(),
                             BRepPrimAPI_MakeCylinder(axis(-40), 15, 40).Shape()).Shape()
    keyway = BRepAlgoAPI_Cut(cylinder, BRepPrimAPI_MakeBox(gp_Pnt(20, -5, -80),
                                                        15, 10, 60).Shape()).Shape()
    prism = BRepPrimAPI_MakeBox(gp_Pnt(0, 0, -100), 30, 40, 100).Shape()
    shapes = {"cylinder_d50_l100": cylinder, "stepped_d30_d60": stepped,
              "asymmetric_keyway": keyway, "pure_prism": prism}
    output.mkdir(parents=True, exist_ok=True)
    STEPControl_Writer()  # Initialize OCCT exchange settings before saving them.
    saved = {key: Interface_Static.CVal_s(key)
             for key in ("write.step.schema", "write.step.unit")}
    try:
        for index, (name, shape) in enumerate(shapes.items()):
            schema = "AP203" if index % 2 == 0 else "AP214IS"
            assert Interface_Static.SetCVal_s("write.step.schema", schema)
            assert Interface_Static.SetCVal_s("write.step.unit", "MM")
            solids = TopExp_Explorer(shape, TopAbs_SOLID)
            solid = solids.Current()
            solids.Next()
            assert not solids.More()
            writer = STEPControl_Writer()
            assert writer.Transfer(solid, STEPControl_AsIs) == IFSelect_RetDone
            path = output / f"{name}.stp"
            assert writer.Write(str(path)) == IFSelect_RetDone
            content = path.read_text(encoding="ascii")
            header = (f"FILE_NAME('{name}.stp','2026-09-09T00:00:00',"
                      "('Vena_IA synthetic fixture'),(''), 'OCCT fixture generator','','');")
            content, count = re.subn(r"FILE_NAME\s*\(.*?;", header, content, count=1, flags=re.S)
            assert count == 1
            # AP203 administrative entities also inherit host/user information.
            # Only synthetic fixture metadata is normalized; preserve entity IDs
            # and all geometry/topology records verbatim.
            content = re.sub(r"^(#[0-9]+ = )PERSON\(.*?\);",
                             r"\1PERSON('OCCT_GENERATOR','', 'VENA_IA_SYNTHETIC',$,$,$);",
                             content, flags=re.M | re.S)
            content = re.sub(r"^(#[0-9]+ = )ORGANIZATION\(.*?\);",
                             r"\1ORGANIZATION('VENA_IA_SYNTHETIC','Synthetic fixtures','');",
                             content, flags=re.M | re.S)
            # AP203 also embeds creation date/time entities outside the header.
            content = re.sub(r"CALENDAR_DATE\([^)]*\)", "CALENDAR_DATE(2026,9,9)", content)
            content = re.sub(r"LOCAL_TIME\([^,]+,[^,]+,[^,]+,(#[0-9]+)\)",
                             r"LOCAL_TIME(0,0,$,\1)", content)
            content = re.sub(r"COORDINATED_UNIVERSAL_TIME_OFFSET\([^)]*\)",
                             "COORDINATED_UNIVERSAL_TIME_OFFSET(0,$,.AHEAD.)", content)
            content = "\n".join(line.rstrip() for line in content.splitlines()) + "\n"
            path.write_text(content, encoding="ascii", newline="\n")
    finally:
        for key, value in saved.items():
            Interface_Static.SetCVal_s(key, value)


if __name__ == "__main__":
    generate(Path(__file__).parent / "turning")

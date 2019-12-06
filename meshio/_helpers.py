import pathlib

import numpy

from . import (
    abaqus,
    ansys,
    cgns,
    dolfin,
    exodus,
    flac3d,
    gmsh,
    h5m,
    mdpa,
    med,
    medit,
    nastran,
    neuroglancer,
    obj,
    off,
    permas,
    ply,
    stl,
    svg,
    tetgen,
    vtk,
    vtu,
    wkt,
    xdmf,
)
from ._common import num_nodes_per_cell
from ._exceptions import ReadError, WriteError
from ._files import is_buffer
from ._mesh import Mesh

input_filetypes = [
    "abaqus",
    "ansys",
    "cgns",
    "dolfin-xml",
    "wkt",
    "exodus",
    "flac3d",
    "gmsh-ascii",
    "gmsh-binary",
    "mdpa",
    "med",
    "medit",
    "moab",
    "nastran",
    "neuroglancer",
    "permas",
    "ply-ascii",
    "ply-binary",
    "obj",
    "off",
    "stl-ascii",
    "stl-binary",
    "vtk-ascii",
    "vtk-binary",
    "vtu-ascii",
    "vtu-binary",
    "xdmf",
]

output_filetypes = [
    "abaqus",
    "ansys-ascii",
    "ansys-binary",
    "cgns",
    "dolfin-xml",
    "wkt",
    "exodus",
    "flac3d",
    "gmsh2-ascii",
    "gmsh2-binary",
    "gmsh4-ascii",
    "gmsh4-binary",
    "mdpa",
    "med",
    "medit",
    "moab",
    "nastran",
    "neuroglancer",
    "obj",
    "off",
    "permas",
    "ply-ascii",
    "ply-binary",
    "stl-ascii",
    "stl-binary",
    "svg",
    "tetgen",
    "vtk-ascii",
    "vtk-binary",
    "vtu-ascii",
    "vtu-binary",
    "xdmf",
    "xdmf-binary",
    "xdmf-hdf",
    "xdmf-xml",
]

_extension_to_filetype = {
    ".bdf": "nastran",
    ".cgns": "cgns",
    ".e": "exodus",
    ".ex2": "exodus",
    ".exo": "exodus",
    ".f3grid": "flac3d",
    ".fem": "nastran",
    ".med": "med",
    ".mesh": "medit",
    ".msh": "gmsh4-binary",
    ".nas": "nastran",
    ".xml": "dolfin-xml",
    ".post": "permas",
    ".post.gz": "permas",
    ".dato": "permas",
    ".dato.gz": "permas",
    ".h5m": "moab",
    ".obj": "obj",
    ".off": "off",
    ".ply": "ply-binary",
    ".stl": "stl-binary",
    ".vtu": "vtu-binary",
    ".vtk": "vtk-binary",
    ".wkt": "wkt",
    ".xdmf": "xdmf",
    ".xmf": "xdmf",
    ".inp": "abaqus",
    ".mdpa": "mdpa",
    ".svg": "svg",
    ".node": "tetgen",
    ".ele": "tetgen",
}


def _filetype_from_path(path):
    ext = ""
    out = None
    for suffix in reversed(path.suffixes):
        ext = suffix + ext
        if ext in _extension_to_filetype:
            out = _extension_to_filetype[ext]

    if out is None:
        raise ReadError("Could not deduce file format from extension '{}'.".format(ext))
    return out


def read(filename, file_format=None):
    """Reads an unstructured mesh with added data.

    :param filenames: The files/PathLikes to read from.
    :type filenames: str

    :returns mesh{2,3}d: The mesh data.
    """
    format_to_reader = {
        "ansys": ansys,
        "ansys-ascii": ansys,
        "ansys-binary": ansys,
        "cgns": cgns,
        #
        "gmsh": gmsh,
        "gmsh-ascii": gmsh,
        "gmsh-binary": gmsh,
        "gmsh2": gmsh,
        "gmsh2-ascii": gmsh,
        "gmsh2-binary": gmsh,
        "gmsh4": gmsh,
        "gmsh4-ascii": gmsh,
        "gmsh4-binary": gmsh,
        #
        "flac3d": flac3d,
        "wkt": wkt,
        "med": med,
        "medit": medit,
        "nastran": nastran,
        "neuroglancer": neuroglancer,
        "dolfin-xml": dolfin,
        "permas": permas,
        "moab": h5m,
        "obj": obj,
        "off": off,
        #
        "ply": ply,
        "ply-ascii": ply,
        "ply-binary": ply,
        #
        "stl": stl,
        "stl-ascii": stl,
        "stl-binary": stl,
        #
        "tetgen": tetgen,
        #
        "vtu-ascii": vtu,
        "vtu-binary": vtu,
        #
        "vtk-ascii": vtk,
        "vtk-binary": vtk,
        #
        "xdmf": xdmf,
        "exodus": exodus,
        #
        "abaqus": abaqus,
        #
        "mdpa": mdpa,
    }

    if is_buffer(filename, "r"):
        if file_format is None:
            raise ReadError("File format must be given if buffer is used")
        if file_format == "tetgen":
            raise ReadError(
                "tetgen format is spread across multiple files, and so cannot be read from a buffer"
            )
        msg = "Unknown file format '{}'".format(file_format)
    else:
        path = pathlib.Path(filename)
        if not path.exists():
            raise ReadError("File {} not found.".format(filename))

        if not file_format:
            # deduce file format from extension
            file_format = _filetype_from_path(path)

        msg = "Unknown file format '{}' of '{}'.".format(file_format, filename)

    if file_format not in format_to_reader:
        raise ReadError(msg)

    return format_to_reader[file_format].read(filename)


def write_points_cells(
    filename,
    points,
    cells,
    point_data=None,
    cell_data=None,
    field_data=None,
    file_format=None,
    **kwargs
):
    points = numpy.asarray(points)
    cells = {key: numpy.asarray(value) for key, value in cells.items()}
    mesh = Mesh(
        points, cells, point_data=point_data, cell_data=cell_data, field_data=field_data
    )
    return write(filename, mesh, file_format=file_format, **kwargs)


def write(filename, mesh, file_format=None, **kwargs):
    """Writes mesh together with data to a file.

    :params filename: File to write to.
    :type filename: str

    :params point_data: Named additional point data to write to the file.
    :type point_data: dict
    """
    if is_buffer(filename, "r"):
        if file_format is None:
            raise WriteError("File format must be supplied if `filename` is a buffer")
        if file_format == "tetgen":
            raise WriteError(
                "tetgen format is spread across multiple files, and so cannot be written to a buffer"
            )
    else:
        path = pathlib.Path(filename)
        if not file_format:
            # deduce file format from extension
            file_format = _filetype_from_path(path)

    try:
        writer = _writer_map[file_format]
    except KeyError:
        raise KeyError(
            "Unknown format '{}'. Pick one of {}".format(
                file_format, sorted(list(_writer_map.keys()))
            )
        )

    # check cells for sanity
    for key, value in mesh.cells.items():
        if key[:7] == "polygon":
            if value.shape[1] != int(key[7:]):
                raise WriteError()
        elif key in num_nodes_per_cell:
            if value.shape[1] != num_nodes_per_cell[key]:
                raise WriteError()
        else:
            # we allow custom keys <https://github.com/nschloe/meshio/issues/501> and
            # cannot check those
            pass

    # Write
    return writer(filename, mesh, **kwargs)


_writer_map = {
    "moab": h5m.write,
    "ansys-ascii": lambda f, m, **kwargs: ansys.write(f, m, **kwargs, binary=False),
    "ansys-binary": lambda f, m, **kwargs: ansys.write(f, m, **kwargs, binary=True),
    "wkt": wkt.write,
    "gmsh2-ascii": lambda f, m, **kwargs: gmsh.write(f, m, "2", **kwargs, binary=False),
    "gmsh2-binary": lambda f, m, **kwargs: gmsh.write(f, m, "2", **kwargs, binary=True),
    "gmsh4-ascii": lambda f, m, **kwargs: gmsh.write(f, m, "4", **kwargs, binary=False),
    "gmsh4-binary": lambda f, m, **kwargs: gmsh.write(f, m, "4", **kwargs, binary=True),
    "med": med.write,
    "medit": medit.write,
    "dolfin-xml": dolfin.write,
    "neuroglancer": neuroglancer.write,
    "obj": obj.write,
    "off": off.write,
    "permas": permas.write,
    "ply-ascii": lambda f, m, **kwargs: ply.write(f, m, **kwargs, binary=False),
    "ply-binary": lambda f, m, **kwargs: ply.write(f, m, **kwargs, binary=True),
    "stl-ascii": lambda f, m, **kwargs: stl.write(f, m, **kwargs, binary=False),
    "stl-binary": lambda f, m, **kwargs: stl.write(f, m, **kwargs, binary=True),
    "tetgen": tetgen.write,
    "vtu-ascii": lambda f, m, **kwargs: vtu.write(f, m, **kwargs, binary=False),
    "vtu-binary": lambda f, m, **kwargs: vtu.write(f, m, **kwargs, binary=True),
    "vtu": lambda f, m, **kwargs: vtu.write(f, m, **kwargs, binary=True),
    "vtk-ascii": lambda f, m, **kwargs: vtk.write(f, m, **kwargs, binary=False),
    "vtk-binary": lambda f, m, **kwargs: vtk.write(f, m, **kwargs, binary=True),
    "vtk": lambda f, m, **kwargs: vtk.write(f, m, **kwargs, binary=True),
    "xdmf": xdmf.write,
    "xdmf-binary": lambda f, m, **kwargs: xdmf.write(f, m, data_format="Binary"),
    "xdmf-hdf": lambda f, m, **kwargs: xdmf.write(f, m, data_format="HDF"),
    "xdmf-xml": lambda f, m, **kwargs: xdmf.write(f, m, data_format="XML"),
    "xdmf3": xdmf.write,
    "xdmf3-binary": lambda f, m, **kwargs: xdmf.write(f, m, data_format="Binary"),
    "xdmf3-hdf": lambda f, m, **kwargs: xdmf.write(f, m, data_format="HDF"),
    "xdmf3-xml": lambda f, m, **kwargs: xdmf.write(f, m, data_format="XML"),
    "abaqus": abaqus.write,
    "exodus": exodus.write,
    "mdpa": mdpa.write,
    "svg": svg.write,
    "nastran": nastran.write,
    "flac3d": flac3d.write,
    "cgns": cgns.write,
}

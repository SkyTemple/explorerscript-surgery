#!/usr/bin/env python3
"""Generate a debugging report for a test case. See README."""
from __future__ import annotations

import argparse
import hashlib
import os
import sys
import traceback
import warnings

from explorerscript.ssb_converting.decompiler.graph_building.graph_minimizer import (
    SsbGraphMinimizer,
)
from explorerscript.ssb_converting.decompiler.label_jump_to_resolver import (
    OpsLabelJumpToResolver,
)
from skytemple_files.common.ppmdu_config.xml_reader import Pmd2XmlReader

from skytemple_files.script.ssb.handler import SsbHandler

RENDER = True


def main(argv):
    parser = argparse.ArgumentParser()
    parser.add_argument("output_dir")
    parser.add_argument("edition")
    parser.add_argument("path_to_problematic_ssb")
    parser.add_argument("path_to_original_source_code")

    args = parser.parse_args()
    os.makedirs(args.output_dir, exist_ok=True)

    args.output_dir = os.path.abspath(args.output_dir)
    write_readme(args.output_dir)

    with open(args.path_to_problematic_ssb, "rb") as f:
        b = f.read()
        ssb = SsbHandler.deserialize(b, static_data=Pmd2XmlReader.load_default(args.edition))
        with open(os.path.join(args.output_dir, "compiled.ssb"), "wb") as f2:
            f2.write(b)

    routine_ops = ssb.get_filled_routine_ops()

    resolver = OpsLabelJumpToResolver(routine_ops)
    routine_ops = list(resolver)

    grapher = SsbGraphMinimizer(routine_ops)
    try:
        draw_graphs(grapher, args, "0_before_optimize")

        grapher.optimize_paths()
        draw_graphs(grapher, args, "1_after_optimize")

        grapher.build_branches()
        draw_graphs(grapher, args, "2_after_branch_before_group")
        grapher.group_branches()
        draw_graphs(grapher, args, "3_after_branch1")
        grapher.invert_branches()
        draw_graphs(grapher, args, "4_after_branch2")

        grapher.build_and_group_switch_cases()
        draw_graphs(grapher, args, "5_after_switch1")
        grapher.group_switch_cases()
        draw_graphs(grapher, args, "6_after_switch2")
        grapher.build_switch_fallthroughs()
        draw_graphs(grapher, args, "7_after_switch3")

        grapher.build_loops()
        draw_graphs(grapher, args, "8_after_loops")

        grapher.remove_label_markers()
        draw_graphs(grapher, args, "9_done")
    except:
        warnings.warn("Failed at least one graph step. Skipping rest. Decompiling will fail.")

    with open(os.path.join(args.output_dir, "original.exps"), "w") as fo:
        with open(args.path_to_original_source_code, "r") as fs:
            fo.write(fs.read())

    try:
        decompiled, _ = ssb.to_explorerscript()
    except:
        warnings.warn("Failed decompiling. Writing failed_decompile_err.txt instead.")
        with open(os.path.join(args.output_dir, "failed_decompile_err.txt"), "w") as ferr:
            ferr.write("".join(traceback.format_exception(*sys.exc_info())))
    else:
        with open(os.path.join(args.output_dir, "decompiled.exps"), "w") as fd:
            fd.write(decompiled)


def draw_graphs(grapher, args, run_name):
    local_output_dir = os.path.abspath(os.path.join(args.output_dir, "graphs", run_name))
    print(f">> {run_name}")
    if not RENDER:
        return
    os.makedirs(local_output_dir, exist_ok=True)
    for i, graph in enumerate(grapher._graphs):
        dot_name = os.path.join(local_output_dir, f"{i}.dot")
        hash_dotfile_before = None
        if os.path.exists(dot_name):
            with open(dot_name, "r") as f:
                hash_dotfile_before = hashlib.md5(f.read().encode("utf-8")).hexdigest()
        with open(dot_name, "w") as f:
            graph.write_dot(f)
        with open(dot_name, "r") as f:
            hash_dotfile_same = (
                hashlib.md5(f.read().encode("utf-8")).hexdigest() == hash_dotfile_before
            )
        unconnected_vertices = []
        if not hash_dotfile_same:
            print("Writing svg for " + dot_name)
            try:
                os.remove(os.path.join(local_output_dir, f"{i}.dot.svg"))
            except FileNotFoundError:
                pass
            os.chdir(local_output_dir)
            os.system(f"dot -Tsvg -O {i}.dot")
            print("done.")
        for v in graph.vs:
            if len(list(v.all_edges())) < 1 and v["name"] != 0:
                unconnected_vertices.append(v["label"])
        if len(unconnected_vertices) > 0:
            warnings.warn(
                f"Routine {i} has unconnected ops: {unconnected_vertices}"
            )


def write_readme(output_dir):
    with open(os.path.join(output_dir, "README.md"), "w") as f:
        f.write("""# <name>
Fixed in ExplorerScript: Not fixed yet.

## Source of ExplorerScript:

...

## Issue description:

...

## How to approach fix:

...

""")


if __name__ == "__main__":
    main(sys.argv)

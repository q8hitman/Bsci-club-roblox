"""Geometry regression checks for the north prototype; no Roblox credentials or network."""
import argparse
import copy
import hashlib
import xml.etree.ElementTree as ET
from pathlib import Path


def name(item):
    return item.find("Properties/string[@name='Name']").text


def signature(item):
    node = copy.deepcopy(item)
    for child in node.iter():
        child.attrib.pop("referent", None)
        if child.tag == "Ref":
            child.text = "reference"
    return hashlib.sha256(ET.tostring(node)).hexdigest()


def map_root(path):
    return ET.parse(path).getroot().find("Item")


def with_bridge_opening(items):
    """The only allowed south change: split its existing wall/window at the bridge."""
    result = []
    wall_count = window_count = 0
    for item in items:
        frame = item.find("Properties/CoordinateFrame[@name='CFrame']")
        pos = tuple(float(frame.find(a).text) for a in 'XYZ') if frame is not None else None
        boxes = None
        if name(item) == 'Cladding' and pos == (0, 56, -30):
            boxes = [((-70, 56, -30), (40, 64, 1.6)), ((30, 56, -30), (120, 64, 1.6)),
                     ((-40, 62, -30), (20, 52, 1.6))]
            wall_count += 1
        if name(item) == 'Ribbon' and pos in ((0, 33, -30.925), (0, 33, -29.075)):
            thickness = float(item.find("Properties/Vector3[@name='size']/Z").text)
            boxes = [((-69.5, 33, pos[2]), (39, 6, thickness)), ((29.5, 33, pos[2]), (119, 6, thickness))]
            window_count += 1
        if name(item) == 'Mullion' and pos[0] in (-48, -39) and pos[1] == 33 and pos[2] in (-31.1, -28.9):
            continue
        if boxes is None:
            result.append(item)
        else:
            for position, size in boxes:
                clone = copy.deepcopy(item)
                for axis, p, s in zip('XYZ', position, size):
                    clone.find(f"Properties/CoordinateFrame[@name='CFrame']/{axis}").text = f'{p:.4f}'
                    clone.find(f"Properties/Vector3[@name='size']/{axis}").text = f'{s:.4f}'
                result.append(clone)
    assert (wall_count, window_count) == (1, 2), 'Expected one specific south bridge wall and two window faces'
    return result


def validate(current, baseline):
    root, old = map_root(current), map_root(baseline)
    campus = next(v for v in root.findall("Item") if name(v) == "Campus")
    old_campus = next(v for v in old.findall("Item") if name(v) == "Campus")
    north = next((v for v in campus.findall("Item") if name(v) == "NorthBuilding"), None)
    assert north is not None, "NorthBuilding missing: v43 has no modular north prototype"
    modules = {name(v): v for v in north.findall("Item")}
    for required in ("Envelope", "Floors", "Atrium", "Circulation", "FlatClassroom_Photo17",
                     "TieredLecture_Photo16", "ExistingAmenities"):
        assert required in modules, f"Missing module: {required}"
    for room in ("FlatClassroom_Photo17", "TieredLecture_Photo16"):
        evidence = modules[room].find("Item/Properties/string[@name='Value']")
        assert evidence is not None and 'placement=C' in evidence.text
    parts = [v for v in north.iter("Item") if v.attrib['class'] in ('Part', 'WedgePart', 'Seat')]
    for item in parts:
        if name(item) == 'LevelSign':
            assert item.find("Properties/bool[@name='CanCollide']").text == 'false', \
                'Level signs must not obstruct the inherited stair exits'
    assert len(parts) <= 1400, f"North budget exceeded: {len(parts)}"
    roof_area = 0
    for item in parts:
        if name(item) == 'ModularRoof':
            size = item.find("Properties/Vector3[@name='size']")
            roof_area += float(size.find('X').text) * float(size.find('Z').text)
    assert abs(roof_area - (180*130 - 42*62)) < .01, 'Unexpected roof opening outside the intended atrium'
    assert not any(v.attrib['class'] in ('Script', 'LocalScript', 'ModuleScript') for v in north.iter('Item'))
    old_items = old_campus.findall('Item')
    start = next(i for i, v in enumerate(old_items) if name(v) == 'GroundFloor'
                 and v.find("Properties/CoordinateFrame[@name='CFrame']/Z").text == '195.0000')
    new_items = campus.findall('Item')
    idx = new_items.index(north)
    expected_campus = with_bridge_opening(old_items[:start])
    assert idx == len(expected_campus), 'North call moved relative to existing campus content'
    assert [signature(v) for v in new_items[:idx]] == [signature(v) for v in expected_campus], \
        'Campus changed beyond the specified south bridge opening'
    assert idx == len(new_items)-1, 'Unexpected campus content appended after north'
    other = [signature(v) for v in root.findall('Item') if name(v) != 'Campus']
    old_other = [signature(v) for v in old.findall('Item') if name(v) != 'Campus']
    assert other == old_other, 'Another world, collectible, or gameplay root changed'
    for prefix in ('Portal|', 'Collect|', 'Checkpoint_'):
        def markers(m):
            return sorted((name(v), signature(v)) for v in m.iter('Item') if name(v).startswith(prefix))
        assert markers(root) == markers(old), f'{prefix} markers changed'
    old_parts = sum(v.attrib['class'] in ('Part', 'WedgePart', 'Seat') for v in old_items[start:])
    delta = len(parts)-old_parts
    assert delta <= 800, f'Net north part increase exceeded 800: {delta}'
    print(f'PASS: north {len(parts)} parts; previous {old_parts}; net {delta:+d}; '
          'south bridge opening only; garden/other worlds/portals/collectibles/checkpoints unchanged.')


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--map', type=Path, default=Path('kuwait-parkour/src/map/Map.rbxmx'))
    parser.add_argument('--baseline', type=Path, required=True)
    args = parser.parse_args()
    validate(args.map, args.baseline)

"""
Dataset audit script for OCT classification suitability.
"""

from collections import Counter, defaultdict
from pathlib import Path


IMAGE_EXTENSIONS = {".jpg", ".jpeg", ".png", ".bmp", ".tif", ".tiff"}
REPORT_KEYWORDS = ("octreport", "report", "radial")


def collect_images(data_path="Krishnendu PCV"):
    root = Path(data_path)
    images = [p for p in root.rglob("*") if p.is_file() and p.suffix.lower() in IMAGE_EXTENSIONS]
    return root, images


def audit_dataset(data_path="Krishnendu PCV"):
    root, images = collect_images(data_path)
    if not root.exists():
        raise FileNotFoundError(f"Dataset folder not found: {root}")

    class_counts = Counter()
    duplicate_name_map = defaultdict(set)
    report_images = []

    for image_path in images:
        class_name = image_path.parent.name
        class_counts[class_name] += 1
        duplicate_name_map[image_path.name].add(class_name)
        lower_name = image_path.name.lower()
        if any(keyword in lower_name for keyword in REPORT_KEYWORDS):
            report_images.append(image_path)

    duplicate_names = {
        name: sorted(classes)
        for name, classes in duplicate_name_map.items()
        if len(classes) > 1
    }

    return {
        "root": root,
        "total_images": len(images),
        "class_counts": dict(sorted(class_counts.items())),
        "duplicate_names": duplicate_names,
        "report_images": report_images,
    }


def print_audit(report):
    print("=" * 60)
    print("OCT DATASET AUDIT")
    print("=" * 60)
    print(f"Dataset: {report['root']}")
    print(f"Total images: {report['total_images']}")
    print(f"Classes: {len(report['class_counts'])}")
    print()

    print("Class counts:")
    for class_name, count in report["class_counts"].items():
        print(f"  {class_name}: {count}")

    print()
    print(f"Cross-class duplicate filenames: {len(report['duplicate_names'])}")
    for index, (name, classes) in enumerate(sorted(report["duplicate_names"].items())[:20], start=1):
        print(f"  {index:02d}. {name} -> {', '.join(classes)}")

    if len(report["duplicate_names"]) > 20:
        print(f"  ... and {len(report['duplicate_names']) - 20} more")

    print()
    print(f"Report-like images: {len(report['report_images'])}")
    for image_path in report["report_images"][:10]:
        print(f"  - {image_path.relative_to(report['root'])}")

    if len(report["report_images"]) > 10:
        print(f"  ... and {len(report['report_images']) - 10} more")

    print()
    if report["duplicate_names"]:
        print("Verdict: not suitable for single-label classification as-is.")
        print("Reason: the same image names appear in multiple class folders.")
    elif report["report_images"]:
        print("Verdict: partially suitable, but report-page images should be removed first.")
    else:
        print("Verdict: dataset structure looks suitable for single-label classification.")
    print("=" * 60)


def main():
    report = audit_dataset()
    print_audit(report)


if __name__ == "__main__":
    main()

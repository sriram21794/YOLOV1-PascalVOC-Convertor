import os
import shutil
import traceback

import click
from pascal_voc_writer import Writer
from skimage.io import imread


def yolov1_to_pascal_voc(source_file, destination_file, image_file):
    with open(source_file) as fp:
        source_lines = [line.strip() for line in fp.readlines()]

    # if len(source_lines) % 2 != 0:
    #     raise Exception("yolov1 representation error in {}".format(source_file))

    image_data = imread(image_file)
    height, width, dummy_ = image_data.shape

    writer = Writer(image_file, width, height)

    for label, bbox in zip(source_lines[::2], source_lines[1::2]):
        xmin, ymin, xmax, ymax = bbox.split(" ")
        writer.addObject(label, xmin, ymin, xmax, ymax)

    writer.save(destination_file)


@click.command()
@click.option('--yolov1_labels_dir', '-y', help='Directory where yolo v1 annotation labels are present.', required=True)
@click.option('--pascal_voc_labels_dir', '-p',
              help='Destination Directory where pascal voc annotation labels should be present.', required=True)
@click.option('--images_dir', '-i', help='Destination Directory where images are present.', required=True)
def convert(yolov1_labels_dir, pascal_voc_labels_dir, images_dir):
    if not os.path.exists(yolov1_labels_dir):
        raise RuntimeError(" yolov1_labels_dir={} doesn't exist.".format(yolov1_labels_dir))

    if os.path.exists(pascal_voc_labels_dir):
        raise RuntimeError(" pascal_voc_labels_dir={} exist.".format(pascal_voc_labels_dir))

    if yolov1_labels_dir[-1] != os.sep:
        yolov1_labels_dir += os.sep

    # TODO: Modify the logic w/o copying the entire directory
    shutil.copytree(yolov1_labels_dir, pascal_voc_labels_dir)

    try:
        for root, directories, filenames in os.walk(yolov1_labels_dir):
            for filename in filenames:
                source_file = os.path.join(root, filename)
                destination_annotation_file = os.path.join(pascal_voc_labels_dir, root[len(yolov1_labels_dir):],
                                                           filename)
                source_image_file = os.path.join(images_dir, root[len(yolov1_labels_dir):],
                                                 filename.replace("txt", "jpeg"))

                yolov1_to_pascal_voc(source_file, destination_annotation_file, source_image_file)
                os.rename(destination_annotation_file, destination_annotation_file.replace("txt", "xml"))
    except Exception as e:
        traceback.print_exc()
        print "Error While converting the annotation. Removing the directory"
        shutil.rmtree(pascal_voc_labels_dir)


if __name__ == "__main__":
    convert()

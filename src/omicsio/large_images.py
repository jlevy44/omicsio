import PIL.Image
import datasets

PIL.Image.MAX_IMAGE_PIXELS = 11140240175

def crop_large_image_for_slide(slide: datasets.Slide, output_image_path: str, downsample=1):
    import tifffile
    
    # Crop the image to the area of the tissue
    xmin, xmax, ymin, ymax = slide.spot_locations.image_x.min(), slide.spot_locations.image_x.max(), slide.spot_locations.image_y.min(), slide.spot_locations.image_y.max()
    xmin = int(xmin)
    xmax = int(xmax)
    ymin = int(ymin)
    ymax = int(ymax)

    width = xmax - xmin
    height = ymax - ymin

    print('Cropping image to', xmin, xmax, ymin, ymax, 'and adding 1024 pixels of padding')
    print('New image size will be', xmax - xmin + 2048, 'x', ymax - ymin + 2048)

    if slide.image_path.endswith('.svs'):
        image = PIL.Image.fromarray(tifffile.imread(slide.image_path)[:, :, :3])
    else:
        image = PIL.Image.open(slide.image_path)
    
    image \
        .crop((max(xmin - 1024, 0), max(ymin - 1024, 0), min(xmax + 1024, image.width), min(ymax + 1024, image.height))) \
        .save(output_image_path)

    # Adjust so (xmin - 1024, ymin - 1024) is at (0, 0)
    cropped_image_x = slide.spot_locations.image_x - (xmin - 1024)
    cropped_image_y = slide.spot_locations.image_y - (ymin - 1024)

    slide_cropped = datasets.Slide(
        image_path=output_image_path,
        spot_locations=datasets.SpotLocations(cropped_image_x, cropped_image_y, slide.spot_locations.row, slide.spot_locations.col, slide.spot_locations.dia),
        spot_counts=slide.spot_counts,
        genes=slide.genes,
    )

    return slide_cropped

    # slide_cropped.save(f'input_data/preprocessed/{slide_name}_cropped.pkl')

def downsample_image(slide_name: str, downsample: int):
    import numpy as np

    slide = datasets.Slide.load(f'input_data/preprocessed/{slide_name}.pkl')
    
    downsampled = np.array(PIL.Image.open(slide.image_path))[::2, ::2, :]
    PIL.Image.fromarray(downsampled).save(f'input_data/preprocessed/{slide_name}_downsampled_by_{downsample}.tif')

    # PIL.Image.open(slide.image_path) \
    #     .resize((slide.image.shape[1] // downsample, slide.image.shape[0] // downsample)) \
    #     .save(f'input_data/preprocessed/{slide_name}_downsampled_by_{downsample}.tif')

    downsampled_image_x = slide.spot_locations.image_x // downsample
    downsampled_image_y = slide.spot_locations.image_y // downsample

    slide_downsampled = datasets.Slide(
        image_path=f'input_data/preprocessed/{slide_name}_downsampled_by_{downsample}.tif',
        spot_locations=datasets.SpotLocations(downsampled_image_x, downsampled_image_y, slide.spot_locations.row, slide.spot_locations.col, slide.spot_locations.dia),
        spot_counts=slide.spot_counts,
        genes=slide.genes,
    )

    slide_downsampled.save(f'input_data/preprocessed/{slide_name}_downsampled_by_{downsample}.pkl')

if __name__ == '__main__':
    crop_large_image_for_slide(
        datasets.Slide.load(f'input_data/preprocessed/autostainer_40x.pkl'),
        f'input_data/preprocessed/autostainer_40x_cropped.tif'
    ).save(f'input_data/preprocessed/autostainer_40x_cropped.pkl')
    downsample_image('autostainer_40x_cropped', 2)

# This code is to convert some heif encoded image to a normal image
# HEIF images cannot be opened by the Windows Photo, so I write this little code to convert it into normal photos so I can organize them.
from PIL import Image
import pillow_heif
import os
from tqdm import tqdm

debug = False

pillow_heif.options.DISABLE_SECURITY_LIMITS = True

def process_img(file):
    # 1) Read the HEIC file (automatically decodes via libheif)
    heif_file = pillow_heif.read_heif(file)

    # 2) Build a PIL Image from the decoded data
    image = Image.frombytes(
        heif_file.mode,       # e.g. "RGB"
        heif_file.size,       # (width, height)
        heif_file.data,       # raw bytes
        "raw",
    )
    if debug:
        print(heif_file.info)
        
        if "exif" not in heif_file.info.keys():
            print(file)
            exit(0)
        print(heif_file.info['exif'])
    # 3) Save out as a “normal” JPEG
    image.save(f"output/{file}", format="JPEG", exif=heif_file.info['exif'] if heif_file.info['exif'] is not None else b'')
    
if __name__ == "__main__":
    files = [file for file in os.listdir() if file.endswith(".jpg")]
    os.makedirs("output", exist_ok=True)
    print(files[0])
    for file in tqdm(files, desc="Processing imgs..."):
        try:
            process_img(file)
        except:
            print(file)
            continue

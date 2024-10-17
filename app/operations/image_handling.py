from PIL import Image
from fastapi import HTTPException
import cv2
import numpy as np
from pathlib import Path
from app.operations.file_handling import get_admin_path
from io import BytesIO
from datetime import datetime


def convert_to_png(image, file_name: str, type_: str = None) -> dict:
    file_name_ = file_name.split(".")[0]
    date_val = datetime.now().isoformat().replace(":", 'H', 1).replace(':', 'M', 1)
    try:
        image = Image.open(BytesIO(image))
        print(image.size)
        image_uploaded_path = Path(get_admin_path()) / ".fastAPI_DATA" / "uploaded" / file_name
        if type_ is not None:
            file_name_ += type_
        image_updated_path = (Path(get_admin_path()) / ".fastAPI_DATA"
                              / "updated" / f"{file_name_}_{date_val}.png")
        image.save(image_uploaded_path)
        image.save(image_updated_path, format="PNG")

        return {"status": True, "image_name": f"{file_name_}_{date_val}", "image_path": image_updated_path,
                "uploaded_image_path": image_uploaded_path}

    except Exception as e:
        raise HTTPException(status_code=500, detail="Could not able to convert the image to PNG" + e.message)


async def image_to_svg_conversion(image_path: str, image_name: str) -> dict:
    image_output_path = Path(get_admin_path()) / ".fastAPI_DATA" / "recreated"
    image_output_file_name = image_name + ".svg"

    try:
        img = cv2.imread(image_path)
        # Convert to grayscale
        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        # Apply thresholding to convert to binary image
        _, thresh = cv2.threshold(gray, 127, 255, cv2.THRESH_BINARY)
        # Find contours (edges) in the image
        contours, _ = cv2.findContours(thresh, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
        # Create an empty canvas for SVG paths
        height, width = img.shape[:2]
        svg_data = f'<svg height="{height}" width="{width}" xmlns="http://www.w3.org/2000/svg">\n'
        # Convert contours to SVG path data
        for contour in contours:
            path = "M " + " L ".join([f"{pt[0][0]} {pt[0][1]}" for pt in contour]) + " Z"

            # Get the color at the first point of the contour (as an approximation)
            x, y = contour[0][0]
            color_bgr = img[y, x]  # BGR format
            color_hex = "#{:02x}{:02x}{:02x}".format(int(color_bgr[2]), int(color_bgr[1]),
                                                     int(color_bgr[0]))  # Convert to hex

            # Add path to SVG with the corresponding fill color
            svg_data += f'<path d="{path}" fill="{color_hex}" stroke="black" />\n'

        svg_data += '</svg>'
        output_path = image_output_path / image_output_file_name
        # Save to the specified path
        with open(output_path, "w") as f:
            f.write(svg_data)
        return {"status": True, "message": "Convertion is successful", "SVG_path": output_path}

    except Exception as e:
        print(f"Error: {str(e)}")
        raise HTTPException(status_code=500, detail={"status": False, "message": e})

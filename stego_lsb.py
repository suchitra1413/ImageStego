from PIL import Image

DELIMITER = b'\x00\x00\x00\x00'

def hide_bytes(image_path, data: bytes, output_path):
    if isinstance(data, str):
        data = data.encode()

    img = Image.open(image_path).convert("RGB")
    pixels = img.load()

    payload = data + DELIMITER
    bits = ''.join(f'{byte:08b}' for byte in payload)

    idx = 0
    total_pixels = img.width * img.height

    if len(bits) > total_pixels * 3:
        raise ValueError("Data too large for image")

    for y in range(img.height):
        for x in range(img.width):
            if idx >= len(bits):
                break

            r, g, b = pixels[x, y]

            if idx < len(bits):
                r = (r & ~1) | int(bits[idx]); idx += 1
            if idx < len(bits):
                g = (g & ~1) | int(bits[idx]); idx += 1
            if idx < len(bits):
                b = (b & ~1) | int(bits[idx]); idx += 1

            pixels[x, y] = (r, g, b)

    img.save(output_path)


def extract_bytes(image_path):
    img = Image.open(image_path).convert("RGB")
    pixels = img.load()

    bits = ""

    for y in range(img.height):
        for x in range(img.width):
            r, g, b = pixels[x, y]
            bits += str(r & 1) + str(g & 1) + str(b & 1)

    data = bytearray()

    for i in range(0, len(bits), 8):
        byte = bits[i:i+8]
        if len(byte) < 8:
            break

        data.append(int(byte, 2))

        if data[-4:] == DELIMITER:
            break

    return bytes(data[:-4])
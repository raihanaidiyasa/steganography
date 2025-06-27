from PIL import Image
import os

def text_to_binary(text):
    """Mengubah string teks menjadi string biner."""
    return ''.join(format(ord(char), '08b') for char in text)

def encode_image(image_path, secret_text, output_filename):
    """Menyembunyikan teks rahasia di dalam gambar dan menyimpannya."""
    try:
        image = Image.open(image_path)
    except FileNotFoundError:
        return None, "Error: File gambar tidak ditemukan."

    delimiter = "$$$END$$$"
    text_to_hide = secret_text + delimiter
    binary_secret_text = text_to_binary(text_to_hide)
    
    image_capacity = image.width * image.height * 3
    if len(binary_secret_text) > image_capacity:
        return None, "Error: Teks terlalu panjang untuk disembunyikan."

    new_image = image.copy()
    pixels = new_image.load()
    data_index = 0
    
    for y in range(new_image.height):
        for x in range(new_image.width):
            r, g, b = pixels[x, y][:3]

            if data_index < len(binary_secret_text):
                r_bin = list(format(r, '08b'))
                r_bin[-1] = binary_secret_text[data_index]
                r = int("".join(r_bin), 2)
                data_index += 1
            
            if data_index < len(binary_secret_text):
                g_bin = list(format(g, '08b'))
                g_bin[-1] = binary_secret_text[data_index]
                g = int("".join(g_bin), 2)
                data_index += 1

            if data_index < len(binary_secret_text):
                b_bin = list(format(b, '08b'))
                b_bin[-1] = binary_secret_text[data_index]
                b = int("".join(b_bin), 2)
                data_index += 1
            
            pixels[x, y] = (r, g, b)

            if data_index >= len(binary_secret_text):
                break
        if data_index >= len(binary_secret_text):
            break

    # Pastikan direktori output ada
    output_dir = "downloads"
    os.makedirs(output_dir, exist_ok=True)
    output_path = os.path.join(output_dir, output_filename)
    
    new_image.save(output_path, "PNG")
    return output_filename, "Encoding berhasil."

def decode_image(image_path):
    """Mengekstrak teks rahasia dari sebuah gambar."""
    try:
        image = Image.open(image_path)
    except FileNotFoundError:
        return "Error: File gambar tidak ditemukan."

    pixels = image.load()
    binary_data = ""
    delimiter = "$$$END$$$"
    
    for y in range(image.height):
        for x in range(image.width):
            r, g, b = pixels[x, y][:3]
            binary_data += format(r, '08b')[-1]
            binary_data += format(g, '08b')[-1]
            binary_data += format(b, '08b')[-1]

    all_bytes = [binary_data[i: i+8] for i in range(0, len(binary_data), 8)]
    
    decoded_text = ""
    for byte in all_bytes:
        if len(byte) == 8:
            decoded_text += chr(int(byte, 2))
            if decoded_text.endswith(delimiter):
                return decoded_text[:-len(delimiter)]
    
    return "Delimiter tidak ditemukan. Mungkin tidak ada pesan tersembunyi."
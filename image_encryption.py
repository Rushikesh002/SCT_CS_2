from PIL import Image
import numpy as np
import sys
import os


def load_image(path):
    img = Image.open(path).convert("RGBA")
    return img, np.array(img, dtype=np.uint8)


def save_image(arr, path):
    Image.fromarray(arr, mode="RGBA").save(path)
    print(f"Saved: {path}")


def xor_cipher(arr, key, mode=None):
    result = arr.copy()
    result[..., :3] ^= key
    return result


def add_cipher(arr, key, mode="encrypt"):
    result = arr.copy()
    k = key if mode == "encrypt" else (256 - key) % 256
    result[..., :3] = (arr[..., :3].astype(int) + k) % 256
    return result


def invert_pixels(arr, key=None, mode=None):
    result = arr.copy()
    result[..., :3] = 255 - arr[..., :3]
    return result


def swap_rb_channels(arr, key=None, mode=None):
    result = arr.copy()
    result[..., 0] = arr[..., 2]
    result[..., 2] = arr[..., 0]
    return result


def swap_rows(arr, key, mode="encrypt"):
    h = arr.shape[0]
    shift = key % h if mode == "encrypt" else (h - key % h) % h
    return np.roll(arr, shift, axis=0)


def bit_shift(arr, key, mode="encrypt"):
    result = arr.copy()
    s = key % 8
    ch = arr[..., :3].astype(np.uint16)
    if mode == "encrypt":
        shifted = ((ch << s) | (ch >> (8 - s))) & 0xFF
    else:
        shifted = ((ch >> s) | (ch << (8 - s))) & 0xFF
    result[..., :3] = shifted.astype(np.uint8)
    return result


OPERATIONS = {
    "1": ("XOR with key (symmetric)", xor_cipher),
    "2": ("Add key (mod 256)", add_cipher),
    "3": ("Invert pixels", invert_pixels),
    "4": ("Swap R <-> B channels", swap_rb_channels),
    "5": ("Swap pixel rows", swap_rows),
    "6": ("Bit-shift channels", bit_shift),
}

NEEDS_KEY = {"1", "2", "5", "6"}
NEEDS_MODE = {"2", "5", "6"}


def get_output_path(input_path, mode, op_name):
    base, ext = os.path.splitext(input_path)
    tag = "encrypted" if mode == "encrypt" else "decrypted"
    op_tag = op_name.split()[0].lower()
    return f"{base}_{tag}_{op_tag}.png"


def main():
    print("=" * 45)
    print("      Image Encryption Tool")
    print("=" * 45)

    while True:
        print("\nOperations:")
        for k, (name, _) in OPERATIONS.items():
            print(f"  {k}. {name}")
        print("  0. Exit")

        choice = input("\nChoose operation (0-6): ").strip()
        if choice == "0":
            print("Goodbye!")
            break
        if choice not in OPERATIONS:
            print("Invalid choice.")
            continue

        op_name, op_fn = OPERATIONS[choice]

        image_path = input("Image path: ").strip().strip('"').strip("'")
        if not os.path.isfile(image_path):
            print(f"File not found: {image_path}")
            continue

        mode = "encrypt"
        if choice in NEEDS_MODE:
            m = input("Mode — (e)ncrypt / (d)ecrypt [default: e]: ").strip().lower()
            mode = "decrypt" if m.startswith("d") else "encrypt"

        key = 42
        if choice in NEEDS_KEY:
            try:
                key = int(input("Key (0-255): ").strip())
                key = max(0, min(255, key))
            except ValueError:
                print("Invalid key, using 42.")
                key = 42

        try:
            img, arr = load_image(image_path)
            print(f"Loaded {img.width}x{img.height} image...")
        except Exception as e:
            print(f"Could not open image: {e}")
            continue

        result = op_fn(arr, key, mode)

        out_path = get_output_path(image_path, mode, op_name)
        save_image(result, out_path)
        print(f"Operation : {op_name}")
        print(f"Mode      : {mode}")
        if choice in NEEDS_KEY:
            print(f"Key       : {key}")
        print(f"Output    : {out_path}")


if __name__ == "__main__":
    main()

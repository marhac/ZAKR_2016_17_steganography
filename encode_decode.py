import sys
from PIL import Image


def decode_image(img):
    """
    check the red portion of an image (r, g, b) tuple for
    hidden message characters (ASCII values)
    """
    width, height = img.size
    msg = ""
    check = ""
    nbits = 0
    index = 0
    if img.mode != 'RGB':
        img = img.convert(mode="RGB")
    # For each and every pixel, decode a header or message character.
    for row in range(height):
        for col in range(width):
            r, g, b = img.getpixel((col, row)) # Go get the pixel's RGB values at a certain location

            if row == 0 and col < 3:
                check += chr(r)  # begin collecting the header
            elif row == 0 and col == 3:
                if check != "stg":
                    print("No message header!")
                    return False, "Error"
                nbits = int(chr(r))  # collect our mask
                check = ""
            elif row == 0 and 3 < col < 8:  # collect the length of the message
                check += chr(r)
            elif row == 0 and col == 8:
                length = int(check)
                msg += chr(r^nbits) # xor output
                index += 1
            elif index < length:  # collect the message
                msg += chr(r^nbits) # xor output
                index += 1
    print("({}, {})".format(width, height))
    return True, msg

    #Helper function to determine capacity of an image.
def capacity(x, y, bites):
    return (3 * (x * y) * bites) / 8

def encode_image(img, output_path, msg, nbits):
    """
    use the red portion of an image (r, g, b) tuple to
    hide the msg string characters as ASCII values
    red value of the first pixel is used for length of string
    """
    msglen = len(msg)
    header = "stg" + str(nbits) + str(len(msg)).zfill(4)  # create the header string
    print("header:", header)
    msg = header + msg  # combine the header and the message
    length = len(msg)
    width, height = img.size
    v = ((width * height) * 3 * nbits) // 8
    # limit length of message to 255
    if length > v:
        print("text too long! (don't exceed {} characters)".format(v))
        return False
    if img.mode != 'RGB':
        img = img.convert(mode="RGB")  # convert to rgb
    # use a copy of image to hide the text in
    encoded = img.copy()
    width, height = img.size # Grab height and width of image.
    index = 0
    xorstring = ""
    for row in range(height):
        for col in range(width):
            r, g, b = img.getpixel((col, row)) # Get pixel's RGB values

            if index < 8: # header and bit
                c = msg[index]
                asc = ord(c)
                xorstring += chr(asc) # Save record for key output.            
            elif index < length: # message
                c = msg[index]
                asc = ord(c)^nbits # xor input
                xorstring += chr(asc) # Save record for key output. 
            else: # excess 
                asc = r
            encoded.putpixel((col, row), (asc, g, b))  # Encode the encrypted character in the red pixel.
            index += 1
    # Save image once done encoding.
    encoded.save(output_path)
    # Print output information for post encode.
    print("({}, {}) {}".format(width, height, img.mode))
    print(capacity(int(width), int(height), int(nbits)) - 8, " byte for " + str(nbits) + "bit")
    print("Mask: {}".format(nbits))
    print("XOR Key: {}".format(xorstring))
    return True


def help():
    print("ERROR: wrong parameters")
    print("--------------------------------")
    print("Hide text to image:")
    print("Steganography -e number input.bmp output.bmp text.txt\n")
    print("Load hidden text from image")
    print("Steganography -d input.bmp text.txt\n")

if len(sys.argv) == 6 and sys.argv[1] == '-t':  # encode
    print("Test begin...")
    used_bite = sys.argv[2]
    input_image_path = sys.argv[3]
    output_image_path = sys.argv[4]
    input_text_path = sys.argv[5]
    test(input_image_path, output_image_path, input_text_path, used_bite)
    print("Done and saved to:{}".format(output_image_path))
elif len(sys.argv) == 6 and sys.argv[1] == '-e':  # encode
    print("Begin.....")
    used_bite = int(sys.argv[2])
    input_image_path = sys.argv[3]
    output_image_path = sys.argv[4]
    input_text_path = sys.argv[5]
    img = Image.open(input_image_path)
    if used_bite > 0 and used_bite <= 6:
        with open(input_text_path) as f:
            text = f.read()
        if encode_image(img, output_image_path, text, used_bite):
            print("Done and saved to: {}".format(output_image_path))
    else:
        print("You must enter 1-6 number of bits. Exiting...")

elif len(sys.argv) == 4 and sys.argv[1] == '-d':  # decode
    input_image_path = sys.argv[2]
    output_text_path = sys.argv[3]
    img = Image.open(input_image_path)

    success, text = decode_image(img)

    if success:
        f = open(output_text_path, 'w') # Open file
        f.write(text) # Write text file
        f.close()
        print("Done and text saved to: {}".format(output_text_path))
else:
    help()
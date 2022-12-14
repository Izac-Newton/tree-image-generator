from PIL import Image
from concurrent.futures import ProcessPoolExecutor
from concurrent.futures import ThreadPoolExecutor
import requests
import io
import json
import os
import shutil
import math
import sys

OUTPUT_IMAGE_SIZE = 1800
ORNAMENT_IMAGE_SIZE = int(OUTPUT_IMAGE_SIZE / 4)
OUTPUT_DIRECTORY_PATH = "outputs/"
IMMEDIATE_DIRECTORY_PATH = "immediate/"


def main():
    if os.path.exists(OUTPUT_DIRECTORY_PATH):
        shutil.rmtree(OUTPUT_DIRECTORY_PATH)
    os.mkdir(OUTPUT_DIRECTORY_PATH)

    if os.path.exists(IMMEDIATE_DIRECTORY_PATH):
        shutil.rmtree(IMMEDIATE_DIRECTORY_PATH)
    os.mkdir(IMMEDIATE_DIRECTORY_PATH)

    args = sys.argv

    if 2 > len(args):
        print("Arguments are too short.", file=sys.stderr)
        sys.exit(1)

    input_json = args[1]

    if not os.path.exists(input_json):
        print("Error: " + input_json + " is not found.", file=sys.stderr)
        sys.exit(1)

    if not input_json.endswith(".json"):
        print("Error: " + input_json + " is not json file.", file=sys.stderr)
        sys.exit(1)

    with open(input_json, "r", encoding="utf-8") as json_open:
        json_load = json.load(json_open)

    block_count = GenerateOrnamentBlockImageFromJson(json_load)

    GenerateOrnamentGroupImageImpl(
        CalculateStepNumber(block_count), 1, OUTPUT_DIRECTORY_PATH + "tree.png"
    )
    return


def GenerateOrnamentImage(json_data, index, image_count_max, image_size):
    if index >= image_count_max:
        return Image.new("RGBA", (image_size, image_size), (255, 255, 255, 0))
    url = json_data[index]["url"]
    try:
        with Image.open(io.BytesIO(requests.get(url).content)) as src:
            base_size = max(src.width, src.height)
            base = Image.new("RGBA", (base_size, base_size), (255, 255, 255, 0))
            base.paste(
                src,
                (
                    int((base.width - src.width) / 2),
                    int((base.height - src.height) / 2),
                ),
            )
            return base.resize((image_size, image_size))
    except:
        return Image.new("RGBA", (image_size, image_size), (255, 255, 255, 0))


def GenerateOrnamentBlockImage(block, json_data, image_count_max, block_size):
    pos1 = 0
    pos2 = int(block_size / 4)
    pos3 = int(block_size / 2)
    pos4 = pos2 + pos3
    bg = Image.new("RGBA", (block_size, block_size), (255, 255, 255, 0))
    executor = ThreadPoolExecutor()
    img_src = []
    with ThreadPoolExecutor() as executor:
        for place in range(8):
            img_src.append(
                executor.submit(
                    GenerateOrnamentImage,
                    json_data,
                    block * 8 + place,
                    image_count_max,
                    int(block_size / 4),
                )
            )
    bg.paste(img_src[0].result(), (pos1, pos1))
    bg.paste(img_src[1].result(), (pos3, pos1))
    bg.paste(img_src[2].result(), (pos2, pos2))
    bg.paste(img_src[3].result(), (pos4, pos2))
    bg.paste(img_src[4].result(), (pos1, pos3))
    bg.paste(img_src[5].result(), (pos3, pos3))
    bg.paste(img_src[6].result(), (pos2, pos4))
    bg.paste(img_src[7].result(), (pos4, pos4))
    bg.save(IMMEDIATE_DIRECTORY_PATH + "/1-" + str(block + 1) + ".png")
    return


def GenerateOrnamentBlockImageFromJson(json_data):
    image_count = int(json_data["info"]["count"])
    block_count = math.ceil(image_count / 8)
    step_number = CalculateStepNumber(block_count)
    block_size = int(OUTPUT_IMAGE_SIZE / (step_number + 1))
    tweet_data = json_data["tweets"]

    for block in range(block_count):
        GenerateOrnamentBlockImage(block, tweet_data, image_count, block_size)

    return block_count


def CalculateStepNumber(block_number):
    step = 1
    while block_number > step:
        block_number -= step
        step += 1
    return step


def CalculateLowerLeftBlockNumber(base_block_number, count):
    for i in range(count):
        base_block_number += CalculateStepNumber(base_block_number)
    return base_block_number


def GetBlockNumberList(
    base_block_number, step_number, index_number, block_count, step_count
):
    ret = []
    for i in range(block_count):
        ret.append(base_block_number + i)
    if block_count != step_count:
        base_block_number = CalculateLowerLeftBlockNumber(base_block_number, 1)
        step_number += 1
        block_count += 1
        ret += GetBlockNumberList(
            base_block_number, step_number, index_number, block_count, step_count
        )
        return ret
    else:
        return ret


def CalculateOrnamentGroup(step, base_block):
    ret = [(step, base_block)]
    if step == 1 or step == 2 or step == 3:
        pass
    elif step % 4 == 0:
        next_step = int(step / 2)
        delta = int(step / 4)
        a = CalculateLowerLeftBlockNumber(base_block, int(step / 4))
        b = CalculateLowerLeftBlockNumber(base_block, int(step / 2))
        ret += CalculateOrnamentGroup(next_step, base_block)
        ret += CalculateOrnamentGroup(next_step, a)
        ret += CalculateOrnamentGroup(next_step, a + delta)
        ret += CalculateOrnamentGroup(next_step, b)
        ret += CalculateOrnamentGroup(next_step, b + delta)
        ret += CalculateOrnamentGroup(next_step, b + delta * 2)
    elif step % 3 == 0:
        next_step = int(step / 3 * 2)
        a = CalculateLowerLeftBlockNumber(base_block, int(step / 3))
        ret += CalculateOrnamentGroup(next_step, base_block)
        ret += CalculateOrnamentGroup(next_step, a)
        ret += CalculateOrnamentGroup(next_step, a + int(step / 3))
    elif step % 2 == 0:
        next_step = int(step * 0.66)
        delta = int((step - next_step) / 2)
        a = CalculateLowerLeftBlockNumber(base_block, step - next_step)
        b = CalculateLowerLeftBlockNumber(base_block, int((step - next_step) / 2))
        ret += CalculateOrnamentGroup(next_step, base_block)
        ret += CalculateOrnamentGroup(next_step, a)
        ret += CalculateOrnamentGroup(next_step, a + delta)
        ret += CalculateOrnamentGroup(next_step, b)
        ret += CalculateOrnamentGroup(next_step, b + delta)
        ret += CalculateOrnamentGroup(next_step, b + delta * 2)
    else:
        next_step = round(step / 3 * 2)
        delta = step - next_step
        a = CalculateLowerLeftBlockNumber(base_block, delta)
        ret += CalculateOrnamentGroup(next_step, base_block)
        ret += CalculateOrnamentGroup(next_step, a)
        ret += CalculateOrnamentGroup(next_step, a + delta)
    return ret


def GenerateOrnamentGroupImageImpl(step, base_block, file_name):
    image_size = int(OUTPUT_IMAGE_SIZE / (step + 1))
    bg = Image.new("RGBA", (OUTPUT_IMAGE_SIZE, OUTPUT_IMAGE_SIZE), (255, 255, 255, 0))
    for i in range(step):
        base_x = int(OUTPUT_IMAGE_SIZE / 2) - int(image_size / 2) * (i + 1)
        base_y = image_size * i + image_size
        current_block = base_block
        for j in range(i + 1):
            file_path = IMMEDIATE_DIRECTORY_PATH + "1-" + str(current_block) + ".png"
            if not os.path.exists(file_path):
                break
            img_src = Image.open(file_path)
            bg.paste(img_src, (base_x + image_size * j, base_y))
            current_block += 1
        base_block = CalculateLowerLeftBlockNumber(base_block, 1)
    bg.save(file_name)
    return


if __name__ == "__main__":
    main()

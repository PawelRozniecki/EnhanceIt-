import sys
sys.path.append('/EnhanceIt')
import torch
from PIL import Image
import numpy as np
import torchvision.transforms as transforms

from src.model import SRCNN
from src.constants import *

def main():
    torch.cuda.empty_cache()
    path = sys.argv[1]

    model = SRCNN()
    model.to(DEVICE)
    model.load_state_dict(torch.load(MODEL_SAVE_PATH,map_location='cpu'))

    model.eval()
    # image to resize
    # for file in os.listdir('/home/pawel/PycharmProjects/EnhanceIt/src/images/1'):

    input_image = Image.open(path)
    input_image = input_image.convert('YCbCr')
    input_image = input_image.resize((int(input_image.size[0]*UPSCALE_FACTOR), int(input_image.size[1]*UPSCALE_FACTOR)), Image.BICUBIC)
    bicubic = input_image.convert('RGB')
    bicubic.save('bicubic.png')

    y, cb, cr = input_image.split()

    input_tensor = transforms.ToTensor()
    input = input_tensor(y).view(1, -1, input_image.size[1], input_image.size[0])

    input = input.to(DEVICE)

    with torch.no_grad():
        torch.cuda.empty_cache()
        output = model(input).clamp(0.0,1.0)

    output = output.cpu()

    out_img_y = output[0].detach().numpy()
    out_img_y *= 255.0
    out_img_y = out_img_y.clip(0, 255)
    out_img_y = Image.fromarray(np.uint8(out_img_y[0]), mode='L')
    out_img = Image.merge('YCbCr', [out_img_y, cb, cr]).convert('RGB')
    out_img.save('output.png')

    print("saved sucesfully ")


main()
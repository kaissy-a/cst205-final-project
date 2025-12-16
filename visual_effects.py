"""
Person 3 deliverable: Create a dynamic background using PIL to analize the dominant colors from the user's image or album cover.
Notes:
- Get the image from another file
- Iterate over every pixel and add it to a dictionary
- If the pixel's color is already in the dictionary, increment its value
- Colors with the highest value are the most dominant
- Select the top few colors to use in dynamic background creation
"""
from PIL import Image, ImageDraw, ImageFilter
import random

def findDominantColor(image, sample: int):
    width, height = image.size
    colorDictionary = {
        (0,0,0) : 0
    }
    for x in range(width):
        for y in range(height):
            currentPixel = image.getpixel((x,y))
            if currentPixel in colorDictionary:
                colorDictionary[currentPixel] = colorDictionary[currentPixel] + 1
            else:
                colorDictionary.update({currentPixel : 1})
    #print(colorDictionary)
    colorList = colorDictionary.items()
    colorList = sorted(colorList, key=lambda item: item[1], reverse=True)
    finalList = []
    for i in range(sample):
        finalList.append(colorList[i])
    return finalList

def createBackground(colors, size, blur):
    backGround = Image.new("RGB", size)
    draw = ImageDraw.Draw(backGround)
    width, height = size
    for i in colors:
        r = random.randint(width // 3, width)   
        #creates circles for drawing. big funny
        x = random.randint(-r, width)
        #keep r negative to avoid empty range error
        #it also looks cooler that way B)
        y = random.randint(-r, height)
        draw.ellipse((x, y, x + r, y + r), fill=i[0])
        #thank you geeksforgeeks.org
    #now we add blur because otherwise it looks like poop
    backGround = backGround.filter(ImageFilter.GaussianBlur(blur))
    #thank you pillow documentation 
    return backGround

def createDynamicBackground(image, sample:int, size, blur:int, debug: bool):
    fullImage = createBackground(findDominantColor(image, sample), size, blur)
    coverW, coverH = image.size
    image.thumbnail((200,200))
    fullImage.paste(image, (100,100))
    if debug:
        fullImage.show()
    return fullImage

# you only need to use create dynamic background method, others are not needed
# what does "create dynamic background" need?
# image - the image u want to sample from (use the album cover)
# sample - the amount of pixels to sample. 1200 is what I like to use
# size - size of the produced image. stick to 400 x 400
# blur - self explanitory. 120 is what I like to use
# debug - keep false

# example I used during debugging:
# image = Image.open("inrainbows.jpg")
# createDynamicBackground(image, 1200, (400,400), 100, True)

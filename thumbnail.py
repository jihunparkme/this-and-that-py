import os
from PIL import Image

# Changing the working path
path = input("input working path : ") + '/'
os.chdir(path)
os.getcwd()

# image size conversion
thumb = input("input thumb name : ")
if thumb in os.listdir(path) :
    image = Image.open(thumb)

    placehold_image = image.resize((230, 129))
    thumb_image = image.resize((535, 301))
    thumb2x_image = image.resize((1070, 602))

    filename, fileExtension = os.path.splitext(thumb)

    if fileExtension == '.jpg':
        placehold_image.save(path + thumb + '_placehold.jpg', quality=95)
        thumb_image.save(path + thumb + '_thumb.jpg', quality=95)
        thumb2x_image.save(path + thumb + '_thumb@2x.jpg', quality=95)
    else:
        placehold_image.convert("RGB").save(path + thumb + '_placehold.jpg')
        thumb_image.convert("RGB").save(path + thumb + '_thumb.jpg')
        thumb2x_image.convert("RGB").save(path + thumb + '_thumb@2x.jpg')

else :
    print('Wrong Thumbnail name. Please check')


import os
from PIL import Image

os.chdir('C:\\Users\\qkrwl\\Desktop\\captcha\\')  # red_img 경로 지정
cur_path = os.getcwd()
file_list = os.listdir(cur_path)

for file_name in file_list:

    if '.png' in file_name:
        r = Image.open('C:\\Users\\qkrwl\\Desktop\\captcha\\' + file_name)

        for i in range(0, r.size[0]):  # x방향 탐색
            for j in range(0, r.size[1]):  # y방향 탐색
                rgb = r.getpixel((i, j))  # i,j 위치에서의 RGB 취득

        for i in range(0, r.size[0]):
            for j in range(0, r.size[1]):
                rgb = r.getpixel((i, j))
                if rgb[0] > 40 and rgb[1] > 40 and rgb[2] > 40:  # 회색
                    r.putpixel((i, j), (0, 0, 255))
                # elif (rgb[0] > 0 and rgb[0] < 20) and (rgb[1] > 0 and rgb[1] < 20) and (rgb[2] > 0 and rgb[2] < 20) :
                #     r.putpixel((i,j),(0, 0, 255))
                elif rgb[3] > 200:  # 검정
                    r.putpixel((i, j), (0, 0, 255))

        converted_path = cur_path + '\\converted'
        # background = Image.open(converted_path + '\\background.png')
        # background = background.resize((120, 40))
        #
        # image1_size = background.size
        # image2_size = r.size
        # new_image = Image.new('RGB',(image1_size[0], image1_size[1]), (250,250,250))
        # new_image.paste(background,(0,0))
        # new_image.paste(r,(0,0))

        r.save(converted_path + '\\' + str(file_name) + '_converted.png')
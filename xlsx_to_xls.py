import glob
import os.path
from tqdm import tqdm

files = glob.glob("*.xlsx")
print(files)
for file in tqdm(files):
    if not os.path.isdir(file):
        filename = os.path.splitext(file)
        try:
            os.rename(file, filename[0] + '.xls')
        except:
            print('fail to convert' + file)
            pass
        print(filename[0] + '.xls')

print('\n\n>> Conversion is complete.\n\n')
os.system('pause')
# pyinstaller --onefile  xlsx_to_xls.py
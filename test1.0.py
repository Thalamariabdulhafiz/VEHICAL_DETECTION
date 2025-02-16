import csv
import os.path
from datetime import datetime
import string
from ultralytics import YOLO
import cv2
import math
import cvzone
import easyocr

# class
clss1 = ['auto', 'mini bus', 'bus', 'car', 'motorcycle', 'tractor', 'mini truck', 'normal truck', 'heavy truck', 'container', 'van']
clss4 = ['8-16', '80-100', '250-700', '40-70', '4-15', '45-65', '70-105', '150-350', '300-600', '800-6000', '35-60']
clss2 = ['Plate']
clss3 = ['0', '1', '2', '3', '4', '5', '6', '7', '8', '9', 'A', 'B', 'C', 'D', 'E', 'F', 'G', 'H',
         'I', 'J', 'K', 'L', 'M', 'N', 'O', 'P', 'Q', 'R', 'S', 'T', 'U', 'V', 'W', 'X', 'Y', 'Z']

char_ = 'OIZJABGS'
int_ = '01234865'

dict_char_to_int = {'O': '0',
                    'I': '1',
                    'Z': '2',
                    'J': '3',
                    'A': '4',
                    'B': '8',
                    'G': '6',
                    'S': '5',
                    'g': '9',
                    '-': '-'}

dict_int_to_char = {'0': 'O',
                    '1': 'I',
                    '2': 'Z',
                    '3': 'J',
                    '4': 'A',
                    '8': 'B',
                    '6': 'G',
                    '5': 'S',
                    '-': '-'}


def data_check(csv_file_path, Lplate):
    with open(csv_file_path, 'r') as f:
        # Create a CSV reader object
        csv_reader = csv.reader(f)

        # Iterate through rows and check the specific column for the target data
        for row in csv_reader:
            if len(row) > 1 and row[2] == Lplate:
                return True  # Target data found in the specified column

    return False


def write_file(Lplate, veh_cls, veh_conf):
    csv_file_path = 'final_path.csv'
    field_names = ['Vehicle', 'Confidance', 'Number Plate', 'capacity', 'Threshold', 'Zone', 'Time']

    # Check if the file exists
    if not os.path.isfile(csv_file_path):
        # Get the current date and time

        # File doesn't exist, create and write the header
        with open(csv_file_path, 'w', newline='') as f:
            current_datetime = datetime.now()
            # Format the datetime as a string
            formatted_datetime = current_datetime.strftime("%Y-%m-%d %H:%M:%S")

            csv_writer1 = csv.DictWriter(f, fieldnames=field_names)
            # Write the header
            csv_writer1.writeheader()

            csv_writer2 = csv.writer(f)

            csv_writer2.writerow([clss1[veh_cls], veh_conf, Lplate, clss4[veh_cls], '1', 'Red', formatted_datetime])

    # Append data to the CSV file
    with open(csv_file_path, 'a', newline='') as f:
        current_datetime = datetime.now()
        if data_check(csv_file_path, Lplate):
            with open(csv_file_path, 'r') as f:
                # Create a CSV reader object
                csv_reader = csv.reader(f)
                data = list(csv_reader)
                # Iterate through rows and check the specific column for the target data
                for row_index, row in enumerate(data):
                    for column_index, cell_value in enumerate(row):
                        if cell_value == Lplate:
                            # Found the target data
                            # Increment its value by 1
                            conf = float(data[row_index][column_index - 1])
                            if conf < veh_conf:
                                data[row_index][column_index - 1] = str(veh_conf)
                                data[row_index][column_index - 2] = clss1[veh_cls]
                            current_value = int(data[row_index][column_index + 2])
                            data[row_index][column_index + 3] = str(current_value + 1)
                            if current_value >= 10:
                                data[row_index][column_index + 4] = 'Yellow'
                            elif current_value >= 20:
                                data[row_index][column_index + 4] = 'Green'
                            elif current_value >= 30:
                                data[row_index][column_index + 4] = 'Premium'
                            elif current_value >= 40:
                                data[row_index][column_index + 4] = 'Gold'
                            else:
                                data[row_index][column_index + 4] = 'Red'
                            data[row_index][column_index + 2] = str(clss4[veh_cls])
                            formatted_datetime = current_datetime.strftime("%Y-%m-%d %H:%M:%S")
                            data[row_index][column_index + 3] = formatted_datetime
                            # Write the updated data back to the CSV file
                            with open(csv_file_path, 'w', newline='') as csv_file:
                                csv_writer = csv.writer(csv_file)
                                csv_writer.writerows(data)
        else:
            # Format the datetime as a string
            formatted_datetime = current_datetime.strftime("%Y-%m-%d %H:%M:%S")
            csv_writer = csv.writer(f)
            # Write the data
            csv_writer.writerow([clss1[veh_cls], veh_conf, Lplate, clss4[veh_cls], '1', 'Red', formatted_datetime])


def plate_format(text):
    if len(text) > 10:
        return False
    elif len(text) == 5:
        if (text[0] in string.ascii_uppercase or text[0] in dict_int_to_char.keys()) and \
                (text[1] in string.ascii_uppercase or text[1] in dict_int_to_char.keys()) and \
                (text[2] in ['0', '1', '2', '3', '4', '5', '6', '7', '8', '9'] or text[
                    2] in dict_char_to_int.keys()) and \
                (text[3] in ['0', '1', '2', '3', '4', '5', '6', '7', '8', '9'] or text[3] in string.ascii_uppercase or
                 text[3] in dict_char_to_int.keys()) and \
                (text[4] in ['0', '1', '2', '3', '4', '5', '6', '7', '8', '9'] or text[4] in dict_char_to_int.keys()):
            return True
    elif len(text) == 6:
        if (text[0] in string.ascii_uppercase or text[0] in dict_int_to_char.keys()) and \
                (text[1] in string.ascii_uppercase or text[1] in dict_int_to_char.keys()) and \
                (text[2] in ['0', '1', '2', '3', '4', '5', '6', '7', '8', '9'] or text[
                    2] in dict_char_to_int.keys()) and \
                (text[3] in ['0', '1', '2', '3', '4', '5', '6', '7', '8', '9'] or text[3] in string.ascii_uppercase or
                 text[3] in dict_char_to_int.keys()) and \
                (text[4] in ['0', '1', '2', '3', '4', '5', '6', '7', '8', '9'] or text[4] in string.ascii_uppercase or
                 text[4] in dict_char_to_int.keys()) and \
                (text[5] in ['0', '1', '2', '3', '4', '5', '6', '7', '8', '9'] or text[5] in dict_char_to_int.keys()):
            return True
    elif len(text) == 7:
        if (text[0] in string.ascii_uppercase or text[0] in dict_int_to_char.keys()) and \
                (text[1] in string.ascii_uppercase or text[1] in dict_int_to_char.keys()) and \
                (text[2] in ['0', '1', '2', '3', '4', '5', '6', '7', '8', '9'] or text[
                    2] in dict_char_to_int.keys()) and \
                (text[3] in ['0', '1', '2', '3', '4', '5', '6', '7', '8', '9'] or text[3] in string.ascii_uppercase or
                 text[3] in dict_char_to_int.keys()) and \
                (text[4] in ['0', '1', '2', '3', '4', '5', '6', '7', '8', '9'] or text[4] in string.ascii_uppercase or
                 text[4] in dict_char_to_int.keys()) and \
                (text[5] in ['0', '1', '2', '3', '4', '5', '6', '7', '8', '9'] or text[5] in string.ascii_uppercase or
                 text[5] in dict_char_to_int.keys()) and \
                (text[6] in ['0', '1', '2', '3', '4', '5', '6', '7', '8', '9'] or text[6] in dict_char_to_int.keys()):
            return True
    elif len(text) == 8:
        if (text[0] in string.ascii_uppercase or text[0] in dict_int_to_char.keys()) and \
                (text[1] in string.ascii_uppercase or text[1] in dict_int_to_char.keys()) and \
                (text[2] in ['0', '1', '2', '3', '4', '5', '6', '7', '8', '9'] or text[
                    2] in dict_char_to_int.keys()) and \
                (text[3] in ['0', '1', '2', '3', '4', '5', '6', '7', '8', '9'] or text[3] in string.ascii_uppercase or
                 text[3] in dict_char_to_int.keys()) and \
                (text[4] in ['0', '1', '2', '3', '4', '5', '6', '7', '8', '9'] or text[4] in string.ascii_uppercase or
                 text[4] in dict_char_to_int.keys()) and \
                (text[5] in ['0', '1', '2', '3', '4', '5', '6', '7', '8', '9'] or text[5] in string.ascii_uppercase or
                 text[5] in dict_char_to_int.keys()) and \
                (text[6] in ['0', '1', '2', '3', '4', '5', '6', '7', '8', '9'] or text[
                    6] in dict_char_to_int.keys()) and \
                (text[7] in ['0', '1', '2', '3', '4', '5', '6', '7', '8', '9'] or text[7] in dict_char_to_int.keys()):
            return True

    elif len(text) == 9:
        if (text[0] in string.ascii_uppercase or text[0] in dict_int_to_char.keys()) and \
                (text[2] in ['0', '1', '2', '3', '4', '5', '6', '7', '8', '9'] or text[
                    2] in dict_char_to_int.keys()) and \
                (text[3] in ['0', '1', '2', '3', '4', '5', '6', '7', '8', '9'] or text[3] in string.ascii_uppercase or
                 text[3] in dict_char_to_int.keys()) and \
                (text[4] in ['0', '1', '2', '3', '4', '5', '6', '7', '8', '9'] or text[4] in string.ascii_uppercase or
                 text[4] in dict_char_to_int.keys()) and \
                (text[5] in ['0', '1', '2', '3', '4', '5', '6', '7', '8', '9'] or text[5] in string.ascii_uppercase or
                 text[5] in dict_char_to_int.keys()) and \
                (text[6] in ['0', '1', '2', '3', '4', '5', '6', '7', '8', '9'] or text[
                    6] in dict_char_to_int.keys()) and \
                (text[7] in ['0', '1', '2', '3', '4', '5', '6', '7', '8', '9'] or text[
                    7] in dict_char_to_int.keys()) and \
                (text[8] in ['0', '1', '2', '3', '4', '5', '6', '7', '8', '9'] or text[8] in dict_char_to_int.keys()):
            return True
    elif len(text) == 10:
        if (text[0] in string.ascii_uppercase or text[0] in dict_int_to_char.keys()) and \
                (text[1] in string.ascii_uppercase or text[1] in dict_int_to_char.keys()) and \
                (text[2] in ['0', '1', '2', '3', '4', '5', '6', '7', '8', '9'] or text[
                    2] in dict_char_to_int.keys()) and \
                (text[3] in ['0', '1', '2', '3', '4', '5', '6', '7', '8', '9'] or text[
                    3] in dict_char_to_int.keys()) and \
                (text[4] in string.ascii_uppercase or text[4] in dict_char_to_int.keys()) and \
                (text[5] in string.ascii_uppercase or text[5] in dict_char_to_int.keys()) and \
                (text[6] in ['0', '1', '2', '3', '4', '5', '6', '7', '8', '9'] or text[
                    6] in dict_char_to_int.keys()) and \
                (text[7] in ['0', '1', '2', '3', '4', '5', '6', '7', '8', '9'] or text[
                    7] in dict_char_to_int.keys()) and \
                (text[8] in ['0', '1', '2', '3', '4', '5', '6', '7', '8', '9'] or text[
                    8] in dict_char_to_int.keys()) and \
                (text[9] in ['0', '1', '2', '3', '4', '5', '6', '7', '8', '9'] or text[9] in dict_char_to_int.keys()):
            return True
    else:
        return False


model1 = YOLO(r"C:\Users\abdul\OneDrive\Documents\truck3\Veh.pt")
model2 = YOLO(r"C:\Users\abdul\OneDrive\Documents\truck3\finalpt.pt")
model3 = YOLO(r"C:\Users\abdul\Downloads\best (5).pt")

# print(model3.names)
# print(model1.names)
# print(model2.names)


# Samples
cap = cv2.VideoCapture(r"C:\Users\abdul\Downloads\pexels-alex-moisieiev-13109344 (1080p).mp4")
# cap = cv2.VideoCapture(r"C:\Users\abdul\Downloads\india_-_8698 (540p).mp4")
# cap = cv2.VideoCapture(r"C:\Users\abdul\Downloads\pexels-mehtab-singh-edhan-18883022 (2160p).mp4")
# cap = cv2.VideoCapture(r"C:\Users\abdul\Downloads\road_-_84222 (1440p).mp4")

# cap = cv2.VideoCapture(r"C:\Users\abdul\Downloads\VID-20240130-WA0008.mp4")
# cap = cv2.VideoCapture(r"C:\Users\abdul\Downloads\2024021675624140 PM.mp4")#1
# cap = cv2.VideoCapture(r"C:\Users\abdul\Downloads\2024021675903060 PM.mp4")
# cap = cv2.VideoCapture(r"C:\Users\abdul\Downloads\2024021680648226 PM.mp4")
# cap = cv2.VideoCapture(r"C:\Users\abdul\Downloads\2024020293244928 PM_703455373_camera 17@DS-7216HQHI-F1(703455373)_17_video.mov")


#cap = cv2.imread(r"C:\Users\abdul\Downloads\im6.jpg")
# res = model1.predict(source= r"C:\Users\abdul\Downloads\download.jpg", conf = 0.5, save = True)
# cap = cv2.imread(r"C:\Users\abdul\Downloads\WhatsApp Image 2024-02-08 at 2.42.05 PM.jpeg")
# cap = cv2.imread(r"C:\Users\abdul\Downloads\archive\Vehicle_5_classes_sample\Tempo Traveller\20210502_10_20_11_000_gzkBuPo3yjZoBEHQDILlKyP61By2_T_4160_3120.jpg")


cap.set(4, 720)
cap.set(5, 520)


while True:
    # res, img = cap.read()#
    img1 =   cv2.resize(cap, (1280,720))
    result1 = model1(img1, stream=True)
    result2 = model2(img1, stream=True)
    for r in result1:
        box = r.boxes
        for b in box:
            veh_conf = math.ceil((b.conf[0] * 100)) / 100
            if veh_conf >= 0.5:
                a1, b1, a2, b2 = b.xyxy[0]
                a1, b1, a2, b2 = int(a1), int(b1), int(a2), int(b2)
                veh_cls = int(b.cls[0])
                cv2.rectangle(img1, (a1, b1), (a2, b2), (246, 25, 25), 2)
                cvzone.putTextRect(img1, f'{clss1[veh_cls]} {veh_conf}', (max(0, a1), max(30, b1)), scale=1,
                                   thickness=1,
                                   colorR=(0, 2, 10))
                for p in result2:
                    box = p.boxes
                    for b in box:
                        x11, y11, x12, y12 = b.xyxy[0]
                        x11, y11, x12, y12 = int(x11), int(y11), int(x12), int(y12)
                        plate_conf = math.ceil((b.conf[0] * 100)) / 100
                        cls = int(b.cls[0])

                        plate_ = img1[y11:y12, x11:x12]
                        # gray = cv2.cvtColor(plate_, cv2.COLOR_RGB2GRAY)
                        # result = reader.readtext(gray)
                        # text = ""
                        #
                        # for res in result:
                        #     if len(result) == 1:
                        #         text = res[1]
                        #     if len(result) > 1 and len(res[1]) > 6 and res[2] > 0.5:
                        #         text = res[1]
                        # text = str(text).upper()
                        # text = text.replace(" ", "")
                        # text = text.replace('-', '')
                        # text = text.replace('{', '')
                        # text = text.replace('}', '')
                        # print('text:', text)
                        text4 = ''
                        result3 = model3(plate_, stream=True)
                        for r in result3:
                            box = r.boxes
                            data = box.data
                            sorted_data = sorted(data, key=lambda x: x[1])
                            j = 0
                            for i in range(0, len(sorted_data) - 1):
                                diff = (int(sorted_data[i + 1][1]) - int(sorted_data[i][1]))
                                if diff > 5:
                                    break
                                else:
                                    j = j + 1
                            if j <= 4:
                                y_sort_data = sorted(sorted_data[0:4], key=lambda x: x[0])
                                ysort_data = sorted(sorted_data[4:], key=lambda x: x[0])
                            elif 4 < j <= 5:
                                y_sort_data = sorted(sorted_data[0:5], key=lambda x: x[0])
                                ysort_data = sorted(sorted_data[6:], key=lambda x: x[0])
                            elif 5 < j <= 6:
                                y_sort_data = sorted(sorted_data[0:6], key=lambda x: x[0])
                                ysort_data = sorted(sorted_data[6:], key=lambda x: x[0])
                            else:
                                y_sort_data = sorted(sorted_data, key=lambda x: x[0])
                                ysort_data = []

                            x = y_sort_data + ysort_data
                            y = x
                            flag = False
                            i = 0
                            j = 1

                            while i < len(x) - 1 and j < len(y):
                                if abs(x[i][0] - y[j][0]) <= 1:
                                    if x[i][4] > y[j][4]:
                                        text4 += clss3[int(x[i][5])]
                                    else:
                                        text4 += clss3[int(y[j][5])]
                                    i = i + 2
                                    j = j + 2
                                    flag = True
                                else:
                                    text4 += clss3[int(x[i][5])]
                                    flag = True
                                    i = i + 1
                                    j = j + 1

                            if flag == True:
                                text4 += clss3[int(x[i][5])]
                            print("text:", text4)

                        if plate_format(text4):
                            cv2.rectangle(img1, (x11, y11), (x12, y12), (6, 39, 255), 3)
                            cvzone.putTextRect(img1, f'{text4} {plate_conf}', (max(x11, x12), max(y11, y12)), scale=1,
                                               thickness=1,
                                               colorR=(0, 2, 10))
                            write_file(text4, veh_cls, veh_conf)

    cv2.imshow('img', img1)
    cv2.waitKey(0)
